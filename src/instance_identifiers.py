# Thomas Merino
# 2/19/2023
# CPSC 4176 Project

DEFAULT_COURSE_CREDIT_HOURS = 3

# The name to give to a course identifier if no descriptions are found
DEFAULT_COURSE_PRINTABLE_NAME = 'Course'

class CourseIdentifier:

    def __init__(self, course_number=None, course_name=None, is_concrete=True, can_exist_multiple_times=False):
        self._course_number = course_number
        self._course_name = course_name
        self._is_concrete = is_concrete and course_number is not None
        self._can_exist_multiple_times = can_exist_multiple_times
        
        self._stub_credits = None
        self._stub_prequisite_tree = None
        self._stub_corequisite_tree = None
    
    def __str__(self):

        return self.get_printable_name()

    def get_printable_name(self):

        result = ''

        if self._is_concrete:
            result = str(self._course_number)
            if self._course_name is not None:
                result +=  f' - {self._course_name}'
        else:
            result = self._course_name or DEFAULT_COURSE_PRINTABLE_NAME
        
        return result


    def get_unique_id(self):
        return self._course_number
    
    def get_name(self):
        return self._course_name or self._course_number

    def is_concrete(self):
        return self._is_concrete

    def can_exist_multiple_times(self):
        return self._can_exist_multiple_times

    def get_credit_hours(self, course_info_container):

        result = self._stub_credits

        if self._is_concrete:
            # TODO: add the actual function call here:
            course_info_container.get_credits(self._course_number)
        elif result is None:
            result = DEFAULT_COURSE_CREDIT_HOURS
        
        return result

    def get_prequisites(self, course_info_container):
        
        result = self._stub_prequisite_tree

        if self._is_concrete:
            # TODO: add the actual function call here:
            course_info_container.get_credits(self._course_number)
        elif result is None:
            result = None # TODO: ADD DEFAULT TREE
        
        return result
        

class StudentIdentifier:

    def __init__(self, student_number=None, student_name=None):
        self._student_number = student_number
        self._student_name = student_name

    def is_concrete(self):
        return self._student_number is not None or self._student_name is not None

    def __str__(self):
        description = 'Student'

        if self._student_name is not None:
            description = self._student_name

            if self._student_number is not None:
                description += f' ({self._student_number})'

        elif self._student_number is not None:
             description = str(self._student_number)

        return description
