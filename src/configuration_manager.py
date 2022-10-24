# Thomas Merino
# 10/24/22
# CPSC 4175 Group Project

import json
from os import path

from driver_fs_functions import *


DEFAULT_CATALOG_NAME = 'input_files/Course Info.xlsx'           # The default name for the catalog/course info file
DEFAULT_EXCUSED_PREREQS_NAME = 'input_files/Course Info.xlsx'   # The default name for the excused prereq.s file
DEFAULT_AVAILABILITY_FILENAME = 'input_files/Course Info.xlsx'  # The default name for the catalog/course availability file
CONFIG_FILENAME = 'config.json'                                 # The name of the config file
DEFAULT_SCHEDULE_NAME = 'Path to Graduation'                    # The default filename for exporting schedules
DEFAULT_NORMAL_HOURS_LIMIT = 18                                 # The upper limit of credit hours students can take per semester (recommended)
DEFAULT_STRONG_HOURS_LIMIT = 30                                 # The absolute limit of credit hours students can take per semester (cannot exceed)
DEFAULT_STRONG_HOURS_MINIMUM = 4                                # The absolute minimum of credit hours students can take per semester (cannot be below)


# In this case "encodable" is just a dictionary where the keys are the attribute names
# and the values are the attribute values

class SessionConfiguration():
    
    @staticmethod
    def make_default():
        '''Static method to make a default session config (and, hence, config file)'''
        result = SessionConfiguration(
            DEFAULT_CATALOG_NAME,
            DEFAULT_EXCUSED_PREREQS_NAME,
            DEFAULT_AVAILABILITY_FILENAME,
            True,
            DEFAULT_SCHEDULE_NAME,
            DEFAULT_NORMAL_HOURS_LIMIT,
            DEFAULT_STRONG_HOURS_LIMIT,
            DEFAULT_STRONG_HOURS_MINIMUM
        )
        return result
    
    expected_attributes = {
        'course_info_filename',
        'excused_prereqs',
        'availability_filename',
        'is_graphical',
        'initial_schedule_name',
        'normal_hours_limit',
        'strong_hours_limit',
        'strong_hours_minimum'
    }
    
    # NOTE: We cannot rely on the default values being used during a default init (use make_default instead)
    
    def __init__(self,
                 course_info_filename=DEFAULT_CATALOG_NAME,
                 excused_prereqs=DEFAULT_EXCUSED_PREREQS_NAME,
                 availability_filename=DEFAULT_AVAILABILITY_FILENAME,
                 is_graphical=True,
                 initial_schedule_name=DEFAULT_SCHEDULE_NAME,
                 normal_hours_limit=DEFAULT_NORMAL_HOURS_LIMIT,
                 strong_hours_limit=DEFAULT_STRONG_HOURS_LIMIT,
                 strong_hours_minimum=DEFAULT_STRONG_HOURS_MINIMUM):
                 
        self.course_info_filename = course_info_filename
        self.excused_prereqs = excused_prereqs
        self.availability_filename = availability_filename
        self.is_graphical = is_graphical
        self.initial_schedule_name = initial_schedule_name
        self.normal_hours_limit = normal_hours_limit
        self.strong_hours_limit = strong_hours_limit
        self.strong_hours_minimum = strong_hours_minimum
    
    def get_encodable(self):
        '''Get an encodable data object that can be used to in a json dump call--in this case "encodable" is just a dictionary where the keys are the attribute names and the values are the attribute values.'''
        return self.__dict__
    
    def set_from_encodable(self, encodable):
        '''Set all of the object's via encodable data--in this case "encodable" is just a dictionary where the keys are the attribute names and the values are the attribute values.'''
        for attribute_name, attribute_value in encodable.items():
            setattr(self, attribute_name, attribute_value)
            
    def get_missing_attributes(self):
        '''Get a list of the missing attributes if any (may be used to check load validity).'''
        result = []
        for expected_attribute in SessionConfiguration.expected_attributes:
            if expected_attribute not in self.__dict__ or self.__dict__[expected_attribute] == None:
                result.append(expected_attribute)
        return result


def load_configuration_session(config_filename=CONFIG_FILENAME):
    
    # Get the config file
    config_filename = path.join(get_source_path(), config_filename)
    
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
                #self.output_error('Invalid config file contents. Please see instructions on how to reconfigure.')
                # TODO: this feel like the list itself should be passed and not a formatted string
                error_message = f'The following required parameter(s) are missing: {", ".join(missing_attributes)}.'
                raise ConfigFileError(error_message)
                
        except json.JSONDecodeError as encoding_error:
            raise ConfigFileError()


def save_configuration_session(session_configuration, config_filename=CONFIG_FILENAME):
    
    # Get the config file
    config_filename = path.join(get_source_path(), config_filename)
    
    with open(config_filename, 'w') as configuration_file:
        try:
            
            missing_attributes = session_configuration.get_missing_attributes()
            
            # Check if all lines exist and are not empty strings
            if not missing_attributes:
                json.dump(session_configuration.get_encodable(), configuration_file)
            
            # return all of the missing attributes
            return missing_attributes
            
        except json.JSONDecodeError as encoding_error:
            # TODO: make this better in the given context
            raise ConfigFileError()
            



