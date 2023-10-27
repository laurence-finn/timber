# Name: Laurence Finn
# Date: 2/25/2023
# Description: Module for the Timber file synchronization/backup functionality.

import os
import re
import shutil
import datetime
import sys

from tqdm import tqdm
from timber_logger import TimberLogger


# Increase the buffer size for shutil.copyfileobj to improve copy speed
def _copyfileobj_patched(fsrc, fdst, length=16 * 1024 * 1024):
    while 1:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)


shutil.copyfileobj = _copyfileobj_patched


class TimberSync:

    def __init__(self):
        self.delete_preference = False
        self.source = ""
        self.destination = ""
        self.new_destination = False
        self.ignored_directories = []
        self.files_to_copy = set()
        self.files_to_delete = []
        self.dirs_to_delete = []

        # Initialize logger
        self.logger = TimberLogger()
        self.logger.log("Timber Sync initialized.")

    def check_corrupt(self, source_file, destination_file):
        # This function checks the size of the source and destination files to see if they match.
        # If they don't match, "false" is returned and file_copy will attempt the copy operation again.
        try:
            if os.path.getsize(destination_file) < os.path.getsize(source_file):
                self.logger.log("File %s is corrupt. Deleting and retrying copy." % destination_file)
                os.remove(destination_file)
                return True
            else:
                return False
        except FileNotFoundError:
            self.logger.log("Error checking file %s. Skipping." % destination_file)
            return False

    def file_analyze_for_copy_update(self, source, destination, ignored_directories):
        # This function analyzes the source and destination directories and determines which files need to be copied
        # and which files need to be updated. The results are stored in the files_to_copy and files_to_update sets.

        self.files_to_copy.clear()
        new_count = 0
        updated_count = 0
        file_size = 0

        print("Analyzing files for copying and updating...")

        for root, dirs, files in os.walk(source):
            dirs[:] = [d for d in dirs if d not in ignored_directories]
            if root != source and os.path.relpath(root, source) in ignored_directories:
                continue

            for file in files:

                source_file = os.path.join(root, file)
                destination_file = os.path.join(destination, os.path.relpath(source_file, source))

                if os.path.exists(destination_file):

                    # If the source file is newer than the destination file, mark it for update.
                    # If the source and destination file have the same timestamp, but the sizes are different,
                    # mark it for update.
                    try:
                        source_time = datetime.datetime.fromtimestamp(os.path.getmtime(source_file))
                        destination_time = datetime.datetime.fromtimestamp(os.path.getmtime(destination_file))
                        source_size = os.path.getsize(source_file)
                        destination_size = os.path.getsize(destination_file)
                    except PermissionError:
                        self.logger.log("Permission denied. Skipping %s" % destination_file)
                        continue
                    if source_time > destination_time or source_size != destination_size:
                        self.files_to_copy.add((source_file, destination_file, True))
                        updated_count += 1
                        file_size += source_size

                elif not os.path.exists(destination_file):
                    self.files_to_copy.add((source_file, destination_file, False))
                    new_count += 1
                    file_size += os.path.getsize(source_file)

        # reformat the file size to megabytes or gigabytes, whichever is appropriate
        if file_size > 1000000000:
            file_size = str(round(file_size / 1000000000, 2)) + " GB"
        elif file_size > 1000000:
            file_size = str(round(file_size / 1000000, 2)) + " MB"

        print("Total file size to copy: %s" % file_size)

        # keep new and updated separate for now because it may be useful in the future
        return new_count + updated_count

    def file_analyze_for_deletion(self, source, destination, ignored_directories):
        # This function will analyze the source and destination directories and determine which files need to be deleted
        # The source file and destination file will be added to the "files_to_delete" set.
        # Directories to delete will be added to the "dirs_to_delete" set.

        self.files_to_delete.clear()
        deleted_count = 0

        print("Analyzing files for deletion...")

        # find files to delete from the destination
        for root, dirs, files in os.walk(destination):
            dirs[:] = [d for d in dirs if d not in ignored_directories]
            if root != destination and os.path.relpath(root, destination) in ignored_directories:
                continue

            for file in files:

                destination_file = os.path.join(root, file)
                common_prefix = os.path.commonprefix([destination_file, destination])
                source_file = os.path.join(source, os.path.relpath(destination_file, common_prefix))

                if not os.path.exists(source_file):
                    self.files_to_delete.append(destination_file)
                    deleted_count += 1

        # find empty directories to delete from the destination
        for root, dirs, files in os.walk(destination, topdown=False):
            dirs[:] = [d for d in dirs if d not in ignored_directories]
            if root != destination and os.path.relpath(root, destination) in ignored_directories:
                continue

            for directory in dirs:
                destination_dir = os.path.join(root, directory)
                common_prefix = os.path.commonprefix([destination_dir, destination])
                source_dir = os.path.join(source, os.path.relpath(destination_dir, common_prefix))
                if not os.path.exists(source_dir):
                    self.dirs_to_delete.append(destination_dir)

        return deleted_count

    def file_copy(self, source, destination, ignored_directories):
        file_count = self.file_analyze_for_copy_update(source, destination, ignored_directories)

        # while analyze_files can count the new and updated files, redoing the count here
        # is more accurate, because file operation failures will not be counted.
        new_count = 0
        updated_count = 0
        new_dir_count = 0

        print("Copying new and updated files...")

        with tqdm(total=file_count, unit='file') as pbar:
            for source_file, destination_file, exists in self.files_to_copy:

                # if the destination directory doesn't exist, create it
                destination_dir = os.path.dirname(destination_file)
                if not os.path.exists(destination_dir):
                    self.logger.log("Creating directory %s" % destination_dir)
                    try:
                        os.makedirs(destination_dir)
                        new_dir_count += 1
                    except PermissionError:
                        self.logger.log("Permission denied. Skipping %s" % destination_dir)
                        continue

                # while the file isn't created or updated properly (due to corruption), keep trying
                while True:
                    # if the file already exists, update it
                    if exists:
                        self.logger.log("Updating %s" % destination_file)
                        # try to delete then copy file, but if it's in use, skip it
                        try:
                            os.remove(destination_file)
                            shutil.copy2(source_file, destination_file)
                            updated_count += 1
                        except PermissionError:
                            self.logger.log("Permission denied. Skipping %s" % destination_file)

                    # if the file doesn't exist, copy it
                    elif not exists:
                        self.logger.log("Copying %s to %s" % (source_file, destination_file))
                        try:
                            shutil.copy(source_file, destination_file)
                            new_count += 1
                        except PermissionError:
                            self.logger.log("Permission denied. Skipping %s" % destination_file)
                    if self.check_corrupt(source_file, destination_file):
                        continue
                    else:
                        break

                pbar.update(1)

        return new_count, updated_count, new_dir_count

    def file_delete(self, source, destination, ignored_directories):
        file_count = self.file_analyze_for_deletion(source, destination, ignored_directories)

        if file_count == 0:
            return 0, 0

        deleted_count = 0
        deleted_dir_count = 0

        print("Deleting files from destination that are not in source...")

        with tqdm(total=file_count, unit='file') as pbar:
            for destination_file in self.files_to_delete:
                self.logger.log("Deleting %s" % destination_file)
                try:
                    os.remove(destination_file)
                    deleted_count += 1
                except PermissionError:
                    self.logger.log("Permission denied. Skipping %s" % destination_file)

                pbar.update(1)

        # delete directories that do not exist in source
        print("Deleting directories that are not in source...")

        for destination_dir in self.dirs_to_delete:
            self.logger.log("Deleting %s" % destination_dir)
            try:
                os.rmdir(destination_dir)
                deleted_dir_count += 1
            except OSError:
                self.logger.log("Could not delete %s." % destination_dir)
                continue

        return deleted_count, deleted_dir_count

    def set_sync_settings(self, source="", destination="", ignored_directories="", delete_preference=False):
        self.source = source

        if not os.path.isdir(self.source):
            msg = "Invalid source directory. Exiting..."
            print(msg), self.logger.log(msg)
            sys.exit(1)

        self.destination = destination

        # check if the destination has a colon or double backslash
        if self.destination[1] != ":" and (self.destination[0] + self.destination[1]) != "\\\\":
            msg = "Invalid destination directory. Exiting..."
            print(msg), self.logger.log(msg)
            sys.exit(1)

        if (self.destination[0] + self.destination[1]) != "\\\\" and not os.path.exists(self.destination[0] + ":"):
            msg = "Invalid destination drive letter. Exiting..."
            print(msg), self.logger.log(msg)
            sys.exit(1)

        if not all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-. "
                   for c in self.destination.split("\\")[-1]):
            msg = "Invalid destination directory due to illegal characters. Exiting..."
            print(msg), self.logger.log(msg)
            sys.exit(1)

        if not os.path.isdir(self.destination):
            try:
                os.makedirs(self.destination)
                self.new_destination = True
                msg = "Destination directory %s was not found. Created the new folder successfully." \
                      % self.destination
                print(msg), self.logger.log(msg)
            except OSError:
                msg = "Could not create directory %s. " \
                      "This may be because you do not have permission to create " \
                      "directories in this location." % self.destination
                print(msg), self.logger.log(msg)
                sys.exit(1)

        if ignored_directories != "":
            self.set_ignored_directories(ignored_directories)

        self.delete_preference = delete_preference

        msg = "Source and destination directories set to %s and %s" % (self.source, self.destination)
        print(msg), self.logger.log(msg)

    def set_ignored_directories(self, ignored_directories=""):
        self.ignored_directories = ignored_directories

        self.ignored_directories = self.ignored_directories.split(",")
        # format the ignored directories to be compatible with the os.walk() function
        for i in range(len(self.ignored_directories)):
            self.ignored_directories[i] = self.ignored_directories[i].replace("\\", "/")
        self.ignored_directories.append("$RECYCLE.BIN")

    def update_dirname_datetime(self, source, new_destination_dirname):
        # If the source directory contains YYYY-MMDD in the name,
        # update the destination directory name to include the correct date.

        # if the source contains regex YYYY-MMDD and destination does too
        if re.search(r"\d{4}-\d{2}\d{2}", source) and re.search(r"\d{4}-\d{2}\d{2}", new_destination_dirname):
            source_date = re.search(r"\d{4}-\d{2}\d{2}", source).group(0)
            new_destination_dirname = re.sub(r"\d{4}-\d{2}\d{2}", source_date, new_destination_dirname)
            # change the destination directory to the new destination name
            os.rename(self.destination, new_destination_dirname)
            msg = "Destination directory name updated to %s" % new_destination_dirname
            print(msg), self.logger.log(msg)

    def sync(self, source, destination, ignored_directories, delete_preference):

        # check if the sync settings are valid and if so, set them
        self.set_sync_settings(source, destination, ignored_directories, delete_preference)

        # copy and update files from source to destination
        new_count, updated_count, new_dir_count = self.file_copy(self.source, self.destination,
                                                                 self.ignored_directories)

        # delete files from destination that are not in source
        if self.delete_preference:
            deleted_count, deleted_dir_count = self.file_delete(self.source, self.destination, self.ignored_directories)
        else:
            deleted_count = 0
            deleted_dir_count = 0

        # Update the destination file name with a new date, if appropriate
        self.update_dirname_datetime(self.source, self.destination)

        # Print and log a summary of the sync
        msg = f"Sync complete.\n" \
              f"{new_count} files copied | {updated_count} files updated | {deleted_count} files deleted\n" \
              f"{new_dir_count} directories created | {deleted_dir_count} directories deleted\n"
        print(msg), self.logger.log(msg)
        print("See timber.log for additional details.")
