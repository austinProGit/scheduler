# Author: Vincent Miller
# Date: 19 September 2022
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd
# TODO: handle restrictions, Honestly think this can be ignored


def parse_catalog(department):
    """inputs 4 letter department acronym, parses website catalog for accurate information
       creates and saves Course Info.xlsx """
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
            _df = pd.read_excel("input_files/course_availabilities.xlsx", sheet_name='Sheet1')
            _availability = _df.loc[_df.index[_df['course_ID'] == _course_id]]['availability'].to_list()
            return _availability[0]
        except IndexError:
            return 'Fa Sp Su'

    # open url, load into bs4 object
    url = "https://catalog.columbusstate.edu/course-descriptions/"+department+"/"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, features="html.parser")

    # extract all course block data
    all_course_blocks = soup.find_all('div', class_='courseblock')

    # create dataframe to hold course info
    course_info_df = pd.DataFrame(columns=['courseID', 'courseName', 'hours', 'availability', 'prerequisites',
                                           'co-requisites', 'recommended', 'isElective', 'restrictions', 'note'])

    # loop to add course data to dataframe
    for index in range(len(all_course_blocks)):
        # extract current course header and body html data
        course_header = all_course_blocks[index].find_all('div', class_='cols noindent')
        course_body = all_course_blocks[index].find_all('p', class_='courseblockextra noindent')
        # extract course id
        course_id = course_header[0].find('span', class_='text col-3 detail-code margin--tiny text--semibold text--huge')
        # extract course name
        course_name = course_header[0].find('span', class_='text col-3 detail-title margin--tiny text--bold text--huge')
        # extract course hours
        course_hours = course_header[0].find('span', class_='text detail-coursehours text--bold text--huge')
        # extract prerequisites
        prerequisites, co_requisites = extract_requisites()
        # get availability
        availability = get_availability(course_id.text)
        # TODO: handle restrictions ('p', class_='cls noindent')
        # add course to dataframe
        course_info_df.loc[len(course_info_df.index)] = [course_id.text, course_name.text, course_hours.text,
                                                         availability, prerequisites, co_requisites, '', 0, '', '']

    # export to excel, and save to specific sheets
    excel = pd.ExcelWriter('Course Info.xlsx')
    course_info_df.to_excel(excel, 'Sheet1', index=False)
    excel.save()
