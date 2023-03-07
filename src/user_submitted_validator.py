# Author: Austin Lee, Max Lewis, and Thomas Merino
# 9/28/22
# CPSC 4175 Group Project

from requirement_parser import RequirementsParser

SEMESTER_TYPE_PREDECESSOR = {'Fa': 'Su', 'Su': 'Sp', 'Sp': 'Fa'} # Translation map from semester K to the next
USER_READABLE_SEMESTER_DESCRIPTION = {'Fa': 'Fall', 'Sp': 'Spring', 'Su': 'Summer'}

def validate_user_submitted_path(container, schedule):
    '''This assumes the last semster in the list of list is Summer.'''
    processed_list = []
    err_list = []
    err_str = ''
    current_semester = 'Su'
    
    for semester in reversed(schedule):

        for course in semester:
            if current_semester not in container.get_availability(course):
                err_str = (f'{course} taken during the {USER_READABLE_SEMESTER_DESCRIPTION[current_semester]} term (not available).')
                err_list.append(err_str)

            #course_coreqs = container.get_coreqs(course)

            # TODO: this was added before presentation for demonstration
            requirements = container.get_coreqs(course) or ''
            tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
            course_coreqs = tree.decision_tree.get_all_aggragate()

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
                if err_str not in err_list and 'XXX' not in course:
                    err_list.append(err_str)

            #course_prereqs = container.get_prereqs(course)
            
            # TODO: this was added before presentation for demonstration
            requirements = container.get_prereqs(course) or ''
            tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
            course_prereqs = tree.decision_tree.get_all_aggragate()

            for prereq in course_prereqs:
                if prereq in processed_list:
                    err_str = (f'{course} taken before/during {prereq}.')
                    err_list.append(err_str)

        # Update the semester term
        current_semester = SEMESTER_TYPE_PREDECESSOR[current_semester]

    # print(err_list)   
    return err_list

    # throw the semester's courses in big list
    # check to see if any of the prereqs for the courses 
    # for the semester you are 
    # on are in the big list. If the are, append to string.
    # If no problems return none

    # New comment to test branch
