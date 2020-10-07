# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0
#Look for an executable called sphinx-build
find_program(
  SPHINX_EXECUTABLE
  NAMES sphinx-build
  DOC "Path to sphinx-build executable"
)

find_program(
  SPHINX_APIDOC_EXECUTABLE
  NAMES sphinx-apidoc
  DOC "Path to sphinx-apidoc executable"
)

find_program(
  SPHINX_PDFLATEX_EXECUTABLE
  NAMES pdflatex
  DOC "Path to pdflatex executable for sphinx pdf docs"
)


include(FindPackageHandleStandardArgs)
#Handle standard arguments to find_package like REQUIRED and QUIET
find_package_handle_standard_args(Sphinx
                                  "Failed to find sphinx-build executable"
                                  SPHINX_EXECUTABLE)
#Handle standard arguments to find_package like REQUIRED and QUIET
find_package_handle_standard_args(Sphinx
                                  "Failed to find sphinx-apidoc executable"
                                  SPHINX_APIDOC_EXECUTABLE)