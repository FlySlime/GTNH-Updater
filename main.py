#!/usr/bin/env python3

import os
import shutil
import sys
import time
import urllib.request
import zipfile

# Import the "requests" module, however make sure that it is installed
# on the user's computer. If it is not installed, then run "pip install"
# to install it.
try:
    import requests
except ImportError:
    print("The 'requests' module is not installed. Installing it now...")
    print()
    os.system("pip install requests")
    import requests

# Global variables
arg = ""
java_9_answer = ""
max_progress = "4"
progress_bar = 0
updater_auto_update = False
updater_files_dir = "./files/"
updater_saves_dir = updater_files_dir + "saves/"


def total_progress():
    """Keeps count of progress and returns the string in format [X/y]."""
    global progress_bar
    progress_bar += 1
    return "[" + str(progress_bar) + "/" + max_progress + "]"


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
            print()
            print(
                "WARNING: If you are hosting a server, make sure to download the server-pack for Java 9+ BEFORE updating.",
            )
            print()
            print(
                "Java 9+ is used as default for the server, since it allows BOTH Java 8 clients and Java 9+ clients to join."
            )
            print()
            print(
                "The updater can't migrate a server from Java 8 -> Java 9+. It can only update Java 9+ -> Java 9+."
            )
        path = input("> ")
        print()
        with open(path_file, "w") as f:
            f.write(path)
    else:
        with open(path_file, "r") as f:
            path = f.readline()
        print("NOTE: Found", path_file, "-> " + path)
        print()

    return path


def get_zip_file(path_file, path):
    """Searches for zip file in current directory.

    User can decide if they want to use "automatic" download, checks text file for updated zip.
    Otherwise, use zip file in current directory.

    Check for odd inputs -> Stop the program and ask gives appropriate error message.
    If zip file is found in current directory -> Copy it over to game directory
    """
    auto_download_file = updater_saves_dir + "autodownload.txt"
    auto_download_answer = "n"
    if not os.path.exists(auto_download_file):
        print(
            "Would you like to 'automatically' fetch the latest version when running the script? [Y/n]"
        )
        auto_download_answer = input("> ").casefold()
        print()
        print(
            "NOTE: Expect the version to be bumped by me within a couple of hours after a new update is released.",
            "That is, if the new update doesn't have any immediate issues.",
        )
        print()
        with open(auto_download_file, "w") as f:
            f.write(auto_download_answer)

    with open(auto_download_file, "r") as f:
        auto_download_answer = f.readline()

    # Uses the URL in "latestversion.txt" to download the "latest" version
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

        # Download Java 8 version, and apply Java 9+ changes
        # if user has chosen so
        latest_version_file = updater_files_dir + "GTNH-java8-version.txt"

        # Ensure we are using the latest version from GitHub
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
        files_dir = os.listdir(".")
        for file in files_dir:
            if file.endswith(".zip"):
                if file == zip_name:
                    new_update = False
                    print(
                        "You are already up-to-date, if you close the script within 5 seconds it won't reinstall."
                    )
                    print()
                    for x in range(5, 0, -1):
                        print(x, "seconds remaining...")
                        time.sleep(1)
                    print()
                remove(file)

        # Download latest version
        if new_update:
            print("New update detected, downloading...")
        else:
            print("Redownloading the game...")
        print()

        print(
            "NOTE: This might take a while depending on your internet speed. Have some patience!"
        )
        print()

        urllib.request.urlretrieve(
            latest_version_url,
            zip_name,
        )

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
        # Only occurs if the user is automatically updating with a launcher.
        # If so, set a flag and skip the copy
        if (current_absolute_path + "/" + zip_file) == game_dir_zip_file:
            print(
                "Detected script running within the game-directory, setting launcher flag..."
            )
            print()
            global updater_auto_update
            updater_auto_update = True

        if not updater_auto_update:
            shutil.copy(zip_file, game_dir_zip_file)
    except:
        print(
            "ERROR: Path doesn't exist, or the zip file is already in the given path."
        )
        remove(path_file)
        exit()

    print("GregTech zip has been found...", total_progress())

    return zip_file


def copy_dir_to_game(folder, path):
    """Copy a folder to a certain path.

    Check if folder exists before performing the action
    """
    if os.path.exists(path + "/" + folder):
        return

    if os.path.exists(folder):
        shutil.copytree(folder, path + "/" + folder)
    else:
        print("   -> No folder '" + folder[2:] + "' found. Skipping this step!")


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

            if updater_auto_update:
                shutil.copy(file_name, path)
            else:
                shutil.move(file_name, path)

        if not updater_auto_update:
            # Delete the folder from the game directory
            remove(folder)

            # Make sure to delete "files" if there are no contents left
            parts = folder.split("/", 2)[:2]
            result = "/".join(parts)
            if os.listdir(result) == []:
                remove(result)


def merge_folders(src_folder, dest_folder):
    """Merge two folders together.

    If files exist in both folders, the destination folder's file will be kept."""
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for item in os.listdir(src_folder):
        src_item = os.path.join(src_folder, item)
        dest_item = os.path.join(dest_folder, item)

        if os.path.isdir(src_item):
            merge_folders(src_item, dest_item)
        elif not os.path.exists(dest_item):
            shutil.copy2(src_item, dest_item)


def get_latest_release_version(repo):
    """Get latest release version from GitHub for a given repository.

    Example, as of 2023-02-23:
    print(get_latest_release_version("GTNewHorizons/lwjgl3ify"))
    => 1.1.32
    """
    url = "https://api.github.com/repos/" + repo + "/releases/latest"
    response = requests.get(url)
    return response.json()["tag_name"]


def add_java_9_to_game(mods_dir):
    """Add/update Java 9+ for client/server."""
    # Retrieve the latest version for the mod from GitHub
    mod_name = "lwjgl3ify"
    repo = "GTNewHorizons/" + mod_name
    version = get_latest_release_version(repo)

    # Set variable names to be used
    mod_name_latest = mod_name + "-" + version
    main_url = (
        "https://github.com/GTNewHorizons/lwjgl3ify/releases/latest/download/"
        + mod_name_latest
    )

    jar_url = main_url + ".jar"
    jar_file = mod_name_latest + ".jar"

    patches_url = main_url + "-multimc.zip"
    patches_file = mod_name_latest + "-multimc.zip"

    forge_url = main_url + "-forgePatches.jar"
    forge_file = mod_name + "-forgePatches.jar"

    if arg == "client":
        # Move to instance directory
        os.chdir("..")

        # Download the mod and patches for the launcher
        urllib.request.urlretrieve(jar_url, jar_file)
        urllib.request.urlretrieve(patches_url, patches_file)

        # Move the jar file into the mod directory
        for object in os.listdir("."):
            if object.endswith("minecraft"):
                shutil.move(jar_file, object + "/" + mods_dir + jar_file)
                break

        # Extract patches and replace if files already exists
        with zipfile.ZipFile(patches_file, "r") as zip_ref:
            zip_ref.extractall(".")

        # Cleanup
        remove(patches_file)

    elif arg == "server":
        # Download the mod and forge patches
        urllib.request.urlretrieve(jar_url, jar_file)
        urllib.request.urlretrieve(forge_url, forge_file)

        # Move the jar file into the mod directory
        shutil.move(jar_file, mods_dir + jar_file)


def remove_java_9_from_game():
    """Remove Java 9+ support from the client.

    Only thing that is required to change if the user has downloaded Java 9+ version
    is to delete the "patches" folder located in the instance folder."""
    # Move to instance directory
    os.chdir("..")

    # Only file required to remove to go back to Java 8
    remove("patches/")


def add_shaders_to_game(folder):
    """Add shaders & configs.

    If OptiFine -> Mod folder
    If OptiFine config -> Game folder
    Otherwise, assume it is shaders or shaders config -> shaders folder
    """
    if not os.path.isdir("shaderpacks"):
        os.mkdir("shaderpacks")

    shaders_files = os.listdir(folder)
    for file in shaders_files:
        src = folder + "/" + file

        if file.casefold().startswith("OptiFine".casefold()):
            dst = os.path.join("mods/", file)
            if updater_auto_update:
                shutil.copy(src, dst)
            else:
                shutil.move(src, dst)

        elif file.startswith("options"):
            dst = os.path.join(file)
            remove(file)
            if updater_auto_update:
                shutil.copy(src, dst)
            else:
                shutil.move(src, dst)

        else:
            dst = os.path.join("shaderpacks/", file)
            if updater_auto_update:
                shutil.copy(src, dst)
            else:
                shutil.move(src, dst)

    if not updater_auto_update:
        # Delete the folder from the game directory
        remove(folder)

        # Make sure to delete "files" if there are no contents left
        parts = folder.split("/", 2)[:2]
        result = "/".join(parts)
        if os.listdir(result) == []:
            remove(result)


def remove(object):
    """Smart remove function, check if file/folder exists first."""
    if os.path.isfile(object) or os.path.islink(object):
        os.remove(object)
    elif os.path.isdir(object):
        shutil.rmtree(object)


def remove_configs(protected):
    """Remove all config files/folders except a select few."""
    try:
        for root, dirs, files in os.walk("./config/"):
            # Create a copy of the dirs list to avoid modifying the original list
            # While iterating over it
            dirs_copy = dirs[:]
            for dirname in dirs_copy:
                # Construct the full directory path
                dir_path = os.path.join(root, dirname)
                # Check if the directory is in the protected list
                if any(
                    os.path.normpath(dir_path).endswith(os.path.normpath(p))
                    for p in protected
                ):
                    # Remove the directory from the list of directories to be searched
                    dirs.remove(dirname)
            for filename in files:
                # Construct the full file path
                file_path = os.path.join(root, filename)
                # Check if the file is not in the protected list
                if any(
                    os.path.normpath(file_path).endswith(os.path.normpath(p))
                    for p in protected
                ):
                    continue
                # Delete the file
                os.remove(file_path)
    except:
        print(
            "ERROR: Invalid path, double-check that the path has the folders: 'config', 'mods', etc."
        )


def extract_game_zip(file, pwd=None):
    """Extract the update file without overwriting existing files."""
    print("Exctracting files...", total_progress())

    # Unzip the zip file without overwriting any existing files
    with zipfile.ZipFile(file) as zf:
        for member in zf.namelist():
            dst_path = os.path.normpath(member.replace("/", os.path.sep))
            if not os.path.exists(dst_path):
                zf.extract(member, ".", pwd)

    print("Cleaning up from extraction...", total_progress())

    # Remove zip file
    remove(file)

    # Remove previous change-log files
    for file in os.listdir():
        if file.startswith("changelog from"):
            remove(file)


def check_shaders():
    """Check if the user wants shaders or not. Remembers the answer."""
    shaders_file = updater_saves_dir + "shaders.txt"
    if not os.path.isfile(shaders_file):
        print("Would you like to install shaders? Expect a drop in 10-40 fps. [Y/n]")
        shader_answer = input("> ").casefold()
        print()

        if shader_answer == "y":
            print(
                "NOTE: Shaders will be installed and this decision will be saved.",
                end=" ",
            )
        else:
            print(
                "NOTE: Shaders will NOT be installed and this decision will be saved.",
                end=" ",
            )
        print("If you change your mind then remove", shaders_file)
        print()

        with open(shaders_file, "w") as f:
            f.write(shader_answer)
    else:
        with open(shaders_file, "r") as f:
            shader_answer = f.readline()
        if shader_answer == "y":
            print("NOTE: Found", shaders_file, "-> Shaders will be installed.")
        else:
            print("NOTE: Found", shaders_file, "-> Shaders will NOT be installed.")
        print()

    # Adjust the progress bar
    if shader_answer == "y":
        global max_progress
        max_progress = str(int(max_progress) + 1)

    return shader_answer


def check_java_version():
    """Ask the user for what version of Java they would like to use."""
    java_version_file = updater_saves_dir + "java-version.txt"
    if not os.path.isfile(java_version_file):
        print(
            "Would you like to use the new and faster, but very experimental, version of Java for GT:NH? [Y/n]"
        )
        print()
        print("WARNING: Java 9+ ONLY works with Prism Launcher.")
        global java_9_answer
        java_9_answer = input("> ").casefold()
        print()

        if java_9_answer == "y":
            print(
                "NOTE: Java 9+ will be used and this decision will be saved.",
                end=" ",
            )
        else:
            print("NOTE: Java 8 will be used and this decision will be saved.", end=" ")
        print("If you change your mind then remove", java_version_file)
        print()

        with open(java_version_file, "w") as f:
            f.write(java_9_answer)
    else:
        with open(java_version_file, "r") as f:
            java_9_answer = f.readline()
        if java_9_answer == "y":
            print("NOTE: Found", java_version_file, "-> Java 9+ will be used.")
        else:
            print("NOTE: Found", java_version_file, "-> Java 8 will be used.")
        print()

    # Adjust the progress bar
    if java_9_answer == "y":
        global max_progress
        max_progress = str(int(max_progress) + 1)


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
    print("Searching for additional mods...", total_progress())
    additional_mods_dir = updater_files_dir + "additional-mods-client"
    copy_dir_to_game(additional_mods_dir, path)

    # Move shaders folder, if user choose so
    shaders_dir = updater_files_dir + "shaders"
    if shader_answer == "y":
        print("Installing shaders...", total_progress())
        copy_dir_to_game(shaders_dir, path)

    # Move into the client directory
    os.chdir(path)

    # Remove certain config folders
    protected = [
        "GregTech/GregTech.cfg",
        "NEI/",
        "betterquesting.cfg",
        "InvTweaks.cfg",
        "InGameInfoXML.cfg",
    ]
    remove_configs(protected)

    # Remove the old directories and files
    for file in to_update:
        remove(file)

    # Extract and update the game
    extract_game_zip(file_name)

    # Add the additional mods to the mod folder
    mods_dir = "./mods/"
    add_dir_to_game(additional_mods_dir, mods_dir)

    # Add shaders & configs
    if shader_answer == "y":
        add_shaders_to_game(shaders_dir)

    # Apply Java 9+ if the user has choosen so
    if java_9_answer == "y":
        print("Applying Java 9+...", total_progress())
        add_java_9_to_game(mods_dir)
    else:
        remove_java_9_from_game()


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
        "Controlling",
        "CustomMainMenu",
        "DefaultWorldGenerator",
        "IC2+Crop+Plugin",
        "InGameInfoXML",
        "MouseTweaks",
        "NettyPatch",
        "OptiFine",
        "ResourceLoader",
        "bettercrashes",
        "betterloadingscreen",
        "boubs-admin-tools",
        "craftpresence",
        "defaultserverlist",
        "fastcraft",
        "inventorytweaks",
        "itlt",
        "journeymap-",
        "oauth",
        "overloadedarmorbar",
        "torohealth",
    ]

    # Move additional mods, if any, to the server folder
    print("Searching for additional mods...", total_progress())
    additional_mods_dir = updater_files_dir + "additional-mods-server"
    copy_dir_to_game(additional_mods_dir, path)

    # Move into the server directory
    os.chdir(path)

    # Remove certain config folders
    protected = [
        "GregTech/GregTech.cfg",
        "aroma1997/",
        "JourneyMapServer/",
        "Morpheus.cfg",
    ]
    remove_configs(protected)

    # Remove the old directories except config
    for dir in dirs_to_update:
        remove(dir)

    # Extract the new files
    extract_game_zip(file_name)

    # Remove client-side mods
    mods_dir = "./mods/"
    mods = os.listdir(mods_dir)
    for mod in mods:
        for client_mod in client_side_mods:
            if mod.casefold().startswith(client_mod.casefold()):
                remove(os.path.join(mods_dir, mod))

    # Add the server version of "JourneyMap", and other additional mods
    # NOTE: Check the version of this mod every "server-pack" update
    add_dir_to_game(additional_mods_dir, mods_dir)

    # Apply Java 9+ to the server
    print("Applying Java 9+...", total_progress())
    add_java_9_to_game(mods_dir)


def update_script():
    print("Pulling the latest version of 'GTNH-Updater'...")
    print()
    zip_name = "GTNH-Updater-latest.zip"
    github_file_name = "GTNH-Updater-main"

    # Define the list of files and folders to remove
    # NOTE: The reason why we don't write the "protected" files instead
    #       is to not accidently delete the entire game directory if
    #       the user wishes to automatically update the game with a launcher.
    to_remove = [
        "./main.py",
        "./UPDATE_CLIENT.bat",
        "./UPDATE_SCRIPT.bat",
        "./UPDATE_SERVER.bat",
        "./files/additional-mods-client",
        "./files/additional-mods-server",
        "./files/shaders",
    ]

    # Loop through every file and folder in the current directory
    for root, dirs, files in os.walk("."):
        for name in files + dirs:
            path = os.path.join(root, name)
            if path in to_remove:
                remove(path)

    # Download latest version
    urllib.request.urlretrieve(
        "https://github.com/flyslime/gtnh-updater/archive/refs/heads/main.zip",
        zip_name,
    )

    # Extract the zip file
    with zipfile.ZipFile(zip_name, "r") as zip_ref:
        zip_ref.extractall(".")

    # Move the new files & folders into the script directory
    merge_folders(github_file_name, ".")

    # Cleanup
    remove(zip_name)
    remove(github_file_name)
    print("UPDATE COMPLETE!")
    print("=> 'GTNH-Updater' has been successfully updated.")


def main():
    # Check for invalid arguments
    try:
        sys.argv[1]
    except:
        print("ERROR: No arguments given. Use 'client', 'server', or 'script'.")
        print()
        print("For example:")
        print("> python main.py client")
        exit()

    # Save the argument globally, used when we are applying Java 9+ for client/server
    global arg
    arg = sys.argv[1]

    if arg == "script":
        # Update the "GTNH-Updater" by pulling latest zip from GitHub
        update_script()
        exit()

    # Create "./files/saves/" if it doesn't exist, as we save the user's data there
    if not os.path.exists(updater_files_dir + "saves"):
        os.makedirs(updater_files_dir + "saves")

    # Check if the user would like to use Java 9+
    # NOTE: Always default to Java 9+ for servers. This is because a
    #       Java 9+ server allows all clients to join, despite Java version.
    if arg == "server":
        global java_9_answer
        java_9_answer = "y"

        global max_progress
        max_progress = str(int(max_progress) + 1)
    else:
        check_java_version()

    # Check if the user wants shaders or not
    shader_answer = ""
    if arg != "server":
        shader_answer = check_shaders()

    client_path = updater_saves_dir + "gamepath.txt"
    server_path = updater_saves_dir + "serverpath.txt"

    # Updater
    if arg == "client":
        path = get_game_path(client_path, "client")
        zip_file = get_zip_file(client_path, path)
        update_client(path, zip_file, shader_answer)

    elif arg == "server":
        path = get_game_path(server_path, "server")
        zip_file = get_zip_file(server_path, path)
        update_server(path, zip_file)
    else:
        print("ERROR: Invalid argument.")
        exit()

    print()
    print("UPDATE COMPLETE!")
    print("=> GT New Horizons", arg, "has successfully been updated.")
    print()
    print("NOTE: Remember to manually update the questbook!")
    print("Use the following command ->", "'/bq_admin default load'")


if __name__ == "__main__":
    main()
