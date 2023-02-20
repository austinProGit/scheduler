# Thomas Merino and Austin Lee
# 2/20/2023
# CPSC 4176 Project

from instance_identifiers import StudentIdentifier
from requirement_parser import RequirementsParser
from courses_needed_container import CoursesNeededContainer

class DegreeExtractionContainer:

    # certain_courses is a list of strings
    # courses_needed_constuction_string is a string with the requirements logic string format
    # degree_plan_name is a string
    # student_number is a string
    # student_name is a string
    def __init__(self, certain_courses, courses_needed_constuction_string, degree_plan_name=None, student_number=None, student_name=None):

        self._certain_courses = certain_courses
        self._courses_needed_constuction_string = courses_needed_constuction_string

        self._degree_plan_name = degree_plan_name

        self._student_number = student_number
        self._student_name = student_name

    def make_courses_needed_container(self):
        parse_results = RequirementsParser.make_from_course_selection_logic_string(self._courses_needed_constuction_string)
        return CoursesNeededContainer(self._degree_plan_name, parse_results.certain_courses, parse_results.decision_tree)

    def make_student_identifier(self):
        return StudentIdentifier(self._student_number, self._student_name)











