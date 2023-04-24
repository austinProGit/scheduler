# Thomas Merino
# 2/27/23
# CPSC 4175 Group Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any
    from io import TextIOWrapper

import json
from os import path

from driver_fs_functions import *

DEFAULT_CATALOG_NAME: str = 'input_files/Course Info.xlsx' # The default name for the catalog/course info file
DEFAULT_EXCUSED_PREREQS_NAME: str = 'input_files/Course Info.xlsx' # The default name for the excused prereq.s file
DEFAULT_AVAILABILITY_FILENAME: str = 'input_files/Course Info.xlsx' # The default name for the catalog/course availability file
DEFAULT_ALAIS_FILENAME: str = 'input_files/Aliases.xlsx' # The default name for the alias file
CONFIG_FILENAME: str = 'config.json' # The name of the config file
DEFAULT_SCHEDULE_NAME: str = 'Path to Graduation' # The default filename for exporting schedules
DEFAULT_NORMAL_HOURS_LIMIT: int = 18 # The upper limit of credit hours students can take per semester (recommended)
DEFAULT_STRONG_HOURS_LIMIT: int = 30 # The absolute limit of credit hours students can take per semester (cannot exceed)
DEFAULT_STRONG_HOURS_MINIMUM: int = 4 # The absolute minimum of credit hours students can take per semester (cannot be below)


# In this case "encodable" is just a dictionary where the keys are the attribute names
# and the values are the attribute values

class SessionConfiguration():
    
    @staticmethod
    def make_default() -> SessionConfiguration:
        '''Static method to make a default session config (and, hence, config file)'''
        result = SessionConfiguration(
            DEFAULT_CATALOG_NAME,
            DEFAULT_EXCUSED_PREREQS_NAME,
            DEFAULT_AVAILABILITY_FILENAME,
            DEFAULT_ALAIS_FILENAME,
            True,
            DEFAULT_SCHEDULE_NAME,
            DEFAULT_NORMAL_HOURS_LIMIT,
            DEFAULT_STRONG_HOURS_LIMIT,
            DEFAULT_STRONG_HOURS_MINIMUM
        )
        return result
    
    expected_attributes: set[str] = {
        'course_info_filename',
        'excused_prereqs',
        'availability_filename',
        'alias_filename',
        'is_graphical',
        'initial_schedule_name',
        'normal_hours_limit',
        'strong_hours_limit',
        'strong_hours_minimum'
    }
    
    # NOTE: We cannot rely on the default values being used during a default init (use make_default instead)
    
    def __init__(self,
                 course_info_filename: str = DEFAULT_CATALOG_NAME,
                 excused_prereqs: str = DEFAULT_EXCUSED_PREREQS_NAME,
                 availability_filename: str = DEFAULT_AVAILABILITY_FILENAME,
                 alias_filename: str = DEFAULT_ALAIS_FILENAME,
                 is_graphical: bool = True,
                 initial_schedule_name: str = DEFAULT_SCHEDULE_NAME,
                 normal_hours_limit: int = DEFAULT_NORMAL_HOURS_LIMIT,
                 strong_hours_limit: int = DEFAULT_STRONG_HOURS_LIMIT,
                 strong_hours_minimum: int = DEFAULT_STRONG_HOURS_MINIMUM) -> None:
                 
        self.course_info_filename: str = course_info_filename
        self.excused_prereqs: str = excused_prereqs
        self.availability_filename: str = availability_filename
        self.alias_filename: str = alias_filename
        self.is_graphical: bool = is_graphical
        self.initial_schedule_name: str = initial_schedule_name
        self.normal_hours_limit: int = normal_hours_limit
        self.strong_hours_limit: int = strong_hours_limit
        self.strong_hours_minimum: int = strong_hours_minimum
    
    def get_encodable(self) -> dict[str, Any]:
        '''Get an encodable data object that can be used to in a json dump call--in this case "encodable" is just a dictionary where the keys are the attribute names and the values are the attribute values.'''
        return self.__dict__
    
    def set_from_encodable(self, encodable: dict[str, Any]) -> None:
        '''Set all of the object's via encodable data--in this case "encodable" is just a dictionary where the keys are the attribute names and the values are the attribute values.'''
        attribute_name: str
        attribute_value: Any
        for attribute_name, attribute_value in encodable.items():
            setattr(self, attribute_name, attribute_value)
            
    def get_missing_attributes(self) -> list[str]:
        '''Get a list of the missing attributes if any (may be used to check load validity).'''
        result = []
        expected_attribute: str
        for expected_attribute in SessionConfiguration.expected_attributes:
            if expected_attribute not in self.__dict__ or self.__dict__[expected_attribute] == None:
                result.append(expected_attribute)
        return result


def load_configuration_session(config_filename=CONFIG_FILENAME):
    
    # Get the config file
    config_filename: str = path.join(get_source_path(), config_filename)
    
    with open(config_filename, 'r') as configuration_file:
        try:
            session_configuration = SessionConfiguration()
            session_configuration.set_from_encodable(json.load(configuration_file))
            missing_attributes = session_configuration.get_missing_attributes()
            
            # Check if all lines exist and are not empty strings
            if not missing_attributes:
                return session_configuration
            else:
                # Configuration is missing important data (raise a config error)
                error_message = f'The following required parameter(s) are missing from the configuration file: {", ".join(missing_attributes)}.'
                raise ConfigFileError(error_message)
                
        except json.JSONDecodeError as encoding_error:
            raise ConfigFileError('Invalid json encoding detected in configuration file.')


def save_configuration_session(session_configuration: SessionConfiguration,
        config_filename: Union[str, Path] = CONFIG_FILENAME) -> list[str]:
    
    # Get the config file
    config_filename: str = path.join(get_source_path(), config_filename)
    missing_attributes: list[str] = []

    configuration_file: TextIOWrapper
    with open(config_filename, 'w') as configuration_file:
        try:
            # Get the missing attributes according to the class's method
            missing_attributes = session_configuration.get_missing_attributes()
            
            # Check if all lines exist and are not empty strings
            if not missing_attributes:
                json.dump(session_configuration.get_encodable(), configuration_file)
            
        except json.JSONDecodeError as encoding_error:
            # TODO: make this better in the given context
            raise ConfigFileError('An issue was encountered while trying to encode json for configuration file.')
    
    # return all of the missing attributes (if any)
    return missing_attributes
            



