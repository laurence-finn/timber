# Timber
A Python script that sychronizes files and directories in a destination (target) directory with a source (original) directory. This is useful for ensuring backups are synchronized on your local machine, external hard drive, or a network drive. I personally run this script weekly to sychronize my external "WD Book" hard drive with the important folders on my computer to ensure I have an updated backup.

## Features
- Synchronizes a destination with a source by copying new or updated files and optionally deleting files that aren't present in the source.
- Allows transfer across local network locations. (Example: \\TESTSERVER\Share\Files_To_Sync)
- Provides a progress bar showing the number of files remaining and the time elapsed.
- Ignores directories specified by the user, allowing you to tailor your synchronization.
- Logs all file operation details to timber.log so that you can check for errors and review statistics for the sync process.
- Updates the destination directory name to the source name if the name includes the date (YYYY-MMDD).
    - For example, syncing a source "C:\Files 2022-0311" and destination "\\NETWORK\Share\Files 2021-0130" would change the destination name to "\\NETWORK\Share\Files 2022-0311".

## Installation
This script requires Python 3.x to be installed on your system before running.

Once Python is installed, run the script in the terminal, using the command line arguments listed below.

Alternately, you can run the latest release .EXE from the Releases tab in GitHub.

## Usage
Timber is run from the command line using the following arguments:
- '-s' : (Required) Sets the source destination directory. Example: 'C:\User\Test'. Works with network locations like '\\TESTCOMPUTER\Shared'.
- '-d' : (Required) Sets the destination directory. 
- '-x' : (Optional) Deletes any files or folders that are present in the destination directory but are not in the source. If this argument is not specified, the program will ignore these files and directories.
- '-i' : (Optional) Sets a list of directories to ignore, separated by commas. Example: 'TestDir,TestDir2,$RECYCLEBIN'

## Ideas for New Features/Improvements
- Check for free space on the destination disk before syncing. (Possibly reorganize the program so deleting happens first, then disk space check, then copying new/updated files)
- Add a progress bar for file analysis. (This is the task that determines which files will be copied or deleted.)
- Add sync for OneDrive and Google Drive.
- Optimize performance/file copy speed by calling the Windows API or Linux equivalent. (https://stackoverflow.com/questions/12330522/how-to-copy-a-file-in-python)
- Add an "advanced sync" feature with extra options.
    - Add advanced duplicate protection: If an identical file is found in the destination folder, the user can choose to keep the original, the duplicate, or both. Additionally, if deleting duplicates creates empty folders, the user can choose to delete the empty folders.
- Separate log files for each run.
    - Possibly add a log management feature to delete old logs.
