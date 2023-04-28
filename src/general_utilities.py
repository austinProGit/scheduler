# Thomas Merino and Max Lewis
# 3/1/2023
# CPSC 4176 Project


# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    SemesterType = int

from datetime import date, timedelta

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


def _determine_next_scheduling_semester() -> SemesterType:
    result: SemesterType = FALL
    month = date.today().month
    if month >= 1 and month <= 5: result = SUMMER
    if month >= 6 and month <= 7: result = FALL
    if month >= 8 and month <= 12: result = SPRING
    return result

def _determine_next_scheduling_year() -> int:
    return (date.today() + timedelta(days = 20)).year


ESTIMATED_NEXT_SEMESTER: SemesterType = _determine_next_scheduling_semester()
ESTIMATED_NEXT_YEAR: int = _determine_next_scheduling_year()


def get_semester_successor(semester: SemesterType) -> SemesterType:
    '''Get the semester that follows the passes semester.'''
    return SEMESTER_TYPE_SUCCESSOR[semester]

