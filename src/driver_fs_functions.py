# Thomas Merino
# 9/23/22
# CPSC 4175 Group Project

# This file contains constants and functions for the the driver/controller and the interface components.

from pathlib import Path

# Constants for export types
PATH_TO_GRADUATION_EXPORT_TYPE = 0x00
PLAIN_TEXT_EXPORT_TYPE = 0x01

# Dictionary from export types to their description
EXPORT_TYPE_DESCRIPTIONS = {
    PATH_TO_GRADUATION_EXPORT_TYPE: 'Path to Graduation Excel',
    PLAIN_TEXT_EXPORT_TYPE: 'Plain txt'
}

# MERINO: Added a handy splitting function for getting the numeric end of a filename
def suffix_split(filtr, sequence):
    '''Split the passed sequence by a suffix: end section of the sequence such that every item meets the passed filter--
    the suffix ends as soon as one item doesn't meet the filter, and the entire sequence may be the suffix if all pass.
    The filter function is expeceted to take an item and returns a boolean. This returns a tuple with the sequence before
    the suffix and then the suffix (both may be esequencempty).'''
    for index in range(len(sequence) - 1, -1, -1):              # Iterate backwards
        if not filtr(sequence[index]):                          # Return if the filter does not pass
            return (sequence[:index + 1], sequence[index + 1:]) # Split on the index
    return (sequence[:0], sequence[:])                          # All items pass
    

def get_real_filepath(filepath):
    '''Function to verify the existence of a file/directory and change any "~" prefix into the user's home directory. This
    returns the corrected path if it exists and None if it does not. The argument is expected to be a string or Path and
    the function returns a Path.'''
    corrected_filepath = Path(filepath).expanduser()                        # Change "~" to the user's home address if present
    return corrected_filepath if corrected_filepath.exists() else None      # Return the path if it exists (otherwise None)


def get_next_free_filename(filepath):
    '''Function that checks if the passed filepath already has a file/directory. If it doesn't, simply return the passed path,
    and if it does, return the next filepath that is free (by changing the trailing number in the filename). Please note this
    is not optimized for large batches because there would be too many FS system calls (slow). This expects to get a valid
    filepath; no checking (other than for uniqueness) or conversion of "~" is performed. the argument is expected to be a
    string or Path and the function return a Path.'''
    
    # NOTE: if we want to use this for batch work, it would be better to simply store a file number and feed the filenames.
    path = Path(filepath)
    
    if path.exists():
        
        # The filepath is already being used (find the next reasonable name)
        
        # Get the filename without any extension and as a string
        filepath_name = str(path.with_suffix(''))
        filepath_extension = path.suffix
        
        # MERINO: Using the new function above
        
        # Seperate the filepath into its non-digit and end-digit section
        pre_digit_path_name, path_digit_section = suffix_split(lambda c : c.isdigit(), filepath_name)
        # If there is no digit at the end of the filename, just add a "2"
        number = int(path_digit_section) + 1 if path_digit_section else 2
        working_filepath = Path(pre_digit_path_name + str(number)).with_suffix(filepath_extension)
        
        # Increase the suffix number until no collision is found
        while working_filepath.exists():
            number += 1
            working_filepath = Path(pre_digit_path_name + str(number)).with_suffix(filepath_extension)
        
        return working_filepath
    
    else:
        # The filepath is free (return it)
        return path
