# Thomas Merino
# 1/3/23
# CPSC 4175 Group Project

#SEMESTER_TYPE_SUCCESSOR = {'Fall': 'Spring', 'Spring':'Summer', 'Summer':'Fall'}    # Translation map from semester K to the next

from general_utilities import *

def plain_text_export(filepath, schedule, starting_semester_type, starting_year) -> None:
    '''Export the passed schedule to a new text file at the passed path. The starting_semester_type
    argument is expended to be "Fall", "Spring", or "Summer".'''
    
    # Check for invalid argument
    if starting_semester_type not in SEMESTER_TYPE_SUCCESSOR:
        raise ValueError('Invalid starting semester type argument in plain text formatter.')
    
    with open(filepath, 'w') as file_reference:
        
        current_semester_type = starting_semester_type
        curent_year = starting_year
        
        # Iterate over each semester
        for semester in schedule:
            file_reference.write('{0} {1}:\n'.format(current_semester_type, curent_year)) # Write semester type and year
            file_reference.write(', '.join(semester) if semester else '-No Course-') # White courses or "-No Courses-"
            file_reference.write('\n\n') # Create spacing in file
            
            # Rotate the semester type and year if entering the spring
            current_semester_type = SEMESTER_TYPE_SUCCESSOR[current_semester_type]
            if current_semester_type == 'Spring':
                curent_year += 1

