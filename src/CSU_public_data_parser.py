# Author: Max Lewis 01 January 2023
# Contributor: Vince Miller

from urllib.request import urlopen
from bs4 import BeautifulSoup
from recursive_descent_parser import *
import re
import pandas as pd
from driver_fs_functions import *
from dataframe_io import *
from course_info_container import *
import datetime
import pickle


# Webcrawls one page to retrieve Baccalaureate Degrees/Majors. (80 degrees as of April 2023) 
def get_baccalaureate_degrees():
    print("Retrieving Baccalaureate Degrees dictionary from https://catalog.columbusstate.edu/academic-degrees-programs/degrees-baccalaureate/")

    url = "https://catalog.columbusstate.edu/academic-degrees-programs/degrees-baccalaureate/"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    degrees = soup.find("div", class_="page_content")
    degrees = degrees.text
    degrees = degrees.replace("\xa0", " ")
    degree_pattern = r"[A-Z][a-z]+\s.+"
    degrees = re.findall(degree_pattern, degrees)
    degree_string = "\n"

    for degree in degrees:
        degree_string += f"{degree}\n"

    major_dict = get_majors_and_tracks(degree_string)
    file1 = get_source_path()
    file1 = get_source_relative_path(file1, "output_files/baccalaureate_degrees_dictionary.pickle")
    with open(file1, "wb") as f:
        pickle.dump(major_dict, f)

    print(f"Baccalaureate Degrees dictionary complete.\n")


# Author: Austin Lee
# Utilized method to tailor majors and tracks
def get_majors_and_tracks(degree_string):
    majors_dict = {}
    unfiltered_majors_list = degree_string.strip().split('\n')
    filtered_majors_list = []
    
    for item in unfiltered_majors_list:
        degree_type_search_obj = None
        degree_type_search_obj = re.search(r'\([a-zA-Z]+\)', item)
        if degree_type_search_obj:
            item = item.replace(degree_type_search_obj.group(), '')
        filtered_majors_list.append(item)
    
    for item in filtered_majors_list:
        if '-' in item:
            pattern = r"\s?-\s?"
            found_hiphen = re.search(pattern, item)
            found_hiphen = found_hiphen.group(0)
            key, value = item.split(found_hiphen, 1)
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


# Webcrawls one page to retrieve 116 department names of CSU.
def get_department_dict():
    url = "https://catalog.columbusstate.edu/course-descriptions/"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.text
    depts = re.findall(r"([A-Z]{3}[A-Z]?)\s-\s.", text)
    dept_dict = {}
    for dept in depts:
        dept_dict[dept] = None
    file1 = get_source_path()
    file1 = get_source_relative_path(file1, "output_files/department_dictionary.pickle")
    with open(file1, "wb") as f:
        pickle.dump(dept_dict, f)
    return dept_dict


# Webcrawls many pages (as of Mar 2023, 116 pages) to retrieve all course IDs (as of Mar 2023, 2854 course IDs) 
# and creates a master dictionary, which we pickle for reuse.  Takes around 35 seconds to perform function; may need to 
# optimize with threading.
def get_course_dict():
    print("Retrieving department dictionary from https://catalog.columbusstate.edu/course-descriptions/")
    depts = get_department_dict()
    l = len(depts)
    print(f"Dictionary complete with {l} departments.\n")
    refined_courses = {}
    for dept in depts:
        url = "https://catalog.columbusstate.edu/course-descriptions/"+str(dept).lower()+"/"
        print("Retrieving course dictionary from " + url)
        html = urlopen(url).read()
        soup = BeautifulSoup(html, features="html.parser")
        courses = soup.find_all("span", class_="text col-3 detail-code margin--tiny text--semibold text--huge")
        for course in courses:
            refined_courses[course.text] = None
        print(f"Course dictionary from {dept} complete.")
    file1 = get_source_path()
    file1 = get_source_relative_path(file1, "output_files/course_dictionary.pickle")
    with open(file1, "wb") as f:
        pickle.dump(refined_courses, f)
    l = len(refined_courses)
    print(f"Dictionary complete with {l} courses.\n")
    return refined_courses


# Using pickled file to retrieve information (dictionary for this case)
def get_pickle_file(filename):
    file1 = get_source_path()
    file1 = get_source_relative_path(file1, "output_files/" + filename)
    with open(file1, "rb") as f:
        obj = pickle.load(f)
    return obj


# This method is for Austin's degree works parser. He can copy and paste to his module.
def get_baccalaureate_degrees_pickle_file():
    file1 = get_source_path()
    file1 = get_source_relative_path(file1, "output_files/baccalaureate_degrees_dictionary.pickle")
    with open(file1, "rb") as f:
        obj = pickle.load(f)
    return obj


def update_course_info(dept=None):
    dept_dict = get_department_dict() #comment out for faster processing
    course_dict = get_course_dict() #comment out for faster processing
    major_dict = get_baccalaureate_degrees() #comment out for faster processing
    df_dict = {}
    dept_dict = get_pickle_file("department_dictionary.pickle") #Quick way
    course_dict = get_pickle_file("course_dictionary.pickle") #Quick way
    if type(dept) == str and dept in dept_dict.keys():
        df = parse_catalog(dept)
        df_dict[dept] = df
    elif type(dept) == list:
        for d in dept:
            if d in dept_dict.keys():
                df = parse_catalog(d)
                df_dict[d] = df
    elif dept == None:
        for depts in dept_dict.keys():
            df = parse_catalog(depts)
            df_dict[depts] = df
    else:
        print("Must specify department, department list, or no param for all departments.")
        return None

    file0 = get_source_path()
    file0 = get_source_relative_path(file0, 'output_files/New Course Info.xlsx')
    #df_dict = load_course_info(file0)
    container = CourseInfoContainer(df_dict)
    write_df_dict_xlsx(container, file0)


def parse_catalog(dept):
    print(f"Updating {dept}...")
    df = pd.DataFrame(columns=['courseID', 'courseName', 'hours', 'availability', 'prerequisites',
                               'co-requisites', 'recommended', 'restrictions', 'note', 'importance'])

    url = "https://catalog.columbusstate.edu/course-descriptions/"+str(dept).lower()+"/"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    all_course_blocks = soup.find_all("div", class_="courseblock")

    for index in range(len(all_course_blocks)):
        courseID = all_course_blocks[index].find("span", class_="text col-3 detail-code margin--tiny text--semibold text--huge").text
        #print(courseID)
        name = all_course_blocks[index].find("span", class_="text col-3 detail-title margin--tiny text--bold text--huge").text
        hours = all_course_blocks[index].find("span", class_="text detail-coursehours text--bold text--huge").text
 
        concurrent_courses = get_concurrent_courses(all_course_blocks[index])
        coreqs = get_coreqs(all_course_blocks[index], concurrent_courses)
        supplementary_prereqs = get_supplementary_prereqs(all_course_blocks[index], coreqs)
        prereqs = get_prereqs(all_course_blocks[index], coreqs, concurrent_courses, supplementary_prereqs)

        df.loc[len(df.index)] = [courseID, name, hours, "", prereqs, coreqs, "", "", "", ""]

    avail_dict = availability_crawl(dept)
    df = avail_placement_helper(df, avail_dict)
    print(f"Updating {dept} complete.")
    return df


def get_supplementary_prereqs(course_block, coreqs):
    supplementary_prereqs = ""
    first_sentence_pattern = r"^.*?(?<=\.)"
    course_body = course_block.find_all("p", class_="courseblockextra noindent")
    if no_supplementary_prereqs(course_body): return ""

    for index in range(len(course_body)):
        section = course_body[index].text
        if re.search(r"Prerequisites?:", section):
            section = re.search(first_sentence_pattern, section)

            # One case has typo: "Prerequisite: Prerequisite" and returns None
            if section == None: return ""
            section = section.group(0)
            section = section.replace("\xa0", " ")
            section = clean_supp_prereqs(section, coreqs)
            if no_req_after_cleaning(section): return ""
            supplementary_prereqs = section
    return supplementary_prereqs


def clean_supp_prereqs(section, coreqs):
    section = remove_coreq_string_and_other(section)
    if one_of_the_following_logic_in_section(section): 
        section = supp_logic_method(section, coreqs)
        return section
    elif any_two_courses_logic_in_section(section): 
        section = any_two_courses_logic_method(section, coreqs)
        return section
    elif comma_and_list_logic_in_section(section): 
        section = comma_and_list_logic_method(section, coreqs)
        return section
    elif any_three_of_the_following_logic_in_section(section): 
        section = any_three_of_the_following_logic_method(section, coreqs)
        return section
    else: 
        section = supp_logic_method(section, coreqs)
        return section


def remove_coreq_string_and_other(section):
    co_pattern = r"Co-?requisites?:.*"
    grade_pattern = r"with a\s*grade of [A-Z] or better"
    match1 = re.search(co_pattern, section)
    match2 = re.search(grade_pattern, section)
    if match1: section = section.replace(match1.group(0), "")
    if match2: section = section.replace(match2.group(0), "")
    return section


def any_three_of_the_following_logic_in_section(section):
    pattern = r"Any three of the following"
    match1 = re.search(pattern, section)
    if match1: return True
    else: return False


# Occurences of this logic is already handled, mapped, and validated per singular format (Requires 1) in the main prereq section. 
# For now we recognize and skip until future implementation.
def any_three_of_the_following_logic_method(section, coreqs):   
    return ""


def comma_and_list_logic_in_section(section):
    pattern = r"Prerequisites?: [A-Z]{3}[A-Z]?\s\d{4}[A-Z]?,"
    no_or_pattern = r"^(?!.*\bor\b).*$"
    match1 = re.search(pattern, section)
    match2 = re.search(no_or_pattern, section)
    if match1 and match2: return True
    else: return False


def comma_and_list_logic_method(section, coreqs):
    section = supp_logic_method(section, coreqs, and_logic=True)
    return section


def any_two_courses_logic_in_section(section):
    pattern = r"Any two courses from|two of the following"
    match1 = re.search(pattern, section)
    if match1: return True
    else: return False


# Occurences of this logic is already handled, mapped, and validated per singular format (Requires 1) in the main prereq section. 
# For now we recognize and skip until future implementation.
def any_two_courses_logic_method(section, coreqs):   
    return ""


def one_of_the_following_logic_in_section(section):
    pattern = r"One of the following:|any of the following courses"
    match1 = re.search(pattern, section)
    if match1: return True
    else: return False


# This method can be reused for numerous situations by adding optional parameters
def supp_logic_method(section, coreqs=None, and_logic=False):
    dept_pattern = r"([A-Z]{3}[A-Z]?)\s\d{4}[A-Z]?"
    digit_pattern = r"^\d{4}[A-Z]?"
    tokens = create_tokenized_logic_for_one_of_the_following_method(section)
    dept = ""

    for i, token in enumerate(tokens):
        if re.search(dept_pattern, token):
            dept = re.search(dept_pattern, token)
            dept = dept.group(1)
        elif re.search(digit_pattern, token):
            tokens[i] = f"{dept} {token}"
        elif token == ",": 
            if and_logic:
                tokens[i] = "and"
            else:
                tokens[i] = "or"
        elif token == ";": 
            if and_logic:
                tokens[i] = "and"
            else:
                tokens[i] = "or"
        elif token == "&": 
            tokens[i] = "and"
        elif token == "/": 
            tokens[i] = "or"

    section = " ".join(tokens) 
    section = validate_courses(section, coreqs)
    return section


def create_tokenized_logic_for_one_of_the_following_method(section):
    tokens = None
    regex_pattern = r"/|&|,|;|\(|\)|and|or|[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?|\d{4}[A-Z]?"
    tokens = re.findall(regex_pattern, section) 
    return tokens


def no_supplementary_prereqs(course_body):
    no = True
    first_sentence_pattern = r"^.*?(?<=\.)"
    for index in range(len(course_body)):
        section = course_body[index].text
        section = section.replace("\xa0", " ")
        section = re.search(first_sentence_pattern, section)
        if section != None:
            section = section.group(0)
            if re.search(r"Prerequisites?:", section) and re.search(r"[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?", section):
                no = False
    return no


def get_concurrent_courses(course_block):
    concurrent_courses = []
    concurrent_pattern = r"([A-Z]{3}[A-Z]?\s\d{4}[A-Z]?)\s\(may be taken concurrently\)"
    course_body = course_block.find_all("p", class_="courseblockextra noindent")
    for index in range(len(course_body)):
        course_body[index] = course_body[index].text
        course_body[index] = course_body[index].replace("\xa0", " ")
    for index in range(len(course_body)):
        courses = re.findall(concurrent_pattern, course_body[index])
        concurrent_courses.extend(courses)
    return concurrent_courses


def avail_placement_helper(df, avail_dict):
    if avail_dict == {}: return df
    df = df
    for course in avail_dict.keys():
        if course in df["courseID"].values:
            avail = avail_translator(avail_dict[course])
            index = df[df['courseID'] == course].index[0]
            df.at[index, "availability"] = avail
    return df   


def avail_translator(number):
    if number == 1: return "-- Sp --"
    elif number == 2: return "-- -- Su"
    elif number == 3: return "-- Sp Su"
    elif number == 4: return "Fa -- --"
    elif number == 5: return "Fa Sp --"
    elif number == 6: return "Fa -- Su"
    elif number == 7: return "Fa Sp Su"
    else: return "Fa Sp Su"


def availability_crawl(dept):
    avail_dict = {}
    year = datetime.datetime.now().year
    course_pattern = r"([A-Z]{3}[A-Z]?\d{4}[A-Z]?)"
    for page in range(3):
        if page == 0: i = 2
        elif page == 1: i = 5
        else: i = 8
        url1 = "https://columbusstate.gabest.usg.edu/B300/hwskcsu.courses?term_in="+str(year)+str(0)+str(i)+"&message_in=&subject="+str(dept)+"&levl=AL"
        html1 = urlopen(url1).read()
        soup1 = BeautifulSoup(html1, features="html.parser")
        all_course_blocks = soup1.find_all("td", class_="courses")
        lst1 = []
        for section in all_course_blocks:
            section = section.text
            course = re.findall(course_pattern, section)
            if course != []: lst1.append(course)

        if page == 0: x = 1
        elif page == 1: x = 2
        else: x = 4
        lst1 = delete_duplicates(lst1)
        if lst1 != []:
            for course in lst1:
                course = split_letter_digit(course[0])
                if course in avail_dict.keys():
                    avail_dict[course] += x
                else:
                    avail_dict[course] = x
    return avail_dict


def split_letter_digit(string):
    match = re.search(r'\d', string)
    if match:
        digit_index = match.start()
        result = string[:digit_index] + " " + string[digit_index:]   
    return result


def get_prereqs(course_block, coreqs, concurrent_courses, supplementary_prereqs):
    prereqs = ""
    course_body = course_block.find_all("p", class_="courseblockextra noindent")
    if no_prereqs(course_body) and supplementary_prereqs == "": return ""
    if no_prereqs(course_body) and supplementary_prereqs != "": return only_supp_prereqs(supplementary_prereqs, concurrent_courses)

    for index in range(len(course_body)):
        section = course_body[index].text
        if re.search(r"Prerequisite\(s\)", section):
            section = clean_prereqs_section(section, coreqs, supplementary_prereqs)
            if no_req_after_cleaning(section): return ""
            prereqs = build_tree_string(section, concurrent_courses)
    return prereqs


def only_supp_prereqs(supplementary_prereqs, concurrent_courses):
    supplementary_prereqs = build_tree_string(supplementary_prereqs, concurrent_courses)
    return supplementary_prereqs


def get_coreqs(course_block, concurrent_courses):
    coreqs = ""
    course_body = course_block.find_all("p", class_="courseblockextra noindent")
    for index in range(len(course_body)):
        course_body[index] = course_body[index].text
        course_body[index] = course_body[index].replace("\xa0", " ")
    if no_coreqs(course_body): return ""
    for index in range(len(course_body)):
        section = course_body[index]
        section = re.search(r"Co-?requisites?:\s*[^\.]+\.", section)
        if section:
            section = section.group(0)
            section = delete_concurrent_courses_from_coreqs(section, concurrent_courses)
            section = supp_logic_method(section)
            if no_req_after_cleaning(section): return ""
            tokens = create_tokenized_logic(section)
            tree = RecursiveDescentParser(tokens)
            tree = tree.expression()
            coreqs = stringify_subtree(tree)
    return coreqs


def delete_concurrent_courses_from_coreqs(section, concurrent_courses):
    for course in concurrent_courses:
        if course in section:
            section = section.replace(course, "")
    return section


def no_prereqs(course_body):
    no = True
    for index in range(len(course_body)):
        section = course_body[index].text
        match1 = re.search(r"Prerequisite\(s\)", section)
        if match1: no = False
    return no


def no_coreqs(course_body):
    no = True
    for index in range(len(course_body)):
        section = course_body[index]
        match1 = re.search(r"Co-?requisites?:\s*[^\.]+\.", section)
        if match1:
            match2 = re.search(r"[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?", match1.group(0))
            if match2:
                no = False
    return no


def no_req_after_cleaning(section):
    no = True
    if re.search(r"[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?", section): no = False
    return no


# Cleaning up text for easier formatting.
def clean_prereqs_section(section, coreqs, supplementary_prereqs):
    concurrently = re.findall(r"( \(may be taken concurrently\))", section)
    letter = re.findall(r" with a minimum grade of ([A-D])", section)
    if concurrently != []: section = section.replace(concurrently[0], "")
    if letter != []: section = section.replace(" with a minimum grade of " + letter[0], "")
    section = section.replace("Prerequisite(s): ", "")
    section = section.replace("\xa0", " ")
    if supplementary_prereqs != "": section = combine_main_prereqs_with_supp_prereqs(section, supplementary_prereqs)
    section = validate_courses(section, coreqs)
    return section


def combine_main_prereqs_with_supp_prereqs(section, supplementary_prereqs):
    pattern = r"[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?"
    main_courses = re.findall(pattern, section)
    supplementary_prereqs = create_tokenized_logic(supplementary_prereqs)

    if main_courses != []:
        for course in main_courses:
            if course in supplementary_prereqs:
                supplementary_prereqs.remove(course)

        while supplementary_prereqs != [] and re.search(pattern, supplementary_prereqs[0]) == None:
            supplementary_prereqs.pop(0)

    supplementary_prereqs = " ".join(supplementary_prereqs)   
    match1 = re.search(pattern, supplementary_prereqs)

    if match1 == None: return section
    else:
        section = f"{section} and {supplementary_prereqs}"
        return section


def validate_courses(section, coreqs=None):
    courses_with_words = verify_and_create_list_logic(section)

    #if coreqs: courses_with_words = delete_coreq_in_prereq(courses_with_words, coreqs)# Uncomment to delete coreqs from prereqs
    courses_with_words = edit_tokens(courses_with_words)
    section = " ".join(courses_with_words)
    return section


def edit_tokens(tokens, repeat=True):
    tokens = tokens
    tokens = delete_extra_parens(tokens)
    tokens = delete_empty_parens(tokens)
    tokens = delete_parens_with_one_course_inside(tokens)
    tokens = delete_false_paren_expression(tokens)
    stack = delete_repeated_values_keep_left_association(tokens)

    # For good measure we edit tokens again. This one step recursion should cover any future updates of CSU website.
    if repeat: stack = edit_tokens(stack, repeat=False)
    return stack


def delete_extra_parens(tokens):
    paren_count = 0
    for token in tokens:
        if token == "(": paren_count += 1
        elif token == ")": paren_count -= 1
    if paren_count > 0:
        for i in range(paren_count):
            tokens.remove("(")
    elif paren_count < 0:
        absolute = abs(paren_count)
        for i in range(absolute):
            tokens.remove(")")
    return tokens


def delete_empty_parens(tokens):
    for index,token in reversed(list(enumerate(tokens))):
        if index+1 < len(tokens) and token == "(" and tokens[index+1] == ")":
            tokens.pop(index+1)
            tokens.pop(index)
    return tokens


def delete_parens_with_one_course_inside(tokens):
    for index,token in reversed(list(enumerate(tokens))):
        if index+2 < len(tokens) and token == "(" and re.search(r"[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?", tokens[index+1]) and tokens[index+2] == ")":
            tokens.pop(index+2)
            tokens.pop(index)
    return tokens


# Delete expressions such as: '(' 'and' ')', '(' 'or' ')'
def delete_false_paren_expression(tokens):
    for index,token in reversed(list(enumerate(tokens))):
        if index+2 < len(tokens) and token == "(" and re.search(r"and|or", tokens[index+1]) and tokens[index+2] == ")":
            tokens.pop(index+2)
            tokens.pop(index+1)
            tokens.pop(index)
    return tokens


# Deletes repeated values leaving left association integrity. Also, corrects for incorrect format and edits accordingly.
def delete_repeated_values_keep_left_association(tokens):
    stack = []
    for token in tokens:
        if token == ")":
            if stack[-1] == "and" or stack[-1] == "or":
                stack.pop()
            stack.append(token)
        elif token == "(":
            stack.append(token)
        elif token == "and" or token == "or":
            while True:
                if stack == []: break
                elif stack[-1] == "and" or stack[-1] == "or":
                    stack.pop()
                else: break
            if stack != [] and stack[-1] != "(":
                stack.append(token)
        else:
                stack.append(token)

    # If 'and' or 'or' at start or end, delete.
    if stack != [] and (stack[0] == "and" or stack[0] == "or"): stack.pop(0)
    if stack != [] and (stack[-1] == "and" or stack[-1] == "or"): stack.pop()
    return stack


# Verifies if course in master dictionary and also creates tokenized logic list.
def verify_and_create_list_logic(section):
    course_dict = get_pickle_file("course_dictionary.pickle") #Quick way
    regex_pattern = r"\(|\)|and|or|[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?"
    course_pattern = r"([A-Z]{3}[A-Z]?\s\d{4}[A-Z]?)"
    courses_with_words = re.findall(regex_pattern, section)
    # Here we validate courses and delete if not valid.
    for course in courses_with_words:
        valid_course = re.findall(course_pattern, course)
        if valid_course != [] and valid_course[0] not in course_dict.keys():
            courses_with_words.remove(valid_course[0])
    return courses_with_words


# Need to refactor, check list of coreqs to delete. As of now we will not delete any coreqs form prereqs.
def delete_coreq_in_prereq(courses_with_words, coreqs):
    if coreqs != "":
        pattern = r"([A-Z]{3}[A-Z]?\s\d{4}[A-Z]?)"
        coreqs = re.findall(pattern, coreqs)
        for req in coreqs:
            if req in courses_with_words:
                courses_with_words.remove(req)
    return courses_with_words


def delete_duplicates(course_list):
    new_list = []
    for course in course_list:
        if course not in new_list:
            new_list.append(course)
    return new_list


def build_tree_string(section, concurrent_courses=None):
    tree_string = ""
    tokens = create_tokenized_logic(section)
    tree = RecursiveDescentParser(tokens)
    tree = tree.expression()
    if concurrent_courses: append_deliverable_concurrent_flag(tree, concurrent_courses)
    tree_string = stringify_subtree(tree)
    return tree_string


def create_tokenized_logic(section):
    tokens = None
    regex_pattern = r"\(|\)|and|or|[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?"
    tokens = re.findall(regex_pattern, section)
    return tokens

#update_course_info()
# print(get_baccalaureate_degrees_pickle_file())