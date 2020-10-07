build
-----
.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :alt: License Apache-2.0
   :target: https://opensource.org/licenses/Apache-2.0
.. image:: https://img.shields.io/badge/Maintained-yes-green.svg
   :alt: Maintained Yes
   :target: https://github.com/alexharvill/build/graphs/commit-activity

Copyright (c) 2020 Alex Harvill.  All rights reserved.

A wrapper to run build systems.  Wraps cmake, xcode, vcpkg where cmake is mostly in charge.  A python virtual env is expected.

.. argparse::
   :filename: ../build.py
   :func: build_parser
   :prog: build.py

.. toctree::
   :maxdepth: 4
   :caption: Python Package:

   vm_build_utils


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
