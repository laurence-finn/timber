# Name: Laurence Finn
# Date: 12/8/2022
# Description: Main module for the Timber program.

import argparse
import sys

from timber_sync import TimberSync

if __name__ == "__main__":

    # if there are no arguments, exit
    if len(sys.argv) == 1:
        sys.exit()

    parser = argparse.ArgumentParser(description="Timber: A file cataloging and backup utility")
    parser.add_argument("-s", "--source", dest="source", required=True,
                        help="Required. The source directory to catalog or synchronize.")
    parser.add_argument("-d", "--destination", dest="destination",
                        help="The destination directory to synchronize.")
    parser.add_argument("-x", "--delete", action="store_true",
                        help="Delete files in the destination directory that do not exist in the source directory.")
    parser.add_argument("-i", "--ignore", dest="ignore", type=str, default="",
                        help="A comma-separated list of directories to ignore when cataloging or synchronizing."
                             "Example: -i temp,documents\\finances,documents\\project\\images")
    args = parser.parse_args()

    sync = TimberSync()
    sync.sync(args.source, args.destination, args.ignore, args.delete)

    sys.exit()
