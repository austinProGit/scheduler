# Thomas Merino
# 11/23/22
# CPSC 4175 Group Project

#from itertools import repeat
from user_submitted_validator import validate_user_submitted_path
from path_to_grad_parser import parse_path_to_grad
from concurrent.futures import ProcessPoolExecutor
from expert_system_module import ExpertSystem, DynamicKnowledge

class ValidationReport:
    '''Class for representing a path to graduation validation report. This stores all errors if present, the path file's description (preferably printable), and the confidence factor.'''
    
    def __init__(self, file_description, confidence_factor, error_list=[], exception=None):
        self.file_description = file_description
        self.confidence_factor = confidence_factor
        self.error_list = error_list
        self.exception = exception

    def is_valid(self):
        '''Returns the validity (boolean) of the path.'''
        return self.error_list == [] and self.exception is None
    


def batch_validation(input_files, course_info_container):
    """Check all passed files using path to graduation parser and validator. This uses the passed course info container and schedule evaluator (expert system), and it returns a list of ValidationReport objects."""
    
    result = []
    
    with ProcessPoolExecutor() as executor:
        processes = [executor.submit(_validate_file, file, course_info_container) for file in input_files]
        
        for process in processes:
            process_result = process.result()
            result.append(process_result)
    
    return result


def _validate_file(input_file, course_info_container):
    '''Validate a single file given the passed file path and info container. This returns the report object.'''
    report = None
    try:
        schedule = parse_path_to_grad(input_file)
        
        error_reports = validate_user_submitted_path(course_info_container, schedule)
        dynamic_knowledge = DynamicKnowledge()
        dynamic_knowledge.set_schedule(schedule)
        confidence_factor = ExpertSystem().calculate_confidence(dynamic_knowledge, course_info_container)
        report = ValidationReport(input_file, confidence_factor=confidence_factor, error_list=error_reports)
    except (IOError, ValueError):
        report = ValidationReport(input_file, confidence_factor=0, exception="Bad file format")
        
    return report


if __name__ == "__main__":
    batch_validation([i for i in range(22)], 123)

