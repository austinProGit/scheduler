#This module takes information give by degreeworks_perserV2 and creates a text file that is easily
#read by the CBR - inputs are filename, student gpa, courses needed string

import os
from pathlib import Path

def format_main(file_name, student_gpa, courses_needed_construction_string):
    
    formatted_courses_needed = split_courses_needed_to_string(courses_needed_construction_string)
    genrated_file_name = generate_file_name(file_name)
    write_to_file(genrated_file_name, student_gpa, formatted_courses_needed)

def split_courses_needed_to_string(courses_needed_construction_string):
    string_with_junk_removed = courses_needed_construction_string[courses_needed_construction_string.find("(")+1:courses_needed_construction_string.find(")")]
    formatted_courses_needed = string_with_junk_removed.split(',')
    return formatted_courses_needed

def format_student_gpa(student_gpa):
    pass

def generate_file_name(file_name):
    new_file_name = file_name[file_name.find("updated_degreeworks/")+20:file_name.find(".")]
    return new_file_name

def write_to_file(generated_file_name, student_gpa, formatted_courses_needed):
    text_file_name = generated_file_name + ".txt"
    path = Path(__file__).parent
    directory = Path(__file__).parent.joinpath('CBR Inputs')
    target_file_path = directory.joinpath(text_file_name)
    if os.path.exists(target_file_path):
        return
    else:
        f = open(target_file_path, "w")
        f.write(generated_file_name)
        f.write("\n")
        f.write("\n")
        f.write("GPA: ")
        f.write(student_gpa)
        f.write("\n")
        f.write("\n")
        for course in formatted_courses_needed:
            f.write(course)
            f.write("\n")
        f.close
