"""Search a file by its name.

Calling this module directly will start an interactive search session, the
json file is read once and subsequent seaches can be made without reloading."""

import re
import os
import argparse

from folder_structure_navigator import JsonTraverser


def path_format(hierarchy, file):
    """format readable"""
    root = hierarchy[0]
    path = os.sep.join(hierarchy[1:])
    return os.path.join(root, path, file)


def search_recursive(traverser, searchstring, files=True, folders=True):
    """Iterate through object and search for searchstring."""
    if files:
        for filename in traverser.files():
            if re.findall(searchstring, filename, re.IGNORECASE):
                print(path_format(traverser.position, filename))
    if folders:
        for filename in traverser.folders():
            if re.findall(searchstring, filename, re.IGNORECASE):
                print(path_format(traverser.position, filename))
    for folder in traverser.folders():
        traverser.down(folder)
        search_recursive(traverser, searchstring, files, folders)
        traverser.up()


def search(traverser, searchstring, files=True, folders=True):
    """Search for a string in a structure. Initial for recursive."""
    search_recursive(traverser, searchstring, files, folders)


def search_from_file(path, searchstring, files=True, folders=True):
    """Seach wrapper that reads from file diretly"""
    traverser = JsonTraverser(path)
    search_recursive(traverser, searchstring, files, folders)


def main():
    """Interactive searcher. Load file only once, search many times."""
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Source json file")
    parser.add_argument("-s", "--search", help="Search string to find")
    arguments = parser.parse_args()
    print("Loading file...")
    if arguments.search:
        search_from_file(arguments.file, arguments.search)
        return
    try:
        traverser = JsonTraverser(jsonfile=arguments.file)
        while True:
            searchstring = input("Enter regular expression to search\n")
            search(traverser, searchstring)
            print("--------")
    except KeyboardInterrupt:
        print("Goodbye!")
        return


if __name__ == '__main__':
    main()
