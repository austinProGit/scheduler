# Author: Vincent Miller 19 September 2022
# Contributor: Max Lewis 01 January 2023

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
from driver_fs_functions import *
from alias_module import get_latest_id

def update_course_info():
    """One click update Course Info.xlsx
       This function will go to the Course Descriptions for CPSC, CYBR, and MATH to pull information
       in order to recreate our current Course Info.xlsx"""
    # create new file and write cpsc courses

    file1 = get_source_path()
    file1 = get_source_relative_path(file1, 'output_files/NEW Course Info.xlsx')
    excel_writer = pd.ExcelWriter(file1)

    parse_catalog(excel_writer, 'cpsc')
    excel_writer.close()
    # open file to append cybr courses to it
    excel_writer = pd.ExcelWriter(file1, mode='a')
    parse_catalog(excel_writer, 'cybr')
    excel_writer.close()
    # open file to append math courses to it
    excel_writer = pd.ExcelWriter(file1, mode='a')
    parse_catalog(excel_writer, 'math')
    excel_writer.close()

    # because our program just reads the first sheet, some data needs to be merged to the first sheet
    # read each sheet as a dataframe
    main_df = pd.read_excel(file1, sheet_name='CPSC')
    cyber_df = pd.read_excel(file1, sheet_name='CYBR')
    math_df = pd.read_excel(file1, sheet_name='MATH')

    # append cybr
    main_df = pd.concat([main_df, cyber_df])
    # append ONLY MATH 1113, MATH 2125, MATH 5125
    main_df = pd.concat([main_df, math_df[math_df["courseID"] == "MATH 1113"]])
    main_df = pd.concat([main_df, math_df[math_df["courseID"] == "MATH 2125"]])
    main_df = pd.concat([main_df, math_df[math_df["courseID"] == "MATH 5125U"]])
    # we don't use the letters, so remove to avoid errors
    main_df = main_df.replace("MATH 5125U", "MATH 5125")
    # some of these courses don't show an availability, Ex: Selected Topics, changed to available
    main_df = main_df.replace("-- -- --", "Fa Sp Su")
    # add cpsc generic elective
    main_df.loc[len(main_df.index)] = ["CPSC 3XXX", "Generic Elective", "(3-0-3)", "Fa Sp Su",
                                       '', '', '', 0, '', '', 60]

    # write final New Course Info.xlsx
    excel_writer = pd.ExcelWriter(file1)
    main_df.to_excel(excel_writer, sheet_name="CPSC", index=False)
    excel_writer.close()

    # add Excused Prerequisites, MISM 3145, MISM 3115, MISM 3109, MATH 1111
    excel_writer = pd.ExcelWriter(file1, mode='a')
    excused_prereq = {'courseID': ["MISM 3145", "MISM 3115", "MISM 3109", "MATH 1111", 'MATH 1131', 'MATH 1132']}
    excused_df = pd.DataFrame(excused_prereq)
    excused_df.to_excel(excel_writer, sheet_name="ExcusedPrereqs", index=False)
    excel_writer.close()


def parse_catalog(excel_writer, department):
    """inputs 4 letter department acronym, parses website catalog for accurate information
       creates and saves Course Info.xlsx """
    file1 = get_source_path()
    file1 = get_source_relative_path(file1, 'input_files/course_availabilities.xlsx')
    def extract_requisites():
        """helper function to parse and return prerequisites and co-requisites"""
        _prerequisites = ''
        _co_requisites = ''
        _course_pattern = r'[A-Z]{4}\s{1}\d{4}'
        _co_requisite_pattern = r'[A-Z]{4}\s{1}\d{4} \(may be taken concurrently\)'

        # course_body[0] is description, [1] is prerequisites OR repeatability [2] is repeatability
        # apparently "restrictions" is a part of this, but I don't know if it ever gets to 4 total
        try:  # course_body list varies in size from 1 to 3
            # extract requisites
            # replace occasional hex value, \xa0, is in between course id's. Ex: MATH\xa01113
            _prerequisites = re.findall(_course_pattern, str(course_body[1].text).replace("\xa0", " "))
            _co_requisites = re.findall(_co_requisite_pattern, str(course_body[1].text).replace("\xa0", " "))

            # remove excess from co-requisite
            _co_requisites = re.findall(_course_pattern, str(_co_requisites))
            # remove co-requisite from prerequisites
            for element in _co_requisites:
                if element in _prerequisites:
                    _prerequisites.remove(element)
            
            # TODO: is this needed?
            # CPSC 2106 became CYBR 2160
            for element in _prerequisites:
                if element == "CPSC 2106":
                    _prerequisites.remove(element)
                    _prerequisites.append("CYBR 2160")

            # remove duplicates by converting to set
            _prerequisites = [*set(_prerequisites)]
            _co_requisites = [*set(_co_requisites)]

            # these courses are either typo's or out of date and shouldn't have been in the catalog
            bad_courses = ['CSCI 1301', 'CYBR 2106', 'CPSC 5115']
            for element in bad_courses:
                if element in _prerequisites:
                    _prerequisites.remove(element)

            # sort for visual pleasure
            _prerequisites.sort()
            _co_requisites.sort()

            # convert back to string, as to not break Lew's container
            _prerequisites = ', '.join(_prerequisites)
            _co_requisites = ', '.join(_co_requisites)
        except IndexError:
            # course has no prerequisites, readability, or restriction; only description
            pass

        return _prerequisites, _co_requisites

    def get_availability(_course_id):
        """helper function to get course availabilities"""
        try:
            _df = pd.read_excel(file1, sheet_name='Sheet1')
            _availability = _df.loc[_df.index[_df['course_ID'] == _course_id]]['availability'].to_list()
            return _availability[0]
        except IndexError:
            return 'Fa Sp Su'

    def get_importance(_course_id):
        """helper function to get course importance"""
        try:
            _df = pd.read_excel(file1, sheet_name='Sheet1')
            _importance = _df.loc[_df.index[_df['course_ID'] == _course_id]]['importance'].to_list()
            return _importance[0]
        except IndexError:
            return '-1'

    # open url, load into bs4 object
    url = "https://catalog.columbusstate.edu/course-descriptions/"+str(department).lower()+"/"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # extract all course block data
    all_course_blocks = soup.find_all('div', class_='courseblock')

    # create dataframe to hold course info
    course_info_df = pd.DataFrame(columns=['courseID', 'courseName', 'hours', 'availability', 'prerequisites',
                                           'co-requisites', 'recommended', 'isElective', 'restrictions', 'note',
                                           'importance'])
    
    # loop to add course data to dataframe
    for index in range(len(all_course_blocks)):
        # extract current course header and body html data
        course_header = all_course_blocks[index].find_all('div', class_='cols noindent')
        course_body = all_course_blocks[index].find_all('p', class_='courseblockextra noindent')
        # extract course id
        course_id = course_header[0].find('span', class_='text col-3 detail-code margin--tiny text--semibold text--huge')
        if re.search(r'CPSC 6', course_id.text):
            break
        course_id = get_latest_id(course_id.text)
        # extract course name
        course_name = course_header[0].find('span', class_='text col-3 detail-title margin--tiny text--bold text--huge')
        # extract course hours
        course_hours = course_header[0].find('span', class_='text detail-coursehours text--bold text--huge')
        # extract prerequisites
        prerequisites, co_requisites = extract_requisites()
        # get availability
        availability = get_availability(course_id)
        # get importance
        importance = get_importance(course_id)
        # add course to dataframe
        course_info_df.loc[len(course_info_df.index)] = [course_id, course_name.text, course_hours.text,
                                                         availability, prerequisites, co_requisites, '', 0, '', '',
                                                         importance]

    course_info_df.to_excel(excel_writer, sheet_name=str(department).upper(), index=False)
    excel_writer.save()
