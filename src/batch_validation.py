# Thomas Merino
# 11/23/22
# CPSC 4175 Group Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pathlib import Path
    from typing import Union
    from course_info_container import CourseInfoContainer
    from end_reports import ExportReport, PathValidationReport

# TODO: implement this using the new module interfacing scheme

#from itertools import repeat
# from user_submitted_validator import validate_user_submitted_path
from path_to_grad_parser import parse_path_to_grad
from concurrent.futures import ProcessPoolExecutor
from expert_system_module import ExpertSystem, DynamicKnowledge



def batch_validation(file_paths: list[Path], course_info_container: CourseInfoContainer) \
        -> list[Union[ExportReport, PathValidationReport]]:
    raise NotImplemented



# def batch_validation(input_files, course_info_container):
#     """Check all passed files using path to graduation parser and validator. This uses the passed course info container and schedule evaluator (expert system), and it returns a list of ValidationReport objects."""
    
#     result = []
    
#     with ProcessPoolExecutor() as executor:
#         processes = [executor.submit(_validate_file, file, course_info_container) for file in input_files]
        
#         for process in processes:
#             process_result = process.result()
#             result.append(process_result)
    
#     return result


# def _validate_file(input_file, course_info_container):
#     '''Validate a single file given the passed file path and info container. This returns the report object.'''
#     report = None
#     try:
#         schedule = parse_path_to_grad(input_file)
        
#         error_reports = validate_user_submitted_path(course_info_container, schedule)
#         dynamic_knowledge = DynamicKnowledge()
#         dynamic_knowledge.set_schedule(schedule)
#         confidence_factor = ExpertSystem().calculate_confidence(dynamic_knowledge, course_info_container)
#         report = ValidationReport(input_file, confidence_factor=confidence_factor, error_list=error_reports)
#     except (IOError, ValueError):
#         report = ValidationReport(input_file, confidence_factor=0, exception="Bad file format")
        
#     return report


# if __name__ == "__main__":
#     batch_validation([i for i in range(22)], 123)

