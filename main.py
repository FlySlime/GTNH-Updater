#!/usr/bin/env python3

import os
from os.path import isdir, isfile
import shutil
import sys
import zipfile

progress_bar = 0
max_progress = "4"


# Keeps count of progress and returns the string in format (X/Y)
def total_progress():
    global progress_bar
    progress_bar += 1
    return "(" + str(progress_bar) + "/" + max_progress + ")"


# Acquire the path for GregTech client/server, either if it stored in file or not.
# Also checks if odd inputs, and then moves the zip into the directory.
def get_zip_file(path_file, arg):
    if not os.path.exists(path_file):
        if arg == "client":
            print(
                "Where is the GT New Horizons game directory stored? (Where 'config', 'mods', 'resources', etc, are stored.)"
            )
        else:
            print(
                "WARNING: Before updating the server, make sure there is a folder called 'additional-mods-server' where the script is stored and move the 'JourneyMapServer' mod there!"
            )
            input("Press any key to continue...\n")
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

    # Tests for some cases where something might go wrong
    file_name = ""
    count = 0
    for file in os.listdir("."):
        if file.endswith(".zip"):
            file_name = file
            count += 1

    # Exit program if odd input
    if file_name == "":
        print(
            "ERROR: Couldn't find a zip file to update with in the current directory."
        )
        exit()
    elif count >= 2:
        print("ERROR: Too many zip files found.")
        exit()
    elif os.path.getsize(file_name) < 300000000:
        print(
            "ERROR: Zip file seems to be too small, double-check it's the GregTech update provided in the Discord server. (300+ MB check)"
        )
        exit()

    # Change to the game/server directory
    try:
        shutil.copy(file_name, path + "/" + file_name)
    except:
        print("ERROR: Invalid path.")
        os.remove(path_file)
        exit()

    print("GregTech zip has been found... " + total_progress())

    return path, file_name


def copy_dir_to_game(folder, path):
    if os.path.exists(path + "/" + folder):
        return -1
    if os.path.exists(folder):
        shutil.copytree(folder, path + "/" + folder)
    else:
        print("   -> No folder '" + folder[2:] + "' found. Skiping this step!")
    return 1


def add_dir_to_game(folder, path):
    if os.path.exists(folder):
        add_mods = os.listdir(folder)
        for mod in add_mods:
            mod_name = os.path.join(folder, mod)
            shutil.move(mod_name, path)
        # Delete the folder from the game directory
        shutil.rmtree(folder)


def remove(object):
    if os.path.isfile(object) or os.path.islink(object):
        os.remove(object)
    elif os.path.isdir(object):
        shutil.rmtree(object)


# Remove all config files/folders except a select few
def remove_configs(protected):
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


# Extract and remove the zip file
def extract_zip(file, pwd=None):
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
    os.remove(file)


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

    # Add shaders, insert everything in "shaderpacks" unless it is "OptiFine"
    if shader_answer == "y":
        if not os.path.isdir("shaderpacks"):
            os.mkdir("shaderpacks")
        shader_files = os.listdir(shaders_dir)
        for file in shader_files:
            if file.casefold().startswith("OptiFine".casefold()):
                shutil.move(shaders_dir + "/" + file, os.path.join("mods/", file))
            else:
                shutil.move(
                    shaders_dir + "/" + file, os.path.join("shaderpacks/", file)
                )

        # Cleanup
        shutil.rmtree(shaders_dir)


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
        "tcnodetracker",
        "torohealth",
    ]

    # Move additional mods, if any, to the server folder
    print("Searching for additional mods..." + total_progress())
    additional_mods_dir = "./additional-mods-server"
    copy_dir_to_game(additional_mods_dir, path)

    # Move into the server directory
    os.chdir(path)

    # Remove certain config folders
    protected = ["aroma1997", "JourneyMapServer", "opencomputers", "Morpheus.cfg"]
    remove_configs(protected)

    # Remove the old directories except config
    for dir in dirs_to_update:
        shutil.rmtree(dir)

    # Extract the new files
    extract_zip(file_name)

    # Remove client-side mods
    mods_dir = "./mods"
    mods = os.listdir(mods_dir)
    for mod in mods:
        for client_mod in client_side_mods:
            if mod.casefold().startswith(client_mod.casefold()):
                os.remove(os.path.join(mods_dir, mod))

    os.remove("README.md")
    shutil.rmtree("resourcepacks")
    shutil.rmtree("resources")

    # Add the server version of "JourneyMap", and other additional mods
    # NOTE: Check the version of this mod every "server-pack" update
    mods_dir = "./mods"
    add_dir_to_game(additional_mods_dir, mods_dir)


def check_shaders():
    # Check if the user wants shaders or not. Remembers the answer.
    shader_file = "shaders.txt"
    if not os.path.isfile(shader_file):
        shader_answer = input("Would you like to install shaders? (y/n)\n> ")
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


def main():
    # Check for invalid arguments
    try:
        sys.argv[1]
    except:
        print("ERROR: No arguments given. Use 'client', 'server', or 'both'.\n")
        print("For example:")
        print("> python main.py client")
        exit()
    arg = sys.argv[1]

    # Check if the user wants shaders or not
    shader_answer = ""
    if arg != "server":
        shader_answer = check_shaders()

    # Updater
    if arg == "client":
        path, file_name = get_zip_file("gamepath.txt", "client")
        update_client(path, file_name, shader_answer)
    elif arg == "server":
        path, file_name = get_zip_file("serverpath.txt", "server")
        update_server(path, file_name)
    elif arg == "both":
        path1, file_name1 = get_zip_file("gamepath.txt", "client")
        script_directory = os.getcwd()
        update_client(path1, file_name1, shader_answer)
        print()

        global progress_bar
        progress_bar = 0
        global max_progress
        max_progress = "4"
        os.chdir(script_directory)

        path2, file_name2 = get_zip_file("serverpath.txt", "server")
        update_server(path2, file_name2)
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
