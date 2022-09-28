# Author: Vincent Miller
# 18 September 2022
# Contributor(s): Thomas Merino

# MERINO: All I have done is encapsulated it in a class with configuration methods, added support for co-reqs,
# added support for starting on any semester, reorganized a bit of stuff (to my weird liking), and fixed a rare bug.

"""
TODO: CPSC 3165, junior+ requirement, honestly unsure of how to handle this
"""

SEMESTER_TYPE_SUCCESSOR = {'Fa': 'Sp', 'Sp': 'Su', 'Su': 'Fa'}    # Translation map from semester K to the next
DEFAULT_HOURS_PER_SEMESTER = 15  # MERINO: updated value


class Scheduler:
    
    def __init__(self):
        self.hours_per_semester = DEFAULT_HOURS_PER_SEMESTER
        self.courses_needed = []
        self.course_info_container = None
        self.semester_type = 'Sp'

    def get_course_info(self):
        return self.course_info_container
        
    def get_courses_needed(self):
        return self.courses_needed[:]
    
    def get_hours_per_semester(self):
        return self.hours_per_semester
        
    def configure_course_info(self, container):
        self.course_info_container = container
        
    def configure_courses_needed(self, courses_needed):
        self.courses_needed = courses_needed[:]
    
    def configure_hours_per_semester(self, number_of_hours):
        self.hours_per_semester = number_of_hours

    def generate_schedule(self):
        course_info = self.course_info_container    # Get the course info container
        courses_needed = self.courses_needed[:]     # Create a copy of the needed courses (workable list)
        
        # Helper functions
        def check_availability(course_id):
            availability = course_info.get_availability(course_id)
            return working_semester_type in availability
            
        def check_precise_hours():
            return current_hours_counter + course_hours <= max_hours
                        
        def check_prerequisites(course_id):
            prerequisites = course_info.get_prereqs(course_id)
            # if prerequisite course is in courses_needed or in semester, can't take course yet.
            for prerequisite in prerequisites:
                if prerequisite in courses_needed or prerequisite in semester:
                    return False
            return True
        
        def check_corequisites(course_id):
            corequisites = course_info.get_coreqs(course_id)
            # If co-requisite course is in the needed courses, can't take course yet.
            for corequisite in corequisites:
                if corequisite in courses_needed:
                    return False
            return True
        
        def complete_check(course_id):
            # Run all three of the above checks (with short circuit evaluation)
            return check_availability(course_id) \
                and check_precise_hours() \
                and check_prerequisites(course_id) \
                and check_corequisites(course_id)

        # Create empty, final schedule, each semester list will be added to this
        full_schedule = []
        # Create a string to track the current semester type ('Fa', 'Sp', or 'Su')
        working_semester_type = self.semester_type
        # variables for lower summer max hours
        summer = False
        temp_hours = 0
        cpsc_4000 = False

        # loop through until courses_needed is empty
        while len(courses_needed):
            # if courses_needed is empty, break out of semester_types loop
            if not len(courses_needed):
                break
            
            semester = []                       # the working list of courses
            current_hours_counter = 0           # counter to hold number of scheduled hours during the current semester

            # MERINO: I am changing the use of this variable, so it only stops the searching cycle if it runs through
            # the entire needed courses list without finding any new courses to register. This is the only solution I
            # have for ensuring we schedule courses that may have been skipped because of co-req requirements. This also
            # prevents a rare bug where the while-loop would end preemptively--this was dues to courses_counter not be
            # corrected when the length of courses_needed was modified.
            # V: Great catch, thanks!

            unregistered_courses_counter = 0    # counter to control iteration through courses_needed
            max_hours = self.hours_per_semester  # the number of hours (max) to register in the loop's semester

            # lower max hours for summer semesters
            if summer:
                max_hours = temp_hours
                summer = False
            if working_semester_type == 'Su':
                temp_hours = max_hours
                max_hours = 6
                summer = True

            # loop to fill out semester, don't loop over max_hours,
            # don't loop through courses_needed more than once, don't loop through courses_needed if empty
            while current_hours_counter < max_hours \
                    and unregistered_courses_counter < len(courses_needed) \
                    and len(courses_needed):
                    
                # get first course in list
                course = courses_needed.pop(0)

                # CPSC belongs in the last semester, skip scheduling if found
                if course == 'CPSC 4000':
                    cpsc_4000 = True
                    continue

                # get hours of course
                course_hours = course_info.get_hours(course)

                # check availability, prerequisites, and co-requisites
                passes_complete_check = complete_check(course)
                if not passes_complete_check:
                    # course cannot be taken, add course back to courses_needed and skip the rest of iteration loop
                    courses_needed.append(course)
                    # Used to detect if all courses have been checked and, indeed, none can be registered
                    unregistered_courses_counter += 1
                    
                else:
                    # add course in semester, increment hours
                    semester.append(course)
                    current_hours_counter += course_hours
                    unregistered_courses_counter = 0
            
            # add semester to full_schedule
            full_schedule.append(semester)
            
            # Rotate to the next semester type
            working_semester_type = SEMESTER_TYPE_SUCCESSOR[working_semester_type]

        # add CPSC 4000 to last semester
        if cpsc_4000:
            full_schedule[-1].append('CPSC 4000')

        return full_schedule
