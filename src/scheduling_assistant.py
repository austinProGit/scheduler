import math
import itertools


# ---------------------------------------- Scheduling System ----------------------------------------

# This module needs to perform 2 functions: pick a set of courses with the highest confidence value given the number of credit hours and the available courses.

# Coreq.s will be handled in the following way: some arguments will have variants. The entire decision-making process will be executed with each possible combination of variants. For example, if there are two courses that appear in two version (say, A1 and A2 and B1 and B2), then the process is executed 4 times: {A1, B1}, {A1, B2}, {A2, B1}, and {A2, B2}. When dealing with coreq.s, we will consider the scenario where only the required course is available and the scenario where the two classes are made into a single compound course.

# NOTE: this does not work when there are coreq overlaps/collisions

LOW_FITNESS = 1
MID_FITNESS = 5.5
HIGH_FITNESS = 10

FITNESS_LISTING = [LOW_FITNESS, MID_FITNESS, HIGH_FITNESS]

# The following are some atomic fitness rules:

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


# Add rule of arb. imprt.

# This is a corequisite rule that may be used by the get_fittest_courses function to ensure
# no coreq rules are broken (and apply fitness points when taking courses together)
class CoreqRule:
    
    def __init__(self, required_course, optional_course, additional_fitness):
        self.required_course = required_course
        self.optional_course = optional_course
        self.additional_fitness = additional_fitness
    
    def apply(self, schedulables, remainging_coreq_rules):
        '''Take a list of '''
        '''Recursive method: this should only be called by recursive calls or by the get_fittest_courses function.'''
        
        # The resulting list of possibilities: a list of dictionaries from course IDs (strings) to _Schedulable objects
        result = []
        more_coreq_rules_remain = len(remainging_coreq_rules) != 0
        
        # Consider the case where only the required course may be taken
        
        normal_set = schedulables
        # Remove the optional course from the set if it is present
        if self.optional_course in schedulables:
            normal_set = schedulables.copy() # Make a copy of the passed schedulables before modifying
            del normal_set[self.optional_course] # Remove the optional course from the "normal" set
        
        if more_coreq_rules_remain:
            # There are other coreq rules to apply (get results from next rule)
            result += remainging_coreq_rules[0].apply(normal_set, remainging_coreq_rules[1:])
        else:
            # Base case for recursive call (simple append the result)
            result.append(normal_set)
        
        
        # Conside the case where both the required and optional courses are taken (create a composite course)
        
        if self.required_course in schedulables and self.optional_course in schedulables:
            composite_set = schedulables.copy() # Make a copy of the passed schedulables before modifying
            
            # Replace the schedulable object for the required and the optional courses with a composite
            # schedulable object that combines the courses, hours, and fitness (plus additional fitness)
            new_composite = composite_set[self.required_course].make_combined(composite_set[self.optional_course])
            new_composite.fitness += self.additional_fitness
            composite_set[self.required_course] = new_composite
            del composite_set[self.optional_course]
            
            if more_coreq_rules_remain:
                # There are other coreq rules to apply (get results from next rule)
                result += remainging_coreq_rules[0].apply(composite_set, remainging_coreq_rules[1:])
            else:
                # Base case for recursive call (simple append the result)
                result.append(composite_set)
        
        return result


# This object represents a set of rules that are applied for fitness
# NOTE: this is also responsible for checking coreq. constraints. Omitting coreq.s will not only lead to
# potentially unoptimized paths, it could lead to invalid paths.
class FitnessConfiguration:
    
    def __init__(self, atomic_rules, coreq_rules):
        self.atomic_rules = atomic_rules
        self.coreq_rules = coreq_rules
    
    # function: (string, course_info_container) -> float
    def add_atomic_rule(self, function):
        self.atomic_rules.add(function)
    
    def add_coreq_rule(self, required_course, optional_course, additional_fitness):
        self.coreq_rules.add(CoreqRule(required_course, optional_course, additional_fitness))
    

# A class for representing schedulable entities (courses or groups of courses). This may be used to construct
# composites courses that simulate dependant courses--like coreq.s.
class _Schedulable:
    
    def __init__(self, course=None, hours=0):
        self.courses = { course } if course is not None else set()
        self.hours = hours
        self.fitness = 0
        
    def make_combined(self, schedulable):
        result = _Schedulable()
        result.courses = self.courses.union(schedulable.courses)
        result.hours = self.hours + schedulable.hours
        result.fitness = self.fitness + schedulable.fitness
        return result
        
    def get_fitness_per_credit_hour(self):
        return self.fitness / max(1, self.hours)


def get_fittest_courses(hours, courses, fitness_configuration, course_info_container):
    
    # Check if the courses list is empty
    if not courses:
        return []
    
    schedulables = {}
    total_course_hours = 0
    
    # Apply atomic rules
    for course in courses:
        
        course_hours = course_info_container.get_hours(course)
        schedulable = _Schedulable(course, course_hours)
        total_course_hours += course_hours
        
        for atomic_rule in fitness_configuration.atomic_rules:
            schedulable.fitness += atomic_rule(course, course_info_container)
            
        schedulables[course] = schedulable
    
    # Return the input list if there is no need to check (enough hours per semester)
    if total_course_hours <= hours:
        return courses
    
    possibilities = [schedulables]
    
    # Apply coreq. rules if present
    coreq_rules = fitness_configuration.coreq_rules
    if coreq_rules:
        possibilities = coreq_rules[0].apply(schedulables, coreq_rules[1:])
        
    # Return the best of all generated possibilites
    best_possibility = _get_best_possibilities(hours, possibilities)
    return best_possibility
    

def _get_best_possibilities(hours, possibilities):
        
    # Create variables to track the best working semester and fitness score
    best_possibility_schedule = []
    best_possibility_fitness = -math.inf
    
    for possibility in possibilities:
        
        # Make a list of course IDs in order of 0="least fit" to n="most fit"
        # Sorting is done via fitness per credit hour
        ordered_possibility = sorted(possibility,
                                     key=lambda course: possibility[course].get_fitness_per_credit_hour())
        # Create variables to track the current semester possibility
        possibility_fitness = 0
        possibility_schedule = []
        possibility_hours_left = hours
        
        # Consume courses until the all courses have been considered or the number of hours left has been exhausted
        while ordered_possibility and possibility_hours_left >= 0:
            top_course = possibility[ordered_possibility.pop()]
            if possibility_hours_left >= top_course.hours:
                possibility_hours_left -= top_course.hours
                possibility_schedule += list(top_course.courses)
                possibility_fitness += top_course.fitness
                
        # Check if the current possibility beats the working best (replace if so)
        if possibility_fitness > best_possibility_fitness:
            best_possibility_schedule = possibility_schedule
            best_possibility_fitness = possibility_fitness
        
    return best_possibility_schedule



