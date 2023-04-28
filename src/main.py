# Team Xolo
# Date: 27 April 2022
# Description: Main file for our program, runs creates and runs the smart planner controller

from program_driver import SmartPlannerController   

if __name__ == '__main__':
    
    planner = SmartPlannerController()
    
    if planner.has_interface():
        while planner.run_top_interface(): pass

    # Close the log file if is still open
    if planner.log_file is not None:
        try:
            planner.log_file.close()
            
        except Exception as e:
            print(e)
