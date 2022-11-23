# Author: Vincent Miller
# 18 September 2022
# Contributor(s): Thomas Merino

# MERINO: All I have done is encapsulated it in a class with configuration methods, added support for co-reqs,
# added support for starting on any semester, reorganized a bit of stuff (to my weird liking), and fixed a rare bug.

SEMESTER_TYPE_SUCCESSOR = {'Fa': 'Sp', 'Sp': 'Su', 'Su': 'Fa'}    # Translation map from semester K to the next
DEFAULT_HOURS_PER_SEMESTER = 15  # MERINO: updated value

LOW_FITNESS = 1
MID_FITNESS = 5.5
HIGH_FITNESS = 10

FITNESS_LISTING = [LOW_FITNESS, MID_FITNESS, HIGH_FITNESS]

from expert_system_module import CoreqRule, FitnessConfiguration, get_fittest_courses
from expert_system_module import ExpertSystem, DynamicKnowledge


# The following are some test atomic fitness rules:
# ---------------------->
def gatekeeper_rule(courseID, course_info_container):
    weight = course_info_container.get_weight(courseID)
    if weight is None:
        weight = LOW_FITNESS
    fitness = HIGH_FITNESS - (HIGH_FITNESS - LOW_FITNESS) / (weight + 1)
    return fitness
    
def availability_rule(courseID, course_info_container):
    # Lew replaced .availability_list(courseID) with .get_availability(courseID)
    availability_list = course_info_container.get_availability(courseID)
    availability_cardinality = 0
    for availability_list in ['Fa', 'Sp', 'Su']:
        if availability_list in availability_list:
            availability_cardinality += 1
    return FITNESS_LISTING[3-availability_cardinality]
    
COREQ_ADDITIONAL_FITNESS = LOW_FITNESS
# <----------------------


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
                for coreq in course_info_container.get_coreqs(courseID):
                    coreq_rules.append(CoreqRule(courseID, coreq, COREQ_ADDITIONAL_FITNESS))
        
        return FitnessConfiguration(atomic_rules, coreq_rules)
    
    def __init__(self):
        self.hours_per_semester = DEFAULT_HOURS_PER_SEMESTER
        self.courses_needed = []
        self.course_info_container = None
        self.semester_type = 'Sp'
        
        self.fitness_configuration = Scheduler._create_default_fitness_configuration()
        self.schedule_evaluator = ExpertSystem()
    
    def get_course_info(self):
        return self.course_info_container
        
    def get_schedule_evaluator(self):
        return self.schedule_evaluator
        
    def get_courses_needed(self):
        return self.courses_needed[:]
    
    def get_hours_per_semester(self):
        return self.hours_per_semester
        
    def configure_course_info(self, container):
        self.course_info_container = container
        self.fitness_configuration = Scheduler._create_default_fitness_configuration(container)
        
    def configure_courses_needed(self, courses_needed):
        self.courses_needed = courses_needed[:]
    
    def configure_hours_per_semester(self, number_of_hours):
        self.hours_per_semester = number_of_hours
    
    def generate_schedule(self):
        """Primary method to schedule a path to graduation
           Inputs: None, but requires course_info and courses_needed setup prior to running
           Returns: list of lists, inner list is one semester of courses, outer list is full schedule"""
        course_info = self.course_info_container # Get the course info container
        courses_needed = self.courses_needed[:] # Create a copy of the needed courses (workable list)
        
        # Helper functions
        def check_availability(course_id):
            availability = course_info.get_availability(course_id)
            return working_semester_type in availability
            
        def check_prerequisites(course_id):
            prerequisites = course_info.get_prereqs(course_id)
            # if prerequisite course is in courses_needed, can't take course yet.
            for prerequisite in prerequisites:
                if prerequisite in courses_needed:
                    return False
            return True
        
        print(courses_needed)
        # Create empty, final schedule, each semester list will be added to this
        full_schedule = []
        # Create a string to track the current semester type ('Fa', 'Sp', or 'Su')
        working_semester_type = self.semester_type
        
        # TODO: add 4000 to last semester
        
        # loop through until courses_needed is empty
        while len(courses_needed):
            # if courses_needed is empty, break out of semester_types loop
            if not len(courses_needed):
                break
            
            possible_course = []
            
            possible_course = list(filter(lambda x: check_availability(x) and check_prerequisites(x), courses_needed))
            
            max_hours = self.hours_per_semester if working_semester_type != 'Su' else 6
            
            semester = get_fittest_courses(max_hours, possible_course, self.fitness_configuration, course_info)
            
            for course in semester:
                courses_needed.remove(course)
            
            # add semester to full_schedule
            full_schedule.append(list(semester))
            
            # Rotate to the next semester type
            working_semester_type = SEMESTER_TYPE_SUCCESSOR[working_semester_type]
        
        # Calculate the confidence factor for the new schedule
        dynamic_knowledge = DynamicKnowledge()
        dynamic_knowledge.set_schedule(full_schedule)
        confidence_factor = self.schedule_evaluator.calculate_confidence(dynamic_knowledge, course_info)
        
        return full_schedule, confidence_factor
    
    
    def first_available(self, semester_type):
        """Performs similar as generate_schedule() without hours limitation or multi semester.
           Input: semester_type, ('Fa', 'Sp', 'Su')
           Returns list of first courses available to selected semester,
               and list of remaining courses needed"""
        course_info = self.course_info_container  # Get the course info container
        courses_needed = self.courses_needed[:]  # Create a copy of the needed courses (workable list)

        # Helper functions TODO: duplication of code
        def check_availability(course_id):
            availability = course_info.get_availability(course_id)
            return working_semester_type in availability

        def check_prerequisites(course_id):
            prerequisites = course_info.get_prereqs(course_id)
            # if prerequisite course is in courses_needed or in semester, can't take course yet.
            for prerequisite in prerequisites:
                if prerequisite in courses_needed or prerequisite in semester:
                    return False
            return True

        def check_corequisites(course_id):
            corequisites = course_info.get_coreqs(course_id)
            # If co-requisite course is in the needed courses, can't take course yet.
            for corequisite in corequisites:
                if corequisite in courses_needed:
                    return False
            return True

        def complete_check(course_id):
            # Run all three of the above checks (with short circuit evaluation)
            return check_availability(course_id) \
                   and check_prerequisites(course_id) \
                   and check_corequisites(course_id)

        working_semester_type = semester_type
        semester = []
        initial_size = len(courses_needed)

        # loop handles first semester
        for i in range(initial_size):
            # get first course in list
            course = courses_needed.pop(0)
            # check availability, prerequisites, and co-requisites
            passes_complete_check = complete_check(course)
            if not passes_complete_check:
                # course cannot be taken, add course back to courses_needed and skip the rest of iteration loop
                courses_needed.append(course)
                # Used to detect if all courses have been checked and, indeed, none can be registered
            else:
                # add course in semester, increment hours
                semester.append(course)
        # returns list of courses and list of remaining courses needed
        return semester, courses_needed

