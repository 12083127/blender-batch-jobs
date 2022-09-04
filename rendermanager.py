

from appmanager import AppData
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
    blend_file: str
    status: JobStatus = JobStatus.QUEUED
    render_settings = None


class RenderManager:
    __job_list: List[RenderJob]

    @classmethod
    def add_render_job(self, filepath: str, rendersettings=None) -> bool:
        return True

    @classmethod
    def remove_render_job(self, index: int) -> bool:
        return True

    @classmethod
    def get_job_list(self):
        return self.__job_list
