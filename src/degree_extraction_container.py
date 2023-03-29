# Thomas Merino and Austin Lee
# 3/24/2023
# CPSC 4176 Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional


from instance_identifiers import StudentIdentifier
from requirement_parser import RequirementsParser
from courses_needed_container import CoursesNeededContainer

class DegreeExtractionContainer:

    # taken_courses is a list of strings
    # courses_needed_constuction_string is a string with the requirements logic string format
    # degree_plan_name is a string
    # student_number is a string
    # student_name is a string
    def __init__(self, taken_courses: list[str], courses_needed_constuction_string: str, degree_plan_name: Optional[str] = None,
            student_number: Optional[str] = None, student_name: Optional[str] = None) -> None:

        self._taken_courses: list[str] = taken_courses
        self._courses_needed_constuction_string: str = courses_needed_constuction_string

        self._degree_plan_name: str = degree_plan_name

        self._student_number: str = student_number
        self._student_name: str = student_name

    def make_courses_needed_container(self) -> CoursesNeededContainer:
        parse_results: RequirementsParser.RequirementsParseReport = \
            RequirementsParser.make_from_course_selection_logic_string(self._courses_needed_constuction_string)
        return CoursesNeededContainer(self._degree_plan_name, parse_results.certain_courses, parse_results.decision_tree)

    def make_student_identifier(self) -> StudentIdentifier:
        return StudentIdentifier(self._student_number, self._student_name)

    def make_taken_courses_list(self) -> list[str]:
        return self._taken_courses

    def __eq__(self, rhs: object) -> bool:
        def strip_to_compare(string: str) -> str:
            if string:
                string = string.replace(" ", "").replace("\t", "").replace("\n","")
                return string
        result: bool = False
        if isinstance(rhs, DegreeExtractionContainer):
            result = self._taken_courses == rhs._taken_courses and \
                strip_to_compare(self._courses_needed_constuction_string) == strip_to_compare(rhs._courses_needed_constuction_string) and \
                strip_to_compare(self._degree_plan_name) == strip_to_compare(rhs._degree_plan_name) and \
                strip_to_compare(self._student_number) == strip_to_compare(rhs._student_number) and \
                strip_to_compare(self._student_name) == strip_to_compare(rhs._student_name)
        return result










