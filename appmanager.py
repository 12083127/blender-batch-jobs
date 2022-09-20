
import subprocess

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class AppData:
    path: str
    name: str
    version: List[int] = field(default_factory=list)

    def __repr__(self) -> str:
        return "AppData(name='{}', version='{}', path='{}')".format(self.name, self.version, self.path)

    def __str__(self) -> str:
        _version_str = ""
        for element in self.version:
            _version_str += str(element) + "."
        return "{} {}".format(self.name, _version_str[:-1])

    def __eq__(self, other) -> bool:
        if isinstance(other, AppData):
            return self.path == other.path and self.version == other.version
        else:
            raise TypeError

    def __gt__(self, other) -> bool:
        if isinstance(other, AppData):
            return self.version > other.version
        else:
            raise TypeError

    def __lt__(self, other) -> bool:
        if isinstance(other, AppData):
            return self.version < other.version
        else:
            raise TypeError


class AppList:
    __app_list: List[AppData] = []
    __active_installation: AppData = None

    @classmethod
    def add_installation(self, path: str) -> bool:
        try:
            _blender = subprocess.run(
                [path, "-v"], stdout=subprocess.PIPE, text=True)
            _first_line = _blender.stdout.split("\n")[0]
            _name = _first_line.split()[0]
            _version_str = _first_line.split()[1]

            if _name != "Blender":
                return False

            _version: list[int] = []
            for element in _version_str.split("."):
                _version.append(int(element))

            # check for duplicates
            _new_app = AppData(
                path=path, name=_name, version=_version)
            if self.__app_list:
                for app in self.__app_list:
                    if app == _new_app:
                        print(
                            "\033[93mApp \"{}@{}\"".format(app, app.path), end="")
                        print(" already exits. Adding failed.\033[0m")
                        return False

            print("Adding new installation: {} ({})".format(
                _new_app, _new_app.path))
            self.__app_list.append(_new_app)

            if not self.__active_installation:
                self.__active_installation = _new_app

            self.sort()

            return True
        except:
            print(self.__name__ + ": Error")
            return False

    @classmethod
    def remove_installation(self, index: int) -> bool:
        try:
            self.__app_list.pop(abs(index))
            return True
        except:
            print("Error removing app installation...")
            return False

    @classmethod
    def get(self) -> List[AppData]:
        return self.__app_list

    @classmethod
    def get_active_installation(self) -> AppData:
        return self.__active_installation

    @classmethod
    def set_active_installation(self, new_app: AppData):
        if new_app is not self.__active_installation:
            self.__active_installation = new_app

    @classmethod
    def sort(self):
        self.__app_list.sort(key=lambda app: app.version, reverse=True)

    @classmethod
    def print(self):
        # header
        print("{}{} {}  {}\t{}{}".format(
            "\033[1m", " ", "ID", "Appname/Version", "Path", "\033[0m"))
        for i in range(100):
            print("-", end="")
        print("")
        # table contents
        for index, app in enumerate(self.__app_list, start=1):
            _active_indicator = " "
            if app == self.__active_installation:
                _active_indicator = ">"
            print("{} {}.  {}\t{}".format(
                _active_indicator, index, app, app.path))
