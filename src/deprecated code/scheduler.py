# Author: Vincent Miller
# 18 September 2022
# Contributor(s): Thomas Merino

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Optional
    from scheduling_parameters_container import ConstructiveSchedulingParametersContainers
    from course_info_container import CourseInfoContainer
    from courses_needed_container import CoursesNeededContainer

# TODO: THIS IS A TEST IMPORT (REMOVE)!!
from degree_extraction_container import DegreeExtractionContainer


from scheduling_assistant import CoreqRule, FitnessConfiguration, get_fittest_courses
from expert_system_module import ExpertSystem, DynamicKnowledge
from schedule_info_container import *
from general_utilities import *
from requirement_parser import RequirementsParser

DEFAULT_HOURS_PER_SEMESTER = 15
INITIAL_SEMESTER = {FALL: [], SPRING: [[]], SUMMER: [[], []]}

# TODO: this should be removed in later versions
SEMESTER_LEGACY_MAP = {FALL: 'Fa', SPRING: 'Sp', SUMMER: 'Su'}

LOW_FITNESS = 1
MID_FITNESS = 5.5
HIGH_FITNESS = 10

FITNESS_LISTING = [LOW_FITNESS, MID_FITNESS, HIGH_FITNESS]
COREQ_ADDITIONAL_FITNESS = LOW_FITNESS



# The following are some test atomic fitness rules:

def gatekeeper_rule(courseID, course_info_container):
    # TODO: this was commented out for the demonstration
    # weight = course_info_container.get_weight(courseID)
    # if weight is None:
    #     weight = LOW_FITNESS
    # fitness = HIGH_FITNESS - (HIGH_FITNESS - LOW_FITNESS) / (weight + 1)
    # return fitness
    return MID_FITNESS
    
def availability_rule(courseID, course_info_container):
    # Lew replaced .availability_list(courseID) with .get_availability(courseID)
    availability_list = course_info_container.get_availability(courseID)
    availability_cardinality = 0
    for availability_list in ['Fa', 'Sp', 'Su']:
        if availability_list in availability_list:
            availability_cardinality += 1
    return FITNESS_LISTING[3-availability_cardinality]
    



class Scheduler:
    
    @staticmethod
    def _create_default_fitness_configuration(course_info_container=None):
        # TODO: complete this
        atomic_rules = [
            gatekeeper_rule,
            availability_rule
        ]
        
        coreq_rules = []
        if course_info_container is not None:
            for courseID in course_info_container.get_courseIDs():

                # TODO: this was added before presentation for demonstration
                requirements = course_info_container.get_coreqs(courseID) or ''
                tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
                coreqs = []#[i.course_number for i in tree.decision_tree.get_all_aggragate()]

                for coreq in coreqs:
                    coreq_rules.append(CoreqRule(courseID, coreq, COREQ_ADDITIONAL_FITNESS))
        
        return FitnessConfiguration(atomic_rules, coreq_rules)
    
    def __init__(self, course_info_container: Optional[CourseInfoContainer], parameters_container: ConstructiveSchedulingParametersContainers):
        #self.hours_per_semester = DEFAULT_HOURS_PER_SEMESTER
        #self.courses_needed = []
        #self.courses_needed_container = None
        self.semester_start: SemesterType = SPRING

        self.course_info_container: Optional[CourseInfoContainer] = course_info_container

        # TODO: REMOVE THIS TEST!!!
        construct_string_2 = '''
        (CPSC 1301, CPSC 1302, CPSC 2105, CPSC 2108, CPSC 3125,
        CPSC 3131, CPSC 3165, CPSC 3175, CPSC 4115, CPSC 4135)

        [c <n=3 Courses, c=3>
            [d <n=CPSC 4121>]
            [c <n=2 Courses, c=2>
                [d <n=CPSC 4126>]
                [d <n=CPSC 4127>]
            ]
            [d <n=CPSC 4130>]
            [d <n=CPSC 4185>]
        ]

        [s <n=2 Selections, c=2>
            [c <n=2 Courses, c=2>
                [d <n=MATH 1100>]
                [d <n=MATH 1101>]
            ]
            [c <n=2 Courses, c=2>
                [d <n=MATH 1200>]
                [d <n=MATH 1201>]
            ]
            [d <n=MATH 1300>]
            [d <n=MATH 1400>]
        ]

        [r <n=6 Credits, c=6>
            [i <n=Insert 4___, gp=[A-Z]{4,5}\s?\d{4}[A-Z]?, ga=Fill out 4___>]
            [p <n=Fill out 4___, gp=[A-Z]{4,5}\s?\d{4}[A-Z]?>]
        ]
        '''
        # DegreeExtractionContainer([], construct_string_2)
        
        self._degree_extraction: Optional[DegreeExtractionContainer] = None
        self._courses_needed_container: Optional[CoursesNeededContainer] = None
        self._parameters_container: ConstructiveSchedulingParametersContainers = parameters_container
        
        self.fitness_configuration: FitnessConfiguration = Scheduler._create_default_fitness_configuration()
        self.schedule_evaluator: ExpertSystem = ExpertSystem()

        #self.courses_needed_container = degree_extraction.make_courses_needed_container()
    
    def get_parameter_container(self):
        return self._parameters_container

    def configure_parameters(self, parameters_containter: ConstructiveSchedulingParametersContainers) -> None:
        self._parameters_container = parameters_containter

    def get_course_info(self) -> Optional[CourseInfoContainer]:
        return self.course_info_container
        
    def get_schedule_evaluator(self):
        return self.schedule_evaluator
        
    def get_courses_needed_container(self):
        return self._courses_needed_container
    
    def get_hours_per_semester(self, semesterType: SemesterType = FALL):
        # TODO: this uses just hours for the Fall (fix)
        return self._parameters_container.get_hours_for(semesterType)
        
    def configure_course_info(self, container):
        self.course_info_container = container
        self.fitness_configuration = Scheduler._create_default_fitness_configuration(container)
        
    def configure_degree_extraction(self, degree_extraction):
        self._degree_extraction = degree_extraction
        self._courses_needed_container = degree_extraction.make_courses_needed_container()
    
    def configure_hours_per_semester(self, number_of_hours):
        # self.hours_per_semester = number_of_hours
        self._parameters_container.set_hours(FALL, number_of_hours)
    
    def generate_schedule(self):
        """Primary method to schedule a path to graduation
           Inputs: None, but requires course_info and courses_needed setup prior to running
           Returns: list of lists, inner list is one semester of courses, outer list is full schedule"""
        course_info = self.course_info_container # Get the course info container
        courses_needed = self._courses_needed_container.get_courses_string_list() # Create a copy of the needed courses (workable list)
        

        # Ensure CPSC 4000 is scheduled in the last semester
        contains_4000 = False
        if 'CPSC 4000' in courses_needed:
            contains_4000 = True
            courses_needed.remove('CPSC 4000')
        
        # Helper functions
        def check_availability(course_id):
            availability = course_info.get_availability(course_id)
            return SEMESTER_LEGACY_MAP[working_semester_type] in availability
            
        def check_prerequisites(course_id):
            # TODO: this was added before presentation for demonstration
            requirements = course_info.get_prereqs(course_id) or ''
            tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
            prerequisites = [i.course_number for i in tree.decision_tree.get_all_aggragate()]
            # if prerequisite course is in courses_needed, can't take course yet.
            for prerequisite in prerequisites:
                if prerequisite in courses_needed:
                    return False
            return True
        
        # Create a string to track the current semester type ('Fa', 'Sp', or 'Su')
        working_semester_type = self.semester_start
                
        # Create empty, final schedule, each semester list will be added to this
        full_schedule = INITIAL_SEMESTER[working_semester_type][:]
        
        # loop through until courses_needed is empty
        while len(courses_needed):
            # if courses_needed is empty, break out of semester_types loop
            if not len(courses_needed):
                break
            
            possible_course = []
            
            possible_course = list(filter(lambda x: check_availability(x) and check_prerequisites(x), courses_needed))
            
            max_hours = self.get_hours_per_semester(FALL).stop if working_semester_type != SUMMER else self.get_hours_per_semester(SUMMER).stop
            
            semester = get_fittest_courses(max_hours, possible_course, self.fitness_configuration, course_info)
            
            for course in semester:
                courses_needed.remove(course)
            
            # add semester to full_schedule
            full_schedule.append(list(semester))
            
            # Rotate to the next semester type
            working_semester_type = SEMESTER_TYPE_SUCCESSOR[working_semester_type]
            
        if contains_4000:
            full_schedule[-1].append('CPSC 4000')
        
        # Calculate the confidence factor for the new schedule
        dynamic_knowledge = DynamicKnowledge()
        dynamic_knowledge.set_schedule(full_schedule)
        confidence_factor = self.schedule_evaluator.calculate_confidence(dynamic_knowledge, course_info)

        # container = ScheduleInfoContainer(full_schedule, confidence_factor)
        
        container = ScheduleInfoContainer.make_from_string_list(full_schedule, confidence_factor)

        #return full_schedule, confidence_factor
        return container
    
#
#    def first_available(self, semester_type):
#        """Performs similar as generate_schedule() without hours limitation or multi semester.
#           Input: semester_type, ('Fa', 'Sp', 'Su')
#           Returns list of first courses available to selected semester,
#               and list of remaining courses needed"""
#        course_info = self.course_info_container  # Get the course info container
#        courses_needed = self.courses_needed[:]  # Create a copy of the needed courses (workable list)
#
#        # Helper functions TODO: duplication of code
#        def check_availability(course_id):
#            availability = course_info.get_availability(course_id)
#            return working_semester_type in availability
#
#        def check_prerequisites(course_id):
#            prerequisites = course_info.get_prereqs(course_id)
#            # if prerequisite course is in courses_needed or in semester, can't take course yet.
#            for prerequisite in prerequisites:
#                if prerequisite in courses_needed or prerequisite in semester:
#                    return False
#            return True
#
#        def check_corequisites(course_id):
#            corequisites = course_info.get_coreqs(course_id)
#            # If co-requisite course is in the needed courses, can't take course yet.
#            for corequisite in corequisites:
#                if corequisite in courses_needed:
#                    return False
#            return True
#
#        def complete_check(course_id):
#            # Run all three of the above checks (with short circuit evaluation)
#            return check_availability(course_id) \
#                   and check_prerequisites(course_id) \
#                   and check_corequisites(course_id)
#
#        working_semester_type = semester_type
#        semester = []
#        initial_size = len(courses_needed)
#
#        # loop handles first semester
#        for i in range(initial_size):
#            # get first course in list
#            course = courses_needed.pop(0)
#            # check availability, prerequisites, and co-requisites
#            passes_complete_check = complete_check(course)
#            if not passes_complete_check:
#                # course cannot be taken, add course back to courses_needed and skip the rest of iteration loop
#                courses_needed.append(course)
#                # Used to detect if all courses have been checked and, indeed, none can be registered
#            else:
#                # add course in semester, increment hours
#                semester.append(course)
#        # returns list of courses and list of remaining courses needed
#        return semester, courses_needed

