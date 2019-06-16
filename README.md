# Folder Structure Navigator
## Why?
Drive Failures are very, annoying, even if you have backups of the importing files. Anyway, after the device has been lost, it's hard to know if really everything important was saved. Also, it can be useful to know what was present on the drive to restore e.g. program files. Even if the device is not fully lost yet, but close to it's end, access times may be very slow and could accelerate the drive's demise.

Even if the device is working alright, it might be useful to have a snapshot of the folder structure which supports quick Aggregation of file sizes of child directories, even if the device is currently not mounted.

For this purpose, I wrote this program.
## Content

### Folder Structure Navigator

This program provides an Exporer-like graphical user interface to navigate though the json file.



### Folder Structure Backup
This program is used by the Navigator, though it can be called by the command line as well e.g. for automatic generation.

This program takes a path and walks though every child directory and files. It writes the output into a .json file. The Folder name will be the key and the child directories the values. Every layer as a key "\_\_/files" which contains the files in the current directory.

As default, the program saves size, modification, creation and last access date for every file. This can be disabled, which results in a smaller file size, hence faster parsing when processing said file.

## Note
No additional libraries are used in this project, it can be started using out-of-the-box Python3. (Except if your distribution does not include tkinter natively. On windows this should be given, on Linux, it can be installed by e.g. `sudo apt-get install python3-tk`).

If you find a bug or a missing feature, feel free to open an issue or drop me a note if you like this.
