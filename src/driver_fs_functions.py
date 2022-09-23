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
        
        # Get the index where the digits suffix begins
        end_digit_index = len(filepath_name)
        # This checks if end_digit_index has reached the zero and if the checked character is numeric
        while end_digit_index and filepath_name[end_digit_index - 1].isdigit():
            end_digit_index -= 1
        
        # Seperate the filepath into its digit and non-digit section
        path_digit_section = filepath_name[end_digit_index:]
        
        # If there is no digit at the end of the filename, just add a "2"
        number = int(filepath_name[end_digit_index:]) + 1 if path_digit_section else 2
        pre_digit_path_name = filepath_name[:end_digit_index]
        working_filepath = Path(pre_digit_path_name + str(number)).with_suffix(filepath_extension)
        
        # Increase the suffix number until no collision is found
        while working_filepath.exists():
            number += 1
            working_filepath = Path(pre_digit_path_name + str(number)).with_suffix(filepath_extension)
        
        return working_filepath
    
    else:
        # The filepath is free (return it)
        return path
