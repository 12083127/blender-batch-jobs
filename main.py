#!/usr/bin/env python3
"""
Module Docstring
"""

from appmanager import AppList

__author__ = "Robert Lehmann"
__version__ = "0.1.0"
__license__ = ""


def main():

    AppList.add_installation("/opt/blender/3.0.1/blender")
    AppList.add_installation("/opt/blender/3.2.2/blender")
    AppList.add_installation("/opt/blender/3.2.2/blender")

    print("\n")

    if AppList.get():
        AppList.print()
    else:
        print("Empty")

    # run the render job
    # p1 = subprocess.Popen(
    #     ["/opt/blender/3.0.1/blender", "-b",  "/home/r083127/Documents/batchrender/sandbox/rendertest-a.blend", "-o", "//rendertest-a_", "-a", ], stdout=subprocess.PIPE, text=True)
    # for line in iter(p1.stdout.readline, ""):
    #     if not line.find("Append frame"):
    #         print(line)


if __name__ == "__main__":
    main()
