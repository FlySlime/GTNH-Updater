#!/usr/bin/env python3

import os
import shutil
import sys
import zipfile
import urllib.request

# Global variables
progress_bar = 0
max_progress = "4"


def total_progress():
    """Keeps count of progress and returns the string in format (X/Y)."""
    global progress_bar
    progress_bar += 1
    return "(" + str(progress_bar) + "/" + max_progress + ")"


def get_game_path(path_file, arg):
    """Acquire the path for GregTech client/server.

    Check if the user has already run the script before -> Use the path saved in "gamepath" or "serverpath"
    Check for odd inputs -> Stop the program and ask gives appropriate error message.

    If zip file is found in current directory -> Copy it over to game directory
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
        print("\n")
        with open(path_file, "w") as f:
            f.write(path)
    else:
        with open(path_file, "r") as f:
            path = f.readline()
        print("NOTE: Using previous path stored in '" + path_file + "': " + path + "\n")

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
        shutil.copy(zip_file, path + "/" + zip_file)
    except:
        print("ERROR: Invalid path.")
        remove(path_file)
        exit()

    print("GregTech zip has been found... " + total_progress())

    return path, zip_file


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
        for modfile in files:
            file_name = os.path.join(folder, modfile)
            shutil.move(file_name, path)
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
        if file.casefold().startswith("OptiFine".casefold()):
            shutil.move(shaders_dir + "/" + file, os.path.join("mods/", file))
        elif file.casefold().startswith("options".casefold()):
            remove(file)
            shutil.move(shaders_dir + "/" + file, os.path.join(file))
        else:
            shutil.move(shaders_dir + "/" + file, os.path.join("shaderpacks/", file))

    # Cleanup
    remove(shaders_dir)


def remove(object):
    """Smart remove function, check if file exist first."""
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


def extract_zip(file, pwd=None):
    """Extract the update, and then cleanup."""
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
        print("\n")

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
    to_update = [
        "mods",
        "resourcepacks",
        "resources",
        "scripts",
        "README.md",
        "server.properties",
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
    extract_zip(file_name)

    # Add the additional mods to the mod folder
    mods_dir = "./mods"
    add_dir_to_game(additional_mods_dir, mods_dir)

    # Add shaders & configs
    if shader_answer == "y":
        add_shaders_to_game(shaders_dir)


def update_server(path, file_name):
    dirs_to_update = [
        "mods",
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
    extract_zip(file_name)

    # Remove client-side mods
    mods_dir = "./mods"
    mods = os.listdir(mods_dir)
    for mod in mods:
        for client_mod in client_side_mods:
            if mod.casefold().startswith(client_mod.casefold()):
                remove(os.path.join(mods_dir, mod))

    remove("README.md")
    remove("resourcepacks")
    remove("resources")

    # Add the server version of "JourneyMap", and other additional mods
    # NOTE: Check the version of this mod every "server-pack" update
    mods_dir = "./mods"
    add_dir_to_game(additional_mods_dir, mods_dir)


def update_script():
    print("Pulling the latest version of 'GTNH-Updater'...\n")
    zip_name = "GTNH-Updater-latest.zip"
    github_file_name = "GTNH-Updater-main"

    # Remove old files, except protected ones
    protected = [".git", "gamepath.txt", "serverpath.txt", "shaders.txt"]
    objects = os.listdir(".")
    for object in objects:
        if not object in protected:
            remove(object)

    # Download latest version
    urllib.request.urlretrieve(
        "https://github.com/FlySlime/GTNH-Updater/archive/refs/heads/main.zip",
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

    # Updater
    if arg == "client":
        path, zip_file = get_game_path("gamepath.txt", "client")
        update_client(path, zip_file, shader_answer)
    elif arg == "server":
        path, zip_file = get_game_path("serverpath.txt", "server")
        update_server(path, zip_file)
    elif arg == "both":
        path, zip_file = get_game_path("gamepath.txt", "client")
        script_directory = os.getcwd()
        update_client(path, zip_file, shader_answer)
        print()

        # Refresh progress
        global progress_bar
        progress_bar = 0
        global max_progress
        max_progress = "4"
        os.chdir(script_directory)

        path, zip_file = get_game_path("serverpath.txt", "server")
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
