# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0

# THE FOLLOWING VARIABLES ARE EXPECTED TO BE DEFINED IN INCLUDING SOURCE:
# set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR})
# set(SPHINX_BUILD ${CMAKE_CURRENT_BINARY_DIR}/sphinx)
# set(SPHINX_PDF_BUILD ${CMAKE_CURRENT_BINARY_DIR}/sphinx_pdf)
# set(SPHINX_INDEX_FILE ${SPHINX_BUILD}/index.html)
# set(SPHINX_PDF_FILE ${SPHINX_PDF_BUILD}/latex/MODULE_NAME.pdf)

# set(SPHINX_GEN_MODULE ${CMAKE_CURRENT_SOURCE_DIR}/MODULE_NAME.rst)

# set(APIDOC_MODULE matchco)
# file(GLOB_RECURSE PYTHON_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/../src/python/*.py)
# list(APPEND PYTHON_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/../src/bin/cli_tool)
# set(DIR_LINKS "")
# list(APPEND DIR_LINKS ${CMAKE_CURRENT_SOURCE_DIR}/../src/python matchco)
# list(APPEND DIR_LINKS ${CMAKE_CURRENT_SOURCE_DIR}/../src/bin bin)


# project(MODULE_NAME)

# set(PROJECT_TARGET "${PROJECT_NAME}_doc")

# set(SPHINX_OUTPUTS "")

find_package(Sphinx REQUIRED)

# if (TARGET sphinx_api_doc)
#   message( INFO " target sphinx_api_doc already found")
# else()
# add_custom_target( sphinx_api_doc ALL )
# endif()


configure_file(index.rst ${CMAKE_CURRENT_BINARY_DIR}/index.rst COPYONLY)
configure_file(conf.py ${CMAKE_CURRENT_BINARY_DIR}/conf.py COPYONLY)

# Only regenerate Sphinx when:
#  - PYTHON_SOURCES have changed
#  - Our doc files have been updated
#  - The Sphinx config has been updated

# make a symlinks to all python source directories
if(DEFINED DIR_LINKS)
  set(LINK_OUTPUTS "")
  list(LENGTH DIR_LINKS N_DIR_LINKS)
  math(EXPR N_DIR_LINKS_1 "${N_DIR_LINKS} - 1")
  foreach(src_index RANGE 0 ${N_DIR_LINKS_1} 2)
    math(EXPR dst_index "${src_index} + 1")
    list(GET DIR_LINKS ${src_index} src)
    list(GET DIR_LINKS ${dst_index} dst)

    add_custom_command(
      OUTPUT ${dst}
      COMMAND
        ln -s ${src} ${dst}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
      COMMENT "make doc link ${dst}"
    )

    list(APPEND LINK_OUTPUTS ${dst})
  endforeach()
endif()

message(STATUS " LINK_OUTPUTS ${LINK_OUTPUTS}")

# generate .rst files for each .py file in module
add_custom_command(
  OUTPUT ${SPHINX_GEN_MODULE}
	COMMAND
    ${SPHINX_APIDOC_EXECUTABLE} --separate --output-dir ${CMAKE_CURRENT_BINARY_DIR} ${APIDOC_MODULE}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
	DEPENDS
		# Other docs files you want to track should go here (or in some variable)
    index.rst
    ${PYTHON_SOURCES}
    ${LINK_OUTPUTS}
	MAIN_DEPENDENCY ${SPHINX_SOURCE}/conf.py
  COMMENT "Generating python api documentation with sphinx-apidoc"
)

# convert .rst files to html
add_custom_command(OUTPUT ${SPHINX_INDEX_FILE}
	COMMAND
		${SPHINX_EXECUTABLE} -v ${CMAKE_CURRENT_BINARY_DIR} ${SPHINX_BUILD}
	WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
	DEPENDS
		# Other docs files you want to track should go here (or in some variable)
    index.rst
    conf.py
    ${PYTHON_SOURCES}
    ${LINK_OUTPUTS}
    ${SPHINX_GEN_MODULE}
	MAIN_DEPENDENCY ${SPHINX_SOURCE}/conf.py
  COMMENT "Generating html documentation with sphinx")

# Nice named target so we can run the job easily

include(GNUInstallDirs)
install(DIRECTORY ${SPHINX_BUILD} DESTINATION ${CMAKE_INSTALL_DOCDIR})

list(APPEND SPHINX_OUTPUTS ${SPHINX_INDEX_FILE})


# convert .rst files to pdf
if(${SPHINX_PDFLATEX_EXECUTABLE} MATCHES "NOTFOUND")
  message( INFO " SKIPPING PDF DOCUMENTATION")

  # add_dependencies( sphinx_api_doc ${SPHINX_INDEX_FILE} )

  # add_custom_target(
  #   sphinx_api_doc ALL DEPENDS ${SPHINX_INDEX_FILE}
  # )

else()
  message( INFO " sphinx pdflatex information:${SPHINX_PDFLATEX_EXECUTABLE}")
  add_custom_command(OUTPUT ${SPHINX_PDF_FILE}
    COMMAND
      ${SPHINX_EXECUTABLE} -M latexpdf ${CMAKE_CURRENT_BINARY_DIR} ${SPHINX_PDF_BUILD}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    DEPENDS
      # Other docs files you want to track should go here (or in some variable)
      index.rst
      conf.py
      ${PYTHON_SOURCES}
      ${LINK_OUTPUTS}
      ${SPHINX_GEN_MODULE}
    MAIN_DEPENDENCY ${SPHINX_SOURCE}/conf.py
    COMMENT "Generating pdf documentation with Sphinx")

    list(APPEND SPHINX_OUTPUTS ${SPHINX_PDF_FILE})

    # add_dependencies( sphinx_api_doc ${SPHINX_INDEX_FILE} ${SPHINX_PDF_FILE} )
    # add_custom_target(
    #   sphinx_api_doc ALL DEPENDS ${SPHINX_INDEX_FILE} ${SPHINX_PDF_FILE}
    # )

  # install optional pdf file
  install(FILES ${SPHINX_PDF_FILE} DESTINATION ${CMAKE_INSTALL_DOCDIR})
endif()


