# Team Xolo
# Date: 31 August 2022
# Description: Main file for our program, runs creates and runs the smart planner controller

from program_driver import SmartPlannerController   

if __name__ == '__main__':
    planner = SmartPlannerController()
    
    if planner.has_interface():
        while planner.run_top_interface(): pass
