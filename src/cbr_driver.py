#cbr main driver. main menu is unused while the cbr is integrated to the rest of smart planner

import output_fetch
import results_analysis
import os
import adaptation
from pathlib import Path

def cbr_main_menu():
    print("Welcome to SmartPlanner CBR")
    print("This program outputs recommended electives based on degreeworks input")
    selected_file = "degreeworks6.txt"
    quit_program = False
    case_retrieved = False
    path = Path(__file__).parent
    while quit_program == False:
        user_input = input("Enter your selection: ")
        if user_input == "1":
            print("Please select input...")
            directory = path.joinpath('Inputs')
            valid_files = []
            bad_input = True
            for filename in os.listdir(directory):
                file = os.path.join(directory, filename)
                if os.path.isfile(file):
                    print(filename)
                    valid_files.append(filename)
            while bad_input == True:
                input_file_name = input("Which file would you like to select? ")
                if input_file_name in valid_files:
                    print("You've selected a valid file: ", input_file_name)
                    bad_input = False
                    selected_file = input_file_name
                    continue_button = input("Please press any key to continue...")
                else:
                    print("Please enter a valid file name: ")
        if user_input == "2":
            cbr_result = output_fetch.output_driver(selected_file)
            adaptation.adaptation_main(cbr_result)
            print('Recommendation for electives: ')
            for each in cbr_result.get_recommended_electives():
                print(each)
            case_retrieved = True
            continue_button = input("Please press any key to continue...")
        if user_input == "3":
            if case_retrieved == False:
                print("Please make a selection before selecting this option")
            elif case_retrieved == True:
                print("Here is the reason...")
                results_analysis.results_driver(selected_file)
                continue_button = input("Please press any key to continue...")
        if user_input == "4":
            quit_program = True
        else:
            pass


def run_cbr_option(selected_file):
    cbr_result = output_fetch.output_driver(selected_file)
    return cbr_result

def give_cbr_reason(selected_file):
    results_analysis.results_driver(selected_file)
