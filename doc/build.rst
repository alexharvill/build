build.py : A wrapper to run build systems
=========================================
Wraps cmake, xcode, vcpkg where cmake is mostly in charge.  A python virtual env is expected.

.. argparse::
   :filename: ../build.py
   :func: build_parser
   :prog: build.py
