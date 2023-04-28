# Team Xolo
# Date: 27 April 2023
# Description: Main file for our program, runs creates and runs the smart planner controller

from program_driver import SmartPlannerController   

if __name__ == '__main__':
    with open('session_log.txt', 'w') as log_file:
            
        planner = SmartPlannerController()
        
        planner.log_file = log_file
        if planner.has_interface():
            while planner.run_top_interface(): pass
