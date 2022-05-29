#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import random
import subprocess
import time
import tempfile
import zipfile

from pathlib import Path
from enum import Enum, auto

class Filetype(Enum):
    UNKNONW = auto()
    TZX = auto()
    ZIP = auto()

def getTZXFromPath(pathname, include_zip=False):
    """
    Returns list of TZX files from a path. Can optionally include ZIP files.
    """
    extensions = {".tzx"}
    if include_zip:
        extensions.add(".zip")
    return [p.resolve() for p in Path(pathname).glob("**/*") if p.suffix in extensions]

def getFiletype(filename):
    """
    Returns the type of file passed into it.
    """
    extension = Path(filename).suffix
    if extension == ".tzx":
        return Filetype.TZX
    elif extension == ".zip":
        return Filetype.ZIP

    return Filetype.UNKNOWN

def playTZXFile(filename, args):
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
    subprocess.run(tzxplay)

def playZIPFile(filename, args):
    """
    Plays a zipped TZX file.
    """
    # Create temporary folder for ZIP
    with tempfile.TemporaryDirectory() as tempdir:
        zipfile.ZipFile(filename).extractall(tempdir)
        tzx_files = getTZXFromPath(tempdir)
        if not tzx_files:
            print(f"No TZX files found in {filename}!")
            return

        game = random.choice(tzx_files)
        playTZXFile(game, args)

def main():
    parser = argparse.ArgumentParser(description='Loads TZX files and uses tzxplay to play them randomly')
    parser.add_argument('folder', metavar='FOLDER', type=str, help='The folder containing the TZX files to load')
    parser.add_argument('--soft', help="Loading sounds are less harsh", action='store_true')
    parser.add_argument('--only48k', help="Enable ZX Spectrum 48k loading only", action='store_true')
    parser.add_argument('--all', help="Play entire TZX file rather than ending at stop-the-tape marker", action='store_true')
    parser.add_argument('--once', help="Play one randomly selected file and then stop", action='store_true')
    parser.add_argument('--noplay', help="Randomly selects games but does not play them", action='store_true')
    parser.add_argument('--gap', type=int, default=5, help="Time (in seconds) to wait between each file (default is 5 seconds")

    args = parser.parse_args()
    
    # Get list of TZX games from folder
    folder = os.path.abspath(args.folder)

    if not os.path.exists(folder):
        raise RuntimeError(f"Invalid folder: {folder}")

    tzx_files = getTZXFromPath(folder, include_zip=True)
    if not tzx_files:
        raise RuntimeError(f"No TZX files found in: {folder}")

    while True:
        game = random.choice(tzx_files)
        print("Loading file: {}".format(game))
        print("==> {}".format(os.path.basename(game)))

        if not args.noplay:
            filetype = getFiletype(game)
            if filetype == Filetype.TZX:
                playTZXFile(game, args)
            elif filetype == Filetype.ZIP:
                playZIPFile(game, args)

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
    
