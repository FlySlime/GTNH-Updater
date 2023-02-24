# GTNH-Updater

### Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Install and Usage](#install-and-usage)
- [Features](#features)
- [Automatic Download with Prism Launcher](#automatic-download-with-prism-launcher)

# Introduction

Do you like staying up-to-date with one of the most brutal Minecraft modpacks, but are sick of constantly manually updating? Well do not worry, you are not alone, here is the solution for lazy people like us!

# Prerequisites

- [Python](https://www.python.org/)
  - If you are using Windows, the Python version from the [Windows Store](https://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5) was the only one that worked for my friends. This might differ on your computer.
- [Prism Launcher](https://prismlauncher.org/)
  - This isn't really a requirement to use the script, but rather what was used while coding the script. It may be possible to use other launchers, but I can't gurantee it'll work out of the box. 
  - However, Java 9+ client update will not work on other launchers - as it is designed to only work on Prism Launcher.

# Install and Usage
Download the [latest version](https://github.com/FlySlime/GTNH-Updater/archive/refs/heads/main.zip) through GitHub, extract it, then run the appropriate batch file.

# Features
- ``UPDATE_CLIENT.bat``
  - Updates the client.
  - Easily switch between Java 8 and Java 9+.
  - (OPTIONAL) "Automatic" downloads.
  - (OPTIONAL & CUSTOMIZABLE) Install shaders.
  - (OPTIONAL & CUSTOMIZABLE) Install additional mods for client.

- ``UPDATE_SERVER.bat``
  - Updates the server.
  - Always updates to Java 9+, supports all version of Java for the client.
  - (OPTIONAL & CUSTOMIZABLE) Install additional mods for server.

- ``UPDATE_SCRIPT.bat``
  - Pulls latest version of the script from GitHub.

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

- Update script:
```sh
$ python main.py script
```

# Automatic Download with Prism Launcher
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

If any issues arise, try running the script manually, `UPDATE_CLIENT.bat`, once and see if it works. If that doesn't fix it then try running `UPDATE_SCRIPT.bat`.
