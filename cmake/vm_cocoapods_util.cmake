# Copyright 2020 Alex Harvill
# SPDX-License-Identifier: Apache-2.0

function(vm_cocoapods_util_add_framework_symlink src_name)
  foreach(c_build_type RelWithDebInfo Release Debug)
    foreach(c_build_device iphoneos iphonesimulator)
      set(
        src_path
        ${CMAKE_BINARY_DIR}/build/${c_build_type}-${c_build_device}/${src_name}
      )
      set( dst_path ${CMAKE_CURRENT_BINARY_DIR}/${c_build_type}-${c_build_device} )
      # message(STATUS " ${dst_path} -> ${src_path}")

      execute_process(
        COMMAND mkdir -p ${dst_path} .
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
      )

      execute_process(
        COMMAND ln -s ${src_path} .
        WORKING_DIRECTORY ${dst_path}
      )
    endforeach(c_build_device)
  endforeach(c_build_type)

endfunction()
