# Author: Austin Lee, Max Lewis, and Thomas Merino
# 9/28/22
# CPSC 4175 Group Project


from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from course_info_container import CourseInfoContainer
    
from schedule_info_container import ScheduleInfoContainer, SemesterDescription
from instance_identifiers import CourseIdentifier, Schedulable
from end_reports import PathValidationReport, VALIDATION_REPORT_PARSED
from scheduling_parameters_container import CreditHourInformer
from general_utilities import *

def validate_user_submitted_path(course_info_container: CourseInfoContainer, raw_schedule: list[list[str]],
        starting_semester: SemesterType = ESTIMATED_NEXT_SEMESTER, starting_year: int = ESTIMATED_NEXT_YEAR,
        excused_courses: list[CourseIdentifier] = []) -> PathValidationReport:
    schedule: ScheduleInfoContainer = ScheduleInfoContainer.make_from_string_list(raw_schedule, course_info_container, starting_semester, starting_year)
    return rigorous_validate_schedule(schedule, taken_courses=excused_courses)


def rigorous_validate_schedule(schedule: ScheduleInfoContainer,
        taken_courses: list[CourseIdentifier] = [],
        prequisite_ignored_courses: list[CourseIdentifier] = [],
        credit_hour_informer: CreditHourInformer = CreditHourInformer.make_unlimited_generator()) -> PathValidationReport:

    # TODO: implement checking for courses not appearing in course info container (unless signed off on)

    # TODO:
    # NOTE: there is a lot of longer than needed searches in this method.
    # It might be a good move to create a sometimes-hashed map for searching. There are 2 parts:
    # 1. hashed map for searching, 2. a shorter list for linear searching or no searching at all.

    running_taken_courses: list[CourseIdentifier] = taken_courses[:]
    error_list: list[PathValidationReport.Error] = []

    semester: SemesterDescription
    for semester in schedule:

        # Get the year and semester information
        working_year: int = semester.year
        working_semester: SemesterType = semester.semester_type

        # Create a tracker to determine if the limit is reached on credits for the semester 
        credits_left: int = credit_hour_informer.get(working_semester, working_year)

        # Create a list of schedulables to check (requirements)--the identifiers will be added to running_taken_courses
        currently_taking_courses: list[Schedulable] = []
        
        error_description: str
        course: Schedulable

        # Check for repeating course within a semester and update the coreq.s
        for course in semester:

            # Clear all the selections (this is the first time encountering the course)
            course.reset_all_selection()

            # Check for repeating course within a semester
            if course not in currently_taking_courses:
                
                

                # Check if the course was taken in another semester
                if course in running_taken_courses:
                    # Repeating course found in different semester (append an error report)
                    error_description = f'Taking {course} again in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                    error_list.append(PathValidationReport.Error(error_description))

                # Make each course recognize the coreq. relationship (bidirectional)
                taking_course: Schedulable
                for taking_course in currently_taking_courses:
                    course.sync_course_taking(taking_course.course_identifier)
                    taking_course.sync_course_taking(course.course_identifier)
                
                # Make each course recognize the prereq.s
                taken_course_identifier: CourseIdentifier
                for taken_course_identifier in running_taken_courses:
                    course.sync_course_taken(taken_course_identifier)

                # Append the course the to the list of currentlyt taking courses
                currently_taking_courses.append(course)

                # Record the credits
                credits_left -= course.hours
                # Check if going over credit limit per semester
                if credits_left < 0:
                    # The semester went over the limit of credits
                    error_description = f'Went over credit limit during {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                    error_list.append(PathValidationReport.Error(error_description))

            else:
                # Repeating course found in the same semester (append an error report)
                error_description = f'Taking {course} multiple times in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(PathValidationReport.Error(error_description))


        # Check for prereq.s/coreq.s and availability
        for course in currently_taking_courses:

            # Check prereq.s/coreq.s
            if not course.can_be_taken() and course not in prequisite_ignored_courses:
                # TODO: add a logic requirement print out to the report (prereq.s and coreq.s)
                # Inadequate fulfillment of requirements (append an error report)
                error_description = f'Not all requirements satisfied before taking {course} in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(PathValidationReport.Error(error_description))

            # Check availability
            if working_semester not in course.availability:
                # Inadequate fulfillment of requirements (append an error report)
                error_description = f'Availability for {course} not present in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(PathValidationReport.Error(error_description))
        

        # Add the semester's courses to the list of courses taken
        for course in currently_taking_courses:

            # TODO: this check may be temp: >>>
            if course.can_be_taken():
                # <<<

                running_taken_courses.append(course.course_identifier)
                
                
        
    return PathValidationReport(error_list, VALIDATION_REPORT_PARSED)




# def validate_user_submitted_path(container, schedule):
#     '''This assumes the last semster in the list of list is Summer.'''
#     processed_list = []
#     err_list = []
#     err_str = ''
#     current_semester = 'Su'
    
#     for semester in reversed(schedule):

#         for course in semester:
#             if current_semester not in container.get_availability(course):
#                 err_str = (f'{course} taken during the {USER_READABLE_SEMESTER_DESCRIPTION[current_semester]} term (not available).')
#                 err_list.append(err_str)

#             #course_coreqs = container.get_coreqs(course)

#             # TODO: this was added before presentation for demonstration
#             requirements = container.get_coreqs(course) or ''
#             tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
#             course_coreqs = []#[i.course_number for i in tree.decision_tree.get_all_aggragate()]

#             for coreq in course_coreqs:
#                 if coreq in processed_list:
#                     err_str = (f'{course} taken before {coreq}.')
#                     err_list.append(err_str)

#         for course in semester:
#             processed_list.append(course)
#         for course in semester:
#             # Check if the course is being scheduled multiple times
#             if processed_list.count(course) > 1:
#                 err_str = (f'{course} scheduled multiple times.')
#                 if err_str not in err_list and 'XXX' not in course:
#                     err_list.append(err_str)

#             #course_prereqs = container.get_prereqs(course)
            
#             # TODO: this was added before presentation for demonstration
#             requirements = container.get_prereqs(course) or ''
#             tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
#             course_prereqs = [i.course_number for i in tree.decision_tree.get_all_aggragate()]
            
#             for prereq in course_prereqs:
#                 if prereq in processed_list:
#                     err_str = (f'{course} taken before/during {prereq}.')
#                     err_list.append(err_str)

#         # Update the semester term
#         current_semester = SEMESTER_TYPE_PREDECESSOR[current_semester]

#     # print(err_list)   
#     return err_list

#     # throw the semester's courses in big list
#     # check to see if any of the prereqs for the courses 
#     # for the semester you are 
#     # on are in the big list. If the are, append to string.
#     # If no problems return none

#     # New comment to test branch
