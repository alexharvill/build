#!/usr/bin/env python
# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0
'''
find source files and apply a license header
'''
import os
import sys
import argparse

AP = argparse.ArgumentParser(description=__doc__)

AP.add_argument(
    '--license',
    help='path to a sample license text file',
)
AP.add_argument(
    '--replace-licenses',
    help='paths to license text files to remove',
    nargs='+',
)

AP.add_argument(
    '--file-types',
    help='list of file extensions',
    nargs='*',
    default=[
        '.py',
        '.swift',
        '.cpp',
        '.h',
        '.proto',
        '.txt',
        '.sh',
        '.md',
        '.rst',
        '.yml',
        '.cmake',
    ],
)
AP.add_argument(
    '--exclude',
    help='list of directory and file names to exclude',
    nargs='*',
    default=['third_party'],
)

AP.add_argument(
    '--directory',
    help='path to a base directory to search inside',
    default='./',
)

AP.add_argument(
    '--action',
    help='path to a base directory to search inside',
    choices=['print', 'execute'],
)


def process_file(ext, path, header, relpace_headers, execute):
  'add a header to a file, possibly changing # style comments to //'
  if ext in ('.md', '.rst'):
    header = header.replace('#', '')
    relpace_headers = [x.replace('#', '') for x in relpace_headers]
    header = header.replace('\n', '\n\n')
    relpace_headers = [x.replace('\n', '\n\n') for x in relpace_headers]
  elif ext not in ('.py', '.sh', '.txt', '.yml', '.cmake'):
    header = header.replace('#', '//')
    relpace_headers = [x.replace('#', '//') for x in relpace_headers]

  with open(path) as fd:
    lines = fd.read()

  shebang = ''
  if lines.startswith('#!'):
    shebang, lines = lines.split('\n', 1)
    shebang = shebang + '\n'

  for relpace_header in relpace_headers:
    if lines.startswith(relpace_header):
      print('replacing ' + path)
      lines = lines[len(relpace_header):]

  if lines.startswith(header):
    print('skipping ' + path)
    return

  if execute:
    with open(path, 'w') as fd:
      fd.write(shebang)
      fd.write(header)
      fd.write(lines)
  else:
    sys.stdout.write(shebang)
    sys.stdout.write(header)
    context = 200
    if len(lines) > context:
      sys.stdout.write(lines[:context])
    else:
      sys.stdout.write(lines)


def main():
  'find files, add license'
  args = AP.parse_args()
  with open(args.license) as fd:
    header = fd.read()

  replace_headers = []
  for rl in args.replace_licenses:
    with open(rl) as fd:
      replace_headers.append(fd.read())

  print(args)
  for rh in replace_headers:
    print('replace:---------------------\n%s-------------' % (rh))
  print('header:---------------------\n%s-------------' % (header))

  exclude = set(args.exclude)
  exts = set(args.file_types)

  items = []

  for root_path, dir_names, file_names in os.walk(args.directory):

    filtered = set(dir_names) - exclude

    del dir_names[:]

    dir_names[:] = filtered
    # for dir_name in filtered:
    # dir_names.append(dir_name)

    for file_name in file_names:
      _, ext = os.path.splitext(file_name)
      if ext not in exts:
        continue
      if file_name in exclude:
        continue
      file_path = os.path.join(root_path, file_name)

      items.append((ext, file_path))

  if args.action == 'print':
    for ext, path in items:
      print('\n\n\n' + path)
      process_file(ext, path, header, replace_headers, False)

  elif args.action == 'execute':
    for ext, path in items:
      print('\n\n\n' + path)
      process_file(ext, path, header, replace_headers, True)
  # if args.action == 'execute':
  # for path in paths:
  # print(path)


if __name__ == '__main__':
  main()
