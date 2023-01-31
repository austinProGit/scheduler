# Austin Lee 1/23/2023
# CPSC 4175 Project

from alias_module import get_latest_id
# from courses_needed_container import CoursesNeededContainer, \
#     DeliverableCourse, CourseProtocol, CourseInserter, ExhaustiveNode, \
#     ShallowCountBasedNode, DeepCountBasedNode, DeepCreditBasedNode
import re
from pypdf import PdfReader

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
        required_courses = []
        still_needed_chunks_list = [] # Holds all unprocessed/filtered chunks
        document_string = '' # Holds the entire parsed pdf text
        for page in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page].extract_text()
            document_string += page_text
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
        for chunk in still_needed_chunks_list:
            if 'of the following:' in chunk or ') or' in chunk: # Indicates the start or continuance of a logical chunk
                currently_in_logical_block = True
            elif currently_in_logical_block:
                    currently_in_logical_block = False
                    logical_chunk_string += chunk # Appends last portion of a logical chunk
                    logically_grouped_list.append(logical_chunk_string)
            if currently_in_logical_block:
                logical_chunk_string += chunk
            else:
                logically_grouped_list.append(chunk) # Appends simple chunks
        filtered_list = [] # Holds the filtered chunks
    
    return required_courses # Does not currently meet final function signature

if __name__ == "__main__":
    print(get_courses_needed('./src/input_files/degreeworks1.pdf'))      

    # TODO: 
        # filter out filler chunks ex: Outcomes Assessment Exam
            # no XXXX XXXX or XXXX X@
        # filter out courses taken information. Ex:
            # find Season Year, backtrack to last mention of XXXX, remove from chunk
        # filter out the case where 'Select one as a pre-requesite for STAT 3127'
            # comes before the still needed
        # filter out the 'still needed:'
        # filter out anything that has no XXXX XXXX or XXXX X@

    # TODO:
        # Create a filtered_list that has all garbage removed from each chunk. Junk chunks are not added to filtered_list

    # TODO:
        # Creat a tokenized_list that has all chunks normalized into predictable logical structures

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

    # Useful code:
        # matches = re.findall(r'[A-Z]{4}\s{1}\d{4}', lines[i][lines[i].index('Still Needed:') + 12:])


    
    