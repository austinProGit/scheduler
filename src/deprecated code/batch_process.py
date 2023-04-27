# Author: Vincent Miller
# Date: 17 October 2022
# Description: Process batches of schedules

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union
    from pathlib import Path
    from course_info_container import CourseInfoContainer
    from end_reports import ExportReport, PathValidationReport
    from scheduling_parameters_container import ConstructiveSchedulingParametersContainers

# TODO: make courses needed parser work in dis file!

from degreeworks_parser import *
from scheduler import Scheduler
from excel_formatter import excel_formatter
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from pathlib import Path
from schedule_info_container import *
import os
import re


from batch_configuration import BatchConfiguration

import traceback


# This may be used to perform validations along with scheduling (can even be interwoven)
def batch_process(batch_configuration: BatchConfiguration, course_info: CourseInfoContainer) \
        -> list[Union[ExportReport, PathValidationReport]]:

    raise NotImplemented



# This may be used to perform validations along with scheduling (can even be interwoven)
def batch_schedule(file_paths: list[Path],  model_scheduling_parameters: ConstructiveSchedulingParametersContainers, course_info: CourseInfoContainer) \
        -> list[Union[ExportReport, PathValidationReport]]:

    raise NotImplemented


# def batch_process(input_path, output_path, template_path, course_info):
#     """function performs multiprocessing using ProcessPoolExecutor
#         which will create as many processes as your computer has cores.
#        inputs: input_path is folder containing degreeworks
#                output_path is the folder for the output schedules
#                template_path for Path to Grad template
#                course_info container
#        outputs: places schedules into the output_path folder"""
#     # get list of files to process
#     files_to_process = os.listdir(input_path)
#     # Lew added regex method to filter out unwanted file types in directory
#     files_to_process = batch_directory_file_excluder(files_to_process)
#     # Lew felt like we might want an indicator that we are batching
#     print('Batching in progress...')
#     # perform multiprocessing, How To: map(function, *args), repeat() is for non list arguments
#     with ProcessPoolExecutor() as executor:
#         executor.map(full_schedule, repeat(input_path), files_to_process, repeat(output_path),
#                      repeat(template_path), repeat(course_info))


# def full_schedule(input_path, courses_needed_filename, output_path, template_path, course_info):
#     """function will produce schedule from start to finish
#        inputs: input_path is the folder containing all degreeworks files
#                file_name,
#                output_path for where to store schedules,
#                template_path for the Path to Grad template,
#                course_info container
#        outputs: places schedule in the output path folder"""
#     try:
#         # read courses needed
#         courses_needed = get_courses_needed(input_path.joinpath(courses_needed_filename))

#         # get hours per semester
#         semester_hours = int(courses_needed_filename[10:12])

#         # run scheduler
#         scheduler = Scheduler()
#         scheduler.configure_course_info(course_info)
#         scheduler.configure_courses_needed(courses_needed)
#         scheduler.configure_hours_per_semester(semester_hours)
#         container = scheduler.generate_schedule()
#         schedule = container.get_schedule()
#         #schedule, _ = scheduler.generate_schedule()

#         output_file_path = Path(output_path).joinpath(Path(courses_needed_filename).stem).with_suffix(".xlsx")
       
#         # export to excel
#         excel_formatter(template_path, output_file_path, schedule, course_info)
#     except:
#         print(traceback.format_exc())

# def batch_directory_file_excluder(folder):
#     for filex in folder:
#         x = re.search("909[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9].pdf", filex)
#         if x == None: folder.remove(filex)
#     return folder
