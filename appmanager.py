
import subprocess

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class AppData:
    path: str
    name: str
    version: List[int] = field(default_factory=list)

    def print_version(self):
        _version_str = ""
        for element in self.version:
            _version_str += str(element) + "."
        return _version_str[:-1]


class AppManager:
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
            if self.__app_list:
                for app in self.__app_list:
                    if app.path == path and app.version == _version:
                        print("App \"" + app.name + "(" + app.path +
                              ") version: " + app.print_version() + "\" already exists.\n" + "No new App installation added.")
                        return False

            _new_app = AppData(
                path=path, name=_name, version=_version)
            print("Adding Installation: " +
                  _new_app.name + "(" + _new_app.path + ") version: " + _new_app.print_version())
            self.__app_list.append(_new_app)

            if not self.get_active_installation():
                self.set_active_installation(_new_app)

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
            return False

    @classmethod
    def get_app_list(self) -> List[AppData]:
        return self.__app_list

    @classmethod
    def get_active_installation(self) -> AppData:
        return self.__active_installation

    @classmethod
    def set_active_installation(self, new_app: AppData):
        if new_app is not self.__active_installation:
            self.__active_installation = new_app
