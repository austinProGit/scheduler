# Max Lewis 09/20/22
# CPSC 4175 Project

import openpyxl
import shutil
from datetime import date
from driver_fs_functions import *


def excel_formatter(input_path, output_file_name, sched):  # first param is source file path
    num = 0
    input_file_name = get_source_relative_path(input_path, 'Path To Graduation Y.xlsx')
    for lst in sched:
        if len(lst) > 6:
            input_file_name = get_source_relative_path(input_path, 'Path To Graduation Z.xlsx')
            num = 4
            break

    shutil.copy2(input_file_name, output_file_name) # Copy file
    edit_excel = openpyxl.load_workbook(output_file_name)
    sheet = edit_excel.active
    format(sheet, sched, num)
    edit_excel.save(output_file_name) # Save the file so we can copy to specified directory
 
# ...............HELPER METHODS...............HELPER METHODS...............HELPER METHODS...............HELPER METHODS
    
def format(sheet, sched, num):
    current_seas = [1, 4] # We can switch to actual date reference by using current_season()
    for i in range(len(sched)):
        if(i > 0): # Skip 1st iteration before we change semester to next
            current_seas = next_season(current_seas, num)
        for x in range(len(sched[i])):
            course = sched[i][x]
            data = f"{course.ID} - {course.name} ({course.avail[0]} {course.avail[1]} {course.avail[2]})"
            co = current_seas[0]
            ro = current_seas[1] + x
            c = current_seas[0] + 1
            r = current_seas[1] + x
            sheet.cell(row=ro, column=co, value=data)
            sheet.cell(row=r, column=c, value=course.hours)


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

#from driver_fs_functions import *
#from course_info_container import *
#from scheduler_driver import *

#file0 = get_source_path()
#file0 = get_source_relative_path(file0, 'input_files/Course Info.xlsx')
#dfdict = load_course_info(file0)
#container = CourseInfoContainer(dfdict)

#course_identifier_CPSC_3121 = DummyCourseIdentifier(course_number="CPSC 3121")
#course_identifier_CPSC_3165 = DummyCourseIdentifier(course_number="CPSC 3165")
#course_identifier_CPSC_4000 = DummyCourseIdentifier(course_number="CPSC 4000")
#course_identifier_CPSC_4135 = DummyCourseIdentifier(course_number="CPSC 4135")
#course_identifier_MATH_1113 = DummyCourseIdentifier(course_number="MATH 1113")
#course_identifier_STAT_3127 = DummyCourseIdentifier(course_number="STAT 3127")
#course_identifier_CPSC_2108 = DummyCourseIdentifier(course_number="CPSC 2108")
#course_identifier_CPSC_3125 = DummyCourseIdentifier(course_number="CPSC 3125")
#course_identifier_CPSC_XXXX = DummyCourseIdentifier(course_number="CPSC XXXX", name="Elective", is_stub=True)
#course_identifier_CPSC_3XX = DummyCourseIdentifier(course_number="CPSC 3@X", name="Elective", is_stub=True)

#cr1 = container.get_course_record(course_identifier_CPSC_3121)
#cr2 = container.get_course_record(course_identifier_CPSC_3165)
#cr3 = container.get_course_record(course_identifier_CPSC_4000)
#cr4 = container.get_course_record(course_identifier_CPSC_4135)
#cr5 = container.get_course_record(course_identifier_MATH_1113)
#cr6 = container.get_course_record(course_identifier_STAT_3127)
#cr7 = container.get_course_record(course_identifier_CPSC_2108)
#cr8 = container.get_course_record(course_identifier_CPSC_3125)
#crX = container.get_course_record(course_identifier_CPSC_XXXX)
#crY = container.get_course_record(course_identifier_CPSC_3XX)

#course_obj_list =[[cr1, cr2, crX], [cr3, cr4, crY], [cr5, cr6, cr7, cr8]]

#template_path = Path(get_source_path(), 'input_files')
#excel_formatter(template_path, 'C:/Users/mel91/Desktop/output_files/Path.xlsx', course_obj_list)