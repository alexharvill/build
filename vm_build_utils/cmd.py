# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0
'''
batch and commandline utilities
'''
from __future__ import print_function
import gc
import os
import ssl
import sys
import site
import shlex
import logging
import warnings
import argparse
import platform
import resource
import subprocess
import time

if sys.version_info.major < 3 or sys.version_info.minor < 5:
  warnings.warn('old python')

#pylint: disable=wrong-import-position
from pathlib import Path
try:
  import numpy
except ImportError:
  numpy = None
try:
  from pynvml.smi import nvidia_smi
except ImportError:
  nvidia_smi = None

CODE_RESET = '\033[0m'
CODE_BLACK = '\033[1;30m'
CODE_RED = '\033[1;31m'
CODE_GREEN = '\033[1;32m'
CODE_YELLOW = '\033[1;33m'
CODE_BLUE = '\033[1;34m'
CODE_MAGENTA = '\033[1;35m'
CODE_CYAN = '\033[1;36m'
CODE_WHITE = '\033[1;37m'

RUN_CMD_ALWAYS = 'RUN_CMD_ALWAYS'
RUN_CMD_CONFIRM = 'RUN_CMD_USER_CONFIRMATION'
RUN_CMD_NEVER = 'RUN_CMD_NEVER'
USER_CONFIRM_ALWAYS = False


def confirm(run_mode, cmd_str):
  'optionally ask user for confirmation with info about a cmd about to be run'

  #pylint: disable=global-statement
  global USER_CONFIRM_ALWAYS

  if run_mode == RUN_CMD_NEVER:
    return False

  if not USER_CONFIRM_ALWAYS and run_mode == RUN_CMD_CONFIRM:
    c = input('run command [%s] ? (N)o / (Y)es / (A)lways:' % (cmd_str))

    if not isinstance(c, str) or c == '':
      return False

    c = c.lower()
    if c == 'n':
      return False

    if c == 'a':
      USER_CONFIRM_ALWAYS = True

  return True


def color_text(text, color, fmt=None):
  'if color control string is not None, wrap like so: color|text|color_rest'
  if text is None:
    return None

  if fmt is not None:
    text = fmt % (text)

  if color is None:
    return str(text)

  return color + str(text) + CODE_RESET


def black_text(text, **kwargs):
  'wrap text in terminal encoding characters'
  return color_text(text, CODE_BLACK, **kwargs)


def red_text(text, **kwargs):
  'wrap text in terminal encoding characters'
  return color_text(text, CODE_RED, **kwargs)


def green_text(text, **kwargs):
  'wrap text in terminal encoding characters'
  return color_text(text, CODE_GREEN, **kwargs)


def yellow_text(text, **kwargs):
  'wrap text in terminal encoding characters'
  return color_text(text, CODE_YELLOW, **kwargs)


def blue_text(text, **kwargs):
  'wrap text in terminal encoding characters'
  return color_text(text, CODE_BLUE, **kwargs)


def magenta_text(text, **kwargs):
  'wrap text in terminal encoding characters'
  return color_text(text, CODE_MAGENTA, **kwargs)


def cyan_text(text, **kwargs):
  'wrap text in terminal encoding characters'
  return color_text(text, CODE_CYAN, **kwargs)


def white_text(text, **kwargs):
  'wrap text in terminal encoding characters'
  return color_text(text, CODE_WHITE, **kwargs)


def color_code_stdout(color_code):
  'write color code to stdout and flush'
  if color_code is not None:
    sys.stdout.write(color_code)
    sys.stdout.flush()


def reset_color_code_stdout(color):
  'reset stdout to non normal color code mode flush'
  if color:
    sys.stdout.write(CODE_RESET)
    sys.stdout.flush()


def execute(
    cmd,
    run_mode=RUN_CMD_ALWAYS,
    cwd=None,
    output=False,
    color=True,
    log_level=logging.DEBUG,
    env=None,
):
  '''
  execute a subprocess with
    logging of commandline before output
    optional color coded output
    optional current working directory override
    a run mode that can disable execution, ask for user confirmation, or execute
  '''

  nottext = color_text('not', CODE_RED) if color else 'not'

  cmd = [str(x) for x in cmd]

  cmd_str = color_text(subprocess.list2cmdline(cmd), CODE_GREEN)

  go = confirm(run_mode, cmd_str)
  verb = 'running' if go else nottext + ' running'

  highlight_color = (CODE_YELLOW if go else CODE_GREEN) if color else None
  result_color = CODE_CYAN if color else None

  cwd_str = color_text(cwd, highlight_color)
  cmd_str = color_text(subprocess.list2cmdline(cmd), highlight_color)

  if cwd is None:
    logging.log(log_level, '%s [%s]', verb, cmd_str)
  else:
    logging.log(log_level, 'from [%s] %s [%s]', cwd_str, verb, cmd_str)

  if not go:
    return None

  if not output:
    color_code_stdout(result_color)
    try:
      subprocess.check_call(cmd, cwd=cwd, env=env)
    finally:
      reset_color_code_stdout(color)

  else:
    return subprocess.check_output(cmd, cwd=cwd, env=env)

  return None


def execute_callback(
    message,
    callback,
    args,
    kwargs,
    run_mode=RUN_CMD_ALWAYS,
    color=True,
    log_arguments=True,
    log_time=False,
    log_level=logging.DEBUG,
):
  '''
  execute a python function with
    a run mode that can disable execution, ask for user confirmation, or execute
  '''
  nottext = color_text('not', CODE_RED) if color else 'not'

  go = confirm(run_mode, message)

  verb = 'calling' if go else nottext + ' calling'

  if log_arguments:
    logging.log(
        log_level,
        '%s [%s.%s] with args %s and kwargs %s',
        verb,
        callback.__module__,
        callback.__name__,
        args,
        kwargs,
    )
  else:
    logging.log(
        log_level,
        '%s [%s.%s] to %s',
        verb,
        callback.__module__,
        callback.__name__,
        message,
    )

  if not go:
    return None

  if log_time:
    with T(message + ' total'):
      result = callback(*args, **kwargs)
  else:
    result = callback(*args, **kwargs)

  return result


def set_log_level(level):
  'set the global logging level'
  logging.getLogger('').setLevel(level)


def setup_logging(
    level=logging.DEBUG,
    setup_matplotlib=True,
    setup_lambda=False,
    numpy_precision=3,
    numpy_suppress=True,
    numpy_linewidth=75,
    stream=None,
    color=True,
):
  'setup reasonable logging defaults'

  if setup_lambda:

    color = False

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.propagate = False

    for modname in ['boto3', 'botocore', 's3transfer', 'urllib3']:
      modlogger = logging.getLogger(modname)
      modlogger.setLevel(logging.WARNING)

  elif level == logging.INFO:
    logging.basicConfig(level=logging.INFO, format='%(message)s', stream=stream)
  else:
    logging.basicConfig(
        level=level,
        format='%(levelname)s %(message)s',
        stream=stream,
    )

  logger = logging.getLogger()
  logger.propagate = False

  for modname in ['boto3', 'botocore', 's3transfer', 'urllib3']:
    modlogger = logging.getLogger(modname)
    modlogger.setLevel(logging.WARNING)

  if setup_matplotlib:
    # force matplotlib to never show debug info!
    mpl_logger = logging.getLogger('matplotlib')
    mpl_logger.setLevel(logging.WARNING)

  for num, name, color_code in [
      (logging.CRITICAL, 'BAD ', CODE_RED),
      (logging.ERROR, 'err ', CODE_RED),
      (logging.WARNING, 'warn', CODE_WHITE),
      (logging.INFO, 'info', CODE_BLACK),
      (logging.DEBUG, 'dbg ', CODE_BLACK),
  ]:
    #name = logging.getLevelName(num).lower().ljust(8)
    resolved_name = name
    if color:
      resolved_name = color_text(name, color_code)
    logging.addLevelName(num, resolved_name)

  if numpy is not None:
    numpy.set_printoptions(
        precision=numpy_precision,
        suppress=numpy_suppress,
        linewidth=numpy_linewidth,
    )


def setup_patching(setup_ssl=True):
  '''
  follow this guide to make sure models can be downloaded without error:
  https://github.com/fchollet/deep-learning-models/issues/33#issuecomment-397257502
  '''
  if setup_ssl:
    #pylint: disable=W0212
    ssl._create_default_https_context = ssl._create_unverified_context


def setup_tensorflow():
  'make tensorflow silent unless '
  tf_log_key = 'TF_CPP_MIN_LOG_LEVEL'
  tf_logger = logging.getLogger('tensorflow')
  if tf_log_key not in os.environ:
    os.environ[tf_log_key] = '3'
    tf_logger.setLevel(logging.INFO)
  else:
    tf_logger.setLevel(logging.DEBUG)
  # redirect stdout/stderr, import keras, then restore stdout/stderr
  # avoids keras cluttering up the console during version or other query cmds
  save_stdout, save_stderr = sys.stdout, sys.stderr
  try:
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = sys.stdout
    #pylint: disable=unused-import,import-outside-toplevel
    import tensorflow.keras

  finally:
    sys.stdout, sys.stderr = save_stdout, save_stderr


class HELP_FMT(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawTextHelpFormatter,
):
  '''
  composite class to provide both default args in help and raw help strings
  goes to crazy lengths to split up lists of choices...
  '''

  def format_help(self):
    tmp = argparse.HelpFormatter.format_help(self)
    result = []
    for line in tmp.split('\n'):
      if '[' in line and '{' in line and line.count(',') > 5:
        test = line

        total_whitespace = line.count(' ')
        test = test.strip()
        leading = total_whitespace - test.count(' ')

        if test[0] == '[' and test[-1] == ']':
          test = test[1:-1]

        # use shlex to hanle list tokenizing
        # by turning lists into strings
        test = test.replace('[', '"')
        test = test.replace(']', '"')
        test = test.replace('{', "'")
        test = test.replace('}', "'")
        test = test.replace(' ...', '')

        parts = shlex.split(test, comments=False)

        # remove crazy duplication of the same list
        A = parts[-1]
        B = parts[-2]
        C = "'%s'" % (B)

        if A == C:
          parts.pop()

        norm_line = ' '.join(parts)

        indent = ' ' * leading

        line = indent + ('\n    ' + indent).join(norm_line.split(','))

      result.append(line)

    return '\n'.join(result)


VERBOSE_MAP = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}


def add_verbose_parse_arg(parser):
  'add verbosity levels to a parser'
  parser.add_argument(
      '-v',
      '--verbose',
      action='count',
      help='verbose level... repeat up to 2 times',
  )


def set_log_level_from_args(args):
  'args is a command line parser result - use it to configure logging'
  if args.verbose is None:
    args.verbose = 0
  set_log_level(VERBOSE_MAP[args.verbose])


def add_run_mode_parse_arg(parser):
  'add controls to run sub commands / persistent system operations'
  RUN_MODE_GROUP = parser.add_mutually_exclusive_group()
  RUN_MODE_GROUP.add_argument(
      '--run-never',
      action='store_true',
      help='no actions will be taken, only logging will be performed')
  RUN_MODE_GROUP.add_argument(
      '--run-confirm',
      action='store_true',
      help='actions will be performed with user confirmation')
  RUN_MODE_GROUP.add_argument(
      '--run-always',
      action='store_true',
      help='actions will be performed always [ default ]',
  )


def setup_run_mode(args):
  'args is a command line parser result - use it to configure the run mode'
  if not args.run_confirm and not args.run_never:
    args.run_always = True

  result = None
  if args.run_never:
    result = RUN_CMD_NEVER

  elif args.run_confirm:
    result = RUN_CMD_CONFIRM

  elif args.run_always:
    result = RUN_CMD_ALWAYS

  else:
    raise ValueError('one of [run-never,run-confirm,run-always] must be True')

  return result


def parse_args(parser, args=None):
  'parse, handle logging and run mode arguments'
  add_verbose_parse_arg(parser)

  add_run_mode_parse_arg(parser)

  args = parser.parse_args(args=args)

  set_log_level_from_args(args)

  args.run_mode = setup_run_mode(args)

  return args


KB = float(10**3)
GB = float(10**9)  # 1000000000
MiB = float(2**20)  # 1048576
GiB = float(2**30)  # 1073741824


def current_platform_is_darwin():
  'returns true if current system is darwin, false on linux or windows'
  return platform.system().lower() == 'darwin'


def current_platform_is_linux():
  'returns true if current system is linux, false on darwin or windows'
  return platform.system().lower() == 'linux'


def get_rss():
  'get high water mark resident memory usage'
  rss_bytes = 0
  maxrss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
  if current_platform_is_darwin():
    rss_bytes = maxrss
  else:
    rss_bytes = maxrss * KB

  rss_gb = rss_bytes / GB

  return rss_gb


def get_rss_and_total():
  'resident and total physical memory in GB'
  total = (os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')) / GB
  return (get_rss(), total)


def get_gpu_used_and_total():
  'total physical memory in GB'

  if nvidia_smi is None:
    return 0, 0

  nvsmi = nvidia_smi.getInstance()
  qresult = nvsmi.DeviceQuery('memory.used, memory.total')
  mem = qresult['gpu'][0]['fb_memory_usage']
  assert mem['unit'] == 'MiB'
  used = (mem['used'] * MiB) / GiB
  total = (mem['total'] * MiB) / GiB
  return used, total


class T(object):
  'simple timer'

  def __init__(self, name, level=logging.INFO):
    self.name = name
    self.start = self.end = self.interval = 0
    self.level = level

  def __enter__(self):
    self.start = time.perf_counter()
    return self

  def __exit__(self, *args):
    self.end = time.perf_counter()
    self.interval = self.end - self.start
    gc.collect()
    rss, total = get_rss_and_total()
    gpu_used, gpu_total = get_gpu_used_and_total()
    logging.log(
        self.level,
        '%s [%s sec] [%s/%s GB] [%s/%s GB gpu]',
        self.name.rjust(40),
        yellow_text('% 7.2f' % (self.interval)),
        yellow_text('% 6.2f' % (rss)),
        yellow_text('%02.2f' % (total)),
        yellow_text('% 6.2f' % (gpu_used)),
        yellow_text('%02.2f' % (gpu_total)),
    )


def format_size(byte_size):
  'convert size in bytes to a human readable string'
  if byte_size > 1000 * 1000:
    return '%.1fMB' % (byte_size / 1000.0 / 1000)
  if byte_size > 10 * 1000:
    return '%ikB' % (byte_size / 1000)
  if byte_size > 1000:
    return '%.1fkB' % (byte_size / 1000.0)
  return '%ibytes' % byte_size


def remove_prefix(value, prefix):
  'remove string prefix'
  if value.startswith(prefix):
    return value[len(prefix):]
  return value


def get_sitepackages_path():
  'get path to python site-packages directory'
  try:
    return site.getsitepackages()[0]
  except AttributeError:
    for path in sys.path:
      if 'local' in path:
        continue
      if 'site-packages' in path:
        return path

  raise ValueError('no site packages found')


def executable_path():
  'get a path to the python interpreter than can be tweaked via env var'
  result = sys.executable
  override = os.environ.get('VM_EXECUTABLE')
  if override is not None:
    result = override
  result = str(result)
  result = remove_prefix(result, '/System/Volumes/Data')
  return Path(result)


def project_path_components():
  'validate and return paths related to /comet/PROJECT/env/DEVREL/bin/python'
  template_path = '"/comet/PROJECT/env/DEVREL/bin/python"'
  err_msg = 'python path must be of the form %s' % (template_path)

  python_exec = executable_path()
  assert len(python_exec.parts) >= 6, err_msg

  user_parts = python_exec.parts[:-4]
  _env, dev_rel, _bin, _python = python_exec.parts[-4:]
  assert (_env, _bin, _python) == ('env', 'bin', 'python'), err_msg

  return user_parts, dev_rel


def project_path():
  'abs path relative to the directory containing env/container/bin/python'
  user_parts, _ = project_path_components()
  return Path().joinpath(*user_parts)


def env_root(rel_path=''):
  'abs path relative to the directory containing bin/python'
  python_exec = executable_path()
  bin_path = python_exec.parent.resolve()
  env = bin_path.parent
  if rel_path:
    result = env / rel_path
  else:
    result = env
  return result
