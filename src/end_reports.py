# Thomas Merino and Austin Lee
# 2/27/2023
# CPSC 4176 Project


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
            self.description = description

        def __str__(self) -> str:
            return self.description

    def __init__(self, file_description: Path, confidence_factor: float, error_list: "list[PathValidationReport.Error]" = [],
                 resultType: ValidationReportResult = VALIDATION_REPORT_PARSED) -> None:
        self.file_description: Path = file_description
        self.confidence_factor: float = confidence_factor
        self.error_list: list[PathValidationReport.Error] = error_list
        self.resultType: ValidationReportResult = resultType

    def is_valid(self) -> bool:
        '''Returns the validity (boolean) of the student's path.'''
        return self.error_list == [] and self.resultType == VALIDATION_REPORT_PARSED
    

    