# Name: Laurence Finn
# Date: 2/27/2023
# Description: Module for saving and loading Timber settings.

import os
import xml.etree.ElementTree as ET


class TimberSettings:
    def __init__(self):
        self.settings_file = "timber_settings.xml"
        self.recent_sources = []
        self.recent_destinations = []
        self.recent_catalogs = []
        self.recent_ignored_directories = []
        self.recent_delete_preferences = []
        self.MAX_RECENT = 5

    def load_settings(self):
        self.recent_sources.clear()
        self.recent_destinations.clear()
        self.recent_catalogs.clear()
        self.recent_ignored_directories.clear()
        self.recent_delete_preferences.clear()

        try:
            if os.path.exists(self.settings_file):
                tree = ET.parse(self.settings_file)
                root = tree.getroot()

                source_count = 0
                dest_count = 0
                ignored_dir_count = 0
                del_pref_count = 0

                for source in root.iter("source"):
                    self.recent_sources.append(source.text)
                    source_count += 1
                for destination in root.iter("destination"):
                    self.recent_destinations.append(destination.text)
                    dest_count += 1
                for catalog in root.iter("catalog"):
                    self.recent_catalogs.append(catalog.text)
                for ignored_directory in root.iter("ignored_directory"):
                    self.recent_ignored_directories.append(ignored_directory.text)
                    ignored_dir_count += 1
                for delete_preference in root.iter("delete_preference"):
                    self.recent_delete_preferences.append(delete_preference.text)
                    del_pref_count += 1

                self.check_corrupt_settings(source_count, dest_count, ignored_dir_count, del_pref_count)
            else:
                print("Settings not found. A new file will be created.")
                self.save_settings()
        except ET.ParseError:
            print("Error: The settings file could not be loaded. Deleting and creating a new one.")
            try:
                os.remove(self.settings_file)
                self.save_settings()
            except OSError:
                print("Error: Could not delete settings file.")

    def check_corrupt_settings(self, source_count, dest_count, ignored_dir_count, del_pref_count):
        if source_count == dest_count == ignored_dir_count == del_pref_count:
            return
        else:
            print("Error: The settings file is corrupt. Deleting and creating a new one.")
            try:
                os.remove(self.settings_file)
                self.load_settings()
            except OSError:
                print("Error: Could not delete settings file.")

    def add_source_and_destination(self, source, destination):
        # If there are already five sources, remove the last one
        if len(self.recent_sources) == self.MAX_RECENT:
            self.recent_sources.pop()

        # Add the source to the beginning of the list
        self.recent_sources.insert(0, source)

        # If there are already five destinations, remove the last one
        if len(self.recent_destinations) == self.MAX_RECENT:
            self.recent_destinations.pop()

        # Add the destination to the beginning of the list
        self.recent_destinations.insert(0, destination)

    def add_catalog(self, catalog):
        # If there are already five catalogs, remove the last one
        if len(self.recent_catalogs) == self.MAX_RECENT:
            self.recent_catalogs.pop()

        # Add the catalog to the beginning of the list
        self.recent_catalogs.insert(0, catalog)

    def add_ignored_directories(self, ignored_directories_string):
        # If there are already five ignored directories, remove the last one
        if len(self.recent_ignored_directories) == self.MAX_RECENT:
            self.recent_ignored_directories.pop()

        # Add the ignored directories string to the beginning of the list
        self.recent_ignored_directories.insert(0, ignored_directories_string)

    def add_delete_preference(self, delete_preference):
        # If there are already five delete preferences, remove the last one
        if len(self.recent_delete_preferences) == self.MAX_RECENT:
            self.recent_delete_preferences.pop()

        # Add the delete preference to the beginning of the list
        self.recent_delete_preferences.insert(0, delete_preference)

    def remove_dupes(self):
        i = 0
        while i < len(self.recent_sources):
            j = i + 1
            while j < len(self.recent_sources):
                if (self.recent_sources[i] == self.recent_sources[j] and
                        self.recent_destinations[i] == self.recent_destinations[j] and
                        self.recent_ignored_directories[i] == self.recent_ignored_directories[j] and
                        self.recent_delete_preferences[i] == self.recent_delete_preferences[j]):
                    self.recent_sources.pop(j)
                    self.recent_destinations.pop(j)
                    self.recent_ignored_directories.pop(j)
                    self.recent_delete_preferences.pop(j)
                else:
                    j += 1
            i += 1

    def save_settings(self):
        self.remove_dupes()
        root = ET.Element("sync_settings")
        for source in self.recent_sources:
            ET.SubElement(root, "source").text = source
        for destination in self.recent_destinations:
            ET.SubElement(root, "destination").text = destination
        for catalog in self.recent_catalogs:
            ET.SubElement(root, "catalog").text = catalog
        for ignored_directory in self.recent_ignored_directories:
            ET.SubElement(root, "ignored_directory").text = ignored_directory
        for delete_preference in self.recent_delete_preferences:
            ET.SubElement(root, "delete_preference").text = delete_preference
        tree = ET.ElementTree(root)
        tree.write(self.settings_file)

    def is_empty(self):
        if len(self.recent_sources) == 0:
            return True
        else:
            return False
