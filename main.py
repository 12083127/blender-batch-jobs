#!/usr/bin/env python3
"""
Module Docstring
"""

from appmanager import AppManager

__author__ = "Robert Lehmann"
__version__ = "0.1.0"
__license__ = ""


def main():

    AppManager.add_installation("/opt/blender/3.0.1/blender")
    AppManager.add_installation("/opt/blender/3.2.2/blender")
    AppManager.add_installation("/opt/blender/3.0.1/blender")

    if AppManager.get_app_list():
        applist = AppManager.get_app_list()
        print(AppManager.get_active_installation())
        AppManager.set_active_installation(applist[1])
        print(AppManager.get_active_installation())

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
