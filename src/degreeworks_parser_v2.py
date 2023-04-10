# Austin Lee 3/30/2023
# CPSC 4176 Project

from degree_extraction_container import DegreeExtractionContainer

import re
from pypdf import PdfReader

# ========================================================================================================
# TODO: integrate the web parser
# TODO: complete test cases for all example inputs
# TODO: implement custom error handling
# TODO: code review with regex focus
# TODO: create error report for the user
# TODO: code cleanup/documentation
# TODO: add GPA to container for the CBR
# TODO: add exceptions to the parser

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
# TODO: account for the case of no spaces around the hyphen
def get_degree_plan_name(document_string):
    degree_plan_name = ''
    raw_major = None
    aliased_major = None

    raw_track = None
    aliased_track = None

    working_string_match_obj = re.search(r'(?:Majors?)(.*?)(?:(?:Minors?|Program))', document_string)      
      
    if working_string_match_obj:
        working_string = working_string_match_obj.group(1).strip()
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

def trim_document_string(document_string):

    key_phrases = [
        'Fall Through',
        'Insufficient',
        'In-progress',
        'Over The Limit',
        'Split Credits',
        'Exceptions',
        'Notes'
    ]

    search_pattern = r'|'.join(re.escape(key_phrase) for key_phrase in key_phrases)
    match_obj = re.search(search_pattern, document_string)

    if match_obj:
        document_string = document_string[:match_obj.start()]

    return document_string

def find_curr_taken_courses(document_string):
    taken_course_year_pairing = set() # The format of this is '{course} - {year}'
    document_string = trim_document_string(document_string)
    season_year_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'(Spring|Fall|Summer)\s(Term|Semester)\s\d{4}', document_string)]))
    course_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'([A-Z\*]{4} [0-9\*]{4}[A-Z]?)|([A-Z\*]{3} [0-9\*]{4})', document_string)]))
    number_of_course_blocks = len(course_block_indices_list)
    curr_taken_courses = []
    working_course_index = 0
    for season_year_block_start_index, season_year_block_end_index in season_year_block_indices_list:
        course_range = course_block_indices_list[working_course_index]
        while course_range[0] > season_year_block_start_index and working_course_index < number_of_course_blocks:
            working_course_index += 1
            course_range = course_block_indices_list[working_course_index]
        if working_course_index < number_of_course_blocks:
            course_number = document_string[course_range[0]:course_range[1]].strip()
            semester_year = document_string[season_year_block_start_index:season_year_block_end_index].strip()
            course_year_pairing = f'{course_number} - {semester_year}'
            if course_year_pairing not in taken_course_year_pairing:
                curr_taken_courses.append(course_number)
                taken_course_year_pairing.add(course_year_pairing)
    return curr_taken_courses

# Courses needed constuction string functions
# ========================================================================================================

def find_index_of_first_ending_trim_phrase(document_string):
    first_ending_trim_phrase_index = -1
    key_phrases = [
        'Fall Through',
        'Insufficient',
        'In-progress',
        'Over The Limit',
        'Split Credits',
        'Exceptions',
        'Notes'
    ]
    search_pattern = r'|'.join(re.escape(key_phrase) for key_phrase in key_phrases)
    match_obj = re.search(search_pattern, document_string)
    if match_obj:
        first_ending_trim_phrase_index = match_obj.start()
    return first_ending_trim_phrase_index

def split_into_still_needed_chunks(document_string):
    # print('splitting into still needed chunks')
    still_needed_chunks = []
    still_needed_chunk_starting_index = document_string.find('Still needed:')
    # print(f'still_needed_chunk_starting_index: {still_needed_chunk_starting_index}')
    while still_needed_chunk_starting_index != -1:
        # print('while loop activated')
        still_needed_chunk_ending_index = document_string.find('Still needed:', still_needed_chunk_starting_index + 1)
        if still_needed_chunk_ending_index != -1:
            # print('if activated')
            still_needed_chunks.append(document_string[still_needed_chunk_starting_index:still_needed_chunk_ending_index])
            still_needed_chunk_starting_index = still_needed_chunk_ending_index
        else:
            # print('else activated')
            still_needed_chunks.append(document_string[still_needed_chunk_starting_index:find_index_of_first_ending_trim_phrase(document_string)])
            break
    # for chunk in still_needed_chunks:
    #     print(chunk)
    #     print()
    return still_needed_chunks

def generate_simple_deliverables_string(document_string):
    logical_grouping_start_match_obj = re.search(r'Still needed:[\s\n]+Choose from \d{1,2} of the following:', document_string)
    if logical_grouping_start_match_obj:
        logical_grouping_start_index = logical_grouping_start_match_obj.start()
        remaining_document_string = document_string[logical_grouping_start_match_obj.end():]
        logical_grouping_end_match_obj = re.search(r'Still needed:', remaining_document_string)
        if logical_grouping_end_match_obj:
            document_string = document_string[:logical_grouping_start_index] + remaining_document_string[logical_grouping_end_match_obj.start():]
    deliverables_str = ''
    still_needed_chunks = split_into_still_needed_chunks(document_string)
    deliverables_list = []
    for chunk in still_needed_chunks:
        # print(chunk)
        if not (re.search(r'1 Class in [A-Z]{4} \d{4}[A-Z@]?[\s\n]+or[\s\n]+',chunk)):
            # print(chunk)
            if(match := re.search(r'1 Class in [A-Z]{4} \d{4}(?:[A-Z](?=[\s\n]))?', chunk)):
                deliverables_list.append(match.group())
    deliverables_str += '('
    for deliverable_index, deliverable in enumerate(deliverables_list):
        match = re.search(r'[A-Z]{4} \d{4}[A-Z]?', deliverable)
        if match:
            deliverables_str += match.group()
        if deliverable_index < len(deliverables_list) - 1:
            deliverables_str += ','
    deliverables_str += ')\n\n'
    return deliverables_str

def find_curr_taken_courses_with_ranges(document_string):
    taken_course_year_pairing = set()
    document_string = trim_document_string(document_string)
    season_year_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'(Spring|Fall|Summer)\s(Term|Semester)\s\d{4}', document_string)]))
    course_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'([A-Z\*]{4} [0-9\*]{4}[A-Z]?)|([A-Z\*]{3} [0-9\*]{4})', document_string)]))
    number_of_course_blocks = len(course_block_indices_list)
    curr_taken_courses = []
    course_year_ranges = []  # Initialize an empty list to store the course_block to season_year_block ranges
    working_course_index = 0
    for season_year_block_start_index, season_year_block_end_index in season_year_block_indices_list:
        course_range = course_block_indices_list[working_course_index]
        while course_range[0] > season_year_block_start_index and working_course_index < number_of_course_blocks:
            working_course_index += 1
            course_range = course_block_indices_list[working_course_index]
        if working_course_index < number_of_course_blocks:
            course_number = document_string[course_range[0]:course_range[1]].strip()
            semester_year = document_string[season_year_block_start_index:season_year_block_end_index].strip()
            course_year_pairing = f'{course_number} - {semester_year}'
            if course_year_pairing not in taken_course_year_pairing:
                curr_taken_courses.append(course_number)
                taken_course_year_pairing.add(course_year_pairing)

                # Store the range from the beginning of the course_block to the end of its paired season_year_block
                course_year_range = (course_range[0], season_year_block_end_index)
                course_year_ranges.append(course_year_range)
    # print(course_year_ranges)
    return course_year_ranges

# TODO: Find the following as a curr/taken course: '*** 1*** Orientation/Student Success B 3 Spring Semester 2021'
# TODO: Find 'HESC 2***'
def remove_all_curr_taken_courses(document_string):
    trimmed_string = trim_document_string(document_string)
    curr_taken_courses_removed_string = ''
    season_year_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'(Spring|Fall|Summer)[\s\n](Term|Semester)\s\d{4}\n?', document_string)]))
    course_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'([A-Z\*]{4} [0-9\*]{4}[A-Z]?)|([A-Z\*]{3} [0-9\*]{4})', document_string)]))
    number_of_course_blocks = len(course_block_indices_list)
    working_course_index = 0
    course_year_ranges = []
    for season_year_block_start_index, season_year_block_end_index in season_year_block_indices_list:
        course_range = course_block_indices_list[working_course_index]
        while course_range[0] > season_year_block_start_index and working_course_index < number_of_course_blocks:
            working_course_index += 1
            course_range = course_block_indices_list[working_course_index]
        if working_course_index < number_of_course_blocks:
            course_year_range = (course_range[0], season_year_block_end_index)
            course_year_ranges.append(course_year_range)
    curr_taken_courses_removed_string = ''
    prev_range_end_index = 0
    reversed_course_year_ranges = list(reversed(course_year_ranges))
    for range_index, range in enumerate(reversed_course_year_ranges):
        curr_taken_courses_removed_string += trimmed_string[prev_range_end_index:range[0]]
        prev_range_end_index = range[1]
    curr_taken_courses_removed_string += trimmed_string[prev_range_end_index:]
    return curr_taken_courses_removed_string

def remove_no_course_still_needed_chunks(still_needed_chunks):
    comprehensive_letter_block_regex_pattern = r'(?:[A-Z]{4}|@)'
    comprehensive_number_block_regex_pattern = r'(?:\d{4}([@A-Z])?|\d@)'
    comprehensive_course_block_regex_pattern = f'{comprehensive_letter_block_regex_pattern}\s{{0,6}}{comprehensive_number_block_regex_pattern}'
    still_needed_chunks_all_non_complex_still_needed_chunks_removed_list = []

    for chunk in still_needed_chunks:
        # print(chunk)
        match = None
        if (match := re.search(comprehensive_course_block_regex_pattern, chunk)):
            # print(chunk)
            # print(f'Match: {match}')
            # print(match.group())
            # print()
            still_needed_chunks_all_non_complex_still_needed_chunks_removed_list.append(chunk)
    # for chunk in still_needed_chunks_all_non_complex_still_needed_chunks_removed_list:
    #     print(chunk)
    return still_needed_chunks_all_non_complex_still_needed_chunks_removed_list
    
    # match = re.search(comprehensive_course_block_regex_pattern, search_string)

    # comprehensive_course_block_regex_pattern = re.search(, search_string)
    # (four capital letters followed by a space or a new line character OR an @ sign followed by a space or a new line character)followed by (an @ or a number followed by an @ or four numbers followed by (an optional @ or an optional capital letter)
# Instances of course blocks in example input 1:
    # POLS 1101, 1305, BIOL 1225K, 1115L, CHEM 1211@, 
    # 2112@, PEDS 1@,  2@, 3@, 4@, 5@, @ 1@
    # cleaned_
    # Remove all previously taken/currently taking still needed chunks
        # Make a comprehensive course block regex
        # # remove all still neededs that don't contain a course block
        # Logically group the chunks
        # Iterate through each logically grouped chunk, classify, and handle
    

    pass

def remove_chunks_not_starting_with_course(still_needed_chunks):
    still_needed_chunks_not_starting_with_course_list = []
    for chunk in still_needed_chunks:
        if (match := re.search('Still needed:\s{0,3}(Choose from|(?:\d{1,2})\sCredit[s]? in|(?:\d{1,2})\sClass[es]? in)', chunk)):
            # print(chunk)
            # print(f' match: {match.group()}')
            # print()
            # print()
            still_needed_chunks_not_starting_with_course_list.append(chunk)
    return still_needed_chunks_not_starting_with_course_list

def remove_student_info(still_needed_chunks):
    still_needed_chunks_student_info_removed_list = []
    for chunk in still_needed_chunks:
        chunk.replace('\n','')
    for chunk in still_needed_chunks:
        if (match := re.search(r'Ellucian University\s{0,3}[a-zA-Z]+\s{0,2},\s{0,2}[a-zA-Z]+\s{0,2}-\s{0,2}\d{9}', chunk)):
            chunk = chunk.replace(match.group(), '')
            # print(chunk)
            # print('match' + match.group())
            still_needed_chunks_student_info_removed_list.append(chunk)
        else:
            still_needed_chunks_student_info_removed_list.append(chunk)
    return still_needed_chunks_student_info_removed_list

def remove_satisfied_by_blocks(still_needed_chunks):
    still_needed_chunks_satisfied_by_removed_list = []
    for chunk in still_needed_chunks:
        if (match_list := re.findall(r'Satisfied by:\s{0,5}[a-zA-Z0-9]+\s{0,2}-\s{0,2}.+-', chunk)):
            for match in match_list:
                # print(f'about to remove match: {match}')
                # print(chunk)
                chunk = chunk.replace(match, '')
                # print(chunk)
                # print('just removed match')
        still_needed_chunks_satisfied_by_removed_list.append(chunk)
    return still_needed_chunks_satisfied_by_removed_list

def remove_area_x_from_chunks(still_needed_chunks):
    area_x_removed_chunks_list = []
    for chunk in still_needed_chunks:
        if (match := re.search(r'Area [A-Z]', chunk)):
            # print(chunk)
            # print(match)
            chunk = chunk[:chunk.find(match.group())]
            # print(chunk)
        area_x_removed_chunks_list.append(chunk)
    return area_x_removed_chunks_list

def remove_major_in_from_chunks(still_needed_chunks):
    major_in_removed_chunks_list = []
    for chunk in still_needed_chunks:
        if (match := re.search(r'Major in', chunk)):
            # print(chunk)
            # print(match)
            chunk = chunk[:chunk.find(match.group())]
            # print(chunk)
        major_in_removed_chunks_list.append(chunk)
    return major_in_removed_chunks_list

def remove_simple_deliverable_chunks(still_needed_chunks):
    simple_deliverables_removed_chunks_list = []
    # chunks_we_be_removin = []
    for chunk in still_needed_chunks:
        num_letter_blocks = len(re.findall(r'(?:[A-Z]{4}|\s{1,2}@\s{1,2})', chunk))
        num_number_blocks = len(re.findall(r'(?:\d{4}([@A-Z])?|\d@)', chunk))
        # print(f'Found {num_letter_blocks} letter blocks and {num_number_blocks} for chunk: {chunk}')
        if (num_letter_blocks > 1 or num_number_blocks > 1) or ('Credit' in chunk):
            simple_deliverables_removed_chunks_list.append(chunk)
        # else:
        #     chunks_we_be_removin.append(chunk)
    # print('chunks we be removin:')
    # for chunk in chunks_we_be_removin:
    #     print(chunk)
    #     print()
    return simple_deliverables_removed_chunks_list

def generate_course_blocks(chunk):
    course_blocks = []
    current_letter_block_iterator = ''
    curent_number_block = ''
    # general_block_tokenized_list = []
    
    # generalized_block_regex_pattern = ''
    comprehensive_letter_block_regex_pattern = r'(?:[A-Z]{4}|\s{1,2}@\s{1,2})'
    comprehensive_number_block_regex_pattern = r'(?:\d{4}([@A-Z])?|\d@)'
    comprehensive_general_block_regex_pattern = r'(?:[A-Z]{4}|\s{1,2}@\s{1,2})|(?:\d{4}([@A-Z])?|\d@)'
    # current_letter_block_iterator = re.finditer(comprehensive_letter_block_regex_pattern, chunk)
    generalized_block_list = list(re.finditer(comprehensive_general_block_regex_pattern, chunk))

    # for match in current_letter_block_iterator:
    #     print(match.group())
    # print(f'current_letter_block: {current_letter_block}')
    # print(generalized_block_list)
    '''
    initialize the letter block to the first item
    for each item in the list:
        check if it is a letter block or a number block
        if it is a letter block:
            set the current letter block to the value
            throw an error print statement
        if it is a number block:
            append current letter block + current block to the list
        if the current letter block is set:
            

    
    '''
    current_letter_block = generalized_block_list[0].group()
    # print(f'current_letter_block: {current_letter_block}')
    for generalized_block in generalized_block_list:
        # print(f'Old current letter block: {current_letter_block}')
        if (match_obj := re.search(comprehensive_letter_block_regex_pattern, generalized_block.group())):
            # print('Reassigning the current letter block')
            current_letter_block = generalized_block.group()
            # print(f'New current letter block: {current_letter_block}')
        elif (match_obj := re.search(comprehensive_number_block_regex_pattern, generalized_block.group())):
            # print('found a number block. about to append to list')
            # print(f'list before: {course_blocks}')
            course_blocks.append(f'{current_letter_block} {match_obj.group()}')
            # print(f'list after: {course_blocks}')
        # print(generalized_block.group())
        # print()
        # print()
    # for generalized_block in generalized_block_lrist:
        # generalized_block_list.append()
        
    return course_blocks

def classify_and_handle_chunks(still_needed_chunks):
    complex_deliverables_string = ''
    node_list = []
    simple_deliverable_list = []
    error_chunk_list = []
    for chunk_index, chunk in enumerate(still_needed_chunks):
        # print(chunk_index, chunk)
        # Special shallow selection node
        if (name := re.search(r'Choose from \d{1} of the following:', chunk)):
            required_count = name.group()[name.group().find(' of the following:') - 1]
            # print(name.group().find(' of the following:'))
            # print(f'required count: {required_count}')
            complex_deliverables_string += f'[s <c={required_count}, n={name.group()}>\n'
            sub_chunk_list = []
            # print(f'The special chunk is the following: {chunk}')
            sub_chunk_start_matches_list = list(re.finditer('\d{1,2} Class(es)?|\d{1,2} Credit[s]?', chunk))
            sub_chunk_start_matches_start_index_list = []
            for sub_chunk_start_match in sub_chunk_start_matches_list:
                sub_chunk_start_matches_start_index_list.append(sub_chunk_start_match.start())
            if not sub_chunk_start_matches_list:
                print('We have found a special shallow selection node with nothin in it. Error')
            for current_index, start_index in enumerate(sub_chunk_start_matches_start_index_list):
                if not current_index + 1 >= len(sub_chunk_start_matches_start_index_list):
                    sub_chunk_list.append(chunk[sub_chunk_start_matches_start_index_list[current_index]:sub_chunk_start_matches_start_index_list[current_index + 1]].strip())
                else:
                    sub_chunk_list.append(chunk[sub_chunk_start_matches_start_index_list[current_index]:])
            # print(f'sub_chunk_list: {sub_chunk_list}')
            # print('about to execute recursively')
            complex_deliverables_string += classify_and_handle_chunks(sub_chunk_list)
            # print('finished executing recursively')
            # for sub_chunk in sub_chunk_list:

            # #     generate_course_blocks(sub_chunk)
            # print('about to execute recursive call')
            # print(f'sub_chunk_list: {sub_chunk_list}')
            # print(f'Inside the special shallow selection node: {classify_and_handle_chunks(sub_chunk_list)}')
            # print('after recursive call')
            # print('about to append the ] in the special chunk')
            complex_deliverables_string += ']\n'#there is an order of execution problem here
            # print('just appended the ] in the special chunk')
        # Normal shallow selection node
        elif (name := re.search(r'\d{1,2} Class(es)? in .*[\s]*(or|and)[\s\n]*', chunk)):
            # print('This chunk is a shallow selection node')
            # print(chunk)
            # # print(still_needed_chunks)
            # # generate_course_blocks(still_needed_chunks)
            # print()
            required_count = re.search(f'\d+(\d+)?', name.group()).group()
            # print(f'required count for {chunk} is {required_count}')
            complex_deliverables_string += f'[s <c={required_count}, n={chunk}>\n'
            # print(f'printing chunk: {chunk}')
            # print('about to execute')
            course_blocks = generate_course_blocks(chunk)
            # print(course_blocks)
            for course in course_blocks:
                if '@' in course:
                    # print('About to append a protocol node')
                    complex_deliverables_string += f'[p <n={course}, m={course}.*]\n'
                    # print('just appended a protocol node')
                else:
                    # print('about to append a deliverable')
                    complex_deliverables_string += f'[d <n={course}]\n'
                    # print('appended a deliverable')
            # print(course_blocks)
            complex_deliverables_string += ']\n'

        # Deliverable node
        elif not (re.search(r'1 Class in [A-Z]{4} \d{4}[A-Z@]?[\s\n]+or[\s\n]+', chunk)) and re.search(r'1 Class in [A-Z]{4} \d{4}(?:[A-Z](?=[\s\n]))?', chunk):
            # print('This chunk is a simple deliverable')
            # print(chunk)
            # generate_course_blocks(chunk)
            # print()
            required_count = re.search('\d+(\d+)?', chunk).group()
            course_blocks = generate_course_blocks(chunk)
            for course in course_blocks:
                complex_deliverables_string += f'[d <n={course}]\n'
            # print(f'required count on a deliverable: {required_count}')
        # Deep credit selection node
        elif (match_obj := re.search(r'\d{1,2} Credit[s]? in', chunk)):
            # print('This chunk is a Deep credit selection node')
            # print(chunk)
            # print()
            required_count = required_count = re.search('\d+(\d+)?', chunk).group()
            complex_deliverables_string += f'[r <c={required_count}, n={chunk}>\n'
            course_blocks = generate_course_blocks(chunk)
            # print(f'required count for {chunk} is {required_count}')

            for course in course_blocks:
                if '@' in course:
                    # print('About to append a protocol node')
                    complex_deliverables_string += f'[p <n={course}, m={course}.*]\n'
                    # print('just appended a protocol node')
                else:
                    # print('about to append a deliverable')
                    complex_deliverables_string += f'[d <n={course}]\n'
            complex_deliverables_string += ']\n'
            
        else:
            # print('This chunk is unclassified')
            # print(chunk)
            # # print(chunk)
            # print()
            complex_deliverables_string += ''
            pass
    return complex_deliverables_string

    # if re.search(r'(\d Credit?s in @)', chunk):
    #     print(chunk)
    #     print('This chunk is a ')

# Note: 44 still needed chunks to process in input 1
def generate_complex_deliverables_string(document_string):
    complex_deliverables_string = ''
    curr_taken_courses_removed_string = remove_all_curr_taken_courses(document_string)
    # identify all still neededs that are not simple and put in a list
    still_needed_chunks_list = split_into_still_needed_chunks(curr_taken_courses_removed_string)
    still_needed_chunks_no_course_removed_list = remove_no_course_still_needed_chunks(still_needed_chunks_list)
    still_needed_chunks_not_starting_with_course_list = remove_chunks_not_starting_with_course(still_needed_chunks_no_course_removed_list)
    # for chunk in still_needed_chunks_not_starting_with_course_list:
    #     print(chunk)
    still_needed_chunks_student_info_removed_list = remove_student_info(still_needed_chunks_not_starting_with_course_list)
    # for chunk in still_needed_chunks_student_info_removed_list:
    #     print(chunk)
    still_needed_chunks_satisfied_by_removed_list = remove_satisfied_by_blocks(still_needed_chunks_student_info_removed_list)
    # for chunk in still_needed_chunks_satisfied_by_removed_list:
    #     print(chunk)
    # for chunk_index, chunk in enumerate(still_needed_chunks_satisfied_by_removed_list):
    #     print(chunk)
    #     print(f'chunk index: {chunk_index}')
    # print(still_needed_chunks_satisfied_by_removed_list)
    area_x_removed_chunks_list = remove_area_x_from_chunks(still_needed_chunks_satisfied_by_removed_list)
    # for chunk_index, chunk in enumerate(area_x_removed_chunks_list):
    #     print(chunk)
    #     print(f'chunk index: {chunk_index}')
    major_in_removed_chunks_list = remove_major_in_from_chunks(area_x_removed_chunks_list)
    # for chunk_index, chunk in enumerate(major_in_removed_chunks_list):
    #     print(chunk)
    #     print(f'chunk index: {chunk_index}')
    simple_deliverables_removed_chunks_list = remove_simple_deliverable_chunks(major_in_removed_chunks_list)
    complex_deliverables_string += classify_and_handle_chunks(simple_deliverables_removed_chunks_list)
    return complex_deliverables_string

def generate_courses_needed_construction_string(document_string):
    courses_needed_construction_string = ''
    courses_needed_construction_string += generate_simple_deliverables_string(document_string)
    courses_needed_construction_string += generate_complex_deliverables_string(document_string)
    # print(f'Courses needed construction string: {courses_needed_construction_string}')
    return courses_needed_construction_string

def generate_degree_extraction_container(file_name):
    with open(file_name, 'rb') as degreeworks_pdf:
        pdf_reader = PdfReader(degreeworks_pdf)
        courses_needed_constuction_string = ''
        document_string = ''
        degree_plan_name = None
        student_number = None
        student_name = None
        curr_taken_courses = []
        for page in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page].extract_text()
            document_string += page_text
        student_name = get_student_name(document_string)
        student_number = get_student_number(document_string)
        degree_plan_name = get_degree_plan_name(document_string)
        curr_taken_courses = find_curr_taken_courses(document_string)
        courses_needed_constuction_string = generate_courses_needed_construction_string(document_string)

    return DegreeExtractionContainer(curr_taken_courses, courses_needed_constuction_string, degree_plan_name, student_number, student_name)

if __name__ == '__main__':
    container = generate_degree_extraction_container('./input_files/updated_degreeworks/S1.pdf')
    # print(f'student name: {container._student_name}')
    # print(f'student number: {container._student_number}')
    # print(f'degree plan: {container._degree_plan_name}')
    # print(container._taken_courses)
    # print(container._courses_needed_constuction_string)