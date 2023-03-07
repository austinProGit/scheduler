# Author: Max Lewis 01 January 2023
# Contributor: Vince Miller

from urllib.request import urlopen
from bs4 import BeautifulSoup
from recursive_descent_parser import *
import re
import pandas as pd
from driver_fs_functions import *
#from alias_module import get_latest_id
from dataframe_io import *
from course_info_container import *
import pickle


# Webcrawls one page to retrieve 115 department names of CSU.
def get_department_dict():
    url = "https://catalog.columbusstate.edu/course-descriptions/"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")
    text = soup.text
    depts = re.findall(r"([A-Z]{3}[A-Z]?)\s-\s.", text) # May need to change ' ' to \s...
    dept_dict = {}
    for dept in depts:
        dept_dict[dept] = None
    file1 = get_source_path()
    file1 = get_source_relative_path(file1, "output_files/department_dictionary.pickle")
    with open(file1, "wb") as f:
        pickle.dump(dept_dict, f)
    return dept_dict


# Webcrawls many pages (as of Feb 2023, 115 pages) to retrieve all course IDs (as of Feb 2023, 2783 course IDs) 
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
        print("Course dictionary from " + str(dept) + " complete.")
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


def update_course_info(dept=None):
    #dept_dict = get_department_dict() #commented out for faster processing
    #course_dict = get_course_dict() #comment out for faster processing
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
        print("Must specify department, department list, or all.")
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
        course_body = all_course_blocks[index].find_all('p', class_='courseblockextra noindent')
        courseID = all_course_blocks[index].find("span", class_="text col-3 detail-code margin--tiny text--semibold text--huge").text
        name = all_course_blocks[index].find("span", class_="text col-3 detail-title margin--tiny text--bold text--huge").text
        hours = all_course_blocks[index].find("span", class_="text detail-coursehours text--bold text--huge").text

        # We get the coreqs first so we can delete them out of the prereqs.
        coreqs = get_coreqs(all_course_blocks[index])
        prereqs = get_prereqs(all_course_blocks[index], coreqs)


        df.loc[len(df.index)] = [courseID, name, hours, "", prereqs, coreqs, "", "", "", ""]

    avail_dict = availability_crawl(dept)
    df = avail_placement_helper(df, avail_dict)
    print(f"Updating {dept} complete.")
    return df


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
    course_pattern = r"([A-Z]{3}[A-Z]?\d{4}[A-Z]?)"
    for page in range(3):
        if page == 0: i = 2
        elif page == 1: i = 5
        else: i = 8
        url1 = "https://columbusstate.gabest.usg.edu/B300/hwskcsu.courses?term_in=20230"+str(i)+"&message_in=&subject="+str(dept)+"&levl=AL"
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


def get_prereqs(course_block, coreqs):
    prereqs = ""
    course_body = course_block.find_all("p", class_="courseblockextra noindent")
    if no_prereqs(course_body): return ""
    for index in range(len(course_body)):
        section = course_body[index].text
        if re.search(r"Prerequisite\(s\)", section):
            section = clean_prereqs_section(section, coreqs)
            if no_req_after_cleaning(section): return ""
            prereqs = build_tree_string(section)
    return prereqs


def get_coreqs(course_block):
    coreqs = ""
    course_body = course_block.find_all("p", class_="courseblockextra noindent")
    for index in range(len(course_body)):
        course_body[index] = course_body[index].text
        course_body[index] = course_body[index].replace("\xa0", " ")
    if no_coreqs(course_body): return ""
    for index in range(len(course_body)):
        section = course_body[index]
        if re.search(r"Co-?requisite:\s[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?|Corequisite:\sConcurrent\senrollment\sin\s[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?", section):
            coreqsA = re.findall(r"Co-?requisite:\s([A-Z]{3}[A-Z]?\s\d{4}[A-Z]?)", section)
            coreqsB = re.findall(r"Corequisite:\sConcurrent\senrollment\sin\s([A-Z]{3}[A-Z]?\s\d{4}[A-Z]?)", section)
            tree = RecursiveDescentParser(coreqsA) if coreqsA != [] else RecursiveDescentParser(coreqsB)
            tree = tree.expression()
            coreqs = stringify_subtree(tree)

    return coreqs


def no_prereqs(course_body):
    no = True
    for index in range(len(course_body)):
        section = course_body[index].text
        match1 = re.search(r"Prerequisite\(s\)", section)
        # Need to handle this in later implementation. Where prereqs are in another section or are in both.  
        #match2 = re.search(r"Prerequisite:\s[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?", section)
        if match1:no = False # or match2: no = False
    return no


def no_coreqs(course_body):
    no = True
    for index in range(len(course_body)):
        section = course_body[index]
        match1 = re.search(r"Co-?requisite:\s[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?", section)
        match2 = re.search(r"Corequisite:\sConcurrent\senrollment\sin", section)
        if match1 or match2: no = False
    return no


def no_req_after_cleaning(section):
    no = True
    if re.search(r"[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?", section): no = False
    return no


# Cleaning up text for easier formatting.
def clean_prereqs_section(section, coreqs):
    concurrently = re.findall(r"( \(may be taken concurrently\))", section)
    letter = re.findall(r" with a minimum grade of ([A-D])", section)
    if concurrently != []: section = section.replace(concurrently[0], "")
    if letter != []: section = section.replace(" with a minimum grade of " + letter[0], "")
    section = section.replace("Prerequisite(s): ", "")
    section = section.replace("\xa0", " ")
    # There is much more cleaning to do in the future when we integrate other prereq sections of the website
    section = validate_courses(section, coreqs)
    return section


def validate_courses(section, coreqs):
    courses_with_words = verify_and_create_list_logic(section)
    courses_with_words = delete_coreq_in_prereq(courses_with_words, coreqs)
    courses_with_words = delete_extra_ands_ors(courses_with_words)
    # Join list together to form string
    section = " ".join(courses_with_words)
    section = section.replace("( ", "(")
    section = section.replace(" )", ")")
    # If only one course in parentheses then remove parentheses.
    section = re.sub(r'\((\s*[A-Z]+\s*\d+[A-Z]?\s*)\)', r'\1', section)
    # If 'or' or 'and' at start or end remove them.
    section = re.sub(r'^\(?\s?or\s?|^\(?\s?and\s?', "", section)
    section = re.sub(r'or\s*$|and\s*$', "", section)
    return section


# Verifies if course in master dictionary and also creates tokenized logic in the form of a list.
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


def delete_coreq_in_prereq(courses_with_words, coreqs):
    if coreqs != "":
        pattern = r"([A-Z]{3}[A-Z]?\s\d{4}[A-Z]?)"
        coreq = re.findall(pattern, coreqs)
        if coreq[0] in courses_with_words:
            courses_with_words.remove(coreq[0])
    return courses_with_words


# Here we delete extra occurences of 'or' or 'and' and other strings; indexing in reverse order
def delete_extra_ands_ors(courses_with_words):
    previous_item = None
    for i in range(len(courses_with_words)-1, -1, -1):
        current_item = courses_with_words[i]
        if current_item == previous_item:
            courses_with_words.pop(i)
        if (current_item == "and" and previous_item == "or") or (current_item == "or" and previous_item == "and"):
            courses_with_words.pop(i)
        if (current_item == "and" or current_item == "or") and (previous_item == ")"):
            courses_with_words.pop(i)
        if (current_item == "(") and (previous_item == "and" or previous_item == "or"):
            courses_with_words.pop(i+1)
        previous_item = current_item
    return courses_with_words


# May not need this later
def delete_duplicates(course_list):
    new_list = []
    for course in course_list:
        if course not in new_list:
            new_list.append(course)
    return new_list


def build_tree_string(section):
    tree_string = ""
    #print(section)
    tokens = create_tokenized_logic(section)
    parser = RecursiveDescentEditor(tokens)
    parser.operator()
    tokens = parser.new_tokens
    tree = RecursiveDescentParser(tokens)
    tree = tree.expression()
    tree_string = stringify_subtree(tree)
    #print(tokens)
    #print(tree_string)
    return tree_string


def create_tokenized_logic(section):
    tokens = None
    regex_pattern = r"\(|\)|and|or|[A-Z]{3}[A-Z]?\s\d{4}[A-Z]?"
    tokens = re.findall(regex_pattern, section)
    return tokens

#lst = ["ACCT", "CPSC", "CYBR"]
#update_course_info()