#!/usr/bin/env python3

import os
import shutil
import sys
import zipfile
import urllib.request
import time

# Global variables
progress_bar = 0
max_progress = "4"
polymc_auto = False


def total_progress():
    """Keeps count of progress and returns the string in format (X/Y)."""
    global progress_bar
    progress_bar += 1
    return "(" + str(progress_bar) + "/" + max_progress + ")"


def get_game_path(path_file, arg):
    """Acquire the path for GregTech client/server.

    Check if the user has already run the script before -> Use the path saved in "gamepath" or "serverpath"
    """
    if not os.path.exists(path_file):
        if arg == "client":
            print(
                "Where is the GT New Horizons game directory stored? (Where 'config', 'mods', 'resources', etc, are stored.)"
            )
        else:
            print(
                "Where is the GT New Horizons server located? (Where 'config', 'mods', etc, are stored.)"
            )

        path = input("> ")
        print()
        with open(path_file, "w") as f:
            f.write(path)
    else:
        with open(path_file, "r") as f:
            path = f.readline()
        print("NOTE: Using previous path stored in '" + path_file + "': " + path + "\n")

    return path


def get_zip_file(path_file, path):
    """Searches for zip file in current directory.

    User can decide if they want to use "automatic" download, checks text file for updated zip.
    Otherwise, use zip file in current directory.

    Check for odd inputs -> Stop the program and ask gives appropriate error message.
    If zip file is found in current directory -> Copy it over to game directory
    """
    auto_download_file = "autodownload.txt"
    auto_download_answer = "n"
    if not os.path.exists(auto_download_file):
        print(
            "Would you like to 'automatically' detect and download the latest version of the game? (y/n)"
        )
        print(
            "NOTE: Expect the version to be bumped by me within a couple of hours after a new update is released."
        )
        auto_download_answer = input("> ")
        print()
        with open(auto_download_file, "w") as f:
            f.write(auto_download_answer)

    with open(auto_download_file, "r") as f:
        auto_download_answer = f.readline()

    # Uses the url in "latestversion.txt" to download the "latest" version
    if auto_download_answer == "y":
        # Pull latest version from GitHub
        zip_name = "GTNH-Updater-latest.zip"
        github_file_name = "GTNH-Updater-main"
        urllib.request.urlretrieve(
            "https://github.com/flyslime/gtnh-updater/archive/refs/heads/main.zip",
            zip_name,
        )

        # Extract latest version
        with zipfile.ZipFile(zip_name, "r") as zip_ref:
            zip_ref.extractall(".")

        # Replace latest version
        latest_version_file = "latestversion.txt"
        remove(latest_version_file)
        shutil.move(github_file_name + "/" + latest_version_file, latest_version_file)
        remove(github_file_name)

        # Acquire the URL
        latest_version_url = ""
        with open(latest_version_file, "r") as f:
            latest_version_url = f.readline()

        # Detects if update is needed, and removes previous zips
        new_update = True
        zip_name = latest_version_url[
            latest_version_url.rfind("/") + 1 : latest_version_url.rfind("?")
        ]
        files = os.listdir(".")
        for file in files:
            if file.endswith(".zip"):
                if file == zip_name:
                    new_update = False
                    print(
                        "You are already up-to-date, if you close the script within 5 seconds it won't reinstall."
                    )
                    print()
                    for x in range(5, 0, -1):
                        print(str(x) + " seconds remaining...")
                        time.sleep(1)
                    print()
                remove(file)

        # Download latest version
        if new_update:
            print("New update detected, downloading...")
        else:
            print("Redownloading the game...")
        print(
            "NOTE: This might take a while depending on your internet speed. Have some patience!"
        )
        urllib.request.urlretrieve(
            latest_version_url,
            zip_name,
        )
        print()

    # Tests for some cases where something might go wrong
    zip_file = ""
    count = 0
    for file in os.listdir("."):
        if file.endswith(".zip"):
            zip_file = file
            count += 1

    # Exit program if odd input
    if zip_file == "":
        print(
            "ERROR: Couldn't find a zip file to update with in the current directory."
        )
        exit()
    elif count >= 2:
        print("ERROR: Too many zip files found.")
        exit()
    elif os.path.getsize(zip_file) < 300000000:
        print(
            "ERROR: Zip file seems to be too small, double-check it's the GregTech update provided in the Discord server. (300+ MB check)"
        )
        exit()

    # Copy the update to game directory
    try:
        game_dir_zip_file = path + "/" + zip_file
        current_absolute_path = os.path.abspath(os.getcwd())
        # This only occurs if the user is automatically updating with PolyMC.
        # If so, set a flag and skip the copy
        if (current_absolute_path + "/" + zip_file) == game_dir_zip_file:
            global polymc_auto
            polymc_auto = True
        if not polymc_auto:
            shutil.copy(zip_file, game_dir_zip_file)
    except:
        print("ERROR: Invalid path.")
        remove(path_file)
        exit()

    print("GregTech zip has been found... " + total_progress())

    return zip_file


def copy_dir_to_game(folder, path):
    """Copy a folder to a certain path.

    Check if folder exists before performing the action
    """
    if os.path.exists(path + "/" + folder):
        return -1
    if os.path.exists(folder):
        shutil.copytree(folder, path + "/" + folder)
    else:
        print("   -> No folder '" + folder[2:] + "' found. Skiping this step!")
    return 1


def add_dir_to_game(folder, path):
    """Add all files in directory to a certain folder.

    Check if folder exists before performing the action
    """
    if os.path.exists(folder):
        files = os.listdir(folder)
        for file in files:
            file_name = os.path.join(folder, file)
            if os.path.exists(path + "/" + file):
                continue
            if polymc_auto:
                shutil.copy(file_name, path)
            else:
                shutil.move(file_name, path)
        if not polymc_auto:
            # Delete the folder from the game directory
            remove(folder)


def add_shaders_to_game(shaders_dir):
    """Add shaders & configs.

    If OptiFine -> Mod foler
    If OptiFine config -> Game folder
    Otherwise, assume it is a shader or shader config -> Shader folder
    """
    if not os.path.isdir("shaderpacks"):
        os.mkdir("shaderpacks")

    shader_files = os.listdir(shaders_dir)
    for file in shader_files:
        src = shaders_dir + "/" + file
        if file.casefold().startswith("OptiFine".casefold()):
            dst = os.path.join("mods/", file)
            if polymc_auto:
                shutil.copy(src, dst)
            else:
                shutil.move(src, dst)
        elif file.startswith("options"):
            dst = os.path.join(file)
            remove(file)
            if polymc_auto:
                shutil.copy(src, dst)
            else:
                shutil.move(src, dst)
        else:
            src = shaders_dir + "/" + file
            dst = os.path.join("shaderpacks/", file)
            if polymc_auto:
                shutil.copy(src, dst)
            else:
                shutil.move(src, dst)
    if not polymc_auto:
        remove(shaders_dir)


def remove(object):
    """Smart remove function, check if file/folder exists first."""
    if os.path.isfile(object) or os.path.islink(object):
        os.remove(object)
    elif os.path.isdir(object):
        shutil.rmtree(object)


def remove_configs(protected):
    """Remove all config files/folders except a select few."""
    try:
        config_dir = "./config"
        configs = os.listdir(config_dir)
        for config in configs:
            if config in protected:
                continue
            remove(config_dir + "/" + config)
    except:
        print(
            "ERROR: Wrong path, double-check that the path has the folders: 'config', 'mods', etc."
        )


def extract_game_zip(file, pwd=None):
    """Extract the update file without overwriting existing files."""
    print("Exctracting files..." + total_progress())

    # https://stackoverflow.com/questions/61351290/unzip-an-archive-without-overwriting-existing-files
    with zipfile.ZipFile(file) as zf:
        members = zf.namelist()
        for member in members:
            arch_info = zf.getinfo(member)
            arch_name = arch_info.filename.replace("/", os.path.sep)
            dst_path = os.path.join(".", arch_name)
            dst_path = os.path.normpath(dst_path)
            if not os.path.exists(dst_path):
                zf.extract(arch_info, ".", pwd)

    print("Cleaning up..." + total_progress() + "\n")
    remove(file)


def check_shaders():
    # Check if the user wants shaders or not. Remembers the answer.
    shader_file = "shaders.txt"
    if not os.path.isfile(shader_file):
        shader_answer = input(
            "Would you like to install shaders? Expect a drop in 10-40 fps. (y/n)\n> "
        )
        print()
        if shader_answer == "y":
            print(
                "NOTE: Shaders will be installed and this decision will be saved, if you change your mind then remove 'shaders.txt'"
            )
        else:
            print(
                "NOTE: Shaders will not be installed and this decision will be saved, if you change your mind then please remove 'shaders.txt'"
            )
        print()

        with open(shader_file, "w") as f:
            f.write(shader_answer)
    else:
        with open(shader_file, "r") as f:
            shader_answer = f.readline()
        if shader_answer == "y":
            print("NOTE: Found " + shader_file + ": Shaders will be installed.")
        else:
            print("NOTE: Found " + shader_file + ": Shaders will not be installed.")
        print()

    # Adjust the progress bar
    if shader_answer == "y":
        global max_progress
        max_progress = "5"

    return shader_answer


def update_client(path, file_name, shader_answer):
    # NOTE: Don't include "config", it is handled further down
    to_update = [
        "mods",
        "resourcepacks",
        "resources",
        "scripts",
        "README.md",
    ]

    # Move additional mods, if any, to the game folder
    print("Searching for additional mods..." + total_progress())
    additional_mods_dir = "./additional-mods-client"
    copy_dir_to_game(additional_mods_dir, path)

    # Move shaders folder, if user choose so
    shaders_dir = "./shaders"
    if shader_answer == "y":
        print("Installing shaders..." + total_progress())
        copy_dir_to_game(shaders_dir, path)

    # Move into the client directory
    os.chdir(path)

    # Remove certain config folders
    protected = ["NEI", "betterquesting.cfg", "InvTweaks.cfg", "InGameInfoXML.cfg"]
    remove_configs(protected)

    # Remove the old directories and files
    for file in to_update:
        remove(file)

    # Extract and update the game
    extract_game_zip(file_name)

    # Add the additional mods to the mod folder
    mods_dir = "./mods"
    add_dir_to_game(additional_mods_dir, mods_dir)

    # Add shaders & configs
    if shader_answer == "y":
        add_shaders_to_game(shaders_dir)


def update_server(path, file_name):
    # NOTE: Don't include "config", it is handled further down
    dirs_to_update = [
        "mods",
        "resourcepacks",
        "resources",
        "scripts",
    ]

    # See: https://gtnh.miraheze.org/wiki/Client-side_Mods
    client_side_mods = [
        "BeeBetterAtBees",
        "BetterAchievements",
        "bettercrashes",
        "betterloadingscreen",
        "boubs-admin-tools",
        "craftpresence",
        "Controlling",
        "CustomMainMenu",
        "defaultserverlist",
        "DefaultWorldGenerator",
        "fastcraft",
        "IC2+Crop+Plugin",
        "inventorytweaks",
        "itlt",
        "journeymap-",
        "MouseTweaks",
        "NettyPatch",
        "oauth",
        "OptiFine",
        "overloadedarmorbar",
        "ResourceLoader",
        "torohealth",
    ]

    # Move additional mods, if any, to the server folder
    print("Searching for additional mods..." + total_progress())
    additional_mods_dir = "./additional-mods-server"
    copy_dir_to_game(additional_mods_dir, path)

    # Move into the server directory
    os.chdir(path)

    # Remove certain config folders
    protected = ["aroma1997", "JourneyMapServer", "Morpheus.cfg"]
    remove_configs(protected)

    # Remove the old directories except config
    for dir in dirs_to_update:
        remove(dir)

    # Extract the new files
    extract_game_zip(file_name)

    # Remove client-side mods
    mods_dir = "./mods"
    mods = os.listdir(mods_dir)
    for mod in mods:
        for client_mod in client_side_mods:
            if mod.casefold().startswith(client_mod.casefold()):
                remove(os.path.join(mods_dir, mod))

    # Add the server version of "JourneyMap", and other additional mods
    # NOTE: Check the version of this mod every "server-pack" update
    mods_dir = "./mods"
    add_dir_to_game(additional_mods_dir, mods_dir)


def update_script():
    print("Pulling the latest version of 'GTNH-Updater'...\n")
    zip_name = "GTNH-Updater-latest.zip"
    github_file_name = "GTNH-Updater-main"

    # Remove most files, except save-files and zip files
    # NOTE: The reason why we don't write the "protected" files instead
    #       is to not accidently delete the entire game directory if
    #       the user wishes to automatically update the game with PolyMC
    to_remove = [
        "additional-mods-client",
        "additional-mods-server",
        "shaders",
        "main.py",
        "UPDATE_CLIENT.bat",
        "UPDATE_SCRIPT.bat",
        "UPDATE_SERVER.bat",
    ]
    objects = os.listdir(".")
    for object in objects:
        if object.endswith(".zip"):
            continue
        if object in to_remove:
            remove(object)

    # Download latest version
    urllib.request.urlretrieve(
        "https://github.com/flyslime/gtnh-updater/archive/refs/heads/main.zip",
        zip_name,
    )

    # Extract the zip file
    with zipfile.ZipFile(zip_name, "r") as zip_ref:
        zip_ref.extractall(".")

    # Move the files into the script directory
    objects = os.listdir(github_file_name)
    for object in objects:
        shutil.move(github_file_name + "/" + object, object)

    # Cleanup
    remove(zip_name)
    remove(github_file_name)
    print("UPDATE COMPLETE: You now have the latest version of 'GTNH-Updater'.")


def main():
    # Check for invalid arguments
    try:
        sys.argv[1]
    except:
        print(
            "ERROR: No arguments given. Use 'client', 'server', 'script', or 'both'.\n"
        )
        print("For example:")
        print("> python main.py client")
        exit()
    arg = sys.argv[1]

    if arg == "script":
        # Update the "GTNH-Updater" by pulling latest zip from GitHub
        update_script()
        exit()

    # Check if the user wants shaders or not
    shader_answer = ""
    if arg != "server":
        shader_answer = check_shaders()

    client_path = "gamepath.txt"
    server_path = "serverpath.txt"

    # Updater
    if arg == "client":
        path = get_game_path(client_path, "client")
        zip_file = get_zip_file(client_path, path)
        update_client(path, zip_file, shader_answer)
    elif arg == "server":
        path = get_game_path(server_path, "server")
        zip_file = get_zip_file(server_path, path)
        update_server(path, zip_file)
    elif arg == "both":
        # Save script directory so we can return to it for server update
        script_directory = os.getcwd()

        # Client update
        path = get_game_path(client_path, "client")
        zip_file = get_zip_file(client_path, path)
        update_client(path, zip_file, shader_answer)
        print()

        # Refresh progress
        global progress_bar
        progress_bar = 0
        global max_progress
        max_progress = "4"

        # Jump back to script directory
        os.chdir(script_directory)

        # Server update
        path = get_game_path(server_path, "server")
        zip_file = get_zip_file(server_path, path)
        update_server(path, zip_file)
    else:
        print("ERROR: Invalid argument.")
        exit()

    print(
        "UPDATE COMPLETE: greggy-boi has successfully been inserted into your "
        + arg
        + "."
    )


if __name__ == "__main__":
    main()
