# Max Lewis 09/20/22
# CPSC 4175 Project

import openpyxl
import shutil
# MERINO: commented this out
#from course_info_container import container
from datetime import date

def excel_formatter(input_file_name, output_file_name, sched, container):  # second param needs to be destination path for copy
    edit_excel = openpyxl.load_workbook(input_file_name)
    sheet = edit_excel.active
    previous_seas = False # Use this boolean as an easy way to skip 1st iteration of outside loop
    current_seas = current_season() # Determined by actual date; depicts the next semester to schedule
    clear_contents(sheet)

    for i in range(len(sched)):
        if(previous_seas): # Skip 1st iteration before we change semester to next
            current_seas = next_season(current_seas)
        for x in range(len(sched[i])):
            if container.validate_course(sched[i][x]): # Use container to get values
                course = sched[i][x]
                avail = container.get_availability(course)
                if avail != []:
                    data = course + ' - ' + container.get_name(course) + ' (' + avail[0] + ' ' + avail[1] + ' ' + avail[2] + ')'
                else:
                    data = course + ' - ' + container.get_name(course) + ' (?? ?? ??)'
                hours = container.get_hours(course)
                co = current_seas[0]
                ro = current_seas[1] + x
                c = current_seas[0] + 1
                r = current_seas[1] + x
                sheet.cell(row=ro, column=co, value=data)
                sheet.cell(row=r, column=c, value=hours)
                previous_seas = True
            else: # course not in container or class info
                course1 = sched[i][x]
                co1 = current_seas[0]
                ro1 = current_seas[1] + x
                c1 = current_seas[0] + 1
                r1 = current_seas[1] + x
                data1 = course1 + ' - Name Unavailable (?? ?? ??)'
                sheet.cell(row=ro1, column=co1, value=data1)
                sheet.cell(row=r1, column=c1, value=3)
                previous_seas = True

    edit_excel.save(input_file_name) # Save the file so we can copy to specified directory
    
    shutil.copy2(input_file_name, output_file_name) # Copy file

    clear_contents(sheet) # Clearing the input file; ready for next student schedule

    edit_excel.save(input_file_name) # Save the cleared file

# ...............HELPER METHODS...............HELPER METHODS...............HELPER METHODS...............HELPER METHODS
    
def clear_contents(sheet):
    minR, maxC, maxR = 4, 6, 10
    minRo, maxCo, maxRo, minCo = 4, 6, 10, 5
    
    for i in range(6):# clear all but sub headers
        for col in sheet.iter_cols(min_row = minR, max_col = maxC, max_row = maxR):# clear Fall and Spring cells
            for cell in col:
                cell.value = None
        minR = minR + 9
        maxR = maxR + 9
        for col in sheet.iter_cols(min_row = minRo, max_col = maxCo, max_row = maxRo, min_col = minCo):# clear Summer cells
            for cell in col:
                cell.value = None
        minRo = minRo + 9
        maxRo = maxRo + 9

def current_season():
    start =[]
    month = date.today().month
    if month >= 1 and month <= 5: start = [5, 4] # [column, row] Summer table
    if month >= 6 and month <= 7: start = [1, 4] # [column, row] Fall table
    if month >= 8 and month <= 12: start = [3, 4] # [column, row] Spring table
    return start

def next_season(current_season):
    next_season = []
    if current_season[0] == 5:
        next_row = current_season[1] + 9
        next_season = [1, next_row]
    if current_season[0] == 1:
        next_season = [3, current_season[1]]
    if current_season[0] == 3:
        next_season = [5, current_season[1]]
    return next_season

# ...............END OF HELPER METHODS...............END OF HELPER METHODS...............END OF HELPER METHODS

# ***************END OF EXCEL_FORMATTER MODULE***************END OF EXCEL_FORMATTER MODULE********************

# list below is not in scheduler order; it is just random list; including generic classes and classes not listed
# in container; the limits are 6 max course per Fall or Spring, 2 max for Summer

# MERINO: commented this out
#rando_list = [['CPSC 3121', 'CPSC 3165', 'CPSC 4000', 'CPSC 4135', 'POLS 1101'],
#              ['STAT 3127', 'CPSC 2108'], ['CPSC 3125', 'MATH 1113']]
#
#excel_formatter('src\input_files\Path To Graduation X.xlsx', 'src\output_files', rando_list, container)
