#parses the CBR input files and Case Base

import os
from pathlib import Path

def input_folder_iter():
    path = Path(__file__).parent
    file_list_input = []
    directory = path.joinpath('CBR Inputs')
    for filename in os.listdir(directory):
        file = os.path.join(directory, filename)
        if os.path.isfile(file):
            file_list_input.append(file)
    return file_list_input

def case_base_iter():
    path = Path(__file__).parent
    file_list_case_base = []
    directory = path.joinpath('Case Base')
    for filename in os.listdir(directory):
        file = os.path.join(directory, filename)
        if os.path.isfile(file):
            file_list_case_base.append(file)
    return file_list_case_base

def get_data(file_list):
    dir_data = []
    for file in file_list:
        file_data = []
        f = open(file, "r")
        for line in f:
            #file_data = []
            if not line.isspace():
                file_data.append(line)
        #file_data.append(f.read())
        split = split_list_data(file_data)
        dir_data.append(split)
    return dir_data

def get_data_single(target_file):
    directory = Path(__file__).parent.joinpath('CBR Inputs')
    target_file = directory.joinpath(target_file)
    file_data = []
    f = open(target_file, "r")
    for line in f:
        if not line.isspace():
            file_data.append(line)
    split = split_list_data(file_data)
    return split

def split_list_data(file_data):
    new_list = []
    for i in file_data:
        element = i.rsplit('\n')[0]
        new_list.append(element)
    return new_list

def batch_input_driver():
    input_batch = input_folder_iter()
    input_data = get_data(input_batch)
    return input_data

def input_driver(target_file):
    input_case = get_data_single(target_file)
    return input_case

def case_base_driver():
    casebase = case_base_iter()
    case_data = get_data(casebase)
    return case_data

