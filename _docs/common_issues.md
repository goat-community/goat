---
title: Common Issues
permalink: /docs/common_issues/
---



If you use Windows as your host OS it might happen that you have issue when executing the shell scripts. Due to the different ways Unix-like systems and Windows are dealing with line endings. You will get an warning like "\r command not found". This especially happens if you open the shell scripts or the config.js with Wordpad or the text editor coming with Windows. You can avoid this by using an editor like Visual Studio Code. 
In the case you still face the issue you can convert the shell scripts and the secret.js with a tool like dos2unix.

You potentially have to run all the following commands:

`sudo apt update` (run on your VM)

`sudo apt install dos2unix` (run on your VM)

`dos2unix ~/app/installation/install_software.sh` (run on your VM)

`dos2unix ~/app/config/goat_config.yaml` (run on your VM)

`dos2unix ~/app/geoserver/install_geoserver.sh` (run on your VM)

