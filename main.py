#!/usr/bin/env python3
"""
Module Docstring
"""

from gui import BBJGUI

__author__ = "Robert Lehmann"
__version__ = "0.1.0"
__license__ = ""

# TODO:
# -user supplied strings should use template strings
# -replace info/debug prints with logging module
# -using pickle module to save and load data
#


def main():

    gui = BBJGUI()
    gui.MainLoop()


if __name__ == "__main__":
    main()
