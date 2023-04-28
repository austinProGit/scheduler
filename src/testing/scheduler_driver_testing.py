# Thomas Merino
# 4/19/2023
# CPSC 4176 Project


# TODO: (IMPORTANT) at the moment, coreq.s in constructive scheduler do not work fully:
#               We just look for "simple coreq.s", which means 1 coreq in which every dependant course's other requirements are ignored.
#               It is assumed the requirements for the course and it's coreq. are the same

# TODO: coreq.s simples are bidirectional (take into account multiple options) and can support multiple options (one-dimensional "OR"s and simplify down to it if it is not possible)

# TODO: change the behavior of maximum iterations allowed for schedule to be ("maximum contiguous empty semesters") <- for constructive/greedy

# TODO: verify mutation entail swapping two courses between semesters

# TODO: for the sake of making the genetic algorithm converge, there is an error produced for EACH courses going over the limit of credits for a semester,
# and the same is the case with not recording courses as taken if the prequisites are not present


from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from course_info_container import CourseInfoContainer
    from end_reports import PathValidationReport

import sys
import os

current = os.path.dirname(os.path.realpath(__file__)) # Gets the name of the directory where this file is present.
parent = os.path.dirname(current) # Gets the parent directory name where the current directory is present.
sys.path.append(parent) # Adds the parent directory to the sys.path.

from scheduling_parameters_container import ConstructiveSchedulingParametersContainers
from degree_extraction_container import DegreeExtractionContainer
from schedule_info_container import *
from general_utilities import *
from scheduler_driver import CreditHourInformer
from user_submitted_validator import rigorous_validate_schedule
from scheduler_driver import ConstuctiveScheduler, CACHE_USAGE



class DummyCourseRecord:
    
    def __init__(self):
        self.course_identifier_obj = None
        self.ID = None
        self.name = None
        self.hours = 3
        self.avail = ["Fa", "Sp", "--"]
        self.prereqs = None
        self.coreqs = None
        self.recommended = None
        self.stub = None

class DummyCourseInfoContainer:

    def __init__(self):
        
        self.dataset = {
            "CPSC 1105": ("Introduction to Computing Principles and Technology", 3, set(['Fa', 'Sp', 'Su']), set(), "", ""),
            "CPSC 1301K": ("Computer Science I", 3, set(['Fa', 'Sp', 'Su']), set(), "", ""),
            "CPSC 1302": ("Computer Science II", 3, set(['Fa', 'Sp', 'Su']), set(), """(CPSC 1301K, MATH 1113)""", ""),
            "CPSC 1555": ("Selected Topics in Computer Science", 3, set([]), set(), "", ""),
            "CPSC 2105": ("Computer Organization", 3, set(['Fa', 'Sp']), set(), """[e <n=Requires All:>
	[s <c=1, n=Requires 1:>
		[d <n=CSCI 1301>]
		[d <n=CPSC 1301K>]
	]
	[d <n=MATH 2125>]
]
""", ""),
            "CPSC 2108": ("Data Structures", 3, set(['Fa', 'Sp', 'Su']), set(), """[s <c=1, n=Requires 1:>
	[e <n=Requires All:>
		[d <n=CPSC 1302>]
		[d <n=MATH 2125>]
	]
	[d <n=MATH 2125>]
]
""", ""),
            "CPSC 2115": ("Information Technology Fundamentals", 3, set([]), set(), "", ""),
            "CPSC 2125": ("Internet Programming", 3, set(['Fa']), set(), """[d <n=CPSC 1301K>]
""", ""),
            "CPSC 2555": ("Selected Topics in Computer Science", 3, set([]), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3105": ("Digital Multimedia Development", 3, set(['Sp']), set(), """[d <n=CPSC 2125>]
""", ""),
            "CPSC 3111": ("COBOL Programming", 3, set(['Fa']), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3116": ("z/OS and JCL", 3, set(['Fa']), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3118": ("Graphical User Interface Development", 3, set(['Sp']), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3121": ("Assembly Language Programming I", 3, set(['Sp']), set(), """[e <n=Requires All:>
	[d <n=CPSC 2105>]
	[d <n=CPSC 1302>]
]
""", ""),
            "CPSC 3125": ("Operating Systems", 3, set(['Fa', 'Sp']), set(), """[s <c=1, n=Requires 1:>
	[e <n=Requires All:>
		[d <n=CPSC 2105>]
		[d <n=CPSC 2108>]
	]
	[d <n=CPSC 2108>]
]
""", ""),
            "CPSC 3131": (" Database Systems I", 3, set(['Fa', 'Sp']), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 3137": ("Natural Language Processing and Text Mining", 3, set([]), set(), """[d <n=CPSC 1301K>]
""", ""),
            "CPSC 3156": ("Transaction Processing", 3, set (['Sp']), set(), """[d <n=CPSC 3111>]
""", ""),
            "CPSC 3165": ("Professionalism in Computing", 3, set(['Fa', 'Sp', 'Su']), set(), "", ""),
            "CPSC 3175": ("Object-Oriented Design", 3, set(['Fa', 'Sp']), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 3415": ("Information Technology (IT) Practicum", 3, set(['Fa', 'Sp', 'Su']), set(), "", ""),
            "CPSC 3555": ("Selected Topics in Computer Science", 3, set(['Fa', 'Sp', 'Su']), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4000": ("Baccalaureate Survey", 3, set(['Fa', 'Sp', 'Su']), set(), "", ""),
            "CPSC 4111": ("Game Programming I", 3, set(['Fa']), set(), """[e <n=Requires All:>
	[d <n=CPSC 3118>]
	[d <n=CPSC 3175>]
]
""", ""),
            "CPSC 4112": ("Game Programming II", 3, set(['Sp']), set(), """[e <n=Requires All:>
	[d <n=CPSC 4111>]
	[d <n=CPSC 4113, mbtc=True>]
]
""", ""),
            "CPSC 4113": ("Game Jam", 3, set(['Sp']), set(), """[e <n=Requires All:>
	[d <n=CPSC 4111>]
	[d <n=CPSC 4112, mbtc=True>]
]
""", ""),
            "CPSC 4115": ("Algorithms", 3, set(['Fa']), set(), """[e <n=Requires All:>
	[d <n=CPSC 2108>]
	[d <n=MATH 5125U>]
]
""", ""),
            "CPSC 4121": ("Robotics Programming I", 3, set(['Fa']), set(), """[d <n=CPSC 1302>]
""", ""),
            "CPSC 4122": ("Robotics Programming II", 3, set([]), set(), """[d <n=CPSC 4121>]
""", ""),
            "CPSC 4125": ("Server-Side Web Development", 3, set(['Fa']), set(), """[e <n=Requires All:>
	[d <n=CPSC 2125>]
	[d <n=CPSC 3131>]
]
""", ""),
            "CPSC 4126": ("Web Development Projects", 3, set(['Sp']), set(), """[d <n=CPSC 4125>]
""", ""),
            "CPSC 4127": ("Computer and Network Security", 3, set([]), set(), """[e <n=Requires All:>
	[d <n=CYBR 2160>]
	[s <c=1, n=Requires 1:>
		[d <n=CYBR 2159>]
		[d <n=MISM 3145>]
	]
]
""", ""),
            "CPSC 4130": ("Mobile Computing", 3, set([]), set(), """[d <n=CPSC 3175>]
""", ""),
            "CPSC 4135": ("Programming Languages", 3, set(['Sp']), set(), """[d <n=CPSC 3175>]
""", ""),
            "CPSC 4138": ("Advanced Database Systems", 3, set([]), set(), """[d <n=CPSC 3131>]
""", ""),
            "CPSC 4145": ("Computer Graphics", 3, set(['Fa']), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4148": ("Theory of Computation", 3, set(['Sp']), set(), """[d <n=CPSC 4115>]
""", ""),
            "CPSC 4155": ("Computer Architecture", 3, set(['Fa']), set(), """[d <n=CPSC 3121>]
""", ""),
            "CPSC 4157": ("Computer Networks", 3, set(['Fa', 'Su']), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4175": ("Software Engineering", 3, set(['Fa']), set(), """[d <n=CPSC 3175>]
""", ""),
            "CPSC 4176": ("Senior Software Engineering Project", 3, set(['Sp']), set(), """[d <n=CPSC 4175>]
""", ""),
            "CPSC 4185": ("Artificial Intelligence and Machine Learning", 3, set(['Sp']), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4205": ("IT Senior Capstone", 3, set(['Fa', 'Sp', 'Su']), set(), "", ""),
            "CPSC 4505": ("Undergraduate Research", 3, set(['Fa', 'Sp']), set(), """[d <n=CPSC 2108>]
""", ""),
            "CPSC 4555": ("Selected Topics in Computer Science", 3, set([]), set(), "", ""),
            "CPSC 4698": ("Internship", 3, set(['Sp']), set(), "", ""),
            "CPSC 4899": ("Independent Study", 3, set(['Sp']), set(), "", ""),
            "CPSC 6000": ("Graduate Exit Examination", 3, set(['Fa', 'Sp', 'Su']), set(), "", ""),
            "CPSC 6103": ("Computer Science Principles for Teachers", 3, set(['Sp']), set(), "", ""),
            "CPSC 6105": ("Fundamental Principles of Computer Science", 3, set(['Fa', 'Sp']), set(), "", ""),
            "CPSC 6106": ("Fundamentals of Computer Programming and Data Structures", 3, set(['Fa', 'Sp', 'Su']), set(), "", ""),
            "CPSC 6107": ("Survey of Modeling and Simulation", 3, set(['Sp']), set(), "", ""),
            "CPSC 6109": ("Algorithms Analysis and Design", 3, set(['Sp']), set(), "", ""),
            "CPSC 6114": ("Fundamentals of Machine Learning", 3, set(['Fa']), set(), "", ""),
            "CPSC 6118": ("Human-Computer Interface Development", 3, set([]), set(), """[d <n=CPSC 6114>]
""", ""),
            "CPSC 6119": ("Object-Oriented Development", 3, set(['Fa', 'Sp']), set(), "", ""),
            "CPSC 6124": ("Advanced Machine Learning", 3, set(['Sp']), set(), """[d <n=CPSC 6114>]
""", ""),
            "CPSC 6125": ("Operating Systems Design and Implementation", 3, set(['Fa']), set(), "", ""),
            "CPSC 6126": ("Introduction to Cybersecurity", 3, set(['Sp', 'Su']), set(), "", ""),
            "CPSC 6127": ("Contemporary Issues in Database Management Systems", 3, set(['Sp']), set(), "", ""),
            "CPSC 6128": ("Network Security", 3, set(['Sp']), set(), """[d <n=CPSC 6126>]
""", ""),
            "CPSC 6129": ("Computer Language Design and Interpretation", 3, set([]), set(), "", ""),
            "CPSC 6136": ("Human Aspects of Cybersecurity", 3, set(['Su']), set(), """[d <n=CPSC 6126>]
""", ""),
            "CPSC 6138": ("Mobile Systems and Applications", 3, set(['Su']), set(), """[d <n=CPSC 6119>]
""", ""),
            "CPSC 6147": ("Data Visualization and Presentation", 3, set(['Sp']), set(), "", ""),
            "CPSC 6155": ("Advanced Computer Architecture", 3, set([]), set(), "", ""),
            "CPSC 6157": ("Network and Cloud Management", 3, set(['Fa']), set(), "", ""),
            "CPSC 6159": ("Digital Forensics", 3, set(['Fa']), set(), """[d <n=CPSC 6126>]
""", ""),
            "CPSC 6167": ("Cybersecurity Risk Management", 3, set(['Sp']), set(), """[d <n=CPSC 6126>]
""", ""),
            "CPSC 6175": ("Web Engineering and Technologies", 3, set(['Sp']), set(), "", ""),
            "CPSC 6177": ("Software Design and Development", 3, set([]), set(), "", ""),
            "CPSC 6178": ("Software Testing and Quality Assurance", 3, set([]), set(), "", ""),
            "CPSC 6179": ("Software Project Planning and Management", 3, set(['Fa']), set(), "", ""),
            "CPSC 6180": ("Software Estimation and Measurement", 3, set([]), set(), "", ""),
            "CPSC 6185": ("Intelligent Systems", 3, set(['Sp']), set(), "", ""),
            "CPSC 6190": ("Applied Cryptography", 3, set([]), set(), """[d <n=CPSC 6106>]
""", ""),
            "CPSC 6555": ("Selected Topics in Computer Science", 3, set(['Su']), set(), "", ""),
            "CPSC 6698": ("Graduate Internship in Computer Science", 3, set([]), set(), "", ""),
            "CPSC 6899": ("Independent Study", 3, set(['Fa', 'Sp']), set(), "", ""),
            "CPSC 6985": ("Research and Thesis", 3, set(['Sp']), set(), "", ""),
            "CPSC 6986": ("Thesis Defense", 3, set(['Sp']), set(), "", ""),
        }

    

    def get_course_record(self, course_identifier_obj: CourseIdentifier) -> DummyCourseRecord:
        courseID = course_identifier_obj.course_number
        stub = course_identifier_obj.is_stub()
        
        if stub:
            course = DummyCourseRecord()
            course.course_identifier_obj = course_identifier_obj
            course.ID = courseID
            course.name = course_identifier_obj.name
            course.stub = True
            return course
        elif self.validate_course(courseID):
            course = DummyCourseRecord()
            course.course_identifier_obj = course_identifier_obj
            course.ID = courseID
            course.name = self.get_name(course_identifier_obj)
            course.hours = self.get_hours(course_identifier_obj)
            course.avail = self.get_availability(course_identifier_obj)
            course.prereqs = self.get_prereqs(course_identifier_obj)
            course.coreqs = self.get_coreqs(course_identifier_obj)
            course.recommended = self.get_recommended(course_identifier_obj)
            return course
        else:
            return None


    def validate_course(self, course_number) -> bool:
        return course_number in self.dataset
    
    def get_name(self, courseid: CourseIdentifier):
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][0]
        else:
            raise KeyError(courseid.course_number + " is not found!")
    
    def get_hours(self, courseid): 
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][1]
        else:
            raise KeyError(courseid.course_number + " is not found!")
    
    def get_availability(self, courseid):
        if courseid.course_number in self.dataset:
            result = self.dataset[courseid.course_number][2]
            return result if len(result) != 0 else set(['Fa', 'Sp'])
        else:
            raise KeyError(courseid.course_number + " is not found!")

    def get_prereqs(self, courseid):
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][4]
        else:
            raise KeyError(courseid.course_number + " is not found!")

    def get_coreqs(self, courseid):
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][5]
        else:
            raise KeyError(courseid.course_number + " is not found!")

    def get_recommended(self, courseid):
        if courseid.course_number in self.dataset:
            return self.dataset[courseid.course_number][3]
        else:
            raise KeyError(courseid.course_number + " is not found!")

    def get_importance(self, courseid):
        return 1

def validation_and_scheduling_unit_test():

    passed_all_tests: bool = True

    course_info_container: DummyCourseInfoContainer = DummyCourseInfoContainer()

    
    print('=============================== Start Scheduling Tests (Validation phase) ===============================\n')


    # ==================================================================================================
    # Expected valid - case 1
    # ==================================================================================================

    test_path_1: ScheduleInfoContainer = ScheduleInfoContainer.make_from_string_list([
        ['CPSC 1301K', 'CPSC 2108'],
        ['CPSC 1302', 'CPSC 1555'],
        [],
        ['CPSC 3175'],
        ['CPSC 2555', 'CPSC 3118'],
        [],
        ['CPSC 4111'],
        ['CPSC 4112', 'CPSC 4113']
    ], course_info_container, starting_semester=FALL, starting_year=2023)
    
    report_1: PathValidationReport = rigorous_validate_schedule(
        test_path_1,
        taken_courses=[CourseIdentifier('MATH 2125'), CourseIdentifier('MATH 1113')],
        prequisite_ignored_courses=[],
        credit_hour_informer=CreditHourInformer.make_unlimited_generator()
    )

    if not report_1.is_valid():
        print('ERROR IN validation in case 1')
        passed_all_tests = False
    else:
        print('Passed path validation case 1')

    
    # ==================================================================================================
    # Expected valid - case 2
    # ==================================================================================================

    test_path_2: ScheduleInfoContainer = ScheduleInfoContainer.make_from_string_list([
        ['CPSC 1302', 'CPSC 1555'],
        ['CPSC 2108'],
        ['CPSC 3175'],
        ['CPSC 3118', 'CPSC 2555'],
    ], course_info_container, starting_semester=SPRING, starting_year=2023)
    
    report_2: PathValidationReport = rigorous_validate_schedule(
        test_path_2,
        taken_courses=[CourseIdentifier('MATH 2125'), CourseIdentifier('MATH 1113'), CourseIdentifier('CPSC 1301K')],
        prequisite_ignored_courses=[],
        credit_hour_informer=CreditHourInformer.make_unlimited_generator()
    )

    if not report_2.is_valid():
        print('ERROR IN validation in case 2')
        passed_all_tests = False
    else:
        print('Passed path validation case 2')

    
    # ==================================================================================================
    # Expected invalid - case 3
    # ==================================================================================================

    test_path_3: ScheduleInfoContainer = ScheduleInfoContainer.make_from_string_list([\
        ['CPSC 1301K'],
        ['CPSC 1302', 'CPSC 1555'],
        [],
        ['CPSC 2108'],
        ['CPSC 3175'],
        ['CPSC 2555', 'CPSC 3118'],
        [],
        ['CPSC 4111'],
        ['CPSC 4112', 'CPSC 4113']
    ], course_info_container, starting_semester=FALL, starting_year=2023)
    
    report_3: PathValidationReport = rigorous_validate_schedule(
        test_path_3,
        taken_courses=[CourseIdentifier('MATH 2125'), CourseIdentifier('MATH 1113')],
        prequisite_ignored_courses=[],
        credit_hour_informer=CreditHourInformer.make_unlimited_generator()
    )

    if report_3.is_valid():
        print('ERROR IN validation in case 3')
        passed_all_tests = False
    else:
        print('Passed path validation case 3')

    
    # ==================================================================================================
    # Expected invalid - case 4
    # ==================================================================================================

    test_path_4: ScheduleInfoContainer = ScheduleInfoContainer.make_from_string_list([
        ['CPSC 1301K', 'CPSC 2108'],
        ['CPSC 1302', 'CPSC 1555'],
        [],
        ['CPSC 3175'],
        ['CPSC 2555', 'CPSC 3118'],
        [],
        ['CPSC 4111'],
        ['CPSC 4112', 'CPSC 4113']
    ], course_info_container, starting_semester=FALL, starting_year=2023)
    
    report_4: PathValidationReport = rigorous_validate_schedule(
        test_path_4,
        taken_courses=[CourseIdentifier('MATH 1113')],
        prequisite_ignored_courses=[],
        credit_hour_informer=CreditHourInformer.make_unlimited_generator()
    )

    if report_4.is_valid():
        print('ERROR IN validation in case 4')
        passed_all_tests = False
    else:
        print('Passed path validation case 4')

    
    # ==================================================================================================
    # Expected invalid - case 5
    # ==================================================================================================

    test_path_5: ScheduleInfoContainer = ScheduleInfoContainer.make_from_string_list([
        ['CPSC 1301K'],
        ['CPSC 1302', 'CPSC 1555'],
        [],
        ['CPSC 1301K']
    ], course_info_container, starting_semester=FALL, starting_year=2023)
    
    report_5: PathValidationReport = rigorous_validate_schedule(
        test_path_5,
        taken_courses=[CourseIdentifier('MATH 1113')],
        prequisite_ignored_courses=[],
        credit_hour_informer=CreditHourInformer.make_unlimited_generator()
    )

    if report_5.is_valid():
        print('ERROR IN validation in case 5')
        passed_all_tests = False
    else:
        print('Passed path validation case 5')

    
    # ==================================================================================================
    # Expected valid - case 6
    # ==================================================================================================

    test_path_6: ScheduleInfoContainer = ScheduleInfoContainer.make_from_string_list([
        ['CPSC 1301K', 'CPSC 1105', 'CPSC 2115', 'CPSC 2108', 'CPSC 3165'],
        ['CPSC 1302', 'CPSC 3415'],
        ['CPSC 2125', 'CPSC 2105', 'CPSC 2555', 'CPSC 1555'],
        ['CPSC 3125', 'CPSC 3131', 'CPSC 3175', 'CPSC 3121', 'CPSC 3105'],
        ['CPSC 3555'],
        ['CPSC 3116', 'CPSC 3111', 'CPSC 3137', 'CPSC 4145', 'CPSC 4125'],
        ['CPSC 3118', 'CPSC 3156', 'CPSC 4130', 'CPSC 4126', 'CPSC 4138']
    ], course_info_container, starting_semester=SPRING, starting_year=2023)
    
    report_6: PathValidationReport = rigorous_validate_schedule(
        test_path_6,
        taken_courses=[CourseIdentifier('MATH 1113'), CourseIdentifier('MATH 2125')],
        prequisite_ignored_courses=[],
        credit_hour_informer=CreditHourInformer.make_unlimited_generator()
    )

    if not report_6.is_valid():
        print([str(r) for r in report_6.error_list])
        print('ERROR IN validation in case 6')
        passed_all_tests = False
    else:
        print('Passed path validation case 6')

    print('=============================== End Scheduling Tests (Validation phase) ===============================\n')



    # ==================================================================================================
    #
    #   Scheduling minimum test (just ensure the scheduler does not crash and generates a valid
    #   schedule given doable conditions):
    #
    # ==================================================================================================

    # NOTE: these tests use random variables, so a seed may need to be set prior

    print('=============================== Start Scheduling Tests (Scheduling minimum phase) ===============================\n')

    NO_ERRORS_FLAG: str = '*No Errors*'

    test_run_count: int = 10
    acceptable_errors_left: int = 1 # works 90% of the time
    invalid_schedules_generated: int = 0
    
    dcspc_list: list[ConstructiveSchedulingParametersContainers] = [
        ConstructiveSchedulingParametersContainers('', [], fall_spring_hours=15, summer_hours=6),
        ConstructiveSchedulingParametersContainers('', [], fall_spring_hours=15, summer_hours=0),
        ConstructiveSchedulingParametersContainers('', [], fall_spring_hours=12, summer_hours=3),
        ConstructiveSchedulingParametersContainers('', [], fall_spring_hours=6, summer_hours=0)
    ]
    
    degree_extraction: DegreeExtractionContainer = DegreeExtractionContainer(curr_taken_courses=['MATH 2125', 'MATH 1113', 'MATH 5125U'],\
            courses_needed_constuction_string='''
    (CPSC 1105, CPSC 2105, CPSC 2115, CPSC 1555, CPSC 2108, CPSC 2555,
        CPSC 2125, CPSC 3105, CPSC 3111, CPSC 1302, CPSC 3116, CPSC 3118,
        CPSC 3121, CPSC 3125, CPSC 3131, CPSC 3137, CPSC 3156, CPSC 3156,
        CPSC 3165, CPSC 3175, CPSC 3415, CPSC 3555, CPSC 4000, CPSC 4111,
        CPSC 4121, CPSC 4122, CPSC 4125, CPSC 1301K, CPSC 4126, CPSC 4130,
        CPSC 4115, CPSC 4130, CPSC 4135, CPSC 4138, CPSC 4145, CPSC 4148
        ) [p <n=COURSE A>][p <n=COURSE B>][p <n=COURSE C>]
    ''')


    prequisite_ignored_courses: list[CourseIdentifier] = [
        CourseIdentifier('MATH 1113')
    ]

    scheduler: ConstuctiveScheduler = ConstuctiveScheduler(course_info_container, dcspc_list[0])
    for test_run in range(test_run_count):
        scheduler.configure_parameters(dcspc_list[test_run % len(dcspc_list)])
        scheduler.configure_degree_extraction(degree_extraction)
        scheduler.get_courses_needed_container().stub_all_unresolved_nodes()
        scheduler.prepare_schedulables()
        path: ScheduleInfoContainer = scheduler.generate_schedule(prequisite_ignored_courses=prequisite_ignored_courses)
        print(str(path))
        generated_report: PathValidationReport = rigorous_validate_schedule(
            path,
            taken_courses=[CourseIdentifier('MATH 2125'), CourseIdentifier('MATH 1113'), CourseIdentifier('MATH 5125U')],
            prequisite_ignored_courses=[],
            credit_hour_informer=scheduler.make_credit_hour_informer()
        )

        print(f'TEST {test_run+1}:')
        print('Used Cache:', CACHE_USAGE['TEST_CACHE_T'])
        print('Calculated:', CACHE_USAGE['TEST_CACHE_F'])
        print('Ratio:', CACHE_USAGE['TEST_CACHE_T']/(CACHE_USAGE['TEST_CACHE_F']+CACHE_USAGE['TEST_CACHE_T']))

        # Reset cache numbers
        CACHE_USAGE['TEST_CACHE_T'] = 0
        CACHE_USAGE['TEST_CACHE_F'] = 0

        errors = generated_report.get_errors_printable()
        if NO_ERRORS_FLAG not in errors:
            print('ERRORS:')
            print(errors)
            acceptable_errors_left -= 1
            invalid_schedules_generated += 1

            if acceptable_errors_left < 0:
                print('EXCEEDED ACCEPTABLE FAILURE RATE FOR SCHEDULING MINIMUM TESTING')
                passed_all_tests = False
            

    print(f'\nInvalid schedules generated: {invalid_schedules_generated}\n')

    print('=============================== Start Scheduling Tests (Scheduling minimum phase) ===============================\n')


    return passed_all_tests


if __name__ == '__main__':
        validation_and_scheduling_unit_test()