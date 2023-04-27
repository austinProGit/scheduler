# Thomas Merino
# 3/1/2023
# CPSC 4176 Project


# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    SemesterType = int

from datetime import date

# Create enum cases to represent each semester
FALL: SemesterType = 0x00
SPRING: SemesterType = 0x01
SUMMER: SemesterType = 0x02

# Create a mapping from a semester (enum) to a string description
SEMESTER_DESCRIPTION_MAPPING: dict[SemesterType, str] = {
    FALL: 'Fall',
    SPRING: 'Spring',
    SUMMER: 'Summer'
}

SEMESTER_TYPE_SUCCESSOR: dict[SemesterType, SemesterType] = {FALL: SPRING, SPRING: SUMMER, SUMMER: FALL}    # Translation map from semester K to the next


ESTIMATED_NEXT_SEMESTER: SemesterType = FALL
ESTIMATED_NEXT_YEAR: int = 2023

def get_semester_successor(semester: SemesterType) -> SemesterType:
    '''Get the semester that follows the passes semester.'''
    return SEMESTER_TYPE_SUCCESSOR[semester]