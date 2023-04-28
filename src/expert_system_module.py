# Thomas Merino
# 11/28/22
# CPSC 4175

import math
import itertools
from schedule_inspector import *


# ---------------------------------------- Expert System ----------------------------------------


# On this expert system:
# This is a very simple example of an expert system (not exemplary). For example, the interface component is nothing more than an
# iteration. This is because the program has access to the path to graduation (input), and, thus, no input is needed by the user, it
# is handled entirely by the program. The greater purpose/application of this is to judge the fitness of the path. Adjusting the values
# of the weights and rules may need more work.


# Use Guide:

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


# NOTE the "schedule" to rules is a list of list of CourseRecord objects at the moment: list[list[CourseRecord]]

# Translation map from semester K to the next

# Lew change global variable name to SEMESTER_TYPE_SUCCESSOR1; conflict with general_utilities.py SEMESTER_TYPE_SUCCESSOR
SEMESTER_TYPE_SUCCESSOR1 = {'Fa': 'Sp', 'Sp': 'Su', 'Su': 'Fa'}
COURSE_RULE = 0b0001
PATH_RULE = 0b0010

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
def confidencerule(confidence=1.0, rule_mask=PATH_RULE):
    def get(method):
        rule = ConfidenceRule(method, confidence, True)
        rule.rule_mask = rule_mask
        return rule
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
def rulebuilder(confidence=1.0, rule_mask=PATH_RULE):
    def get(method):
        rule = ConfidenceRule(_LazyRule(method), confidence, True)
        rule.rule_mask = rule_mask
        return rule
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
        self.course_rules = []
        self.path_rules = []
        
        for attribute_name in dir(self):
            attribute = getattr(self, attribute_name)
            if type(attribute) == ConfidenceRule and attribute.is_used:
                self.add_rule(attribute)
            
    
    def add_rule(self, confidence_rule):
        if confidence_rule.rule_mask & COURSE_RULE != 0:
            self.course_rules.append(confidence_rule)
            
        if confidence_rule.rule_mask & PATH_RULE != 0:
            self.path_rules.append(confidence_rule)
    
    # This is the inference engine
    def calculate_confidence(self, dynamic_knowledge, course_info):
        
        courses_path_cf_sum = 0
        schedule = dynamic_knowledge.get_schedule()
        semester_type = 'Fa'
        
        for semester_index, semester in enumerate(schedule):
            
            semester_cf_sum = 0
            # Create a semester container with the type, index, and courses
            semester_info = SemesterInfoContainer(semester_type, semester_index, semester)
            
            for course in semester:
                course_cf = 1
                for rule in self.course_rules:
                    rule_factor = rule(course, dynamic_knowledge.facts, semester_info, course_info)
                    course_cf = min(course_cf, rule_factor)
                semester_cf_sum += course_cf
            # Lew suggests fix below: Division by 0 error can occur for empty semester; empty semesters are common.
            semester_average = 1 if len(semester) == 0 else semester_cf_sum / len(semester)
            courses_path_cf_sum += semester_average
            
            # Lew change global variable name to SEMESTER_TYPE_SUCCESSOR1; conflict with general_utilities.py SEMESTER_TYPE_SUCCESSOR
            semester_type = SEMESTER_TYPE_SUCCESSOR1[semester_type]
        # Lew suggests fix below: Division by 0 error can occur for empty schedule: may never happen, but better to be safe.
        courses_average_cf = 1 if len(schedule) == 0 else courses_path_cf_sum / len(schedule)
        
        # Path to graduation rules (complete schedule taken into account)
        # TODO: make this not look dumb
        path_path_cf_sum = 0
        for rule in self.path_rules:
            path_path_cf_sum += rule(schedule, dynamic_knowledge.facts, course_info)
            
        path_rules_count = len(self.path_rules)
        path_average_cf = path_path_cf_sum / path_rules_count if path_rules_count != 0 else courses_average_cf
        
        # TODO: make something better here (such as weighted average)
        return (courses_average_cf + path_average_cf) / 2.0



    @confidencerule(confidence=1.0, rule_mask=PATH_RULE)
    def stub_rule(schedule, facts, course_info):
        
        semester_upper_half_count = 0
        semester_lower_half_count = 0
        semester_half = len(schedule)

        for semester_number, semester in enumerate(schedule):
            for course in semester:
                if course.stub:
                    if semester_number < semester_half:
                        semester_upper_half_count += 1
                    else:
                        semester_lower_half_count += 1
            
        score = math.atan((semester_upper_half_count - semester_lower_half_count)/7) / math.pi + 0.5
        return score


    @confidencerule(confidence=1.0, rule_mask=PATH_RULE)
    def importance_rule(schedule, facts, course_info):
        
        # TODO: implement
        for semester_number, semester in enumerate(schedule):
            for course in semester:
                if course.importance:
                    pass
        
        return 1


    #  .................................... Lew's Rules ....................................
    #  ------------------------------------ Senior Rule ------------------------------------
    #  The senior_rule checks for 1000/2000 level classes in the senior year semesters.

    @confidencerule(confidence=1.0, rule_mask=PATH_RULE)
    def senior_rule(schedule, facts, course_info):
        es = ExpertSystem
        rule = es.rule_senior_ok | es.rule_senior_a
        return rule(schedule, facts, course_info)

    @rulepart(confidence=1)
    def rule_senior_ok(schedule, facts, course_info):
        if senior_with_1000_level_courses(schedule): return 0
        if senior_with_2000_level_courses(schedule): return 0
        return 1

    @rulepart(confidence=1)
    def rule_senior_a(schedule, facts, course_info):
        cf = 1
        info1000 = senior_with_1000_level_count(schedule)
        info2000 = senior_with_2000_level_count(schedule)
        count1000, message1000 = info1000[0], info1000[1]
        count2000, message2000 = info2000[0], info2000[1]  
        cf -= (high() * count1000)  
        cf -= (low() * count2000)
        return cf

    # ------------------------------------ Junior Rule ------------------------------------
    #  The junior_rule checks for 1000 level classes in junior year semesters.

    @confidencerule(confidence=1.0, rule_mask=PATH_RULE)
    def junior_rule(schedule, facts, course_info):
        es = ExpertSystem
        rule = es.rule_junior_ok | es.rule_junior_a
        return rule(schedule, facts, course_info)

    @rulepart(confidence=1)
    def rule_junior_ok(schedule, facts, course_info):
        if junior_with_1000_level_courses(schedule): return 0
        return 1

    @rulepart(confidence=1)
    def rule_junior_a(schedule, facts, course_info):
        cf = 1
        info = junior_with_1000_level_count(schedule)
        count, message = info[0], info[1]
        cf -= (high() * count)
        return cf

     # ------------------------------------ Sophmore Rule -----------------------------------
     # The sophmore_rule checks for 4000 level classes in sophmore year semesters.

    @confidencerule(confidence=1.0, rule_mask=PATH_RULE)
    def sophmore_rule(schedule, facts, course_info):
        es = ExpertSystem
        rule = es.rule_sophmore_ok | es.rule_sophmore_a
        return rule(schedule, facts, course_info)

    @rulepart(confidence=1)
    def rule_sophmore_ok(schedule, facts, course_info):
        if sophmore_with_4000_level_courses(schedule): return 0
        return 1

    @rulepart(confidence=1)
    def rule_sophmore_a(schedule, facts, course_info):
        cf = 1
        info = sophmore_with_4000_level_count(schedule)
        count, message = info[0], info[1]
        cf -= (high() * count)
        return cf

    # ------------------------------------ Freshman Rule -----------------------------------
    # The freshman_rule checks for 4000/3000 level classes in freshman year semesters.

    @confidencerule(confidence=1.0, rule_mask=PATH_RULE)
    def freshman_rule(schedule, facts, course_info):
        es = ExpertSystem
        rule = es.rule_freshman_ok | es.rule_freshman_a
        return rule(schedule, facts, course_info)

    @rulepart(confidence=1)
    def rule_freshman_ok(schedule, facts, course_info):
        if freshman_with_3000_level_courses(schedule): return 0
        if freshman_with_4000_level_courses(schedule): return 0
        return 1

    @rulepart(confidence=1)
    def rule_freshman_a(schedule, facts, course_info):
        cf = 1
        info3000 = freshman_with_3000_level_count(schedule)
        info4000 = freshman_with_4000_level_count(schedule)[0], freshman_with_4000_level_count(schedule)[1]
        count3000, message3000 = info3000[0], info3000[1]
        count4000, message4000 = info4000[0], info4000[1]
        cf -= (low() * count3000)
        cf -= (high() * count4000)
        return cf

    # ------------------------------------ Empty Rule ----------------------------------
    # The empty_rule detects empty semesters.  Two empty semesters is cause for concern.

    @confidencerule(confidence=1.0, rule_mask=PATH_RULE)
    def empty_rule(schedule, facts, course_info):
        es = ExpertSystem
        rule = es.rule_empty_ok | es.rule_empty_a
        return rule(schedule, facts, course_info)

    @rulepart(confidence=1)
    def rule_empty_ok(schedule, facts, course_info):
        count = empty_lists_in_schedule_count(schedule)[0]
        if count > 1: return 0
        return 1

    @rulepart(confidence=1)
    def rule_empty_a(schedule, facts, course_info):
        cf = 1
        info = empty_lists_in_schedule_count(schedule)
        count, message = info[0], info[1]
        count -= 1
        cf -= (high() * count)
        return cf

# ........................................ End Lew's Rules ................................
# ---------------------------------------- Testing ----------------------------------------
# Testing:

#if __name__ == '__main__':
    
#    # Scheduling testing (NOTE: none of these courses exist):
    
#    prereqs = {
#        '1302': ['1301'],
#        '2105': ['1301'],
#    }
    
#    class DummyContainer:
#        def get_hours(self, course):
#            return 3
#        def get_prereqs(self, course):
#            return prereqs[course] if course in prereq else []

#    # Test coreq. rules: (required course, optional course, extra fitness points for scheduling together)
#    r1 = CoreqRule('2005', '2006', 9)
#    r2 = CoreqRule('3005', '3006', 6)
#    r3 = CoreqRule('4005', '4006', 5)

#    # Test atomic rules
#    a1 = lambda c, i: 8 if 'e' in c else 0   # Rule that adds 8 fitness points if 'e' is in the course name
#    a2 = lambda c, i: int(c[0])              # Rule that sets the fitness to the first digit in the course name
#    a3 = lambda c, i: 100 if 'h' in c else 0 # Rule that adds 100 fitness points if 'h' is in the course name
    
#    test_hours = 13
#    test_courses = ['2005', '2006', '3005', '3006', '5300', '1h00', '4e00']
    
#    test_fitness_configuration_1 = FitnessConfiguration([a1, a2, a3], [r1, r2, r3])
#    test_fitness_configuration_2 = FitnessConfiguration([], [r1, r2, r3])
    
#    output_1 = get_fittest_courses(test_hours, test_courses, test_fitness_configuration_1, DummyContainer())
#    output_2 = get_fittest_courses(test_hours, test_courses, test_fitness_configuration_2, DummyContainer())
#    print(output_1)
#    print(output_2)
    
    
#    es = ExpertSystem.get_default_instance()
#    #print([(r, r.confidence) for r in es.rules])
#    kb = DynamicKnowledge()
#    schedule = [['1301'], ['1302', '2105']]
#    #kb.load_facts({'Needs_' + c for c in courses})
#    kb.set_schedule(schedule)
    
#    print(es.calculate_confidence(kb, DummyContainer()))

# ---------------------------------------- Lew Testing ----------------------------------------

#from driver_fs_functions import *
#from course_info_container import *
#from scheduler_driver import *

#file0 = get_source_path()
#file0 = get_source_relative_path(file0, 'input_files/Course Info.xlsx')
#dfdict = load_course_info(file0)
#container = CourseInfoContainer(dfdict)

#course_identifier_CPSC_3121 = DummyCourseIdentifier(course_number="CPSC 3121")
#course_identifier_CPSC_3165 = DummyCourseIdentifier(course_number="CPSC 3165")
#course_identifier_CPSC_4000 = DummyCourseIdentifier(course_number="CPSC 4000")
#course_identifier_CPSC_4135 = DummyCourseIdentifier(course_number="CPSC 4135")
#course_identifier_MATH_1113 = DummyCourseIdentifier(course_number="MATH 1113")
#course_identifier_STAT_3127 = DummyCourseIdentifier(course_number="STAT 3127")
#course_identifier_CPSC_2108 = DummyCourseIdentifier(course_number="CPSC 2108")
#course_identifier_CPSC_3125 = DummyCourseIdentifier(course_number="CPSC 3125")
#course_identifier_CPSC_XXXX = DummyCourseIdentifier(course_number="CPSC XXXX", name="Elective", is_stub=True)
#course_identifier_CPSC_3XX = DummyCourseIdentifier(course_number="CPSC 3@X", name="Elective", is_stub=True)

#cr1 = container.get_course_record(course_identifier_CPSC_3121)
#cr2 = container.get_course_record(course_identifier_CPSC_3165)
#cr3 = container.get_course_record(course_identifier_CPSC_4000)
#cr4 = container.get_course_record(course_identifier_CPSC_4135)
#cr5 = container.get_course_record(course_identifier_MATH_1113)
#cr6 = container.get_course_record(course_identifier_STAT_3127)
#cr7 = container.get_course_record(course_identifier_CPSC_2108)
#cr8 = container.get_course_record(course_identifier_CPSC_3125)
#crX = container.get_course_record(course_identifier_CPSC_XXXX)
#crY = container.get_course_record(course_identifier_CPSC_3XX)

#bad_list =[[cr1, cr2, crX], [cr3, cr4, crY], [cr5, cr6, cr7, cr8], 
#         [cr1, cr2, crX], [cr3, cr4, crY], [cr5, cr6, cr7, cr8], 
#         [cr1, cr2, crX], [cr3, cr4, crY], [cr5, cr6, cr7, cr8], 
#         [cr1, cr2, crX], [cr3, cr4, crY], [cr5, cr6, cr7, cr8]]

#good_list =[[cr5, cr5, cr5], [cr7, cr7, cr7], [cr5, cr5, cr5, cr5], 
#         [cr1, cr2, cr7], [cr1, cr2, cr7], [cr1, cr2, cr7, cr1], 
#         [cr3, cr4, cr6], [cr3, cr4, cr6], [cr3, cr4, cr6, cr3], 
#         [cr8, crX, crY], [cr8, crX, crY], [cr8, crX, crY, cr8]]


#es = ExpertSystem.get_default_instance()
#kb = DynamicKnowledge()

#kb.set_schedule(good_list)
#print(es.calculate_confidence(kb, container))



