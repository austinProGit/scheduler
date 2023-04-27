# Thomas Merino
# 3/1/2023
# CPSC 4176 Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional, Callable, Any
    from pathlib import Path
    from driver_fs_functions import ExportType, PATH_TO_GRADUATION_EXPORT_TYPE

from general_utilities import *
from math import inf

DEFAULT_SPRING_FALL_HOURS: int = 15
DEFAULT_SUMMER_HOURS: int = 3
DEFAULT_SPRING_FALL_MINIMUM_HOURS: int = 4
DEFAULT_SUMMER_MINIMUM_HOURS: int = 0


DEFAULT_DESTINATION_FILENAME = "Path to Graduation"



class CreditHourInformer:

    @staticmethod
    def make_unlimited_generator() -> CreditHourInformer:
        result: CreditHourInformer = CreditHourInformer(None)
        result._generator = lambda s, y: inf
        return result

    def _invalid_generator(self, semester: SemesterType, year: int) -> int:
        raise ValueError('Illegal credit hour informer state encountered.')

    def __init__(self, meta_informer: Any):
        self._generator: Callable[[SemesterType, int], float] = self._invalid_generator
        if meta_informer is None:
            pass
        else:
            # isinstance(meta_inrformer, ConstuctiveScheduler) would be good if cyclic imports did not happen
            self._generator = lambda s, y: meta_informer.get_hours_per_semester(s).stop

    def get(self, semester: SemesterType, year: int) -> int:
        return self._generator(semester, year)

    

# This is a base for a container of scheduler parameters. This will be alike the constuctive parameter
# container. In the event this changes, the constuctive parameter container will override to be consistent
# the current implementation.
class SchedulerParameterContainer:

    def __init__(self, path: Path, export_types: list[ExportType], fall_spring_hours=DEFAULT_SPRING_FALL_HOURS, summer_hours=DEFAULT_SUMMER_HOURS) -> None:

        # Create the default directory to export to. This is always
        # expected to be an existing path. Do not set it purely based on user input
        self._destination_directory: Path = path


        self._destination_filename: str = DEFAULT_DESTINATION_FILENAME

        # Create a list to track the export methods to use
        self._export_types: list[ExportType] = export_types[:] 

        # Set some basic instance variables for tracking the hours per a given semester (this implementation
        # does not differ by year).
        self._fall_spring_hours: int = fall_spring_hours
        self._summer_hours: int = summer_hours

        # Set the minimums for the credit hours' ranges
        self._fall_spring_minimum_hours: int = DEFAULT_SPRING_FALL_MINIMUM_HOURS
        self._summer_minimum_hours: int = DEFAULT_SUMMER_MINIMUM_HOURS


    def get_destination_directory(self) -> Path:
        '''Get the Path to export to (never None).'''
        return self._destination_directory

    def set_destination_directory(self, path: Path) -> bool:
        '''Set the destination path (Path object, not None).'''
        self._destination_directory = path
        return True

    def get_destination_filename(self) -> str:
        '''get the destination filename'''
        return self._destination_filename

    def set_destination_filename(self, name: str) -> None:
        '''Set the destination filename'''
        self._destination_filename = name

    def get_export_types(self) -> list[ExportType]:
        '''Get a copy of the export types listing where each element is an export format. This
        may return an empty list.'''
        return self._export_types[:]
    
    def add_export_type(self, export_type: ExportType) -> bool:
        '''Add an export type to use during the next export. This will not allow for duplicates.
        The success of the addition is returned (bool).'''

        will_add: bool = export_type not in self._export_types
        if will_add:
            self._export_types.append(export_type)
        return will_add

    def remove_export_type(self, export_type: ExportType) -> bool:
        '''Remove an export type to from the next export. This will account for nonexistent elements.
        The success of the removal is returned (bool).'''

        will_removed: bool = export_type in self._export_types
        if will_removed:
            self._export_types.remove(export_type)
        return will_removed

    def set_export_type(self, export_types: list[ExportType]) -> None:
        '''Set the export types list to be a copy of the passed list.'''
        self._export_types = export_types[:]

    def get_hours_for(self, semester_type: SemesterType, year: Optional[int] = None) -> range:
        '''Get the acceptability range for hours for a given semester type and year.'''
        return range(self._fall_spring_minimum_hours, self._fall_spring_hours) if semester_type != SUMMER else \
            range(self._summer_minimum_hours, self._summer_hours)

# A standard scheduler parameters container (the current implementation treats this the same as the base class).
class ConstructiveSchedulingParametersContainers (SchedulerParameterContainer):
    
    def set_hours(self, semester_type: SemesterType, hours: int) -> None:
        '''Get the acceptability range for hours for a given semester type and year.'''
        if semester_type != SUMMER:
            self._fall_spring_hours = hours
        else:
            self._summer_hours = hours


