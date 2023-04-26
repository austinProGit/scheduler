# Thomas Merino and Austin Lee
# 2/27/2023
# CPSC 4176 Project

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional


# The following are imported for type annotation
from pathlib import Path

ValidationReportResult = int
VALIDATION_REPORT_PARSED = 0x00
VALIDATION_REPORT_ERRORS = 0x01
VALIDATION_REPORT_NO_FILE = 0x02
VALIDATION_REPORT_WORKING = 0x03

class ExportReport:
    
    def __init__(self, did_succeed):
        self.did_succeed = did_succeed



class PathValidationReport:
    '''Class for representing a path to graduation validation report. This stores all errors if present,
     the path file's description (preferably printable), and the confidence factor.'''
    
    class Error:
        def __init__(self, description: str) -> None:
            self.description: str = description

        def __str__(self) -> str:
            return self.description

    def __init__(self, error_list: Optional[list[PathValidationReport.Error]] = None,
                 resultType: ValidationReportResult = VALIDATION_REPORT_WORKING,
                 file_description: Optional[Path] = None, confidence_factor: Optional[float] = None) -> None:
        self.file_description: Optional[Path] = file_description
        self.confidence_factor: Optional[float] = confidence_factor
        self.error_list: list[PathValidationReport.Error] = error_list if error_list is not None else []
        self.resultType: ValidationReportResult = resultType

    def __str__(self):
        return 'Valid' if self.is_valid() else 'Invalid'
    
    def is_valid(self) -> bool:
        '''Returns the validity (boolean) of the student's path.'''
        return self.error_list == [] and (self.resultType == VALIDATION_REPORT_PARSED or 
            self.resultType == VALIDATION_REPORT_WORKING)

    def get_errors_printable(self) -> str:
        return '\n'.join([str(error) for error in self.error_list]) if len(self.error_list) != 0 else '*No Errors*'

    