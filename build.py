#!/usr/bin/env python
# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0
'''
run a build using cmake and make or xcode
'''
from __future__ import print_function
import os
import re
import sys
import argparse
import logging
import subprocess
import unittest
import importlib
import pprint
from pathlib import Path

sys.dont_write_bytecode = True

#pylint: disable=wrong-import-position
import vm_build_utils.cmd
import vm_build_utils.git_module_info
import vm_build_utils.vcpkg


def build_parser():
  'build commands'

  AP = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=vm_build_utils.cmd.HELP_FMT,
  )
  AP.add_argument(
      '--swift',
      help='compile swift code using the xcode toolchain',
      action='store_true',
  )
  AP.add_argument(
      '--ios',
      help='configure the xcode toolchain to build for ios',
      action='store_true',
  )
  AP.add_argument(
      '--toolchain-path',
      help='path to a toolchain file - stomped by --ios and --swift',
      default='../foundation/third_party/vcpkg/scripts/buildsystems/vcpkg.cmake',
  )
  AP.add_argument(
      '--build-type',
      help='compile release, debug or release optimization with debug symbols',
      choices=['RelWithDebInfo', 'Release', 'Debug'],
      default='Release',
  )
  AP.add_argument(
      '--build-target',
      help='specify a target to build',
      default=None,
  )

  AP.add_argument(
      '--open-xcode',
      help='does nothing',
      action='store_true',
  )

  AP.add_argument(
      '--xcode-proj',
      help='name of the project to open / build',
      default=None,
  )

  AP.add_argument(
      '--doc',
      help='run a documentation specific build',
      action='store_true',
  )
  AP.add_argument(
      '--resource',
      help='run a resource specific build',
      action='store_true',
  )
  AP.add_argument(
      '--unit-tests',
      help='build unit-tests',
      action='store_true',
  )
  AP.add_argument(
      '--threads',
      help='number of make threads to use',
      default=8,
  )
  AP.add_argument(
      '--project-dir',
      help='path to the project',
      default='.',
  )
  AP.add_argument(
      '--bundle-path',
      help='path to the bundle executable (builds ruby projects)',
      default='/usr/local/opt/ruby/bin/bundle',
  )
  commands = AP.add_subparsers(
      dest='command',
      help='available commands to run',
  )

  commands.add_parser(
      'uninstall',
      help='remove artifacts installed by last build',
  )

  incremental = commands.add_parser(
      'incremental',
      help='run a build only updating those things that are known changed',
  )
  incremental.add_argument('dummy', help='vestigial', nargs='?')

  clean = commands.add_parser(
      'clean',
      help='run a fresh build after removing all build artifacts',
  )
  clean.add_argument('clean', help='vestigial', nargs='?')

  test = commands.add_parser(
      'test',
      help='run a fresh build after removing all build artifacts',
  )
  test.add_argument(
      'pattern',
      help='optional regexp to match a test suite or individual test function',
      nargs='?',
  )

  lint = commands.add_parser(
      'lint',
      help='keep track of the current pylint score for a directory',
  )
  lint.add_argument(
      'lint_path',
      help='path to python module on which to run pylint',
  )

  vcpkg = commands.add_parser(
      'vcpkg',
      help='build foundational c++ libraries with vcpkg',
  )
  vcpkg.add_argument(
      '--vcpkg-json',
      help='path to the vcpkg json config',
      default='etc/vcpkg/vcpkg.json',
  )

  return AP


class Build():
  'describes build paths and commands to call'

  def __init__(self):

    self.swift = self.ios = self.build_type = self.build_target = None
    self.open_xcode = self.doc = self.resource = self.unit_tests = None
    self.threads = self.project_dir = self.command = self.pattern = None
    self.lint_path = self.verbose = self.run_mode = self.run_never = None
    self.run_always = self.run_confirm = self.dummy = self.incremental = None
    self.clean = self.uninstall = self.test = self.lint = None
    self.toolchain_path = self.vcpkg_json = self.xcode_proj = None
    self.bundle_path = None

    args = vm_build_utils.cmd.parse_args(build_parser())

    # copy args into self
    for key, value in vars(args).items():
      assert hasattr(self, key)
      setattr(self, key, value)

    if self.swift:
      logging.debug('turning off resources for swift build')
      self.resource = False

    _, self.devrel = vm_build_utils.cmd.project_path_components()
    self.root = vm_build_utils.cmd.project_path()
    self.project_dir = Path(self.project_dir).resolve()
    self.project = self.project_dir.name
    self.venv_root = vm_build_utils.cmd.env_root()

    devrel_toolchain = [self.devrel]

    self.toolchain = ''
    if self.ios:
      self.toolchain = 'ios'
      self.swift = True
    elif self.swift:
      self.toolchain = 'osx'

    if self.toolchain:
      devrel_toolchain.append(self.toolchain)
      self.toolchain_path = os.path.join(
          self.project_dir,
          'build',
          'cmake',
          self.toolchain + '_toolchain.cmake',
      )

    devrel_tc_dir = '_'.join(devrel_toolchain)
    self.build_dir = self.root / 'build' / devrel_tc_dir / self.project

    project_vendor = self.project + '_vendor'
    self.gem_bundle_path = self.root / 'build' / devrel_tc_dir / project_vendor

    logging.debug(pprint.pformat(dict(vars(self))))

    self.bundle_path = Path(self.bundle_path)

    self.run()

  def check_call(self, cmd, cwd):
    'call a subprocess, exit on error or return on success'
    try:
      vm_build_utils.cmd.execute(
          cmd,
          cwd=str(cwd),
          run_mode=self.run_mode,
          log_level=logging.INFO,
      )
    except subprocess.CalledProcessError:
      sys.exit(666)

  @staticmethod
  def filter_matching_tests(test_suite, pattern):
    'yields a flat sequence of unittests matching regexp pattern'
    for test in test_suite:
      if isinstance(test, unittest.TestSuite):
        for sub_match in Build.filter_matching_tests(test, pattern):
          yield sub_match

      else:
        match = bool(re.search(pattern, test.id()))
        logging.debug('%s pattern:%s match:%s ', test.id(), pattern, match)
        if match:
          yield test

  def run_vcpkg(self):
    'run a vcpkg build'
    vcpkg_build = vm_build_utils.vcpkg.Build(
        self.run_mode,
        self.project_dir,
        self.vcpkg_json,
    )
    vcpkg_build.bootstrap()
    vcpkg_build.build()

  def run_lint(self):
    'run lint for python only right now'
    if self.swift:
      raise ValueError('only python linting supported')

    self.check_call(
        [
            'python',
            '-m',
            'pylint',
            self.lint_path,
        ],
        '.',
    )

  def run_test(self):
    'run tests using ctest  / xctest for xcode or python test otherwise'
    if self.swift:

      pattern = self.pattern
      if pattern is None:
        pattern = '.'

      self.check_call(
          [
              'ctest',
              '--verbose',
              '--verbose',
              '--build-config',
              self.build_type,
              '--tests-regex',
              pattern,
          ],
          self.build_dir,
      )
      return

    pattern = self.pattern
    if pattern is None:
      pattern = '.'

    if pattern.endswith('.py'):
      pattern = pattern[:-3]

    test_suite = unittest.TestSuite()

    test_dir = self.project_dir / 'test/python'
    sys.path.insert(0, str(test_dir))
    for root_path, _, file_names in os.walk(test_dir):

      for file_name in file_names:
        if file_name == '__init__.py':
          continue
        abs_file_path = Path(root_path) / file_name
        if abs_file_path.suffix != '.py':
          continue
        rel_file_path = abs_file_path.relative_to(test_dir)
        module_path = str(rel_file_path).replace('/', '.').replace('.py', '')
        with vm_build_utils.cmd.T('import ' + module_path, level=logging.DEBUG):
          module = importlib.import_module(module_path)
          tmp_test_suite = unittest.loader.findTestCases(module)
          for test in self.filter_matching_tests(tmp_test_suite, pattern):
            test_suite.addTest(test)

    with vm_build_utils.cmd.T('build runner', level=logging.DEBUG):
      runner = unittest.runner.TextTestRunner(verbosity=2)

    with vm_build_utils.cmd.T('configure logs', level=logging.DEBUG):
      logger = logging.getLogger()
      logger.propagate = False

      for modname in ['boto3', 'botocore', 's3transfer', 'urllib3']:
        modlogger = logging.getLogger(modname)
        modlogger.setLevel(logging.WARNING)

    with vm_build_utils.cmd.T('run test suite', level=logging.DEBUG):
      return runner.run(test_suite)

  def run_ios(self, cmake_cmd):
    'run cmake to create build dir, run cocoa pods install, open xcode'

    self.check_call(cmake_cmd, cwd=self.build_dir)

    is_gem = (self.build_dir / 'Gemfile').exists()
    is_gem_lock = (self.build_dir / 'Gemfile.lock').exists()

    pod_exec_prefix = []
    if is_gem:
      pod_exec_prefix = [self.bundle_path, 'exec']
      if not is_gem_lock:
        logging.info('installing Gem bundle')
        self.check_call(
            [self.bundle_path, 'config', 'set', 'path', self.gem_bundle_path],
            cwd=self.build_dir,
        )

        self.check_call(
            [self.bundle_path, 'install'],
            cwd=self.build_dir,
        )

    if self.xcode_proj is not None:
      xcode_prjs = list(self.build_dir.glob(self.xcode_proj + '/*.xcodeproj'))
    else:
      xcode_prjs = list(self.build_dir.glob('*/*.xcodeproj'))

    for xcode_prj in xcode_prjs:

      xc_build_dir = xcode_prj.parent

      is_pod = (xc_build_dir / 'Podfile').exists()

      if is_pod:
        orig_xcode_prj = xcode_prj

        xcode_prj = str(orig_xcode_prj.with_suffix('.xcworkspace'))

        logging.info('installing Pods')
        self.check_call(
            pod_exec_prefix + ['pod', 'install'],
            cwd=xc_build_dir,
        )

      self.check_call(['open', xcode_prj], cwd=xc_build_dir)

  def run(self):
    'inspect python executable path and cwd, run build appropriately'

    if self.command == 'vcpkg':
      return self.run_vcpkg()

    if self.command == 'lint':
      return self.run_lint()

    if self.command == 'test':
      return self.run_test()

    module_info = vm_build_utils.git_module_info.get_all_module_info(
        self.project_dir)

    default_vm_sdk_info = dict(
        branch='master',
        commit='9312884026cd9637cc97c4684a8236547941b49c',
        date='2019-12-02 12:36:33 -0800',
        name='vm-sdk',
        now='2019-12-02 16:22:28.452174',
        path=os.path.join(self.project_dir, '/third_party/vm-sdk-internal'),
    )

    vm_sdk_info = module_info.get('vm-sdk', default_vm_sdk_info)

    cmake_opts = dict(
        PYTHON_EXECUTABLE=os.path.normpath(os.path.abspath(sys.executable)),
        SITE_PACKAGES=vm_build_utils.cmd.get_sitepackages_path(),
        # CMAKE_FIND_ROOT_PATH=self.venv_root,
        CMAKE_INSTALL_PREFIX=self.venv_root,
        CMAKE_BUILD_TYPE=self.build_type,
        TEST_DATA_PATH=self.root / 'data' / 'test',
        VM_LIB_DATE='"%s"' % vm_sdk_info['date'],
        VM_LIB_BRANCH='"%s"' % vm_sdk_info['branch'],
        VM_LIB_COMMIT='"%s"' % vm_sdk_info['commit'],
        DOC_BUILD=str(int(self.doc)),
        RESOURCE_BUILD=str(int(self.resource)),
        SWIFT_BUILD=str(int(self.swift)),
        TEST_BUILD=str(int(self.unit_tests)),
    )

    if self.command == 'uninstall':
      with open(os.path.join(self.build_dir, 'install_manifest.txt'),
                'r') as fd:
        installed_files = fd.read().split('\n')

      for installed_file in installed_files:
        self.check_call(['rm', '-f', installed_file], self.root)

        if installed_file.endswith('.py'):
          self.check_call(['rm', '-f', installed_file + 'c'], self.root)

      return

    if self.command == 'clean':
      self.check_call(['rm', '-rf', self.build_dir], self.root)

    self.check_call(['mkdir', '-p', self.build_dir], self.root)

    cmake_cmd_suffix = []
    cmake_cmd = ['cmake', '--target', 'clean']
    for varname, value in cmake_opts.items():
      cmake_cmd.append('-D%s=%s' % (varname, value))

    cmake_cmd.append(self.project_dir)

    if self.toolchain_path is not None:
      cmake_cmd.append('-D%s=%s' % (
          'CMAKE_TOOLCHAIN_FILE',
          self.toolchain_path,
      ))

    if self.ios:
      return self.run_ios(cmake_cmd)

    if self.swift:
      cmake_cmd += [
          '-GXcode',
          '--debug-trycompile',
      ]
      cmake_cmd_suffix += ['-quiet']
    self.check_call(cmake_cmd, cwd=self.build_dir)

    build_cmd = ['cmake', '--build', '.']

    build_target = self.build_target
    if not self.swift and build_target is None:
      build_target = 'install'

    if build_target is not None:
      build_cmd += ['--target', build_target]

    build_cmd += ['--config', self.build_type]

    if self.verbose:
      build_cmd += ['--verbose']

    build_cmd += ['--parallel', str(self.threads)]
    if cmake_cmd_suffix:
      build_cmd.append('--')
      build_cmd += cmake_cmd_suffix

    self.check_call(build_cmd, cwd=self.build_dir)


if __name__ == '__main__':
  vm_build_utils.cmd.setup_logging()
  Build()
