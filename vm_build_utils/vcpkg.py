# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0
'utilities for vcpkg builds'
import sys
import json
import logging
import subprocess
from pathlib import Path
from . import cmd


class Build():
  'calls vcpkg to build and then potentially install libs into venv'

  def __init__(self, run_mode, source_root, json_path):

    self.run_mode = run_mode
    self.source_root = Path(source_root).resolve()

    with open(json_path) as fd:
      config = json.load(fd)

    os = sys.platform.lower()
    if os.startswith('linux'):
      os = 'linux'
    assert os in config, 'missing os[%s] in[%s]' % (os, str(json_path))
    self.config = config[os]

    self.vcpkg_path = self.source_root / self.config['vcpkg_path']
    self.pkg_root = self.source_root / self.config['pkg_root']

    self.pkgs = self.config['pkgs']
    self.triplet_overlay = self.config['triplet_overlay']
    self.ports_overlay = self.config['triplet_overlay'] + '/ports'

  def check_call(self, cmd_args, cwd, **kwargs):
    'call a subprocess, exit on error or return on success'
    try:
      return cmd.execute(cmd_args,
                         cwd=str(cwd),
                         run_mode=self.run_mode,
                         log_level=logging.INFO,
                         **kwargs)
    except subprocess.CalledProcessError:
      sys.exit(666)

  def rel_vcpkg_path(self):
    'relative path to vcpkg'
    return self.vcpkg_path.relative_to(self.source_root)

  def bootstrap(self):
    'build vcpkg for the first time if needed'

    if self.vcpkg_path.exists():
      logging.debug('skipping vcpkg bootstrap')
      return

    bootstrap_path = self.vcpkg_path.parent / 'bootstrap-vcpkg.sh'
    assert bootstrap_path.exists(), 'missing vcpkg build files'

    self.check_call([str(bootstrap_path)], self.source_root)

  def build(self):
    'run a vcpkg install command to build libs'

    lib_dir = str(cmd.env_root('lib'))
    for pkg, triplets in self.pkgs.items():
      for triplet in triplets:

        build_cmd = ' '.join([
            'INSTALL_NAME_DIR=' + lib_dir,
            str(self.vcpkg_path),
            'install',
            '--recurse',
            '--triplet',
            triplet,
            '--overlay-triplets=%s' % self.triplet_overlay,
            '--overlay-ports=%s' % self.ports_overlay,
            pkg,
        ])
        logging.info(build_cmd)
        subprocess.check_call(build_cmd, shell=True)
