# Thomas Merino
# 3/7/23
# CPSC 4175 Group Project

#SEMESTER_TYPE_SUCCESSOR = {'Fall': 'Spring', 'Spring':'Summer', 'Summer':'Fall'}    # Translation map from semester K to the next

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from schedule_info_container import ScheduleInfoContainer, SemesterDescription
    from pathlib import Path

from general_utilities import *

def plain_text_export(filepath: Path, schedule: ScheduleInfoContainer, \
        starting_semester_type: SemesterType, starting_year: int) -> None:
    '''Export the passed schedule to a new text file at the passed path. The starting_semester_type
    argument is expected to be a SemesterType.'''
    
    # Check for invalid argument
    if starting_semester_type not in SEMESTER_TYPE_SUCCESSOR:
        raise ValueError('Invalid starting semester type argument in plain text formatter.')
    
    with open(filepath, 'w') as writer:
        
        current_semester_type: SemesterType = starting_semester_type
        curent_year: int = starting_year
        
        # Iterate over each semester
        semester: SemesterDescription
        for semester in schedule.get_schedule():
            writer.write(f'{SEMESTER_DESCRIPTION_MAPPING[current_semester_type]} {curent_year}:\n') # Write semester type and year
            writer.write(', '.join(semester.str_iterator()) if semester else '-No Courses-') # White courses or "-No Courses-"
            writer.write('\n\n') # Create spacing in file
            
            # Rotate the semester type and year if entering the spring
            current_semester_type = SEMESTER_TYPE_SUCCESSOR[current_semester_type]
            if current_semester_type == SPRING:
                curent_year += 1

