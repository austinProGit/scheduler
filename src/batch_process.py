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

# TODO: File names as ID_Hours.pdf


def batch_process(input_path, output_path, template_path, course_info):
    # TODO: DOCSTRING
    # get list of files to process
    files_to_process = os.listdir(input_path)
    # perform multiprocessing, How To: map(function, *args), repeat() is for non list arguments
    with ProcessPoolExecutor() as executor:
        executor.map(full_schedule, files_to_process, repeat(output_path),
                     repeat(template_path), repeat(course_info))


def full_schedule(courses_needed_filename, output_path, template_path, course_info):
    # TODO: DOCSTRING
    # read courses needed
    courses_needed = get_courses_needed("batch_process_input/" + courses_needed_filename)

    # TODO: strip hours from file name
    # get hours per semester
    semester_hours = 15

    # run scheduler
    # TODO: Scheduler with constructor to accept multiple configures, MUST use setters currently
    scheduler = Scheduler()
    scheduler.configure_course_info(course_info)
    scheduler.configure_courses_needed(courses_needed)
    scheduler.configure_hours_per_semester(semester_hours)
    schedule = scheduler.generate_schedule()

    # TODO: make correct output names, student_ID.xlsx
    output_file_path = output_path + Path(courses_needed_filename).stem + ".xlsx"
    # export to excel
    excel_formatter(template_path, output_file_path, schedule, course_info)
