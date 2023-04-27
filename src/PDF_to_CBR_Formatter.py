#This module takes information give by degreeworks_perserV2 and creates a text file that is easily
#read by the CBR - inputs are filename, student gpa, courses needed string

import os
from pathlib import Path
import re

def format_main(file_name, student_gpa, courses_needed_construction_string):
    elective_count = get_elective_count(courses_needed_construction_string)
    formatted_courses_needed = split_courses_needed_to_string(courses_needed_construction_string, elective_count)
    genrated_file_name = generate_file_name(file_name)
    write_to_file(genrated_file_name, student_gpa, formatted_courses_needed)

def get_elective_count(courses_needed_construction_string):
    elective_credits = None
    # print(f'courses_needed_construction_string: {courses_needed_construction_string}')
    if (match_obj := re.search(r'\d{1,2} Credits in CPSC', courses_needed_construction_string)):
        # print('if statement activated')
        elective_credits = re.match(r'\d{1,2}', match_obj.group()).group()
    #print(f'elective_credits: {elective_credits}')
    if elective_credits == None:
        elective_credits = 0
    elective_count = int(elective_credits) / 3
    return elective_count

def split_courses_needed_to_string(courses_needed_construction_string, elective_count):
    string_with_junk_removed = courses_needed_construction_string[courses_needed_construction_string.find("(")+1:courses_needed_construction_string.find(")")]
    formatted_courses_needed = string_with_junk_removed.split(',')
    while elective_count > 0:
        formatted_courses_needed.append("CPSC 3000")
        elective_count -= 1
    #print(f"formatted courses needed: {formatted_courses_needed}")
    return formatted_courses_needed

def format_student_gpa(student_gpa):
    pass

def generate_file_name(file_name):
    head_tail_tuple = os.path.split(file_name)
    new_file_name = head_tail_tuple[1]
    new_file_name.strip(".pdf")
    #new_file_name = file_name[file_name.find("updated_degreeworks/")+20:file_name.find(".")]
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
