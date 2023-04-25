# Max Lewis
# 11/18/22

def high():
    return 0.5

def low():
    return 0.25

def schedule_length(schedule):
    return len(schedule)

def semester_length(semester):
    return len(semester)

def semester_type_sequence(schedule):
    SEMESTER_TYPE_SUCCESSOR = {'Fa': 'Sp', 'Sp': 'Su', 'Su': 'Fa'}
    sequence = None
    previous_season = 'Su'
    if schedule_length(schedule) > 0:
        sequence = []
        for semester in schedule:
            sequence.append(SEMESTER_TYPE_SUCCESSOR[previous_season])
            previous_season = SEMESTER_TYPE_SUCCESSOR[previous_season]
    return sequence

def first_semester_type(schedule):
    semester_types = semester_type_sequence(schedule)
    if semester_types != None:
        return semester_types[0]
    else: return None

def last_semester_type(schedule):
    semester_types = semester_type_sequence(schedule)
    if semester_types != None:
        return semester_types[-1]
    else: return None

def semester_type_of_course(schedule, course_report_obj):
    semester_type = None
    sequence = semester_type_sequence(schedule)
    for semester in range(schedule_length(schedule)):
        if course_report_obj in schedule[semester]:
            semester_type = sequence[semester]
            break
    return semester_type

def semester_position_of_course(schedule, course_report_obj):
    semester_position = None
    sequence = semester_type_sequence(schedule)
    for semester in range(schedule_length(schedule)):
        if course_report_obj in schedule[semester]:
            semester_position = semester
            break
    return semester_position

def length_of_all_semesters(schedule):
    lengths = None
    if schedule_length(schedule) > 0:
        lengths = []
        for semester in schedule:
            lengths.append(semester_length(semester))
    return lengths

def semester_length_of_course(schedule, courseID):
    length = None
    for semester in schedule:
        if courseID in semester:
            length = semester_length(semester)
            break
    return length

def empty_lists_in_schedule_count(schedule):
    count = 0
    message = ''
    for semester in range(schedule_length(schedule)):
        if schedule[semester] == []:
            count += 1
            message += 'Semester ' + str(semester + 1) + ' is empty.\n'
    return count, message

def empty_lists_in_schedule(schedule):
    found = False
    for semester in schedule:
        if semester == []:
            found = True
            break
    return found

def senior_interval(schedule):
    last_type = last_semester_type(schedule)
    if last_type == 'Su':
        return -3
    if last_type == 'Sp':
        return -2
    if last_type == 'Fa':
        return -1

def senior_year_semesters_list_of_lists(schedule):
    if schedule == None or schedule == [] or schedule == [[]]:
        return None
    senior_semesters = []
    index = senior_interval(schedule)
    for i in range(index, 0):
        senior_semesters.append(schedule[i])
    return senior_semesters

def senior_year_semesters_list(schedule):
    if schedule == None or schedule == [] or schedule == [[]]:
        return None
    senior_semesters = []
    index = senior_interval(schedule)
    for i in range(index, 0):
        for semester in schedule[i]:
            senior_semesters.append(semester)
    return senior_semesters

def senior_with_1000_level_courses(schedule):
    found = False
    senior_year = senior_year_semesters_list(schedule)
    if senior_year != None:
        for course in senior_year:
            if ' 1' in course.ID:
                found = True
                break
    return found

def senior_with_1000_level_count(schedule):
    message = ''
    count = 0
    senior_year = senior_year_semesters_list(schedule)
    if senior_year != None:
        for course in senior_year:
            if ' 1' in course.ID:
                count += 1
                message += '1000 level course ' + course.ID + ' detected in senior year.\n'
    return count, message

def senior_with_2000_level_courses(schedule):
    found = False
    senior_year = senior_year_semesters_list(schedule)
    if senior_year != None:
        for course in senior_year:
            if ' 2' in course.ID:
                found = True
                break
    return found

def senior_with_2000_level_count(schedule):
    message = ''
    count = 0
    senior_year = senior_year_semesters_list(schedule)
    if senior_year != None:
        for course in senior_year:
            if ' 2' in course.ID:
                count += 1
                message += '2000 level course ' + course.ID + ' detected in senior year.\n'
    return count, message

def junior_interval(schedule):
    last_type = last_semester_type(schedule)
    junior_schedule = schedule
    length = schedule_length(schedule)
    if last_type == 'Su' and length > 3:
        return junior_schedule[:length-3]
    if last_type == 'Sp' and length > 2:
        return junior_schedule[:length-2]
    if last_type == 'Fa' and length > 1:
        return junior_schedule[:length-1]

def junior_year_semesters_list_of_lists(schedule):
    junior_semesters = schedule
    if junior_semesters != None and schedule_length(schedule) > 0:
        junior_semesters = junior_interval(schedule)
        junior_semesters = senior_year_semesters_list_of_lists(junior_semesters)
    return junior_semesters

def junior_year_semesters_list(schedule):
    junior_semesters = schedule
    if junior_semesters != None and schedule_length(schedule) > 0:
        junior_semesters = junior_interval(schedule)
        junior_semesters = senior_year_semesters_list(junior_semesters)
    return junior_semesters

def junior_with_1000_level_courses(schedule):
    found = False
    junior_year = junior_year_semesters_list(schedule)
    if junior_year != None:
        for course in junior_year:
            if ' 1' in course.ID:
                found = True
                break
    return found

def junior_with_1000_level_count(schedule):
    message = ''
    count = 0
    junior_year = junior_year_semesters_list(schedule)
    if junior_year != None:
        for course in junior_year:
            if ' 1' in course.ID:
                count += 1
                message += '1000 level course ' + course.ID + ' detected in junior year.\n'
    return count, message

def sophmore_interval(schedule):
    last_type = last_semester_type(schedule)
    sophmore_schedule = schedule
    length = schedule_length(schedule)
    if last_type == 'Su' and length > 6:
        return sophmore_schedule[:length-6]
    if last_type == 'Sp' and length > 5:
        return sophmore_schedule[:length-5]
    if last_type == 'Fa' and length > 4:
        return sophmore_schedule[:length-4]

def sophmore_year_semesters_list_of_lists(schedule):
    sophmore_semesters = schedule
    if sophmore_semesters != None and schedule_length(schedule) > 0:
        sophmore_semesters = sophmore_interval(schedule)
        sophmore_semesters = senior_year_semesters_list_of_lists(sophmore_semesters)
    return sophmore_semesters

def sophmore_year_semesters_list(schedule):
    sophmore_semesters = schedule
    if sophmore_semesters != None and schedule_length(schedule) > 0:
        sophmore_semesters = sophmore_interval(schedule)
        sophmore_semesters = senior_year_semesters_list(sophmore_semesters)
    return sophmore_semesters

def sophmore_with_4000_level_courses(schedule):
    found = False
    sophmore_year = sophmore_year_semesters_list(schedule)
    if sophmore_year != None:
        for course in sophmore_year:
            if ' 4' in course.ID:
                found = True
                break
    return found

def sophmore_with_4000_level_count(schedule):
    count = 0
    message = ''
    sophmore_year = sophmore_year_semesters_list(schedule)
    if sophmore_year != None:
        for course in sophmore_year:
            if ' 4' in course.ID:
                count += 1
                message += '4000 level course ' + course.ID + ' detected in sophmore year.\n'
    return count, message

def freshman_interval(schedule):
    last_type = last_semester_type(schedule)
    freshman_schedule = schedule
    length = schedule_length(schedule)
    if last_type == 'Su' and length > 9:
        return freshman_schedule[:length-9]
    if last_type == 'Sp' and length > 8:
        return freshman_schedule[:length-8]
    if last_type == 'Fa' and length > 7:
        return freshman_schedule[:length-7]

def freshman_year_semesters_list_of_lists(schedule):
    freshman_semesters = schedule
    if freshman_semesters != None and schedule_length(schedule) > 0:
        freshman_semesters = freshman_interval(schedule)
        freshman_semesters = senior_year_semesters_list_of_lists(freshman_semesters)
    return freshman_semesters

def freshman_year_semesters_list(schedule):
    freshman_semesters = schedule
    if freshman_semesters != None and schedule_length(schedule) > 0:
        freshman_semesters = freshman_interval(schedule)
        freshman_semesters = senior_year_semesters_list(freshman_semesters)
    return freshman_semesters

def freshman_with_3000_level_courses(schedule):
    found = False
    freshman_year = freshman_year_semesters_list(schedule)
    if freshman_year != None:
        for course in freshman_year:
            if ' 3' in course.ID:
                found = True
                break
    return found

def freshman_with_3000_level_count(schedule):
    message = ''
    count = 0
    freshman_year = freshman_year_semesters_list(schedule)
    if freshman_year != None:
        for course in freshman_year:
            if ' 3' in course.ID:
                count += 1
                message += '3000 level course ' + course.ID + ' detected in freshman year.\n'
    return count, message

def freshman_with_4000_level_courses(schedule):
    found = False
    freshman_year = freshman_year_semesters_list(schedule)
    if freshman_year != None:
        for course in freshman_year:
            if ' 4' in course.ID:
                found = True
                break
    return found

def freshman_with_4000_level_count(schedule):
    message = ''
    count = 0
    freshman_year = freshman_year_semesters_list(schedule)
    if freshman_year != None:
        for course in freshman_year:
            if ' 4' in course.ID:
                count += 1
                message += '4000 level course ' + course.ID + ' detected in freshman year.\n'
    return count, message

# Testing ------------------------------------------------------------------------------------------------

#from driver_fs_functions import *
#from course_info_container import *
#from scheduler_driver import *

#file0 = get_source_path()
#file0 = get_source_relative_path(file0, 'input_files/Course Info.xlsx')
#dfdict = load_course_info(file0)
#container = CourseInfoContainer(dfdict)

#course_identifier_MATH_1113 = DummyCourseIdentifier(course_number="MATH 1113")
#course_identifier_STAT_3127 = DummyCourseIdentifier(course_number="STAT 3127")
#course_identifier_CPSC_2108 = DummyCourseIdentifier(course_number="CPSC 2108")
#course_identifier_CPSC_3125 = DummyCourseIdentifier(course_number="CPSC 3125")
#course_identifier_CPSC_XXXX = DummyCourseIdentifier(course_number="CPSC XXXX", name="Elective", is_stub=True)
#course_identifier_CPSC_3XX = DummyCourseIdentifier(course_number="CPSC 3@X", name="Elective", is_stub=True)

#cr5 = container.get_course_record(course_identifier_MATH_1113)
#cr6 = container.get_course_record(course_identifier_STAT_3127)
#cr7 = container.get_course_record(course_identifier_CPSC_2108)
#cr8 = container.get_course_record(course_identifier_CPSC_3125)
#crX = container.get_course_record(course_identifier_CPSC_XXXX)
#crY = container.get_course_record(course_identifier_CPSC_3XX)

#course_obj_list =[[crX], [crY], [cr5, cr6, cr7, cr8], 
#                  [crX], [crY], [cr5, cr6, cr7, cr8], 
#                  [crX], [crY], [cr5, cr6, cr7, cr8], 
#                  [crX], [crY], [cr5, cr6, cr7, cr8]]

#print(senior_year_semesters_list_of_lists(course_obj_list))
#print(senior_with_1000_level_courses(course_obj_list))
#print(senior_with_2000_level_courses(course_obj_list))
#print(junior_year_semesters_list_of_lists(course_obj_list))
#print(junior_with_1000_level_courses(course_obj_list))
#print(sophmore_year_semesters_list_of_lists(course_obj_list))
#print(sophmore_with_4000_level_courses(course_obj_list))
#print(freshman_year_semesters_list_of_lists(course_obj_list), '\n')
#print(freshman_with_3000_level_courses(course_obj_list))
#print(freshman_with_4000_level_courses(course_obj_list))
