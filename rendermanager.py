
import re

from appmanager import AppList, AppData
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import List


@unique
class JobStatus(Enum):
    QUEUED = "Queued"
    RENDERING = "Rendering..."
    SUSPENDED = "Suspended"
    SUCCESSFUL = "Successful"
    ERROR = "Error"


@unique
class RenderFormat(Enum):
    DEFAULT = 0
    TGA = "TGA"
    RAWTGA = "RAWTGA"
    JPEG = "JPEG"
    IRIS = "IRIS"
    IRIZ = "IRIZ"
    AVIRAW = "AVIRAW"
    AVIJPEG = "AVIJPEG"
    PNG = "PNG"
    BMP = "BMP"
    HDR = "HDR"
    TIFF = "TIFF"
    OPENEXR = "OPEN_EXR"
    OPENEXR_MULTILAYER = "OPEN_EXR_MULTILAYER"
    MPEG = "MPEG"
    CINEON = "CINEON"
    DPX = "DPX"
    DDS = "DDS"
    JP2 = "JP2"
    WEBP = "WEBP"


@unique
class RenderEngine(Enum):
    DEFAULT = 0
    EEVEE = "BLENDER_EEVEE"
    WORKBENCH = "BLENDER_WORKBENCH"
    CYCLES = "CYCLES"


@dataclass
class BlendFile:
    path: str
    version: List[int]
    startframe: int
    endframe: int

    def __repr__(self) -> str:
        return f"BlendFile(path='{self.path}', version='{self.version}', startframe='{self.startframe}', endframe='{self.endframe}')"

    def __eq__(self, other) -> bool:
        if isinstance(other, AppData | BlendFile):
            return self.version == other.version
        else:
            raise TypeError

    def __ne__(self, other) -> bool:
        if isinstance(other, AppData | BlendFile):
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

    def __le__(self, other) -> bool:
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
        return f"{self.path} - ver.{_version_str[:-1]}"


@dataclass
class RenderSettings:
    frames: str = ""
    startframe: int = -1
    endframe: int = -1
    framejump: int = -1
    output: str = ""
    engine: RenderEngine = RenderEngine.DEFAULT
    format: RenderFormat = RenderFormat.DEFAULT
    threads: int = 0

    def __repr__(self) -> str:
        return f"RenderSettings(frames='{self.frames}', startframe='{self.startframe}', endframe='{self.endframe}', framejump='{self.framejump}', output='{self.output}', engine='{self.engine}', format='{self.format}', threads='{self.threads}')"

    def __str__(self) -> str:
        _str = ""
        if self.engine != RenderEngine.DEFAULT:
            _str += " -E " + self.engine.value

        if self.output != "":
            _str += " -o ", self.output

        if self.format != RenderFormat.DEFAULT:
            _str += " -F " + self.format.value

        if self.startframe != -1:
            _str += " -s " + str(self.startframe)

        if self.endframe != -1:
            _str += " -e " + str(self.endframe)

        if self.framejump != -1:
            _str += " -j " + str(self.framejump)

        if self.threads != 0:
            _str += " -t " + str(self.threads)

        if self.frames != "":
            _str += " -f " + self.frames

        if _str == "":
            _str = "No Overrides"

        return _str


@dataclass
class RenderJob:
    app: AppData
    blendfile: BlendFile
    render_settings: RenderSettings
    status: JobStatus = JobStatus.QUEUED
    total_render_time: float = 0
    progress: float = field(init=False, default_factory=float)
    __frames_to_render: int = field(init=False, default_factory=int)

    def __repr__(self) -> str:
        return f"RenderJob(app='{self.app}', blendfile='{self.blendfile}', render_settings='{self.render_settings}', progress='{self.progress}', status='{self.status}')"

    def __order_frame_range(self, input: str, separator: str) -> str:
        _range = input.split(separator)
        _startrange = int(_range[0])
        _endrange = int(_range[1])
        if _startrange > _endrange:
            self.__frames_to_render += (_startrange - _endrange + 1)
            return (_range[1] + ".." + _range[0])
        elif _startrange == _endrange:
            self.__frames_to_render += 1
            return _range[0]
        self.__frames_to_render += (_endrange - _startrange + 1)
        return input

    def update_progress(self, current_frame: int):
        if self.__frames_to_render <= 0:
            self.progress = 0.0
        else:
            self.progress = current_frame / self.__frames_to_render

    def print_progress(self) -> str:
        return f"{self.progress * 100:3.0f}%"

    def generate_cmd_str(self) -> List[str]:
        _cmd_str = [self.app.path, "-b", self.blendfile.path]

        _engine = self.render_settings.engine
        _output = self.render_settings.output
        _format = self.render_settings.format
        _startframe = self.render_settings.startframe
        _endframe = self.render_settings.endframe
        _framejump = self.render_settings.framejump
        _threads = self.render_settings.threads

        if _engine != RenderEngine.DEFAULT:
            _cmd_str.extend(["-E", _engine.value])

        if _output != "":
            _cmd_str.extend(["-o", _output])

        if _format != RenderFormat.DEFAULT:
            _cmd_str.extend(["-F", _format.value])

        _cmd_str.extend(["-x", "1"])

        if _startframe != -1:
            _cmd_str.extend(["-s", str(abs(_startframe))])
            self.__frames_to_render -= (_startframe - 1)

        if _endframe != -1:
            _cmd_str.extend(["-e", str(abs(_endframe))])
            if _endframe <= _startframe:
                _startframe = _endframe
                self.__frames_to_render = 1
            else:
                self.__frames_to_render -= (self.blendfile.endframe -
                                            _endframe)

        if _framejump != -1:
            _cmd_str.extend(["-j", str(abs(_framejump))])

        if _threads != 0:
            _threads_clamped = max(0, min(_threads, 64))
            _cmd_str.extend(["-t", str(_threads_clamped)])

        if self.render_settings.frames == "":
            _cmd_str.append("-a")
            self.__frames_to_render += self.blendfile.endframe - \
                (self.blendfile.startframe - 1)
        else:
            # input validation
            _frames = self.render_settings.frames.replace(" ", "")
            _frames = _frames.replace(";", ",")
            _frames = _frames.split(",")
            _invalid_entries = []
            for index, element in enumerate(_frames):
                # search for single numerics
                if re.search("^[0-9]{1,}$", element):
                    self.__frames_to_render += 1
                    continue
                # search for frame range using "..", e.g. 4..10
                if re.search("^[0-9]{1,}\.\.[0-9]{1,}$", element):
                    _frames[index] = self.__order_frame_range(element, "..")
                # search for frame range using "-", e.g. 4-10
                elif re.search("^[0-9]{1,}-[0-9]{1,}$", element):
                    _frames[index] = element.replace("-", "..")
                    _frames[index] = self.__order_frame_range(
                        _frames[index], "..")
                # search for empty fields in list
                elif re.search("^$", element):
                    _invalid_entries.append(element)
                else:
                    _invalid_entries.append(element)

            for element in _invalid_entries:
                _frames.remove(element)

            _frames_str = ""
            for element in _frames:
                _frames_str += element+","

            # check if we have usable input after validation and append it with -f
            if _frames_str != "":
                _cmd_str.extend(["-f", _frames_str[:-1]])
            else:  # if not fall back to rendering all frames with -a
                _cmd_str.append("-a")
                self.__frames_to_render += self.blendfile.endframe - \
                    (self.blendfile.startframe - 1)

        return _cmd_str


class JobList:
    __job_list: List[RenderJob] = []

    @classmethod
    def add_render_job(self, filepath: str, render_settings: RenderSettings = RenderSettings()) -> bool:
        # TODO:
        # -check for changed app location
        # -exception checking
        _blender_path = AppList.get_active_installation()
        if not _blender_path:
            print("No active installation. Please add at least one valid Blender install")
            return False
        # try opening the blend file
        try:
            with open(filepath, "rb") as file:
                _identifer = file.read(7).decode()
                if _identifer != "BLENDER":
                    print("File is not a valid .blend file.")
                    file.close()
                    return False

                file.read(1)  # pointer size byte, no use for it atm

                _endianness = file.read(1).decode()
                if _endianness == "v":
                    _endianness = "little"
                elif _endianness == "V":
                    _endianness = "big"

                _version = list(map(int, file.read(3).decode()))

                file.read(24)  # 24 bytes I don't care about

                _startframe = int.from_bytes(file.read(4), _endianness)
                _endframe = int.from_bytes(file.read(4), _endianness)

                _new_file = BlendFile(filepath, _version,
                                      _startframe, _endframe)
        except:
            print("Error opening file")
            return False
        finally:
            file.close()

        _new_job = RenderJob(_blender_path, _new_file, render_settings)
        self.__job_list.append(_new_job)

        return True

    @classmethod
    def remove_render_job(self, index: int) -> bool:
        try:
            self.__job_list.pop(abs(index))
            return True
        except:
            print("Error removing render job...")
            return False

    @classmethod
    def get(self) -> List[RenderJob]:
        return self.__job_list

    @classmethod
    def print(self):
        # TODO: replace with tabulate
        # header
        print("{:2}. {:13}  {:65}\t{:120}\t{:12}".format(
            "\033[1m" "ID", "App/Version", "Blend File Path", "Render Settings", "Status" "\033[0m"))
        for i in range(260):
            print("-", end="")
        print("")
        # table contents
        for index, job in enumerate(self.__job_list, start=1):
            print("{:2}. {}  {}\t{}\t{}".format(
                index, job.app, job.blendfile.path, job.render_settings, job.status.value))
