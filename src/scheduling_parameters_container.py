# Thomas Merino
# 2/19/2023
# CPSC 4176 Project

from general_utilities import *

DEFAULT_SPRING_FALL_HOURS = 15
DEFAULT_SUMMER_HOURS = 3


class ConstructiveSchedulingParametersContainers:

    def __init__(self, fall_spring_hours=DEFAULT_SPRING_FALL_HOURS, summer_hours=DEFAULT_SUMMER_HOURS):
        self._fall_spring_hours = fall_spring_hours
        self._summer_hours = summer_hours

    def get_hours_for(self, year, semester_type):
        return self._fall_spring_hours if semester_type != SUMMER else self._summer_hours


