#!/usr/bin/env python3
"""
Module Docstring
"""

import subprocess
from appmanager import AppList
from rendermanager import JobList, JobStatus, RenderSettings

__author__ = "Robert Lehmann"
__version__ = "0.1.0"
__license__ = ""


def main():
    AppList.add_installation("/opt/blender/3.0.1/blender")
    AppList.add_installation("/opt/blender/3.2.2/blender")
    AppList.add_installation("/opt/blender/3.2.2/blender")

    _render_settings = RenderSettings(startframe=5, endframe=20)
    JobList.add_render_job(
        "/home/r083127/Documents/blender-batch-jobs/sandbox/rendertest-a.blend", _render_settings)
    JobList.add_render_job(
        "/home/r083127/Documents/blender-batch-jobs/sandbox/rendertest-b.blend")

    print()
    JobList.print()
    print()

    # iterate over job list and render according to settings
    for job in JobList.get():

        if job.status == JobStatus.SUSPENDED:
            continue
        job.status = JobStatus.RENDERING
        p = subprocess.Popen(job.generate_cmd_str(),
                             stdout=subprocess.PIPE, text=True)
        _frame_count = 0
        for line in iter(p.stdout.readline, ""):
            if not line.find("Append frame"):
                _current_frame = int(line[12:])
                _frame_count += 1
                job.update_progress(_frame_count)
                print("Progress: " + job.print_progress() + " " + str(_current_frame) + " " +
                      str(_frame_count) + "/" + str(job._RenderJob__frames_to_render))
        job.status = JobStatus.SUCCESSFUL

    JobList.print()


if __name__ == "__main__":
    main()
