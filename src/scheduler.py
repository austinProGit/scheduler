# Author: Vincent Miller
# 12 September 2022
"""
TODO: CPSC 4000, only to be taken in last semester
TODO: CPSC 3165, junior+ requirement
TODO: CPSC 1301K, handle the k, temporarily removed the k from course_info.xlsx
TODO: Create automatic semester types, Spring -> Sp, Summer -> Su, Fall -> Fa
TODO: Create co-requisites check
TODO: Deal with list sorting low level CYBR behind ALL CPSC courses, pointless if I get ALL courses through crawler?
TODO: Summer courses are not able to support the same amount of maximum courses, add fix for this

Over commented as usual for your reading pleasure.
"""
from courses_needed_parser import get_courses_needed
from course_info_container import *


def schedule(courses_needed_file_name, course_info_file_name, max_courses):
    """TODO: Write docstring for function"""

    # helper functions
    def check_availability(_course_id, _current_semester):
        # MERINO: changed method call name for course_info
        _availability = course_info.get_availability(_course_id)
        if _current_semester in _availability:
            return True
        else:
            return False

    def check_prerequisites(_course_id):
        # MERINO: changed method call name for course_info
        _prerequisites = course_info.get_prereqs(_course_id)
        # if prerequisite course is in courses_needed or in semester, can't take course yet.
        for _prerequisite in _prerequisites:
            if _prerequisite in courses_needed or _prerequisite in semester:
                return False
        return True

    # get data being worked with
    courses_needed = get_courses_needed(courses_needed_file_name)
    # MERINO: changed type name for container
    course_info = CourseInfoContainer(load_course_info(course_info_file_name))

    # sorting should speed up the scheduler, as lower level courses are more likely to be required sooner
    # TODO: Low level CYBR courses will be pushed behind ALL CPSC courses, fix
    courses_needed.sort()

    # create empty, final schedule, each semester list will be added to this
    full_schedule = []
    # temporary solution to deal with rotation of semester types
    semester_types = ["Sp", "Su", "Fa"]
    # loop through until courses_needed is empty
    while len(courses_needed):
        # loops through each semester type
        # TODO: will need to adjust this loop with automatic semester type/date
        for semester_type in semester_types:
            # if courses_needed is empty, break out of semester_types loop
            if not len(courses_needed):
                break

            # create empty semester, and set counters to 0
            semester = []
            current_courses_counter = 0  # counter to control max_courses
            courses_counter = 0  # counter to control iteration through needed_courses

            # loop to fill out semester, don't loop over max_courses,
            # don't loop through courses_needed more than once, don't loop through courses_needed if empty
            while current_courses_counter < max_courses \
                    and courses_counter <= len(courses_needed) \
                    and len(courses_needed):

                # get first course in list
                course = courses_needed.pop(0)
                courses_counter += 1

                # check availability
                available = check_availability(course, semester_type)
                if not available:
                    # course not available, add course back to courses_needed and skip rest of loop iteration
                    courses_needed.append(course)
                    continue

                # check prerequisites
                prerequisites = check_prerequisites(course)
                if not prerequisites:
                    # prerequisite not met, add course back to courses_needed and skip rest of loop iteration
                    courses_needed.append(course)
                    continue

                # check co-requisites
                # TODO: create co-requisites check

                # add course in semester, increment counter
                semester.append(course)
                current_courses_counter += 1

            # add semester to full_schedule
            full_schedule.append(semester)

    # finished scheduling
    return full_schedule
