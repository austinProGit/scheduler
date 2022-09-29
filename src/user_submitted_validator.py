# Author: Austin Lee and Max Lewis
# 9/28/22
# CPSC 4175 Group Project

def validate_user_submitted_path(container, schedule):
    processed_list = []
    err_list = []
    err_str = ''
    for semester in reversed(schedule):
        for course in semester:
            course_coreqs = container.get_coreqs(course)
            for coreq in course_coreqs:
                if coreq in processed_list:
                    err_str = (f'{course} taken before {coreq}.')
                    err_list.append(err_str)

        for course in semester:
            processed_list.append(course)
        for course in semester:
            # Check if the course is being scheduled multiple times
            if processed_list.count(course) > 1:
                err_str = (f'{course} scheduled multiple times.')
                if err_str not in err_list:
                    err_list.append(err_str)
            course_prereqs = container.get_prereqs(course)
            for prereq in course_prereqs:
                if prereq in processed_list:
                    err_str = (f'{course} taken before/during {prereq}.')
                    err_list.append(err_str)
    return err_list

    # throw the semester's courses in big list
    # check to see if any of the prereqs for the courses 
    # for the semester you are 
    # on are in the big list. If the are, append to string.
    # If no problems return none