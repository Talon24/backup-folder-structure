"""Export a file structure of a drive"""

import os
import sys
# import time
import json
# import pprint
import pathlib
import argparse


def main2():
    """Print output like with tree, but without lines"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Path of root")
    arguments = parser.parse_args()
    path = arguments.path
    print(path)
    minlength = len(pathlib.Path(next(os.walk(path))[0]).parts)
    for current, _, files in os.walk(path):
        name = pathlib.Path(current).name
        length = len(pathlib.Path(current).parts) - minlength
        try:
            print(length * "\t", name, sep="")
        except UnicodeEncodeError:
            print((length + 1) * "\t", "cannot read name of folder", sep="")
            print("Cannot read folder", name, file=sys.stderr)
        for file in files:
            try:
                print((length + 1) * "\t", file.replace("\ufeff", ""), sep="")
            except UnicodeEncodeError:
                print((length + 1) * "\t", "cannot read name of file", sep="")
                print("Cannot read file", file, file=sys.stderr)
                # print(current, file=sys.stderr)
                # print(files, file=sys.stderr)
                # print(file, file=sys.stderr)
                # print("stop execution", file=sys.stderr)
                # sys.exit()


def iterate_path(target_path, mode):
    """Walk through the given path and return subfolder / file information."""
    path = target_path
    # path = pathlib.Path("E:\\")
    minlength = len(pathlib.Path(next(os.walk(path))[0]).parts)
    # output = entry(path.name, "folder")
    output = {}
    for current, _, files in os.walk(path):
        current = pathlib.Path(current)
        substructure = current.parts[minlength-1:]
        cur_level = output
        for layer in substructure:
            if layer not in cur_level:
                cur_level[layer] = {}
            cur_level = cur_level[layer]
        if mode == "fast":
            cur_level["__/files"] = files
        else:
            cur_level["__/files"] = {}
            for file in files:
                try:
                    stats = os.stat(pathlib.Path(current) / file)
                    cur_level["__/files"][file] = {
                        "size": stats.st_size,
                        "modified": stats.st_mtime,
                        "created": stats.st_mtime,
                        "accessed": stats.st_atime
                    }
                except OSError:  # File cannot be accessed
                    cur_level["__/files"][file] = {
                        "size": 0,
                        "modified": 0,
                        "created": 0,
                        "accessed": 0
                    }
    return output


def save(dictionary, output_filename):
    """Write the given dictionary to a file."""
    with open(output_filename, "w") as file:
        file.write(json.dumps(dictionary, indent=4))


def iterate_and_save(target_path, target_filename, mode="big"):
    """Combine Generation and saving as easier interface."""
    dictionary = iterate_path(target_path, mode)
    save(dictionary, target_filename)


def main():
    """Output neat json"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Path of root")
    parser.add_argument("-m", "--mode", help="Generation mode. 'Fast' does "
                        "not include file size e.g. and will result "
                        "in a smaller file", choices=["fast", "big"],
                        default="big")
    arguments = parser.parse_args()
    dictionary = iterate_path(arguments.path, arguments.mode)
    save(dictionary, "file system structure4.txt")


if __name__ == '__main__':
    # start = time.time()
    main()
    # print("Took", int(time.time() - start))
