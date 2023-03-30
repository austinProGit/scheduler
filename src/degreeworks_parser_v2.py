# Austin Lee 3/30/2023
# CPSC 4176 Project

from degree_extraction_container import DegreeExtractionContainer

import re
from pypdf import PdfReader

# Hard coded major and track information
unprocessed_majors_string = '''
Accounting (BBA)
Art (BA)
Art (BFA)
Art Education (BSEd)
Art History (BA)
Biology (BA)
Biology (BA) - Secondary Education Track
Biology (BS)
Biology (BS) - Secondary Education Track
Chemistry (BA) - Biochemistry Track
Chemistry (BA) - Chemistry and Secondary Education Track
Chemistry (BS)
Chemistry (BS) - ACS Certified Track
Chemistry (BS) - Forensic Track
Communication (BA) - Communication Studies Track
Communication (BA) - Film Production Track
Communication (BA) - Integrated Media Track
Communication (BA) - Public Relations Track
Computer Science (BS) - Education Track
Computer Science (BS) - Games Programming Track
Computer Science (BS) - Software Systems Track
Computer Science (BS) - Web Development Track
Criminal Justice (BS)
Cybersecurity (BS)
Earth and Space Science (BS) - Astrophysics and Planetary Geology Track
Earth and Space Science (BS) - Environmental Science Track
Earth and Space Science (BS) - Geology Track
Earth and Space Science (BS) - Secondary Education Track
Elementary Education (BSEd)
English (BA) - Creative Writing Concentration
English (BA) - Literature Concentration
English (BA) - Professional Writing Concentration
English (BA) - Secondary Education Concentration
Finance (BBA)
General Business (BBA)
General Business (BBA) - International Business Track
Health Science (BS)
History (BA)
History (BA) - Secondary Education Track
Information Technology (BSIT)
Information Technology (online) (BSIT)
Interdisciplinary Studies (BS)
Kinesiology (BS) - Exercise Science Concentration
Kinesiology (BS) - Health & Physical Education Non-Certification Concentration
Kinesiology (BS) - Health & Physical Education Teacher Certification Concentration
Management (BBA)
Management (BBA) - Entrepreneurship Concentration
Management (BBA) - Human Resource Concentration
Management Information Systems (BBA)
Management Information Systems (BBA) - Business Analytics Concentration 
Management Information Systems (BBA) - Cybersecurity Management Concentration
Management Information Systems - Online (BBA)
Marketing (BBA)
Mathematics (BS)
Mathematics (BS) - Applied Mathematics Concentration
Mathematics (BS) - Applied Mathematics Sciences
Mathematics (BS) - Secondary Education Concentration
Modern Language and Culture (BA) - Spanish Literature and Culture Track
Modern Language and Culture (BA) - Spanish with Teacher Certification Track
Music (BA)
Music Education (BM) - Choral Concentration
Music Education (BM) - Instrumental Concentration
Music Performance (BM) - Instrumental Concentration
Music Performance (BM) - Piano/Organ Concentration
Music Performance (BM) - Vocal Concentration
Nursing (BSN)
Nursing RN-to-BSN (BSN)
Political Science (BS)
Psychology (BS)
Robotics Engineering (BS)
Sociology (BS) - Crime, Deviance, and Society Track
Sociology (BS) - General Track
Sociology (BS) - Social Services Track
Special Education (BSEd) - General Curriculum - Reading Concentration
Theatre (BA)
Theatre (BFA) - Performance Track
Theatre (BFA) - Theatre Design & Technology Track
Theatre Education (BSEd) - Certification Track
Theatre Education (BSEd) - Non-Certification Track
'''

# Student information helper functions
# ========================================================================================================

# Takes a string containing semi-structured major information and returns a dictionary of structured major/track information
def get_majors_and_tracks(unprocessed_majors_string):
    majors_dict = {}
    unfiltered_majors_list = unprocessed_majors_string.strip().split('\n')
    filtered_majors_list = []
    
    for item in unfiltered_majors_list:
        degree_type_search_obj = None
        degree_type_search_obj = re.search(r'\([a-zA-Z]+\)', item)
        if degree_type_search_obj:
            item = item.replace(degree_type_search_obj.group(), '')
        filtered_majors_list.append(item)
    
    for item in filtered_majors_list:
        if ' - ' in item:
            key, value = item.split(' - ', 1)
            key = key[:key.find(' (')]
            if key in majors_dict:
                if value not in majors_dict[key]:
                    majors_dict[key].append(value)
            else:
                majors_dict[key] = [value]
        else:
            key = item.strip()
            value = 'NONE'
            if key in majors_dict:
                if value not in majors_dict[key]:
                    majors_dict[key].insert(0, value)
            else:
                majors_dict[key] = [value]

    return majors_dict

# Gets a student's name from the Degreeworks document.
def get_student_name(document_string):
    student_name = None
    working_string = document_string[document_string.find('Ellucian University ') + len('Ellucian University '):document_string.find('Student name')]
    student_name_match_obj = re.search(r'[a-zA-Z]+, [a-zA-Z]+ - ', working_string)
    if student_name_match_obj:
        student_name = student_name_match_obj.group()[:student_name_match_obj.group().find(' - ')]
    return student_name

# Gets a student's student number (CSU student ID) from a Degreeworks document
def get_student_number(document_string):
    student_number = None
    working_string = document_string[document_string.find('Ellucian University ') + len('Ellucian University '):document_string.find('Student name')]
    student_number_match_obj = re.search(r'\d{9}', working_string)
    if student_number_match_obj:
        student_number = student_number_match_obj.group()
    # print(working_string)
    return student_number

# Gets a student's degree plan from a Degreeworks document
def get_degree_plan_name(document_string):
    degree_plan_name = ''
    raw_major = None
    aliased_major = None

    raw_track = None
    aliased_track = None

    working_string_match_obj = re.search(r'(?:Majors?)(.*?)(?:(?:Minors?|Program))', document_string)      
      
    if working_string_match_obj:
        working_string = working_string_match_obj.group(1).strip()
        # print(f'working_string: {working_string}')
    majors_raw_strings_list = []
    majors_dict = get_majors_and_tracks(unprocessed_majors_string)
    major_dict = {}
    if ',' in working_string:
        majors_raw_strings_list = working_string.split(',')
    else:
        majors_raw_strings_list.append(working_string)
    for i, major in enumerate(majors_raw_strings_list):
        if ' - ' in major:
            raw_major = major[:major.find(' - ')].strip()
            raw_track = major[major.find(' - ') + len(' - '):].strip()
        else:
            raw_major = major
            raw_track = 'NONE'
        for key in majors_dict.keys():
            if raw_major in key:
                aliased_major = raw_major
                major_dict = {key: majors_dict[key]}
                break
        for key, value in major_dict.items():
            for string in value:
                if string.find(raw_track) != -1:
                    aliased_track = string
                else:
                    aliased_track = raw_track
        degree_plan_name += aliased_major + ' - ' + aliased_track
        if i < len(majors_raw_strings_list) - 1:
            degree_plan_name += ', '

    # print(degree_plan_name)
    return degree_plan_name

# Current/taken courses helper functions
# ========================================================================================================

def find_curr_taken_courses(document_string):
    taken_course_year_pairing = set() # The format of this is '{course} - {year}'
    season_year_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'(Spring|Fall|Summer)\s(Term|Semester)\s\d{4}', document_string)]))
    course_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'[A-Z]{4} \d{4}[A-Z]?|[A-Z]{4} \d{1}\*\*\*', document_string)]))
    print(course_block_indices_list)
    for course_block_indeces_instance in course_block_indices_list:
        print(document_string[course_block_indeces_instance[0]:course_block_indeces_instance[1]])
    # number_of_course_blocks = len(course_block_indices_list)
    # curr_taken_courses = []
    # working_course_index = 0
    # for season_year_block_start_index, season_year_block_end_index in season_year_block_indices_list:
    #     course_range = course_block_indices_list[working_course_index]
    #     while course_range[0] > season_year_block_start_index and working_course_index < number_of_course_blocks:
    #         working_course_index += 1
    #         course_range = course_block_indices_list[working_course_index]
    #     if working_course_index < number_of_course_blocks:
    #         course_number = string[course_range[0]:course_range[1]].strip()
    #         semester_year = string[season_year_block_start_index:season_year_block_end_index].strip()
    #         course_year_pairing = f'{course_number} - {semester_year}'
    #         if course_year_pairing not in taken_course_year_pairing:
    #             curr_taken_courses.append(course_number)
    #             taken_course_year_pairing.add(course_year_pairing)
        
    # return curr_taken_courses

def generate_degree_extraction_container(file_name):
    with open(file_name, 'rb') as degreeworks_pdf:
        pdf_reader = PdfReader(degreeworks_pdf)
        courses_needed_constuction_string = ''
        document_string = ''
        degree_plan_name = None
        student_number = None
        student_name = None
        curr_taken_courses = []
        still_needed_chunks_list = []
        for page in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page].extract_text()
            document_string += page_text
        print(document_string)
        student_name = get_student_name(document_string)
        student_number = get_student_number(document_string)
        degree_plan_name = get_degree_plan_name(document_string)
        curr_taken_courses = find_curr_taken_courses(document_string[:document_string.find('Fallthrough Courses')])

    return DegreeExtractionContainer(curr_taken_courses, courses_needed_constuction_string, degree_plan_name, student_number, student_name)


if __name__ == '__main__':
    container = generate_degree_extraction_container('./input_files/updated_degreeworks/S7.pdf')
    # print(container._taken_courses)
    # print(container._courses_needed_constuction_string)
    # print(f'degree plan: {container._degree_plan_name}')
    # print(f'student name: {container._student_name}')
    # print(f'student number: {container._student_number}')
    # print(get_majors_and_tracks(unprocessed_majors_string))
