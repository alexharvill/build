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
 OSX             10.15.7 https://support.apple.com/en-us/HT201372
 Xcode           12.2    https://developer.apple.com/download/more
 Xcode CLI tools 11.2    https://developer.apple.com/download/more
 cmake           3.18.4  https://github.com/Kitware/CMake/releases/download/v3.18.4/cmake-3.18.4-Darwin-x86_64.dmg
 vscode          latest  https://code.visualstudio.com/download
 python          3.8.2   use default system python
 =============== ======= ====================================================================================================


Install OSX
-----------
Download catalina installer in Mac AppStore ( using https://itunes.apple.com/us/app/macos-catalina/id1466841314?ls=1&mt=12 )
make bootable usb drive

.. code-block:: bash

  sudo /Applications/Install\ macOS\ Catalina.app/Contents/Resources/createinstallmedia --volume /Volumes/MyVolume
|
reboot
boot from usb by holding option on reboot
erase HD in disk util
format HD in disk util using APFS encrypted( case insensitive)
turn on FileVault
|

Set umask
------------------------------------

.. code-block:: bash

   sudo launchctl config system umask 002
|

Set login screen
------------------------------------
Reboot your mac holding Cmd+R to get into recovery mode
Open up the terminal window

.. code-block:: bash

   diskutil apfs list
|

find your drive-name like disk2s1 and and decrypt hd

.. code-block:: bash

   diskutil apfs unlockVolume /dev/disk2s1 # ( or whatever you found above )
|

Copy loging screen background ( file types need not match)

.. code-block:: bash

   cp /Volumes/DriveName\ -\ Data/Users/Shared/bg.png /Volumes/DriveName/System/Library/Desktop\ Pictures/Catalina.heic
|
Reboot into normal mode
Change any option in System Preferences -> Users & Groups -> Login Options to invalidate the cached image
Enjoy your new shiny login background.

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
