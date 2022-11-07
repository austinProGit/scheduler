# Thomas Merino
# 11/7/22
# CPSC 4175

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
    weight = course_info_container.get_weight(courseID)
    if weight is None:
        weight = LOW_FITNESS
    fitness = HIGH_FITNESS - (HIGH_FITNESS - LOW_FITNESS) / (weight + 1)
    return fitness
    
def availability_rule(courseID, course_info_container):
    availability_list = course_info_container.availability_list(courseID)
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
            normal_set = schedulables.copy()        # Make a copy of the passed schedulables before modifying
            del normal_set[self.optional_course]    # Remove the optional course from the "normal" set
        
        if more_coreq_rules_remain:
            # There are other coreq rules to apply (get results from next rule)
            result += remainging_coreq_rules[0].apply(normal_set, remainging_coreq_rules[1:])
        else:
            # Base case for recursive call (simple append the result)
            result.append(normal_set)
        
        
        # Conside the case where both the required and optional courses are taken (create a composite course)
        
        if self.required_course in schedulables and self.optional_course in schedulables:
            composite_set = schedulables.copy()     # Make a copy of the passed schedulables before modifying
            
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
    def add_atomic_rule(function):
        self.atomic_rules.add(function)
    
    def add_coreq_rule(required_course, optional_course, additional_fitness):
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
        result.fitness = self.fitness + self.fitness
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




# ---------------------------------------- Expert System ----------------------------------------


# NOTE/README:
# I had the realization that the model I had been working on should not apply to individual semesters. We should
# instead judge an entire path per expert system call. The format when all is said and done should be creating
# boolean rules that have associated with them a confidence factor/value. It might be valuable to assign the
# relevant inputs for a given rule--irrelevant courses should be assumed to return True since the antecedent
# would be False.


# Guide:

# There are 3 rules:

# confidencerule(confidence=1.0): this rule will be detected and used by the ES automatically. Methods that have confidencerule
# decorators are expected to have the following signature: (course, facts, semester_info, course_info) -> float. The float
# return is the level truth (fuzzy boolean) of adhering to the rule. This is multiplied by the confidence afterwards
# automatically to get the CF result.

# rulepart(confidence=1.0): this is the same as a confidencerule, but it is not used automatically by the ES. These are intended
# to be used to construct other rules.

# rulebuilder(confidence=1.0): this is similar to a confidencerule (detected and used by the ES automatically). However, the
# signature is () -> ConfidenceRule or RuleCompositeNode. This uses a lazy call to make and store the rule, using it every time
# afterward when the rule is called (via the same signature as confidencerule). This is just a version of confidencerule that
# is better optmized for using composite rules (via |, &, +). This does not have the same flexibility as confidencerule, however.


# There are the following 3 rule operations:

# For the following, we are going to imagine the CF is like the change of picking (by chance) a piece of candy from a bag of
# marbles. The confidence is the maximum amount (0 to 1) of the bag that can be composed of candy. The return value of the rule
# is the amount (0 to 1) of that maximum that happens to be candy for the passed arguments. The result/return of the rule is alike
# the chance of picking a piece of candy from a bag.

# |: this is like selecting from the two passed bags the bag that gives the BEST change of picking a piece of candy. This is
# essentially getting the MAX of the return values. This also uses short-circuit evaluation if a 1 is encountered.

# &: this is like selecting from the two passed bags the bag that gives the WORST change of picking a piece of candy. This is
# essentially getting the MIN of the return values. This also uses short-circuit evaluation if a 0 is encountered.

# +: this is like trying to pick a piece of candy from the first bag and, if a marble is picked, then try the other bag. This is
# a more real-life "or" operation.

# The reason there is no "average" operation is that taking the average would require n-many arguments, and the
# operations can only be binary (2 arguments). To get the average, you will have to use a confidencerule and for
# each operand calculate the value (float). After that, you can calculate the average.


# CF is the average of CF of each semester
# CF for semester is the average of courses
# CF for course is the minimum of all rules' CF (critical/thorough advisor)
# CF of rule is application (0 to 1--if not applicable, then return 1)
# Each CF method/function also has associated with it a CF to apply (expert data)
# Outer most CF rules should have a confidence of 1 (partial rules can be less when used in conjuction with "+" operation)


# Potential rules:
# Standard deviation, 1000 courses taken with 4000 courses
# taking high-weight courses early, taking recommended pairs close to each other (from perspective of later course)
# Taking courses at a given time/semester


# Translation map from semester K to the next
SEMESTER_TYPE_SUCCESSOR = {'Fa': 'Sp', 'Sp': 'Su', 'Su': 'Fa'}


class ConfidenceRule:

    # This is used to create a binary tree of operations
    class RuleCompositeNode:
        
        # LHS and RHS are either ConfidenceRules or RuleCompositeNodes (or mixed)
        def __init__(self, lhs, rhs, operation):
            self.lhs = lhs
            self.rhs = rhs
            self.operation = operation
                    
        def __call__(self, *args):
            return self.operation(self, *args)
                
                
        def __add__(self, other):
            return ConfidenceRule.RuleCompositeNode(self, other, ConfidenceRule.RuleCompositeNode.add_operation)
            
        def __and__(self, other):
            return ConfidenceRule.RuleCompositeNode(self, other, ConfidenceRule.RuleCompositeNode.and_operation)
            
        def __or__(self, other):
            return ConfidenceRule.RuleCompositeNode(self, other, ConfidenceRule.RuleCompositeNode.or_operation)
        
        
        @staticmethod
        def and_operation(self, *args):
            lhs_factor = self.lhs(*args)
            if lhs_factor == 0:
                return 0
            return min(lhs_factor, self.rhs(*args))
        
        @staticmethod
        def or_operation(self, *args):
            lhs_factor = self.lhs(*args)
            if lhs_factor == 1:
                return 1
            return max(lhs_factor, self.rhs(*args))
        
        @staticmethod
        def add_operation(self, *args):
            lhs_factor = self.lhs(*args)
            rhs_factor = self.rhs(*args)
            return lhs_factor + rhs_factor - lhs_factor * rhs_factor
            
        
    
    def __init__(self, method, confidence, is_used):
        self.method = method
        self.confidence = confidence
        self.is_used = is_used
    
    def __call__(self, *args):
        return self.confidence * self.method(*args)
            
    def __add__(self, other):
        return ConfidenceRule.RuleCompositeNode(self, other, ConfidenceRule.RuleCompositeNode.add_operation)
        
    def __and__(self, other):
        return ConfidenceRule.RuleCompositeNode(self, other, ConfidenceRule.RuleCompositeNode.and_operation)
    
    def __or__(self, other):
        return ConfidenceRule.RuleCompositeNode(self, other, ConfidenceRule.RuleCompositeNode.or_operation)
    
    

# This is a method decorator that lets a method pass as a ConfidenceRule.
def confidencerule(confidence=1.0):
    def get(method):
        return ConfidenceRule(method, confidence, True)
    return get


# This is a method decorator that lets a method pass as a ConfidenceRule.
def rulepart(confidence=1.0):
    def get(method):
        return ConfidenceRule(method, confidence, False)
    return get

    
class _LazyRule:
    def __init__(self, method):
        self.rule = None
        self.method = method
    
    def __call__(self, *args):
        if self.rule is None:
            self.rule = self.method()
        return self.rule(*args)


# This is a method decorator that lets a method pass as a ConfidenceRule.
def rulebuilder(confidence=1.0):
    def get(method):
        return ConfidenceRule(_LazyRule(method), confidence, True)
    return get



# This is the dynamic part of the knowledge base (the course info container is the static)

class DynamicKnowledge:
    
    def __init__(self):
        # This is the database/working memory
        
        # The list of lists that contains course IDs
        self.schedule = []
        # The general fact mapping--this may be used for passing in other arguments that rules utilize
        self.facts = {}
    
    def get_schedule(self):
        return self.schedule
    
    def load_facts(self, fact_mapping):
        self.facts.update(fact_mapping)
        
    def set_schedule(self, schedule):
        '''Set the schedule (list of lists of course IDs) for the instance. Note that the first list is assumed to be the Fall, then Spring, then Summer, then back to Fall, and so on.'''
        self.schedule = schedule
        

class SemesterInfoContainer:
    
    def __init__(self, semester_type, semester_index, courses):
        self.semester_type = semester_type
        self.semester_index = semester_index
        self.courses = courses
    

class ExpertSystem:

    _default_instance = None
    
    @staticmethod
    def get_default_instance():
        if ExpertSystem._default_instance is None:
            ExpertSystem._default_instance = ExpertSystem()
        return ExpertSystem._default_instance
    
    def __init__(self):
        
        # These are the rules for the system
        self.rules = []
        
        for attribute_name in dir(self):
            attribute = getattr(self, attribute_name)
            if type(attribute) == ConfidenceRule and attribute.is_used:
                self.add_rule(attribute)
            
    
    def add_rule(self, confidence_rule):
        self.rules.append(confidence_rule)
    
    # This is the inference engine
    def calculate_confidence(self, dynamic_knowledge, course_info):
        
        path_cf_sum = 0
        schedule = dynamic_knowledge.get_schedule()
        semester_type = 'Fa'
        
        for semester_index, semester in enumerate(schedule):
            
            semester_cf_sum = 0
            # Create a semester container with the type, index, and courses
            semester_info = SemesterInfoContainer(semester_type, semester_index, semester)
            
            for course in semester:
                course_cf = 1
                for rule in self.rules:
                    rule_factor = rule(course, dynamic_knowledge.facts, semester_info, course_info)
                    course_cf = min(course_cf, rule_factor)
                semester_cf_sum += course_cf
            
            semester_average = semester_cf_sum / len(semester)
            path_cf_sum += semester_average
            
            semester_type = SEMESTER_TYPE_SUCCESSOR[semester_type]
        
        average_cf = path_cf_sum / len(schedule)
        return average_cf
    
    
    @confidencerule(confidence=1.0)
    def coreq_fitness(course, facts, semester_info, course_info):
        # TODO: implement
        return 1 # False
    
    @confidencerule(confidence=1.0)
    def gatekeeper_rule(course, facts, semester_info, course_info):
        # TODO: implement
        #return course_info.get_weight(course) > 2
        return 1 # False
    
    
    # TESTING rules:
    
    @rulepart(confidence=0.3)
    def rule_a1(course, facts, semester_info, course_info):
        return 1 if course in ['1301'] else 0
    
        
    @rulepart(confidence=0.3)
    def rule_a2(course, facts, semester_info, course_info):
        return 1 if course in ['1302'] else 0
    
        
    @rulepart(confidence=0.3)
    def rule_a3(course, facts, semester_info, course_info):
        return 1 if course in ['1301', '1302'] else 0
    
    @rulepart(confidence=0.9)
    def rule_b(course, facts, semester_info, course_info):
        return 1 if '13' in course or '21' in course else 0
        
            
    @confidencerule()
    def new_rule1(course, facts, semester_info, course_info):
        es = ExpertSystem
        rule = es.rule_b + es.rule_b + es.rule_b + es.rule_b | es.rule_a3
        return rule(course, facts, semester_info, course_info)
        
    @rulebuilder()
    def new_rule2():
        es = ExpertSystem
        rule = (es.rule_a1 + es.rule_a2 + es.rule_a3) + es.rule_b
        return rule



# ---------------------------------------- Testing ----------------------------------------

# Testing:


if __name__ == '__main__':
    
    # Scheduling testing (NOTE: none of these courses exist):
    
    prereqs = {
        '1302': ['1301'],
        '2105': ['1301'],
    }
    
    class DummyContainer:
        def get_hours(self, course):
            return 3
        def get_prereqs(self, course):
            return prereqs[course] if course in prereq else []

    # Test coreq. rules: (required course, optional course, extra fitness points for scheduling together)
    r1 = CoreqRule('2005', '2006', 9)
    r2 = CoreqRule('3005', '3006', 6)
    r3 = CoreqRule('4005', '4006', 5)

    # Test atomic rules
    a1 = lambda c, i: 8 if 'e' in c else 0   # Rule that adds 8 fitness points if 'e' is in the course name
    a2 = lambda c, i: int(c[0])              # Rule that sets the fitness to the first digit in the course name
    a3 = lambda c, i: 100 if 'h' in c else 0 # Rule that adds 100 fitness points if 'h' is in the course name
    
    test_hours = 13
    test_courses = ['2005', '2006', '3005', '3006', '5300', '1h00', '4e00']
    
    test_fitness_configuration_1 = FitnessConfiguration([a1, a2, a3], [r1, r2, r3])
    test_fitness_configuration_2 = FitnessConfiguration([], [r1, r2, r3])
    
    output_1 = get_fittest_courses(test_hours, test_courses, test_fitness_configuration_1, DummyContainer())
    output_2 = get_fittest_courses(test_hours, test_courses, test_fitness_configuration_2, DummyContainer())
    print(output_1)
    print(output_2)
    
    
    es = ExpertSystem.get_default_instance()
    #print([(r, r.confidence) for r in es.rules])
    kb = DynamicKnowledge()
    schedule = [['1301'], ['1302', '2105']]
    #kb.load_facts({'Needs_' + c for c in courses})
    kb.set_schedule(schedule)
    
    print(es.calculate_confidence(kb, DummyContainer()))
