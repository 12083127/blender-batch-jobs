
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rendermanager import BlendFile

import subprocess

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class AppData:
    path: str
    name: str
    version: List[int] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"AppData(name='{self.name}', version='{self.version}', path='{self.path}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, AppData):
            return self.path == other.path and self.version == other.version
        elif isinstance(other, BlendFile):
            return self.version == other.version
        else:
            raise TypeError

    def __ne__(self, other) -> bool:
        if isinstance(other, AppData):
            return self.path != other.path or self.version != other.version
        elif isinstance(other, BlendFile):
            return self.version != other.version
        else:
            raise TypeError

    def __ge__(self, other) -> bool:
        if isinstance(other, AppData | BlendFile):
            return self.version >= other.version
        else:
            raise TypeError

    def __gt__(self, other) -> bool:
        if isinstance(other, AppData | BlendFile):
            return self.version > other.version
        else:
            raise TypeError

    def __lt__(self, other) -> bool:
        if isinstance(other, AppData | BlendFile):
            return self.version <= other.version
        else:
            raise TypeError

    def __lt__(self, other) -> bool:
        if isinstance(other, AppData | BlendFile):
            return self.version < other.version
        else:
            raise TypeError

    def __str__(self) -> str:
        _version_str = ""
        for element in self.version:
            _version_str += str(element) + "."
        return f"{self.name}  {_version_str[:-1]}"


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

            _version: list[int] = [int(element) for element in _version_str.split(".")]

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
            _active_installation_index = self.get_active_installation_index()
            self.__app_list.pop(abs(index))
            # check if we removed the active selected app
            # if so, update the reference
            if _active_installation_index == index:
                self.set_active_installation(None)
                if self.is_populated():
                    self.set_active_installation(self.__app_list[0])

            return True
        except:
            print("Error removing app installation...")
            return False

    @classmethod
    def is_populated(self) -> bool:
        if len(self.__app_list) == 0:
            return False
        return True

    @classmethod
    def get_choice_list(self) -> list[str]:
        return [app.__str__() for app in self.__app_list]

    @classmethod
    def get(self) -> List[AppData]:
        return self.__app_list

    @classmethod
    def get_active_installation(self) -> AppData:
        return self.__active_installation

    @classmethod
    def get_active_installation_index(self) -> int:
        return self.__app_list.index(self.__active_installation)

    @classmethod
    def set_active_installation(self, new_app: AppData):
        if new_app is not self.__active_installation:
            self.__active_installation = new_app

    @classmethod
    def sort(self):
        self.__app_list.sort(key=lambda app: app.version, reverse=True)

    @classmethod
    def print(self):
        # TODO: replace with tabulate
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


@dataclass
class AppSettings:
    shutdown_on_completion: bool
    global_output_path: str
    global_threads_count: int
    window_position: tuple = (200, 200)
    window_size: tuple = (1280, 960)

    def __repr__(self) -> str:
        return (f"AppSettings(shutdown_on_completion={self.shutdown_on_completion},"
                f"global_output={self.global_output_path},"
                f"global_threads={self.global_threads_count})")

    def save():
        pass

    def load():
        pass
