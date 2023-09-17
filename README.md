# timber
A console application that helps you keep your file tree organized.
- **File Catalog:** Creates an Excel spreadsheet catalog of all files in a given folder.
- **Sync:** Sychronizes the contents of two folders.

## Ideas for New Features/Improvements
- BUG FIX: Don't delete directories that were set to ignore.
- Add sync for OneDrive and Google Drive.
- Add an "image organizer" feature.
- Optimize performance/file copy speed by calling the Windows API or Linux equivalent. (https://stackoverflow.com/questions/12330522/how-to-copy-a-file-in-python)
- Add an "advanced sync" feature with extra options.
-- Add advanced duplicate protection: If an identical file is found in the destination folder, the user can choose to keep the original, the duplicate, or both. Additionally, if deleting duplicates creates empty folders, the user can choose to delete the empty folders.
- Separate log files for each run.
-- Possibly add a log management feature to delete old logs.
- Add progress bar for deleting directories