# Name: Laurence Finn
# Date: 2/25/2023
# Description: Module for the Timber menus.

from timber_catalog import TimberCatalog
from timber_sync import TimberSync

class TimberConsole:
    def __init__(self):
        pass

    def menu(self):
        print("============================================")
        print("Timber: A file cataloging and backup utility")
        print("============================================")
        print("1. Catalog a directory")
        print("2. Synchronize (back up) folders")
        print("3. Exit")
        while True:
            choice = input("> ")
            try:
                choice = int(choice)
            except ValueError:
                print("Invalid choice. Please try again.")
                continue
            if choice == 1:
                catalogger = TimberCatalog()
                catalogger.catalog()
                return
            elif choice == 2:
                sync = TimberSync()
                sync.sync()
                return
            elif choice == 3:
                return
            else:
                print("Invalid choice. Please try again.")
                continue
