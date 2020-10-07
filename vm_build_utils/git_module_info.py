#!/usr/bin/env python
# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0
'''
list information for git submodules
'''
from __future__ import print_function
import os
import json
import datetime
import subprocess


def get_module_info(path):
  'return branch and commit for a git repo or submodule'
  path = str(path)
  branch = subprocess.check_output(
      [
          'git',
          'rev-parse',
          '--abbrev-ref',
          'HEAD',
      ],
      cwd=path,
  ).decode('utf-8').strip()
  commit = subprocess.check_output(
      [
          'git',
          'rev-parse',
          'HEAD',
      ],
      cwd=path,
  ).decode('utf-8').strip()
  date = subprocess.check_output(
      [
          'git',
          'show',
          '-s',
          '--format=%ci',
          commit,
      ],
      cwd=path,
  ).decode('utf-8').strip()
  try:
    subprocess.check_call(
        [
            'git',
            'update-index',
            '--ignore-submodules',
            '--refresh',
        ],
        cwd=path,
    )
  except subprocess.CalledProcessError:
    commit += '-dirty'

  return dict(
      name=os.path.basename(path),
      path=path,
      branch=branch,
      commit=commit,
      date=date,
      now=str(datetime.datetime.now()),
  )


def get_all_module_info(root_path):
  'return a dictionary of branch, commit for repo and submodules'
  root_path = str(root_path)
  r = subprocess.check_output(
      [
          'git',
          'submodule',
          '--quiet',
          'foreach',
          '--recursive',
          'echo `pwd`',
      ],
      cwd=root_path,
  )
  info = get_module_info(root_path)
  result = {}
  result[info['name']] = info

  for path in r.decode('utf-8').split('\n'):
    if path == '':
      continue
    info = get_module_info(path)
    result[info['name']] = info

  filter_names = {}
  for name, info in result.items():
    filter_names[name.replace('-internal', '')] = info
  return filter_names


def main():
  'print module info to stdout as json'
  result = get_all_module_info(os.getcwd())
  print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
  main()
