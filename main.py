#!/usr/bin/env python3
"""
Module Docstring
"""

import subprocess
import time

from appmanager import AppList
from rendermanager import JobList, JobStatus, RenderSettings


__author__ = "Robert Lehmann"
__version__ = "0.1.0"
__license__ = ""

# TODO:
# -user supplied strings should use template strings
# -replace info/debug prints with logging module
# -using pickle module to save and load data
#


def main():
    AppList.add_installation("/opt/blender/3.0.1/blender")
    AppList.add_installation("/opt/blender/3.2.2/blender")
    AppList.add_installation("/opt/blender/3.2.2/blender")

    _render_settings = RenderSettings(startframe=1, endframe=3)
    JobList.add_render_job(
        "/home/r083127/Documents/blender-batch-jobs/sandbox/rendertest-a.blend", _render_settings)
    # JobList.add_render_job(
    #     "/home/r083127/Documents/blender-batch-jobs/sandbox/rendertest-b.blend")

    # iterate over job list and render according to settings
    for job in JobList.get():

        if job.status == JobStatus.SUSPENDED:
            continue

        job.status = JobStatus.RENDERING

        p = subprocess.Popen(job.generate_cmd_str(),
                             stdout=subprocess.PIPE, text=True)
        _frame_count = 0
        _total_time = 0
        _time_start = time.time()
        _time_per_frame = 0
        _eta = 0
        for line in iter(p.stdout.readline, ""):
            # get progress of the current job
            if line.find("Append frame") == 0:
                _current_frame = int(line[12:])
                _frame_count += 1
                job.update_progress(_frame_count)
                print(
                    f"Progress: {job.print_progress()} {str(_current_frame)} {str(_frame_count)}/{str(job._RenderJob__frames_to_render)}")
                _total_time += (time.time() - _time_start)

            # calculate an ETA
            if line.find(" Time:") == 0:
                _time_start = time.time()
                _time_per_frame = _total_time/_frame_count
                _frames_left = job._RenderJob__frames_to_render - _frame_count
                _eta = _time_per_frame * _frames_left
                print(f"Estimated time left: {_eta}")

        print(f"Total Render Time: {_total_time}")
        job.total_render_time = _total_time
        p.wait()
        if p.returncode == 0:
            job.status = JobStatus.SUCCESSFUL
        else:
            job.status = JobStatus.ERROR


if __name__ == "__main__":
    main()
