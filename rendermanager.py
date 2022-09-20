
from appmanager import AppList, AppData
from dataclasses import dataclass
from enum import Enum, unique
from typing import List


@unique
class JobStatus(Enum):
    QUEUED = 1
    RENDERING = 2
    SUSPENDED = 3
    SUCCESSFUL = 4
    ERROR = 5


@dataclass
class RenderJob:
    app: AppData
    blend_filepath: str
    status: JobStatus = JobStatus.QUEUED
    render_settings = None

    def generate_cmd_str(self) -> list[str]:
        _cmd_str = [self.app.path, "-b"]
        return _cmd_str


class RenderManager:
    __job_list: List[RenderJob]

    @classmethod
    def add_render_job(self, filepath: str, rendersettings=None) -> bool:
        if not AppList.get_active_installation():
            return False

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
    def get_job_list(self) -> List[RenderJob]:
        return self.__job_list
