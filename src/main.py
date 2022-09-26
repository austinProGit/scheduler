# Author: Vincent Miller
# Date: 31 August 2022

# MERINO: changed this to just run a smart planner controller

from program_driver import SmartPlannerController

if __name__ == "__main__":

    planner = SmartPlannerController()

    if planner.has_interface():
        while planner.run_top_interface(): pass


## currently a test bench
## noobs
#from courses_needed_parser import get_courses_needed
#from scheduler import schedule
#
#file_name1 = 'Sample Input1.pdf'
#file_name2 = 'Sample Input2.pdf'
#file_name3 = 'Sample Input3.pdf'
#
#courses_needed1 = get_courses_needed(file_name1)
#courses_needed2 = get_courses_needed(file_name2)
## courses_needed3 = get_courses_needed(file_name3)  # TODO: returns empty dataframe, fix
## print(courses_needed3)
#
## print full schedule, maximum 5 courses per semester
#print("Schedule 1")
#print(schedule(file_name1, "input_files/Course Info.xlsx", 5))
#
## print full schedule, maximum 3 courses per semester
#print("Schedule 2")
#print(schedule(file_name2, "input_files/Course Info.xlsx", 3))

