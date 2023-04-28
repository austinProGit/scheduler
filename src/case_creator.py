#creates Case objects from parsed data obtained form cbr_parser

import Case
import cbr_parser
from pathlib import Path
import os

def fetch_case_base_data():
    case_base_cases = cbr_parser.case_base_driver()
    return case_base_cases

def fetch_batch_input_data():
    input_cases = cbr_parser.batch_input_driver()
    return input_cases

def print_cases(case_list):
    print(case_list)

def create_case_objects(case_base_cases):
    case_base_object_list = []
    for case in case_base_cases:
        courses = []
        for element in case:
            filename = case[0]
            gpa = case[1]
            courses.append(element)
            type = "case_base"
        new_case = Case.Case(filename, gpa, courses, type)
        case_base_object_list.append(new_case)
    return case_base_object_list

def create_input_objects(input_cases):
    input_object_list = []
    for case in input_cases:
        courses = []
        for element in case:
            filename = case[0]
            gpa = case[1]
            courses.append(element)
            type = "input"
        new_case = Case.Case(filename, gpa, courses, type)
    input_object_list.append(new_case)
    return input_object_list

def create_single_input_object(input_case):
    courses = []
    for element in input_case:
            filename = input_case[0]
            gpa = input_case[1]
            courses.append(element)
            type = "input"
    new_case = Case.Case(filename, gpa, courses, type)
    return new_case

def get_case_object_gpa(case_object_list):
    for case in case_object_list:
        print(case.get_gpa())

def get_case_object_file_names(case_object_list):
    for case in case_object_list:
        print(case.get_file_name())

def get_case_object_courses(case_object_list):
    for case in case_object_list:
        return case.get_course_list()

def get_case_object_type(case_object_list):
    for case in case_object_list:
        return case.get_type()

def print_case_objects(case_base_object_list):
    print(case_base_object_list)

def print_input_objects(input_object_list):
    print(input_object_list)

def case_base_object_driver():
    case_base_cases = fetch_case_base_data()
    case_object_list = create_case_objects(case_base_cases)
    return case_object_list

def input_object_driver():
    input_cases = fetch_batch_input_data()
    input_object_list = create_input_objects(input_cases)
    return input_object_list

def single_input_object_driver(selected_file):
    path = Path(__file__).parent
    directory = path.joinpath('CBR Inputs')
    for filename in os.listdir(directory):
        file = os.path.join(directory, filename)
        if file == selected_file:
            continue
    input_case = cbr_parser.input_driver(selected_file)
    return input_case

