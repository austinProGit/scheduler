# Max Lewis 09/20/22
# CPSC 4175 Project

import openpyxl
import shutil
# MERINO: commented this out
# from course_info_container import *
from datetime import date

def excel_formatter(input_path, output_file_name, sched, container):  # first param is source file path
    num = 0
    input_file_name = input_path + '/Path To Graduation Y.xlsx'
    for lst in sched:
        if len(lst) > 6:
            input_file_name = input_path + '/Path To Graduation Z.xlsx'
            num = 4
            break

    shutil.copy2(input_file_name, output_file_name) # Copy file
    edit_excel = openpyxl.load_workbook(output_file_name)
    sheet = edit_excel.active
    format(sheet, sched, container, num)
    edit_excel.save(output_file_name) # Save the file so we can copy to specified directory
 
# ...............HELPER METHODS...............HELPER METHODS...............HELPER METHODS...............HELPER METHODS
    
def format(sheet, sched, container, num):
    current_seas = current_season() # Determined by actual date; depicts the next semester to schedule
    for i in range(len(sched)):
        if(i > 0): # Skip 1st iteration before we change semester to next
            current_seas = next_season(current_seas, num)
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
            else: # course not in container or class info
                course1 = sched[i][x]
                co1 = current_seas[0]
                ro1 = current_seas[1] + x
                c1 = current_seas[0] + 1
                r1 = current_seas[1] + x
                data1 = course1 + ' - Name Unavailable (?? ?? ??)'
                sheet.cell(row=ro1, column=co1, value=data1)
                sheet.cell(row=r1, column=c1, value=3)

def current_season():
    start =[]
    month = date.today().month
    if month >= 1 and month <= 5: start = [5, 4] # [column, row] Summer table
    if month >= 6 and month <= 7: start = [1, 4] # [column, row] Fall table
    if month >= 8 and month <= 12: start = [3, 4] # [column, row] Spring table
    return start

def next_season(current_season, num):
    next_season = []
    if current_season[0] == 5:
        next_row = current_season[1] + 8 + num
        next_season = [1, next_row]
    if current_season[0] == 1:
        next_season = [3, current_season[1]]
    if current_season[0] == 3:
        next_season = [5, current_season[1]]
    return next_season

# ...............END OF HELPER METHODS...............END OF HELPER METHODS...............END OF HELPER METHODS

# ***************END OF EXCEL_FORMATTER MODULE***************END OF EXCEL_FORMATTER MODULE********************
#Internal testing below
#container = CourseInfoContainer(load_course_info('scheduler/src/input_files/Course Info.xlsx'))
#rando_list = [['CPSC 3121', 'CPSC 3165', 'CPSC 4000', 'CPSC 4135', 'POLS 1101', 'MATH 1113'],
#              ['STAT 3127', 'CPSC 2108'], ['CPSC 3125', 'MATH 1113']]

#excel_formatter('scheduler/src/input_files', 'C:/Users/mel91/Desktop/output_files/Path.xlsx', rando_list, container)
#"C:\Users\mel91\Desktop\output_files"