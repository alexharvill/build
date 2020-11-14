====================
ubuntu configuration
====================

Linux Requirements
==================
    Ubuntu 20.04.1 LTS
    NVIDIA GPU ( recommend 1080Ti 11GB or better )

Ubuntu 20.04.1 Setup Notes
==========================
Install Ubuntu with user ubuntu

LOCAL: Setup Anisble
    You will install OpenSSH and Ansible as root, run these in a terminal

.. code-block:: bash

   sudo apt-get upgrade
   sudo apt-get update && apt-get install -y python3-pip python3-dev openssh-server
   sudo pip3 install --upgrade pip
   sudo pip3 install ansible==2.9.11


LOCAL: Get IP Address

.. code-block:: bash

   hostname -I


REMOTE: install ansible

.. code-block:: bash

   source /path/to/virtualenv/bin/activate
   pip install ansible==2.9.11


REMOTE: install sshpass
download ssh pass and save in /tmp

.. code-block:: bash

   cd /tmp
   tar -xzf sshpass-1.06.tar.gz
   cd sshpass-1.06
   ./configure
   sudo make install


REMOTE: Confirm SSH and establish key

.. code-block:: bash

   export REMOTE_IP=192.168.1.XXX
   ssh ubuntu@${REMOTE_IP}


REMOTE: run playbooks

.. code-block:: bash

   ansible-playbook ansible/core_platform.yml -i ${REMOTE_IP}, --user ${USER} --ask-pass --ask-become-pass
   ansible-playbook ansible/core_cmake.yml -i ${REMOTE_IP}, --user ${USER} --ask-pass --ask-become-pass
   ansible-playbook ansible/core_nvidia_desktop.yml -i ${REMOTE_IP}, --user ${USER} --ask-pass --ask-become-pass
   ansible-playbook ansible/core_cuda_10_1.yml -i ${REMOTE_IP}, --user ${USER} --ask-pass --ask-become-pass


REMOTE: run app playbooks {optional}

.. code-block:: bash

   ansible-playbook ansible/app_tev.yml -i ${REMOTE_IP}, --user ${USER} --ask-pass --ask-become-pass
   ansible-playbook ansible/app_vscode.yml -i ${REMOTE_IP}, --user ${USER} --ask-pass


Copyright (c) 2020 Alex Harvill.  All rights reserved.
