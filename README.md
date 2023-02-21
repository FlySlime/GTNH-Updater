# GTNH-Updater

### Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
  * [Windows](#windows)
- [Install](#install)
- [Usage](#usage)
- [Automatic Download with Prism Launcher](#prismlauncher)

# Introduction

Do you like staying up-to-date with one of the most brutal Minecraft modpacks, but are sick of constantly manually updating? Well do not worry, you are not alone, here is the solution nobody asked for!

# Prerequisites
Python is the only requirement, make sure you have it installed and you'll be good.

## Windows
The Python version from the [Windows Store](https://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5) was the only one that worked for my friends, might differ for you. Not sure why this is the case.

# Install
Simply download the repository, extract it, and then run the appropriate batch file.

# Usage
- ``UPDATE_CLIENT.bat``
  - Updates the game.
  - (OPTIONAL) "Automatic" downloads by using the URL provided in ``latestversion.txt``.
  - (OPTIONAL) Installs shaders.
  - Installs additional mods for client.
- ``UPDATE_SERVER.bat``
  - Updates the server.
  - Installs additional mods for server.
- ``UPDATE_SCRIPT.bat``
  - Pulls latest version of the script.
  - Does not update the game zip file.

## CLI
If you are feeling cool and want to use CLI, then use one of the following arguments:

- Update client:
```sh
$ python main.py client
```
- Update server:
```sh
$ python main.py server
```
- Update both client and server:
```sh
$ python main.py both
```
- Update script:
```sh
$ python main.py script
```

# PrismLauncher
**NOTE: Make sure you have reasonable internet, e.g. 10+ Mbps, as you will be downloading a 300+ MB file.**

If you want to always update the game and script when running the game, you can do the following:

1. Download the script and then extract it into the game directory.
  - ``Prism Launcher -> Click on GT:NH -> Folder``
2. Make sure to run the script once.
3. Open Prism Launcher and navigate to custom commands in Prism Launcher.
  - ``Prism Launcher -> Edit -> Settings -> Custom commands`` 
4. Write the following commands into the text-boxes as shown by the image.

**Pre-launch command:**
```sh
python main.py client
```

**Post-exit command:**
```sh
python main.py script
```

![custom-commands](https://i.imgur.com/FbTJ6zq.png)

There you go! Now you'll be downloading the latest version of GTNH when you start the game, and then updating the script so you never have to check back here again.

If any issues arise, try running the script manually, `UPDATE_CLIENT.bat`, once and see if it works. If that doens't fix it then try running `UPDATE_SCRIPT.bat`.
