# Author: Vincent Miller, Thomas Merino
# Date: 31 August 2022
# Description: Main file for our program, runs smart planner controller

from program_driver import SmartPlannerController

# TODO: Move this to demo code file until Thomas understands how it works and implements
# imports required to run batch_process
from batch_process import batch_process
from course_info_container import CourseInfoContainer
from course_info_parser import get_course_info

if __name__ == "__main__":
    # get course_info container
    course_info = CourseInfoContainer(get_course_info("input_files/Course Info.xlsx"))
    # get required directory paths
    input_path = "batch_process_input/"
    output_path = "batch_process_schedules/"
    template_path = "input_files/Path To Graduation Y.xlsx"

    batch_process(input_path, output_path, template_path, course_info)

""" COMMENTED OUT BELOW IS ORIGINAL CODE
    planner = SmartPlannerController()

    if planner.has_interface():
       while planner.run_top_interface(): pass
"""
