# Austin Lee and Thomas Merino 1/23/2023
# CPSC 4175 Project

from alias_module import get_latest_id
from degree_extraction_container import DegreeExtractionContainer

# from courses_needed_container import CoursesNeededContainer, \
#     DeliverableCourse, CourseProtocol, CourseInserter, ExhaustiveNode, \
#     ShallowCountBasedNode, DeepCountBasedNode, DeepCreditBasedNode

import re
from pypdf import PdfReader
from degree_extraction_container import DegreeExtractionContainer

# TODO:
    # 1. Create a tokenized_list that has all chunks normalized into predictable logical structures
    # 2. Process each chunk fully with all trimming functions in a loop until the chunk no longer changes.
        # Once all chunks are static, remove all empty chunks.
    # 3. Interface with tree generator.
    # 4. Figure out the situation with the '3 to 6 Credits'...ask Dr. Carroll
    # 5. Standardize the 'course blocks' etc.

# 
def remove_substring_after_last_relevant(input_string):
    match_reversed = re.search(r'[0-9]{4}|@|\)', input_string[::-1])
    end_index = len(input_string) - match_reversed.start() if match_reversed else 0
    return input_string[:end_index]

# Searches for 'Minor in ' in a given chunk. One time function
def remove_minor_in(chunk, index, lst):
    chunk = chunk[:chunk.find('Minor in ')] if 'Minor in ' in chunk else chunk
    return chunk

# Searches for 'Select one as a pre-requesite for ' and removes everything from the phrase to the end of the chunk. Need this because
# it contains a course block and could cause issues. One time function.
def remove_select_one(chunk, index, lst):
    chunk = chunk[:chunk.find('Select one as a pre-requesite for ')] if 'Select one as a pre-requesite for ' in chunk else chunk
    return chunk

# Removes 
def remove_empty(chunk, index, lst):
    if len(chunk) == 0:
        lst.pop(index)

def remove_empty_items(lst):
    return [item for item in lst if item]

def remove_major_in(chunk, index, lst):
    chunk = chunk[:chunk.find('Major in ')] if 'Major in ' in chunk else chunk
    return chunk

def remove_AREA_X(chunk, index, lst):
    chunk = chunk[:chunk.find('AREA ')] if 'AREA ' in chunk else chunk
    return chunk

def remove_chunk_without_course_block(chunk, index, lst):
    if not re.search(r'([A-Z]{4}\s{1})', chunk):
        chunk = ''
    return chunk

# find the number of season year groups
# find all instances of course block patterns and record their end indices
# get end index of the (number of season year groups + 1 from the end of the list)
def remove_curr_taken_courses(chunk, index, lst):
    new_chunk = ''
    # print(chunk)
    # print()
    num_season_year_blocks = len(re.findall(r'(Spring|Fall)\s\d{4}', chunk))
    courses_block_iterator = re.finditer(r'([A-Z]{4}\s{1}\d{4}( \))?)|(or \d{4}( \))?)|(, \d{4}( \))?)|(\d@( \))?)|[A-Z]{4} \d\*\*\*', chunk)
    course_block_indices_list = []
    for course in courses_block_iterator:
        course_block_indices_list.append(course.end())
    if num_season_year_blocks:
        new_chunk = chunk[:course_block_indices_list[len(course_block_indices_list) - num_season_year_blocks - 1]]
        # print(f'chunk containing courses taken: {chunk[course_block_indices_list[len(course_block_indices_list) - num_season_year_blocks - 1]:]}')
        # courses_block_iterator = re.finditer(r'([A-Z]{4} \d{4}[A-Z]?)', chunk)
        # for course_match in courses_block_iterator:
        #     curr_taken_list.append(course_match.group())
    else:
        new_chunk = chunk
    return new_chunk

# TODO: Complete get_curr_taken_courses
import re

def find_curr_taken_courses(string):
    taken_course_year_pairing = set() # The format of this is '{course} - {year}'
    season_year_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'(Spring|Fall)\s\d{4}', string)]))
    course_block_indices_list = list(reversed([(match.start(), match.end()) for match in re.finditer(r'[A-Z]{4} \d{4}[A-Z]?|[A-Z]{4} \d{1}\*\*\*', string)]))
    number_of_course_blocks = len(course_block_indices_list)
    curr_taken_courses = []
    working_course_index = 0
    for season_year_block_start_index, season_year_block_end_index in season_year_block_indices_list:
        course_range = course_block_indices_list[working_course_index]
        while course_range[0] > season_year_block_start_index and working_course_index < number_of_course_blocks:
            working_course_index += 1
            course_range = course_block_indices_list[working_course_index]
        if working_course_index < number_of_course_blocks:
            course_number = string[course_range[0]:course_range[1]].strip()
            semester_year = string[season_year_block_start_index:season_year_block_end_index].strip()
            course_year_pairing = f'{course_number} - {semester_year}'
            if course_year_pairing not in taken_course_year_pairing:
                curr_taken_courses.append(course_number)
                taken_course_year_pairing.add(course_year_pairing)
        
    return curr_taken_courses

def filter_deliverables(chunk):
    deliverable = None
    if (re.match(r'(\d{1} Class in [A-Z]{4} [0-9]{4})$|([A-Z]{4} [0-9]{4})$', chunk)):
        deliverable = (re.search(r'([A-Z]{4} [0-9]{4})$', chunk)).group(1)
    return deliverable

def input_deliverables_to_export_str(input_list):
    result_str = '('
    for i, item in enumerate(input_list):
        if i < len(input_list) - 1:
            result_str += f'{item},'
        else:
            result_str += f'{item})'
    return result_str

def classify_and_handle_chunk(chunk):
    working_intermediate_substring = ''
    # indicates that a shallow_selection node has been found 's'
    if (match_obj := re.search(r'(Choose from \d{1} of the following:)', chunk)):
        match_str = match_obj.group(1)
        required_count = match_str[match_str.find(' of the following:') - 1]
        working_intermediate_substring += f'[s <c={required_count}, n={match_str}>'
        # print(f'intermediate_substring: {intermediate_substring}')
        chunk = chunk.replace('Ellucian Degree Works Report','')
        chunk = re.sub(r'Choose from \d{1} of the following:\n', '', chunk)
        options_chunks_list = []
        options_chunks_list = chunk.split(') or\n')
        for index in range(len(options_chunks_list) - 1):
            options_chunks_list[index] = options_chunks_list[index] + ') or'
        
        for chunk in options_chunks_list:
            courses_block_list = []
            name = chunk[0:chunk.find('Still Needed:')]
            if (match_obj := re.search(r'(\( \d{1} Credit?s)', chunk)):
                match_str = match_obj.group(1)
                required_count = match_str[match_str.find(' Credit') - 1]
                courses_block_iterator = re.finditer(r'([A-Z]{4}\s{1}\d{4}( \))?)|(or \d{4}( \))?)|(, \d{4}( \))?)|(\d@( \))?)', chunk)
                for course_match in courses_block_iterator:
                    courses_block_list.append(course_match.group())
                current_letter_block = courses_block_list[0][0:4]
                for index in range(len(courses_block_list)):
                    number_block = re.search(r'\d{4}', courses_block_list[index]).group(0)
                    if (re.search(r'([A-Z]{4})', courses_block_list[index])):
                        current_letter_block = re.search(r'[A-Z]{4}', courses_block_list[index]).group(0)
                    else:
                        courses_block_list[index] = f'{current_letter_block} {number_block}'
                working_intermediate_substring += f'[r <c={required_count}, n={name}>'
                for course in courses_block_list:
                    working_intermediate_substring += f'[d <n={course}>]'
                working_intermediate_substring += ']'
            elif (match_obj := re.search(r'(\( \d{1} Class?es)', chunk)):
                match_str = match_obj.group(1)
                required_count = match_str[match_str.find(' Class') - 1]
                courses_block_iterator = re.finditer(r'([A-Z]{4}\s{1}\d{4}( \))?)|(or \d{4}( \))?)|(, \d{4}( \))?)|(\d@( \))?)|(and \d{4})', chunk)
                for course_match in courses_block_iterator:
                    courses_block_list.append(course_match.group())
                current_letter_block = courses_block_list[0][0:4]
                for index in range(len(courses_block_list)):
                    number_block = re.search(r'\d{4}', courses_block_list[index]).group(0)
                    if (re.search(r'([A-Z]{4})', courses_block_list[index])):
                        current_letter_block = re.search(r'[A-Z]{4}', courses_block_list[index]).group(0)
                    else:
                        courses_block_list[index] = f'{current_letter_block} {number_block}'
                working_intermediate_substring += f'[c <c={required_count}, n={name}>'
                for course in courses_block_list:
                    working_intermediate_substring += f'[d <n={course}>]'
                working_intermediate_substring += ']'
        working_intermediate_substring += ']'
        formatted_string = working_intermediate_substring.replace("]", "]\n")
    elif (match_obj := re.search(r'(\d Credit?s in @)', chunk)):
        chunk = re.sub(r'\n', '', chunk)
        courses_block_list = []
        exceptions_block_list = []
        name=chunk[:chunk.find('Except')]
        text_instructions = chunk[chunk.find('Except'):]
        required_count = re.match(r'^\d{1,2}', chunk[:4])
        if required_count:
            required_count = re.match(r'^\d{1,2}', chunk[:4]).group()
        working_intermediate_substring += f'[r <c={required_count}, n={name}, i={text_instructions}>'
        courses_block_iterator = re.finditer(r'(\d@[A-Z]?)', chunk)
        for course_match in courses_block_iterator:
            courses_block_list.append(course_match.group())
        exceptions_block_iterator = re.finditer(r'([A-Z]{4} \d{4}|\d{4})', chunk)
        for exception_match in exceptions_block_iterator:
            exceptions_block_list.append(exception_match.group())
        current_letter_block = re.search(r'([A-Z]{4})', exceptions_block_list[0]).group()
        for index in range(len(exceptions_block_list)):
            number_block = re.search(r'\d{4}', exceptions_block_list[index]).group(0)
            if (re.search(r'([A-Z]{4})', exceptions_block_list[index])):
                current_letter_block = re.search(r'[A-Z]{4}', exceptions_block_list[index]).group(0)
            else:
                exceptions_block_list[index] = f'{current_letter_block} {number_block}'
        exceptions_string = '|'.join(exceptions_block_list)
        for course in courses_block_list:
            course_suffix = course[-1] if course[-1].isupper() else '[A-Z]?'
            working_intermediate_substring += f'[i <n=Insert {course}, ga={course} Course, gp=^(?!{exceptions_string})[A-Z]{{4}} {course[0]}\d{{3}}{course_suffix}>]'
        working_intermediate_substring += ']'
    # indicates that a deep credit selection node has been found 'r'
    elif (match_obj := re.match(r'(\d Credit?s in [A-Z])', chunk)):
        courses_block_list = []
        name = chunk
        match_str = match_obj.group(1)
        required_count = re.match(r'^\d{1,2}', match_str)
        if required_count:
            required_count = re.match(r'^\d{1,2}', match_str).group()
        courses_block_iterator = re.finditer(r'([A-Z]{4} \d{1}@|\d{1}@)', chunk)
        for course_match in courses_block_iterator:
            courses_block_list.append(course_match.group())
        current_letter_block = re.search(r'([A-Z]{4})', courses_block_list[0]).group()
        for index in range(len(courses_block_list)):
            number_block = re.search(r'\d{4}|\d@', courses_block_list[index]).group(0)
            if (re.search(r'([A-Z]{4})', courses_block_list[index])):
                current_letter_block = re.search(r'[A-Z]{4}', courses_block_list[index]).group(0)
            else:
                courses_block_list[index] = f'{current_letter_block} {number_block}'
        working_intermediate_substring += f'[r <c={required_count}, n={name}>'
        
        for course in courses_block_list:
            working_intermediate_substring += f'[i <n=Insert {course}, ga={course} Course, gp={course[:-1]}\d{3}[A-Z]?>]'
        working_intermediate_substring += ']'

    elif (match_obj := re.match(r'(\d Classe?s? in [A-Z]{4})(?=.* or )', chunk)):
        courses_block_list = []
        name = chunk
        match_str = match_obj.group(1)
        required_count = re.match(r'^\d{1,2}', match_str)
        if required_count:
            required_count = re.match(r'^\d{1,2}', match_str).group()
        courses_block_iterator = re.finditer(r'([A-Z]{4} \d{4}@?|\d{4}@?)', chunk)
        for course_match in courses_block_iterator:
            courses_block_list.append(course_match.group())
        current_letter_block = re.search(r'([A-Z]{4})', courses_block_list[0]).group()
        for index in range(len(courses_block_list)):
            number_block = re.search(r'\d{4}@?', courses_block_list[index]).group(0)
            if (re.search(r'([A-Z]{4})', courses_block_list[index])):
                current_letter_block = re.search(r'[A-Z]{4}', courses_block_list[index]).group(0)
            else:
                courses_block_list[index] = f'{current_letter_block} {number_block}'
        working_intermediate_substring += f'[s <c={required_count}, n={name}>'
        for course in courses_block_list:
            if re.search(r'\d{4}@', course):
                working_intermediate_substring += f'[p <n={course}, m={course[:-1]}.*>]'
            else:
                working_intermediate_substring += f'[d <n={course}>]'
        working_intermediate_substring += ']'
    return working_intermediate_substring    

def get_degree_plan_name(string):
    degree_plan_name = ''
    string = (string[:string.find('Degree Progress')])
    degree_plan_name = re.search(r'Major [A-Z]{4}.*?\n', string).group()
    degree_plan_name = degree_plan_name[degree_plan_name.find('Major ') + len('Major '):]
    return degree_plan_name


def generate_degree_extraction_container(file_name): 
    
    with open(file_name, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        intermediate_str = ''
        still_needed_chunks_list = [] # Holds all unprocessed/filtered chunks
        document_string = '' # Holds the entire parsed pdf text
        for page in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page].extract_text()
            document_string += page_text
        degree_plan_name = get_degree_plan_name(document_string)
        curr_taken_courses = find_curr_taken_courses(document_string[:document_string.find('Fallthrough Courses')])
        # print(f'curr_taken_courses: {curr_taken_courses}')
        start = document_string.find("Still Needed:") # Used to initiate every chunk
        while start != -1:
            end = document_string.find("Still Needed:", start + 1) # Searches for next instance of phrase
            if end != -1:
                still_needed_chunks_list.append(document_string[start:end]) 
                start = end
            else: # This case accounts for the final instance of the phrase
                still_needed_chunks_list.append(document_string[start:document_string.find('Fallthrough', start + 1)])
                break
        currently_in_logical_block = False # Used to track if currently parsing a multi-line logical block
        logically_grouped_list = [] # Holds the chunks that contain all logical groupings of needed courses
        logical_chunk_string = '' # Holds the current chunk being parsed
        # for chunk in still_needed_chunks_list:
        #     print(chunk)
        
        for chunk in still_needed_chunks_list:
            if 'of the following:' in chunk or ') or' in chunk: # Indicates the start or continuance of a logical chunk
                currently_in_logical_block = True
                logical_chunk_string += chunk # Appends last portion of a logical chunk
            else:
                if currently_in_logical_block:
                    logical_chunk_string += chunk
                    logically_grouped_list.append(logical_chunk_string)
                    currently_in_logical_block = False
                    logical_chunk_string = ''
                else:
                    logically_grouped_list.append(chunk) # Appends simple chunks

        filtered_list = [] # Holds the filtered chunks
        # for chunk in filtered_list:
        #     print(chunk)
        #     print()
        # print(f'logically_grouped_list: {logically_grouped_list}')
        # print()
        for chunk in logically_grouped_list:
            if not 'See ' in chunk and not 'YOU MUST APPLY FOR GRADUATION' in chunk and not 'Still Needed: Outcomes Assessment Exam' in chunk:
                delimiter = 'Still Needed:'
                chunk = chunk[chunk.index(delimiter)+(len(delimiter)+1):]
                if chunk[0] == ' ':
                    chunk = chunk[1:]
                chunk = remove_substring_after_last_relevant(chunk)
                filtered_list.append(chunk)
        # print(filtered_list)
        filtered_list = remove_empty_items(filtered_list)
        for index in range(len(filtered_list)):
            filtered_list[index] = remove_curr_taken_courses(filtered_list[index], index, filtered_list)
        filtered_list = remove_empty_items(filtered_list)
        for index in range(len(filtered_list)):
            filtered_list[index] = remove_minor_in(filtered_list[index], index, filtered_list)
        filtered_list = remove_empty_items(filtered_list)
        for index in range(len(filtered_list)):
            filtered_list[index] = remove_select_one(filtered_list[index], index, filtered_list)
        filtered_list = remove_empty_items(filtered_list)
        for index in range(len(filtered_list)):
            filtered_list[index] = remove_major_in(filtered_list[index], index, filtered_list)
        filtered_list = remove_empty_items(filtered_list)
        for index in range(len(filtered_list)):
            filtered_list[index] = remove_AREA_X(filtered_list[index], index, filtered_list)
        filtered_list = remove_empty_items(filtered_list)
        for index in range(len(filtered_list)):
            filtered_list[index] = remove_substring_after_last_relevant(filtered_list[index])
        filtered_list = remove_empty_items(filtered_list)
        for index in range(len(filtered_list)):
            filtered_list[index] = remove_chunk_without_course_block(filtered_list[index], index, filtered_list)
        filtered_list = remove_empty_items(filtered_list)
        deliverables_list = []
        complex_list = []
        for chunk in filtered_list:
            if (deliverable := filter_deliverables(chunk)):
                deliverables_list.append(deliverable)
            else:
                complex_list.append(chunk)
        intermediate_str += input_deliverables_to_export_str(deliverables_list)
        for chunk in complex_list:
            intermediate_str += classify_and_handle_chunk(chunk)
    return DegreeExtractionContainer(curr_taken_courses, intermediate_str, degree_plan_name)

if __name__ == '__main__':
    container = generate_degree_extraction_container('./input_files/degreeworks1.pdf')
    print(container._taken_courses)
    print(container._courses_needed_constuction_string)
    print(container._degree_plan_name)
    # Cases:
        # Case 1: 'POLS 1101'
        # Case 2: 'CPSC 4157 or 5157'
        # Case 3: 'POLS 1201 or CPSC 1234'
        # Case 4: 'POLS 1201 and 
        # Case 5: 'HIST 2111, 2112 or GA History Exam'
        # We need to load the course info dtb before handling case 6:
        # Case 6: 'CPSC 3@ or 4@ or 5@'
        # We need to handle electives
        # Case 7: Except Case: 1 Credit in @ 1@ or 2@ or 3@ or 4@ or 5@U Except ENGL 1101 or 1102*


# Shallow count node: requires n-many courses to be selected directly below it
# Select 2 of the following: ABCD 1234 or ASDF 1234 or AIDJ 1234
# Deep count node: requires n-many courses to be selected anywhere below it
# Possibly will not use
# Deep credit node: requires n-many credits to be selected anywhere below it
# Select 6 credits from the following; ABDC 1234 or ANFO 1256 or OAJF 1295
# Exhaustive node: a node suited for requiring all nodes directly below it
# APFN 1234 and ALJD 1235
# List node: a node suited for requiring all courses directly below it (no groups)
# Do not implement
# Deliverable course: an explicit instance of a course with a name and credits
# AJDH 1234
# Course protocol node: a regex form that may be filled out to become any course matching that regex pattern (protocol)
# Any course with an @
# Inserter node: a node that, when selected, adds another node of a given form (for sections that have variable number of selections).



# def get_courses_needed(file_name):
#     """
#     Gets the needed courses from the Degree Works.

#     Parameters
#     ----------
#     arg1 : file_name
#         File name of the DegreeWorks being parsed

#     Returns
#     -------
#     courses_needed_container
#         This container contains a recursively-defined tree data structure 
#         that holds the relationships between all needed courses found in
#         a DegreeWorks pdf.

#     """
#     intermediate_str = generate_tree_string(file_name)
#     container_name = 'Degree Plan'
#     return CoursesNeededContainer.make_from_course_selection_logic_string(container_name, intermediate_str)
