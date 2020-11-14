=================
OSX configuration
=================

Follow these instructions to configure and install MacosX.

OSX Requirements
------------------------

The following third party packages are required

 =============== ======= ====================================================================================================
 name            version download url
 =============== ======= ====================================================================================================
 OSX             10.15.7 https://9to5mac.com/2019/06/27/how-to-create-a-bootable-macos-catalina-10-15-usb-install-drive-video
 Xcode           12.2    https://developer.apple.com/download/more
 Xcode CLI tools 11.2    https://developer.apple.com/download/more
 cmake           3.18.4  https://github.com/Kitware/CMake/releases/download/v3.18.4/cmake-3.18.4-Darwin-x86_64.dmg
 vscode          latest  https://code.visualstudio.com/download
 python          3.8.2   use default system python
 =============== ======= ====================================================================================================


Install Xcode
-------------

| Drag Xcode.app to applications directory.
| If Xcode gets stuck of verify stage, you can optionally disable quarantine:

.. code-block:: bash

   sudo xattr -rd com.apple.quarantine /Applications/Xcode.app
|

Install Xcode Command Line Tools
--------------------------------

| open xcode cli tools .pkg file and continue through normal install wizard.
|

Install CMake
-------------

Double click the dmg file, drag cmake icon to applications directory.

.. code-block:: bash

   sudo "/Applications/CMake.app/Contents/bin/cmake-gui" --install
|

Set umask
------------------------------------

.. code-block:: bash
 TODO
|

Set Login Desktop
------------------------------------

.. code-block:: bash
 TODO


