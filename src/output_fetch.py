#module fetches output matched to most similar pair found in similarity_measure
#expected data type inputting into this module is [target(case object), source(case object), global_similarity(int)]

import similarity_measure
import cbr_parser
import Result
import os
from pathlib import Path

def get_similar_pair(selected_file):
    similar_pair = similarity_measure.sim_measure_main(selected_file)
    return similar_pair

def get_solutions():
    path = Path(__file__).parent
    solution_data = cbr_parser.get_data_single(path.joinpath('solutions.txt'))
    return solution_data

def format_object_data_for_parsing(similar_pair):
    formatted_pair = [similar_pair[0].get_file_name(), similar_pair[1].get_file_name(), similar_pair[2]]
    return formatted_pair

def parse_solutions_for_output(formatted_pair, solution_data):
    substring = formatted_pair[1]
    index = 0
    for line in solution_data:
        split_string = line.split()
        if substring == split_string[3]:
            #printed line looks like 'Recommendedation for electives: CPSC 3555, CPSC 4125 Practicum, etc 
            elective_line = solution_data[index +1]
            stripped_line = elective_line.lstrip("Recommendedation for electives: ")
            elective_list = stripped_line.split(", ")
            #print(solution_data[index +1])
            return elective_list
        index += 1

def output_driver(selected_file):
    similar_pair = get_similar_pair(selected_file)
    formatted_pair = format_object_data_for_parsing(similar_pair)
    solution_data = get_solutions()
    elective_list = parse_solutions_for_output(formatted_pair, solution_data)
    cbr_result = Result.Result(similar_pair[0], similar_pair[1], elective_list, similar_pair[2])
    return cbr_result

####################################################################################
#output_driver()
#print(Path(__file__).parent)
