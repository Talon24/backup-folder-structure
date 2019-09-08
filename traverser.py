"""Traverser library."""


import os
import datetime
import json


def sizeof_fmt(num, suffix='B'):
    """Human readable file size"""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


class OutOfStructureException(Exception):
    """Raise this if beyond boundaries of Structure."""


class JsonTraverser():
    """Navigate through the object."""
    def __init__(self, data=False, jsonfile=False):
        if data:
            self.data = data
        elif jsonfile:
            with open(jsonfile, "r") as file:
                self.data = json.load(file)
        elif not data and not json:
            raise ValueError("No data given")
        # self.position = list(data.keys())
        self.position = []
        self.current = self.data
        self._base = self.position[:]
        # pprint(self.position)

    def up(self):  # pylint: disable=invalid-name
        """Go to the parent directory."""
        if not self.position:
            raise OutOfStructureException
        self.position.pop()
        current = self.data
        for folder in self.position:
            current = current[folder]
        self.current = current
        return self

    def down(self, name):
        """Go to the specified child directory."""
        name = self.clear_name(name)
        try:
            self.current = self.current[name]
            self.position.append(name)
            return self
        except KeyError:
            raise FileNotFoundError

    def folders(self):
        """Get the folders in the current folder."""
        folders = list(self.current.keys())
        try:
            folders.remove("__/files")
        except ValueError:
            pass  # Root dir
        return folders

    def files(self):
        """Get the files in the current folder."""
        return self.current.get("__/files", [])

    def content(self):
        """Get everything in current folder."""
        return self.folders() + self.files()

    def content_nice(self):
        """Folder content with indictor Emoji."""
        return (["\ud83d\udcc1 " + folder for folder in self.folders()] +
                ["\ud83d\udcdd " + file for file in self.files()])

    def current_folder_info(self):
        """Return how many folders and how many files in the current folder."""
        return len(self.folders()), len(self.files())

    def current_path(self):
        """Get the path of the current position."""
        # print(self.position)
        return os.sep.join([i.replace(os.sep, "") for i in self.position])

    def subdir_info(self, name, current_directory=False):
        """Count subfolders and files."""
        name = self.clear_name(name)
        folders_n = files_n = size = 0
        if current_directory:
            structure = self.current
        else:
            structure = self.current[name]
        for _, files in self.walk(structure):
            folders_n += 1
            files_n += len(files)
            try:
                size += sum([file.get("size", 0) for file in files.values()])
            except AttributeError:
                pass
        folders_n -= 1  # remove self
        size = sizeof_fmt(size)
        return folders_n, files_n, size

    def file_info(self, name):
        """Get information about a file."""

        def timeformat(timestamp):
            return datetime.datetime.utcfromtimestamp(
                timestamp).strftime('%Y-%m-%d %H:%M:%S')
        name = self.clear_name(name)
        try:
            file = self.current["__/files"][name]
        except TypeError:
            return None, None, None, None
        size = sizeof_fmt(file.get("size"))
        accessed = timeformat(file.get("accessed"))
        modified = timeformat(file.get("modified"))
        created = timeformat(file.get("created"))
        return (size, created, modified, accessed)

    # @staticmethod
    def walk(self, structure):
        """Recursively walk the structure."""
        try:
            files = structure.get("__/files", {})
        except AttributeError:  # root element is list
            files = {}
        folders = list(structure.keys())
        if "__/files" in folders:
            folders.remove("__/files")
        yield folders, files
        if folders is None:
            folders = []
        for folder in folders:
            yield from self.walk(structure[folder])

    @staticmethod
    def clear_name(name):
        """Remove Indicator emoji if present"""
        if name.startswith("\ud83d\udcdd") or name.startswith("\ud83d\udcc1"):
            name = name[3:]
        return name

    def is_folder(self, name):
        """Is given name a folder?"""
        return self.clear_name(name) in self.folders() or name == ".."
