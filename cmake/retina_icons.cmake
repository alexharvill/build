# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0
# use like so:
# set( asset_name node_one.xcassets)
# set( iconsets "")

# include( retina_icons )

# build_retina_icons( vm.appiconset vm.png )
# build_retina_icons( record-button.imageset record-button.png )

# add_custom_target( node_one_icons ALL DEPENDS ${iconsets} )

set( retina_icons_script ${CMAKE_SOURCE_DIR}/build/vm_build_utils/retina_icons.py )

set( asset_build_directory ${CMAKE_CURRENT_BINARY_DIR}/${asset_name})

include(GNUInstallDirs)

macro( build_retina_icons iconset_name src_icon_name pad_mode )

  set( output_iconset ${asset_build_directory}/${iconset_name} )
  list(APPEND iconsets ${output_iconset})

  add_custom_command( OUTPUT ${output_iconset}
    COMMAND
      ${PYTHON_EXECUTABLE}
      ${retina_icons_script}
      --verbose
      --asset-build-dir ${asset_build_directory}
      --iconset ${iconset_name}
      --src ${CMAKE_CURRENT_SOURCE_DIR}/${src_icon_name}
      --pad-mode ${pad_mode}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Generating icons"
  )

  install(
    DIRECTORY ${output_iconset}
    DESTINATION ${CMAKE_INSTALL_PREFIX}/icons/${asset_name}
  )

endmacro(build_retina_icons)
