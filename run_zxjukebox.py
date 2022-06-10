#!/usr/bin/env python3
"""
This is a simple program that can scan for TZX and randomly select and play them continuously.
It will also select all ZIP files in the same folder and include those in its random selection.
"""
import argparse
import sys
import os
import random
import subprocess
import time
import tempfile
import zipfile

from pathlib import Path
from enum import Enum, auto

class Filetype(Enum):
    """
    Define the filetypes this application supports
    """
    UNKNONW = auto()
    TZX = auto()
    ZIP = auto()

def get_tzx_from_path(pathname, match="", include_zip=False):
    """
    Returns list of TZX files from a path. Can optionally include ZIP files.
    """
    extensions = {".tzx"}
    pattern = match.lower()
    if include_zip:
        extensions.add(".zip")
    return [p.resolve() for p in Path(pathname).glob("**/*") if p.suffix in extensions and str(p).lower().find(pattern) != -1]

def get_filetype(filename):
    """
    Returns the type of file passed into it.
    """
    extension = Path(filename).suffix
    if extension == ".tzx":
        return Filetype.TZX
    elif extension == ".zip":
        return Filetype.ZIP

    return Filetype.UNKNOWN

def play_tzx_file(filename, args):
    """
    Plays a TZX file using the utility 'tzxplay'
    """
    # Prepare the arguments
    tzxplay = ["tzxplay"]
    tzxplay.append("--verbose")
    if args.soft:
        tzxplay.append("--sine")
    if args.only48k:
        tzxplay.append("--48k")
    if not args.all:
        tzxplay.append("--stop")

    tzxplay.append(filename)
    try:
        subprocess.run(tzxplay, check=True)
    except subprocess.CalledProcessError:
        pass

def play_zip_file(filename, args):
    """
    Plays a zipped TZX file.
    """
    # Create temporary folder for ZIP
    with tempfile.TemporaryDirectory() as tempdir:
        zipfile.ZipFile(filename).extractall(tempdir)
        tzx_files = get_tzx_from_path(tempdir, args.match)
        if not tzx_files:
            print(f"No TZX files found in {filename}!")
            return

        game = random.choice(tzx_files)
        play_tzx_file(game, args)

def main():
    parser = argparse.ArgumentParser(description='Loads TZX files and uses tzxplay to play them randomly')
    parser.add_argument('folder', metavar='FOLDER', type=str, help='The folder containing the TZX files to load')
    parser.add_argument('--soft', help="Loading sounds are less harsh", action='store_true')
    parser.add_argument('--only48k', help="Enable ZX Spectrum 48k loading only", action='store_true')
    parser.add_argument('--all', help="Play entire TZX file rather than ending at stop-the-tape marker", action='store_true')
    parser.add_argument('--once', help="Play one randomly selected file and then stop", action='store_true')
    parser.add_argument('--noplay', help="Randomly selects games but does not play them", action='store_true')
    parser.add_argument('--gap', type=int, default=5, help="Time (in seconds) to wait between each file (default is 5 seconds")
    parser.add_argument('--match', type=str, default="", help="Find all files matching sub-string (not case sensitive)")
    parser.add_argument('--list', help="List all TZX files found and exit", action='store_true')

    args = parser.parse_args()

    # Get list of TZX games from folder
    folder = os.path.abspath(args.folder)

    if not os.path.exists(folder):
        raise RuntimeError(f"Invalid folder: {folder}")

    tzx_files = get_tzx_from_path(folder, args.match, include_zip=True)
    if not tzx_files:
        raise RuntimeError(f"No TZX files found in: {folder}")

    if args.list:
        for tzxfile in tzx_files:
            name = str(tzxfile).replace(folder, "", 1)
            print(f".{name}")
        return 0

    while True:
        game = random.choice(tzx_files)
        print(f"Loading file: {game}")
        print(f"==> {os.path.basename(game)}")

        if not args.noplay:
            filetype = get_filetype(game)
            if filetype == Filetype.TZX:
                play_tzx_file(game, args)
            elif filetype == Filetype.ZIP:
                play_zip_file(game, args)

        print("-" * 80)
        time.sleep(args.gap)

        if args.once:
            break

    return 0

if __name__ == '__main__':
    major = sys.version_info.major
    minor = sys.version_info.minor
    if major < 3 or (major == 3 and minor < 7):
        raise RuntimeError(f"This app requires at least python v3.7 to work (this is v{major}.{minor}")

    sys.exit(main())
