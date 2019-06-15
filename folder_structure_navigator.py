"""Gui"""

import os
import json
import datetime
import tkinter as tk
from tkinter import font
from tkinter import filedialog
# from pprint import pprint


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
    def __init__(self, data):
        self.data = data
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
        try:
            return self.current["__/files"]
        except KeyError:
            return []  # Root dir

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
        # print("started")
        files = structure["__/files"]
        # print(structure.keys())
        # print(list(structure.keys()).remove("__/files"))
        # folders = list(structure.keys()).remove("__/files")
        folders = list(structure.keys())
        folders.remove("__/files")
        # print(folders)
        yield folders, files
        if folders is None:
            folders = []
        # print(folders, files)
        for folder in folders:
            # print("entering", folder)
            # print(structure[folder].keys())
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


class App(tk.Tk):
    """Navigator"""
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Structure Backup Navigator")
        # with open("file system structure4.txt", "r") as file:
        #     data = json.load(file)
        # self.traverser = JsonTraverser(data)
        self.traverser = None
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=16)
        self.option_add("*Font", default_font)
        self.init_listbox()
        self.init_infobox()
        self.init_menu()
        # self.update_()

    def init_data(self, name):
        """Load data"""
        if not name:
            return
        self.status["text"] = "Parsing file..."
        self.status.update()
        with open(name, "r") as file:
            data = json.load(file)
        self.traverser = JsonTraverser(data)
        self.update_()

    def init_listbox(self):
        """start listbox"""
        frame = tk.Frame(self)
        frame.grid(row=0, column=0, sticky="news")
        tk.Grid.rowconfigure(self, 0, weight=1)
        tk.Grid.columnconfigure(self, 0, weight=1)
        tk.Grid.rowconfigure(frame, 0, weight=1)
        tk.Grid.columnconfigure(frame, 0, weight=1)
        tk.Grid.columnconfigure(frame, 1, weight=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="news")
        listbox = tk.Listbox(frame, width=40, yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        listbox.configure(exportselection=False)
        # listbox.config(font=("TkDefaultFont", "19"))
        # default_font = font.nametofont("TkDefaultFont")
        # default_font.configure(size=16)
        # listbox.option_add("*Font", default_font)

        status = tk.Label(self, text="Please open a Structure file.",
                          bd=2, relief=tk.SUNKEN,
                          justify="left", anchor="w")
        status.grid(row=100, columnspan=2, sticky="news")
        self.status = status

        def double_click_function(event):
            """Determine if genuine double click, if not,
            simulate single-click, else enter selected directory."""
            try:
                current = self.current_val()
            except KeyError:
                index = self.listbox.index("@{},{}".format(event.x, event.y))
                self.listbox.select_set(index)
                return
            # print(current.encode("utf-8", "ignore").decode())
            if current != "..":
                self.down(current)
            else:
                self.up()

        def select_function(_):
            """Called when entry is selected"""
            try:
                self.update_infobox()
            except KeyError:
                pass
            # return self.current_val()
        listbox.bind("<<ListboxSelect>>", select_function)
        listbox.bind('<Double-Button-1>', double_click_function)
        listbox.grid(row=0, column=0, sticky="NEWS")
        # listbox.popup_menu = tk.Menu(listbox, tearoff=0)
        # listbox.popup_menu.add_command(
        #     label="Delete", command=lambda x: print("Delete"))
        # listbox.popup_menu.add_command(
        #     label="Select All", command=lambda x: print("Select"))
        # listbox.bind("<Button-3>", lambda x: self.popup(listbox, x))
        self.listbox = listbox
        # self.update_()
        # listbox.select_set(0)

    def init_infobox(self):
        """Generate Right hand info page."""
        infobox = tk.Label(self, text="", justify="left")
        infobox.grid(row=0, column=1, sticky="n")
        self.infobox = infobox

    def init_menu(self):
        """Make the menu bar"""

        def select_file():
            """Show file explorer to select json file"""
            filename = filedialog.askopenfilename(
                initialdir=os.getcwd(), title="Select Backup file...",
                filetypes=(("Text files", "*.txt"),
                           ("JSON files", "*.json")))
            self.init_data(filename)
        menu = tk.Menu(self)
        self.config(menu=menu)
        # file_menu = tk.Menu(menu)
        # menu.add_cascade(label="File", menu=file_menu)
        # file_menu.add_command(label="Open...", command=select_file)
        menu.add_command(label="Open...", command=select_file)

    def update_(self):
        """Call all update functions"""
        self.update_listbox()
        self.update_statusbar()

    def update_listbox(self):
        """Clear and refresh listbox"""
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, "..")
        for item in self.traverser.content_nice():
            self.listbox.insert(tk.END, item)

    def update_statusbar(self):
        """statusbar update"""
        # print("Hi")
        # print(self.traverser.current_path())
        self.status["text"] = "{} Ordner, {} Dateien\n{}".format(
            *self.traverser.current_folder_info(), self.traverser.current_path())

    def update_infobox(self):
        """Write Infos to the infobox."""
        try:
            selection = self.current_val()
        except IndexError:
            return
        if self.traverser.is_folder(selection):
            text = "Subfolders:\n{}\n\nSubfiles:\n{}\n\nSize:\n{}".format(
                *self.traverser.subdir_info(selection, selection == ".."))
            self.infobox["text"] = text
        else:
            text = ("Size:\n{}\n\nCreated:\n{}\n\n"
                    "Last Modified:\n{}\n\nLast Accessed:\n{}\n\n").format(
                        *self.traverser.file_info(selection))
            self.infobox["text"] = text

    @staticmethod
    def popup(element, event):
        """Put a popup."""
        try:
            element.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            element.popup_menu.grab_release()

    def current_val(self):
        """Get the currently selected value. Exception if nothing selected."""
        try:
            return self.listbox.get(self.listbox.curselection()[0])
        except IndexError:
            raise KeyError("Nothing selected")

    def up(self):  # pylint: disable=invalid-name
        """up"""
        try:
            self.traverser.up()
            self.update_()
        except OutOfStructureException:
            pass

    def down(self, name):
        """down"""
        # print(name.encode("ascii", "ignore"))
        try:
            self.traverser.down(name)
            self.update_()
        except FileNotFoundError:
            pass


def main():
    """main"""
    App().mainloop()


if __name__ == '__main__':
    main()
