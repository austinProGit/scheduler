# Thomas Merino
# 10/24/22
# CPSC 4175 Group Project

# This file contains constants and functions for the the driver/controller and the interface components.
# TODO: rename get_real_filepath (it looks like "relative filepath")

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union, Optional, Callable, TypeVar, Sequence
    T = TypeVar('T')
    ExportType = int


# NOTE: keep this file in the same directory as the config file

from pathlib import Path
import os



# Constants for export types
PATH_TO_GRADUATION_EXPORT_TYPE: ExportType = 0x00
PLAIN_TEXT_EXPORT_TYPE: ExportType = 0x01
PDF_EXPORT_TYPE: ExportType = 0x02

# Dictionary from export types to their description
EXPORT_TYPE_DESCRIPTIONS: dict[ExportType, str] = {
    PATH_TO_GRADUATION_EXPORT_TYPE: 'Path to Graduation Excel',
    PLAIN_TEXT_EXPORT_TYPE: 'Plain txt',
    PDF_EXPORT_TYPE: 'PDF'
}


# This exception is used when an issue with the config file is encountered.
class ConfigFileError(Exception):
    pass


def get_source_path() -> Path:
    '''Get the path of the program's directory (a Path object).'''
    return Path(__file__).parent
    

def suffix_split(filtr: Callable[[T], bool], sequence: Sequence[T]):
    '''Split the passed sequence by a suffix: end section of the sequence such that every item meets the passed filter--
    the suffix ends as soon as one item doesn't meet the filter, and the entire sequence may be the suffix if all pass.
    The filter function is expeceted to take an item and returns a boolean. This returns a tuple with the sequence before
    the suffix and then the suffix (both may be empty).'''
    for index in range(len(sequence) - 1, -1, -1): # Iterate backwards
        if not filtr(sequence[index]): # Return if the filter does not pass
            return (sequence[:index + 1], sequence[index + 1:]) # Split on the index
    return (sequence[:0], sequence[:]) # All items pass
    

def get_real_filepath(filepath: Union[str, Path]) -> Optional[Path]:
    '''Function to verify the existence of a file/directory and change any "~" prefix into the user's home directory. This
    returns the corrected path if it exists and None if it does not. The argument is expected to be a string or Path and
    the function returns a Path.'''
    try:
        corrected_filepath = Path(filepath).expanduser() # Change "~" to the user's home address if present
        return corrected_filepath if corrected_filepath.exists() else None # Return the path if it exists (otherwise None)
    except RuntimeError:
        # Runtime error occurred, which is likely a bad user directory expansion (return None)
        return None

def get_source_relative_path(directory_path, additional_path):
    '''Get the absolute path of the passed path as if the working directory is the passed directory. directory is
    assumed to be absolute.'''
    possible_path = Path(additional_path)
    if possible_path.is_absolute():
        return possible_path
    else:
        return Path(directory_path, additional_path)

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
