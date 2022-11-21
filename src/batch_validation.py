# Thomas Merino
# 11/17/22
# CPSC 4175 Group Project

#from itertools import repeat
from user_submitted_validator import validate_user_submitted_path
from path_to_grad_parser import parse_path_to_grad
from concurrent.futures import ProcessPoolExecutor


class ValidationReport:
    
    def __init__(self, file_description, confidence_factor, error_list=[], exception=None):
        self.file_description = file_description
        self.confidence_factor = confidence_factor
        self.error_list = error_list
        self.exception = exception

    def is_valid(self):
        return self.error_list == [] and self.exception is None
    
    def description(self):
        return f'{self.file_description}'


def batch_validation(input_files, course_info_container):
    """Check all passed files using path to graduation parser and validator. This uses the passed course info container, and return a list of ValidationReport objects."""
    
    result = []
    
    with ProcessPoolExecutor() as executor:
        processes = [executor.submit(_validate_file, file, course_info_container, result) for file in input_files]
        
        for process in processes:
            process_result = process.result()
            result.append(process_result)
    
    return result


def _validate_file(input_file, course_info_container, results_list):
    report = None
    try:
        schedule = parse_path_to_grad(input_file)
        error_reports = validate_user_submitted_path(course_info_container, schedule)
        # TODO: implement confidence factor here
        report = ValidationReport(input_file, confidence_factor=1, error_list=error_reports)
    except (IOError, ValueError):
        report = ValidationReport(input_file, confidence_factor=0, exception="Bad file format")
        
    return report


if __name__ == "__main__":
    batch_validation([i for i in range(22)], 123)

