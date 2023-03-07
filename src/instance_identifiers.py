# Thomas Merino
# 2/19/2023
# CPSC 4176 Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional
    from course_info_container import CourseInfoContainer
    from requirement_container import RequirementsContainer


DEFAULT_COURSE_CREDIT_HOURS: int = 3

# The name to give to a course identifier if no descriptions are found
DEFAULT_COURSE_PRINTABLE_NAME: str = 'Course'

class CourseIdentifier:

    def __init__(self, course_number: Optional[str] = None, course_name: Optional[str] = None, is_concrete: bool = True, \
            can_exist_multiple_times: bool = False) -> None:
        self._course_number: Optional[str] = course_number
        self._course_name: Optional[str] = course_name
        self._is_concrete: bool = is_concrete and course_number is not None
        self._can_exist_multiple_times: bool = can_exist_multiple_times
        
        self._stub_credits: Optional[int] = None
        self._stub_prequisite_tree: Optional[RequirementsContainer] = None
        self._stub_corequisite_tree: Optional[RequirementsContainer] = None
    
    def __str__(self) -> str:
        return self.get_printable_name()

    def get_printable_name(self) -> str:

        result: str = ''

        if self._is_concrete:
            result = str(self._course_number)
            if self._course_name is not None:
                result +=  f' - {self._course_name}'
        else:
            result = self._course_name or DEFAULT_COURSE_PRINTABLE_NAME
        
        return result


    def get_unique_id(self) -> Optional[str]:
        return self._course_number
    
    def get_name(self) -> Optional[str]:
        return self._course_name or self._course_number

    def is_concrete(self) -> bool:
        return self._is_concrete

    def can_exist_multiple_times(self) -> bool:
        return self._can_exist_multiple_times

    def get_credit_hours(self, course_info_container: CourseInfoContainer) -> int:

        result: int = self._stub_credits

        if self._is_concrete:
            # TODO: add the actual function call here:
            course_info_container.get_credits(self._course_number)
        elif result is None:
            result = DEFAULT_COURSE_CREDIT_HOURS
        
        return result

    def get_prequisites(self, course_info_container) -> Optional[RequirementsContainer]:
        
        result: Optional[RequirementsContainer] = self._stub_prequisite_tree

        if self._is_concrete:
            # TODO: add the actual function call here:
            course_info_container.get_credits(self._course_number)
        elif result is None:
            result = None # TODO: ADD DEFAULT TREE
        
        return result
        

class StudentIdentifier:

    def __init__(self, student_number: Optional[str] = None, student_name: Optional[str] = None) -> None:
        self._student_number: Optional[str] = student_number
        self._student_name: Optional[str] = student_name

    def is_concrete(self) -> bool:
        return self._student_number is not None or self._student_name is not None

    def __str__(self) -> str:
        description: str = 'Student'

        if self._student_name is not None:
            description = self._student_name

            if self._student_number is not None:
                description += f' ({self._student_number})'

        elif self._student_number is not None:
             description = str(self._student_number)

        return description
