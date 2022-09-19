from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pandas as pd


def extract_requisites():
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
        print("Prerequisites:", _prerequisites)
        print("Co-Requisites:", _co_requisites)
    except IndexError:
        # course has no prerequisites, readability, or restriction; only description
        pass

    return _prerequisites, _co_requisites


# open url, load into bs4 object
url = "https://catalog.columbusstate.edu/course-descriptions/cpsc/"
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
    print("Course:", course_id.text)
    # extract course name
    course_name = course_header[0].find('span', class_='text col-3 detail-title margin--tiny text--bold text--huge')
    # extract course hours TODO: only need credit hours, remove physical class and lab hours
    course_hours = course_header[0].find('span', class_='text detail-coursehours text--bold text--huge')
    # extract prerequisites
    prerequisites, co_requisites = extract_requisites()
    # add course to dataframe
    course_info_df.loc[len(course_info_df.index)] = [course_id.text, course_name.text, course_hours.text, '',
                                                     prerequisites, co_requisites, '', 0, '', '']
    # TODO: handle restrictions ('p', class_='cls noindent')

# export to excel, and save to specific sheets TODO: create and add CYBR sheet separately
excel = pd.ExcelWriter('Course Info.xlsx')
# TODO: fix sheet labeling, breaks too much if it's CPSC
course_info_df.to_excel(excel, 'Sheet1', index=False)
excel.save()
