#insert result gained from adaptation module into case base, solution text file
#reminder: Result object contains (target_case_object, retrieved_case_object, recommended_electives[], similarity measure)

from pathlib import Path
import shutil

def insert_into_case_base_solution(result):
    target_case = result.get_target_case()
    target_case_file_name = target_case.get_file_name()
    new_case_name = target_case_file_name.lstrip(".txt")
    elective_list = result.get_recommended_electives()
    print(elective_list)
    formatted_elective_list = ", ".join(elective_list)
    first_line_string = "Solution for Case " + new_case_name
    second_line_string = "Recommendation for electives: " + formatted_elective_list
    path = Path(__file__).parent
    solutions_file = open(path.joinpath('solutions.txt'), "a")
    solutions_file.write("\n")
    solutions_file.write(first_line_string)
    solutions_file.write("\n")
    solutions_file.write(second_line_string)
    solutions_file.write("\n")
    solutions_file.write("\n")

def insert_into_case_base_problem(result):
    path = path = Path(__file__).parent
    input_directory = path.joinpath('CBR Inputs')
    case_base_directory = path.joinpath('Case Base')
    target_case = result.get_target_case()
    target_case_file_name = target_case.get_file_name() + ".txt"
    copy_source_string =  input_directory.joinpath(target_case_file_name)
    copy_destination_string = case_base_directory.joinpath(target_case_file_name)
    shutil.copy(copy_source_string, copy_destination_string)
