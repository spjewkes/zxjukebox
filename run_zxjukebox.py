#!/usr/bin/env python3

import argparse
import sys
import os
import glob
import random
import subprocess
import time

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
    tzx_files = glob.glob(os.path.join(folder, "**/*.tzx"), recursive=True)

    # Prepare main arguments
    tzxplay = ["tzxplay"]
    tzxplay.append("--verbose")
    if args.soft:
        tzxplay.append("--sine")
    if args.only48k:
        tzxplay.append("--48k")
    if not args.all:
        tzxplay.append("--stop")

    # Last item is always the game to play, add a dummy entry to be replace every iteration
    tzxplay.append("DUMMY")

    while True:
        game = random.choice(tzx_files)
        print("Loading file: {}".format(game))
        print("==> {}".format(os.path.basename(game)))

        if not args.noplay:
            tzxplay[-1] = game
            subprocess.run(tzxplay)

        print("-" * 80)
        time.sleep(args.gap)

        if args.once:
            break

    return 0

if __name__ == '__main__':
    sys.exit(main())
    
