# Author: Vincent Miller
# 18 September 2022
# Contributor(s): Thomas Merino


# NOTE: this was modified from Vincent's schdeuler. All I have done is encapsulated it in a class with configuration methods, added support
# for coreqs, added support for starting on any semester, reorganized a bit of stuff (to my weird liking), and fixed a rare bug.

"""
TODO: This has not been tested rigorously (please try to break it).
TODO: CPSC 4000, only to be taken in last semester
TODO: CPSC 3165, junior+ requirement
TODO: CPSC 1301K, handle the k, temporarily removed the k from course_info.xlsx
TODO: Deal with list sorting low level CYBR behind ALL CPSC courses, pointless if I get ALL courses through crawler?
TODO: Summer courses are not able to support the same amount of maximum courses, add fix for this
TODO: (CHECK) Handling hours going over the limit
TODO: (CHECK) Use hours instead of course count
Over commented as usual for your reading pleasure.
"""

SEMESTER_TYPE_SUCCESSOR = {'Fa': 'Sp', 'Sp':'Su', 'Su':'Fa'}    # Translation map from semester K to the next
DEFAULT_HOURS_PER_SEMESTER = 15 # MERINO: updated value

# Dummy container made in part by Austin (thanks)
# The values have the form (prereqs, availability, coreqs)
course_info = {
    'MATH 1113': ([], 'Fa Sp Su', []),
    'MATH 2125': (['MATH 1113'], 'Fa Sp Su', []),
    'MATH 5125': (['MATH 2125'], 'Fa Sp Su', []),
    'CPSC 2108': (['CPSC 1302'], 'Fa Sp Su', []),
    'CPSC 1301K': ([], 'Fa Sp Su', []),
    'CPSC 1302': (['CPSC 1301K'], 'Fa Sp Su', []),
    'CPSC 2105': (['CPSC 1301K'], 'Fa Sp Su', []),
    'CYBR 2159': (['CPSC 1301K'], 'Fa Sp --', []),
    'CYBR 2106': (['CPSC 1301K'], 'Fa Sp Su', []),
    'CPSC 3175': (['CPSC 2108'], 'Fa Sp --', []),
    'CPSC 3125': (['CPSC 2108', 'CPSC 2105'], 'Fa Sp --', []),
    'CPSC 3131': (['CPSC 1302'], 'Fa Sp --', []),
    'CPSC 4135': (['CPSC 3175'], '-- Sp --', []),
    'CPSC 3165': ([], 'Fa Sp Su', []),
    'CPSC 3121': (['CPSC 2105'], '-- Sp --', []),
    'CPSC 4155': (['CPSC 3121'], 'Fa -- --', []),
    'CPSC 4157': (['CYBR 2159', 'CPSC 2108'], 'Fa -- Su', []),
    'CPSC 4175': (['CPSC 3175'], 'Fa -- --', []),
    'CPSC 4115': (['MATH 5125', 'CPSC 2108'], 'Fa -- --', []),
    'CPSC 4148': (['CPSC 4115'], '-- Sp --', []),
    'CPSC 4176': (['CPSC 4175'], '-- Sp --', []),
    'CPSC 4000': ([], 'Fa Sp Su', []),
}

class DummyCourseInfoDataframeContainer:

    def __init__(self):
        self.dictionary = course_info
    
    def get_availability_list(self, course_id):
        # WE MAY ONLY NEED A STRING, THOUGH
        return self.dictionary[course_id][1].split()
        
    def get_prereqs(self, course_id):
        return self.dictionary[course_id][0]
                
    def get_coreqs(self, course_id):
        return self.dictionary[course_id][2]


class Scheduler:
    
    def __init__(self):
        self.hours_per_semester = DEFAULT_HOURS_PER_SEMESTER
        self.courses_needed = []
        self.course_info_container = None
        self.semester_type = 'Sp'
        # Removed mention course number
            
    # MERINO: added two more getters
    
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
        
        # Sorting
        # TODO: Make this better-er
        self.courses_needed.sort()
    
    def configure_hours_per_semester(self, number_of_hours):
        self.hours_per_semester = number_of_hours
    
    # MERINO: the method now uses hours per semester
    def generate_schedule(self):
        
        course_info = self.course_info_container    # Get the course info container
        courses_needed = self.courses_needed[:]     # Create a copy of the needed courses (workable list)
        
        # Helper functions
        
        def check_availability(course_id):
            # MERINO: changed method call name for course_info
            availability = course_info.get_availability(course_id) # Get a list that can contain 'Fa', 'Sp', 'Su', and/or '--'
            return working_semester_type in availability
            
        def check_precise_hours(course_id):
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
            # If corequisite course is in the needed courses, can't take course yet.
            for corequisite in corequisites:
                if corequisite in courses_needed:
                    return False
            return True
        
        def complete_check(course_id):
            # Run all three of the above checks (with short circuit evaluation)
            return check_availability(course_id) \
                and check_precise_hours(course_id) \
                and check_prerequisites(course_id) \
                and check_corequisites(course_id)
        
        full_schedule = []                          # Create empty, final schedule, each semester list will be added to this
        working_semester_type = self.semester_type  # Create a string to track the current semester type/season ('Fa', 'Sp', or 'Su')
        
        # loop through until courses_needed is empty
        while len(courses_needed):
            
            # if courses_needed is empty, break out of semester_types loop
            if not len(courses_needed):
                break
            
            semester = []                       # the working list of courses
            current_hours_counter = 0           # counter to hold number of scheduled hours during the current semester
            # NOTE: I am changing the use of this variable so it only stops the searching cycle if it runs through the entire needed
            # courses list without finding any new courses to register. This is the only solution I have for ensuring we schedule courses
            # that may have been skipped because of coreq requirements. This also prevents a rare bug where the while-loop would end
            # preemptively--this was dues to courses_counter not be corrected when the length of courses_needed was modified.
            unregistered_courses_counter = 0    # counter to control iteration through courses_needed
            
            # NOTE: we can easily set this depending on the semester type so there're fewer courses in the summer.
            max_hours = self.hours_per_semester # the number of hours (max) to register in the loop's semester
            
            # loop to fill out semester, don't loop over max_hours,
            # don't loop through courses_needed more than once, don't loop through courses_needed if empty
            while current_hours_counter < max_hours \
                    and unregistered_courses_counter < len(courses_needed) \
                    and len(courses_needed):
                    
                # get first course in list
                course = courses_needed.pop(0)
                course_hours = course_info.get_hours(course)

                # check availability, prerequisites, and corequisites
                passes_complete_check = complete_check(course)
                if not passes_complete_check:
                    # course cannot be taken, add course back to courses_needed and skip the rest of iteration loop
                    courses_needed.append(course)
                    unregistered_courses_counter += 1   # Used to detect if all courses have been check and, indeed, none can be registered
                    
                else:
                    # add course in semester, increment hours
                    semester.append(course)
                    current_hours_counter += course_hours
                    unregistered_courses_counter = 0
            
            # add semester to full_schedule
            full_schedule.append(semester)
            
            # Rotate to the next semester type/season
            working_semester_type = SEMESTER_TYPE_SUCCESSOR[working_semester_type]
            
        return full_schedule



# Testing:
    
# MERINO: removed "K" from 1301K and updated container name (this is just for testing, though)
        
# This is just for reference
courses = ['MATH 1113', 'MATH 2125', 'MATH 5125', 'CPSC 2108', 'CPSC 1301', 'CPSC 1302', 'CPSC 2105', 'CYBR 2159', 'CYBR 2106', 'CPSC 3175', 'CPSC 3125', 'CPSC 3131', 'CPSC 4135', 'CPSC 3165', 'CPSC 3121', 'CPSC 4155', 'CPSC 4157', 'CPSC 4175', 'CPSC 4115', 'CPSC 4148', 'CPSC 4176', 'CPSC 4000']

if __name__ == '__main__':
    from course_info_container import *
    s = Scheduler()
    container = CourseInfoContainer(load_course_info('input_files/Course Info.xlsx'))
    s.configure_course_info(container)
    print("Schedule 1:")
    s.configure_courses_needed(['MATH 1113', 'MATH 2125', 'MATH 5125', 'CPSC 2108', 'CPSC 1301', 'CPSC 1302', 'CPSC 2105', 'CYBR 2159', 'CYBR 2106', 'CPSC 3175', 'CPSC 3125', 'CPSC 3131', 'CPSC 4135', 'CPSC 3165', 'CPSC 3121', 'CPSC 4155', 'CPSC 4157', 'CPSC 4175', 'CPSC 4115', 'CPSC 4148', 'CPSC 4176', 'CPSC 4000'])
    s.configure_hours_per_semester(15)
    print(s.generate_schedule())
    
