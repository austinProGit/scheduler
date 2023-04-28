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

def plain_text_export(filepath: Path, schedule: ScheduleInfoContainer) -> None:
    '''Export the passed schedule to a new text file at the passed path.'''
    
    with open(filepath, 'w') as writer:
        
        # Iterate over each semester
        semester: SemesterDescription
        for semester in schedule.get_schedule():
            current_semester_type: SemesterType = semester.semester_type
            curent_year: int = semester.year
            writer.write(f'{SEMESTER_DESCRIPTION_MAPPING[current_semester_type]} {curent_year}:\n') # Write semester type and year
            writer.write(', '.join(semester.str_iterator()) if semester else '-No Courses-') # White courses or "-No Courses-"
            writer.write('\n\n') # Create spacing in file
            

