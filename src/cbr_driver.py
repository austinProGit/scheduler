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
    print_options()
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
                    print_options()
                else:
                    print("Please enter a valid file name: ")
        if user_input == "2":
            cbr_result = output_fetch.output_driver(selected_file)
            #new code below
            adaptation.adaptation_main(cbr_result)
            #end new code
            print('Recommendation for electives: ')
            for each in cbr_result.get_recommended_electives():
                print(each)
            case_retrieved = True
            continue_button = input("Please press any key to continue...")
            print_options()
        if user_input == "3":
            if case_retrieved == False:
                print("Please make a selection before selecting this option")
            elif case_retrieved == True:
                print("Here is the reason...")
                results_analysis.results_driver(selected_file)
                continue_button = input("Please press any key to continue...")
                print_options()
        if user_input == "4":
            quit_program = True
        else:
            pass


def run_cbr_option(selected_file):
    cbr_result = output_fetch.output_driver(selected_file)
    #adaptation.adaptation_main(cbr_result)
    #print('Recommendation for electives: ')
    #for each in cbr_result.get_recommended_electives():
    #    print(each)
    return cbr_result

def give_cbr_reason(selected_file):
    #print("Here is the reason...")
    results_analysis.results_driver(selected_file)

def print_options():
    #print("Please select an option")
    #print("1. Choose input file")
    #print("2. Run CBR")
    #print("3. Give reasoning for elective selections")
    #print("4. Quit")
    pass
