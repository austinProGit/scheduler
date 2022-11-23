# Author: Vincent Miller
# Date: 17 October 2022
# Description: Process batches of schedules
from courses_needed_parser import get_courses_needed
from scheduler import Scheduler
from excel_formatter import excel_formatter
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
from pathlib import Path
import os
import re


import traceback


def batch_process(input_path, output_path, template_path, course_info):
    """function performs multiprocessing using ProcessPoolExecutor
        which will create as many processes as your computer has cores.
       inputs: input_path is folder containing degreeworks
               output_path is the folder for the output schedules
               template_path for Path to Grad template
               course_info container
       outputs: places schedules into the output_path folder"""
    # get list of files to process
    files_to_process = os.listdir(input_path)
    # Lew added regex method to filter out unwanted file types in directory
    files_to_process = batch_directory_file_excluder(files_to_process)
    # Lew felt like we might want an indicator that we are batching
    print('Batching in progress...')
    # perform multiprocessing, How To: map(function, *args), repeat() is for non list arguments
    with ProcessPoolExecutor() as executor:
        executor.map(full_schedule, repeat(input_path), files_to_process, repeat(output_path),
                     repeat(template_path), repeat(course_info))


def full_schedule(input_path, courses_needed_filename, output_path, template_path, course_info):
    """function will produce schedule from start to finish
       inputs: input_path is the folder containing all degreeworks files
               file_name,
               output_path for where to store schedules,
               template_path for the Path to Grad template,
               course_info container
       outputs: places schedule in the output path folder"""
    try:
        # read courses needed
        courses_needed = get_courses_needed(input_path.joinpath(courses_needed_filename))

        # get hours per semester
        semester_hours = int(courses_needed_filename[10:12])

        # run scheduler
        scheduler = Scheduler()
        scheduler.configure_course_info(course_info)
        scheduler.configure_courses_needed(courses_needed)
        scheduler.configure_hours_per_semester(semester_hours)
        schedule = scheduler.generate_schedule()

        output_file_path = Path(output_path).joinpath(Path(courses_needed_filename).stem).with_suffix(".xlsx")
       
        # export to excel
        excel_formatter(template_path, output_file_path, schedule, course_info)
    except:
        print(traceback.format_exc())

def batch_directory_file_excluder(folder):
    for filex in folder:
        x = re.search("909[0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9].pdf", filex)
        if x == None: folder.remove(filex)
    return folder