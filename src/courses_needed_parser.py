# Austin Lee and Thomas Merino 1/23/2023
# CPSC 4175 Project

from alias_module import get_latest_id
# from courses_needed_container import CoursesNeededContainer, \
#     DeliverableCourse, CourseProtocol, CourseInserter, ExhaustiveNode, \
#     ShallowCountBasedNode, DeepCountBasedNode, DeepCreditBasedNode
import re
from pypdf import PdfReader

# TODO:
    # 1. Create a tokenized_list that has all chunks normalized into predictable logical structures
    # 2. Process each chunk fully with all trimming functions in a loop until the chunk no longer changes.
        # Once all chunks are static, remove all empty chunks.
    # 3. Interface with tree generator.

def remove_substring_after_last_relevant(input_string):
    match_reversed = re.search(r'[0-9]{4}|@|\)', input_string[::-1])
    end_index = len(input_string) - match_reversed.start() if match_reversed else 0
    return input_string[:end_index]

def remove_minor_in(chunk, index, list):
    chunk = chunk[:chunk.find('Minor in ')] if 'Minor in ' in chunk else chunk
    return chunk

def remove_select_one(chunk, index, list):
    chunk = chunk[:chunk.find('Select one as a pre-requesite for ')] if 'Select one as a pre-requesite for ' in chunk else chunk
    return chunk

def remove_empty(chunk, index, list):
    if len(chunk) == 0:
        list.pop(index)

def remove_empty_items(list):
    return [item for item in list if item]

def remove_major_in(chunk, index, list):
    chunk = chunk[:chunk.find('Major in ')] if 'Major in ' in chunk else chunk
    return chunk

def remove_AREA_X(chunk, index, list):
    chunk = chunk[:chunk.find('AREA ')] if 'AREA ' in chunk else chunk
    return chunk

def remove_chunk_without_course_block(chunk, index, list):
    if not re.search(r'([A-Z]{4}\s{1})', chunk):
        print(f'executing on chunk: {chunk}')
        chunk = ''
    return chunk

# find the number of season year groups
# find all instances of course block patterns and record their end indices
# get end index of the (number of season year groups + 1 from the end of the list)
def remove_curr_taken_courses(chunk, index, list):
    new_chunk = ''
    num_season_year_blocks = len(re.findall(r'(Spring|Fall)\s\d{4}', chunk))
    courses_block_iterator = re.finditer(r'([A-Z]{4}\s{1}\d{4}( \))?)|(or \d{4}( \))?)|(, \d{4}( \))?)|(\d@( \))?)', chunk)
    course_block_indices_list = []
    # print(f'chunk: {chunk}')
    # print(f'courses_block_iterator: {courses_block_iterator}')
    for course in courses_block_iterator:
        # print(f'course_block_iterator_item: {course.groups()}')
        # print(course.end())
        course_block_indices_list.append(course.end())
    # print(course_block_indices_list)
        # print(f'course_block_iterator_item: {course.groups()}')
    # print(f'chunk before slicing: {chunk}')
    # print()
    # print(course_block_indices_list)
    
    if num_season_year_blocks:
        # print('block ACTIVATEDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
        # print(chunk)
        # print(f'course_block_indices_list: {course_block_indices_list}')
        # print(f'len(course_block_indices_list: {len(course_block_indices_list)}')
        # print(f'num_season_year_blocks: {num_season_year_blocks}')
        # print(f'course_block_indices_list[len(course_block_indices_list) - num_season_year_blocks] - 1: {course_block_indices_list[len(course_block_indices_list) - (num_season_year_blocks + 1)] + 1}')
        new_chunk = chunk[:course_block_indices_list[len(course_block_indices_list) - num_season_year_blocks - 1]]
        # print(f'new chunk: {new_chunk}')
    else:
        new_chunk = chunk
    # print(f'newchunk: {new_chunk}')
    return new_chunk

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
    intermediate_substring = ''

    # indicates that a ... has been found
    if (re.search(r'(Choose [0-9]{1} of the following:)', chunk)):
        pass
    
    if (re.search(r'()', chunk)):
        pass
    


def get_courses_needed(file_name): 
    """
    Gets the needed courses from the Degree Works.

    Parameters
    ----------
    arg1 : file_name
        File name of the DegreeWorks being parsed

    Returns
    -------
    courses_needed_container
        This container contains a recursively-defined tree data structure 
        that holds the relationships between all needed courses found in
        a DegreeWorks pdf.

    """
    with open(file_name, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        intermediate_str = ''
        still_needed_chunks_list = [] # Holds all unprocessed/filtered chunks
        document_string = '' # Holds the entire parsed pdf text
        for page in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page].extract_text()
            document_string += page_text
        # print(document_string)
        start = document_string.find("Still Needed:") # Used to initiate every chunk
        while start != -1:
            end = document_string.find("Still Needed:", start + 1) # Searches for next instance of phrase
            if end != -1:
                still_needed_chunks_list.append(document_string[start:end]) 
                start = end
            else: # This case accounts for the final instance of the phrase
                still_needed_chunks_list.append(document_string[start:document_string.find('Fallthrough', start + 1)])
                break
        # for chunk in still_needed_chunks_list:
        #     print(chunk)
        #     print()
        currently_in_logical_block = False # Used to track if currently parsing a multi-line logical block
        logically_grouped_list = [] # Holds the chunks that contain all logical groupings of needed courses
        logical_chunk_string = '' # Holds the current chunk being parsed

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
        for chunk in logically_grouped_list:
            if not 'See ' in chunk and not 'YOU MUST APPLY FOR GRADUATION' in chunk and not 'Still Needed: Outcomes Assessment Exam' in chunk:
                delimiter = 'Still Needed:'
                chunk = chunk[chunk.index(delimiter)+(len(delimiter)+1):]
                if chunk[0] == ' ':
                    chunk = chunk[1:]
                chunk = remove_substring_after_last_relevant(chunk)
                filtered_list.append(chunk)
        
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
        print(intermediate_str)
        print('-'*60)
        for item in complex_list:
            print(item)
            print()
    
    return intermediate_str

if __name__ == "__main__":
    print(get_courses_needed('./src/input_files/degreeworks1.pdf'))

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
def check_pdf_parser_consistency(filename):
    with open(filename, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        document_string = '' # Holds the entire parsed pdf text
        for page in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page].extract_text()
            document_string += page_text

        for i in range(1, 11):
            with open(f'{filename}_{i}.txt', 'w') as txt_file:
                txt_file.write(document_string)

        contents = []
        for i in range(1, 11):
            with open(f'{filename}_{i}.txt', 'r') as txt_file:
                contents.append(txt_file.read())

        for content in contents[1:]:
            if content != contents[0]:
                return False
        return True