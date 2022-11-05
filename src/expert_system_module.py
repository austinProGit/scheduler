# Thomas Merino
# 11/4/22
# CPSC 4175

import math
import itertools

# ---------------------------------------- Scheduling System ----------------------------------------

# This module needs to perform 2 functions: pick a set of courses with the highest confidence value given the number of credit hours and the available courses.

# Coreq.s will be handled in the following way: some arguments will have variants. The entire decision-making process will be executed with each possible combination of variants. For example, if there are two courses that appear in two version (say, A1 and A2 and B1 and B2), then the process is executed 4 times: {A1, B1}, {A1, B2}, {A2, B1}, and {A2, B2}. When dealing with coreq.s, we will consider the scenario where only the required course is available and the scenario where the two classes are made into a single compound course.

# NOTE: this does not work when there are coreq overlaps/collisions

class CoreqRule:
    
    def __init__(self, required_course, optional_course, additional_fitness):
        self.required_course = required_course
        self.optional_course = optional_course
        self.additional_fitness = additional_fitness
    
    def apply(self, schedulables, remainging_coreq_rules):
        '''Recursive method: this should only be called by recursive calls or by the get_fittest_courses function.'''
        
        result = []
        
        normal_set = schedulables.copy()
        if self.optional_course in schedulables:
            del normal_set[self.optional_course]
        
        if len(remainging_coreq_rules) != 0:
            result += remainging_coreq_rules[0].apply(normal_set, remainging_coreq_rules[1:])
        else:
            result.append(normal_set)
        
        
        if self.required_course in schedulables and self.optional_course in schedulables:
            composite_set = schedulables.copy()
            new_composite = composite_set[self.required_course].make_combined(composite_set[self.optional_course])
            new_composite.fitness += self.additional_fitness
            composite_set[self.required_course] = new_composite
            del composite_set[self.optional_course]
            
            if len(remainging_coreq_rules) != 0:
                result += remainging_coreq_rules[0].apply(composite_set, remainging_coreq_rules[1:])
            else:
                result.append(composite_set)
        
        return result



class FitnessConfiguration:
    
    def __init__(self, atomic_rules, coreq_rules):
        self.atomic_rules = atomic_rules
        self.coreq_rules = coreq_rules
    
    # function: (string, course_info_container) -> float
    def add_atomic_rule(function):
        self.atomic_rules.add(function)
    
    def add_coreq_rule(required_course, optional_course, additional_fitness):
        self.coreq_rules.add(CoreqRule(required_course, optional_course, additional_fitness))
    


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
        
    best_possibility_schedule = []
    best_possibility_fitness = -math.inf
        
    for possibility in possibilities:
        
        ordered_possibility = sorted(possibility,
                                     key=lambda course: possibility[course].get_fitness_per_credit_hour())
        possibility_fitness = 0
        possibility_schedule = []
        possibility_hours_left = hours
        
        while ordered_possibility and possibility_hours_left >= 0:
            top_course = possibility[ordered_possibility.pop()]
            if possibility_hours_left >= top_course.hours:
                possibility_hours_left -= top_course.hours
                possibility_schedule += list(top_course.courses)
                possibility_fitness += top_course.fitness
                
        
        if possibility_fitness > best_possibility_fitness:
            best_possibility_schedule = possibility_schedule
            best_possibility_fitness = possibility_fitness
        
    return best_possibility_schedule




# ---------------------------------------- Expert System ----------------------------------------


# 'Courses' have the following format:
# <COURSE>: the process
# Needs_<COURSE>: the fact that the course need to be taken
# Can_Take_<COURSE>: the fact that the course can be taken for the current semester


# NOTE/README:
# I had the realization that the model I had been working on should not apply to individual semesters. We should
# instead judge an entire path per expert system call. The format when all is said and done should be creating
# boolean rules that have associated with them a confidence factor/value. It might be valuable to assign the
# relevant inputs for a given rule--irrelevant courses should be assumed to return True since the antecedent
# would be False.

class ConfidenceRule:
    def __init__(self, method, confidence):
        self.method = method
        self.confidence = confidence
    
    def __call__(self, *args):
        return self.method(*args)

def confidencerule(confidence):
    def get(method):
        return ConfidenceRule(method, confidence)
    return get


# This is the dynamic part of the knowledge base (the course info container is the static)

class ScheduleDynamicMemory:
    
    def __init__(self):
        # This is the database/working memory
        self.process_list = []          # The processes to iterate over during inference engine running
        self.facts = set()              # The general working memory
        self.fitness_mapping = {}       # Working fitness mapping for determining results
        
    
    class DrawIterator:
        
        def __init__(self, dynamic_knowledge):
            self.dynamic_knowledge = dynamic_knowledge
        
        def __iter__(self):
            return self
        
        def __next__(self):
            element = self.dynamic_knowledge.draw()
            if element:
                return element
            else:
                raise StopIteration()
    
    # TODO: remove this (not needed)
    def draw(self):
        '''Pop the best item.'''
        
        # Get the value with the highest fitness factor
        result = None
        working_fitness = -math.inf
        for (process, fitness) in self.fitness_mapping.items():
            if working_fitness < fitness:
                result = process
                working_fitness = fitness
        
        if working_fitness <= 0:
            result = None
        
        if result:
            # Remove data related to the popped item (assumed to be taken)
            del self.fitness_mapping[result]
            self.process_list.remove(result)
            self.facts = self.facts.difference({'Can_Take_' + result, 'Needs_' + result})
        
        return result
    
    def load_facts(self, fact_set):
        self.facts.update(fact_set)
        
    def load_process(self, process_list):
        self.process_list += process_list


class ExpertSystem:
    
    def __init__(self):
        
        # These are the rules for the system
        self.rules = [ExpertSystem.coreq_fitness, ExpertSystem.gatekeeper_fitness]
    
    # Method so you can just iterate over a path to a graduation
    def run_on(self, dynamic_knowledge, course_info):
        return ExpertSystem.KnowledgeBaseIterator(self, dynamic_knowledge, course_info)
    
    class KnowledgeBaseIterator:
        
        def __init__(self, inference_engine, dynamic_knowledge, course_info):
            self.inference_engine = inference_engine
            self.dynamic_knowledge = dynamic_knowledge
            self.course_info = course_info
            
        def __iter__(self):
            return self
        
        def __next__(self):
            if not self.dynamic_knowledge.process_list:
                raise StopIteration()
            self.inference_engine.run_inference_engine(self.dynamic_knowledge, self.course_info)
            return ScheduleDynamicMemory.DrawIterator(self.dynamic_knowledge)
    
    def add_rule(self, confidence_rule):
        self.rules.append(confidence_rule)
    
    # This is the inference engine
    def run_inference_engine(self, dynamic_knowledge, course_info, execution_limit=1000):
        
        # NOTE: this is still the old code for generating a schedule, not judging a submitted schedule
        
        # Check if the process list is empty and exit if so
        if not dynamic_knowledge.process_list:
            return
        
        # Reset the to-be-final fitness value mapping
        dynamic_knowledge.fitness_mapping = {process:-math.inf for process in dynamic_knowledge.process_list}
        
        process_index = 0                           # The iteration index
        process = dynamic_knowledge.process_list[0]    # The iteration value
        iteration_goal = 0                          # The iteration index that, once met, will end iteration
        execution_count = execution_limit           # The absolute limit of iteration passes
        
        # Iterate until the execution limit is met (or iteration_goal is met and the loop breaks)
        while execution_count > 0:
            # The working fitness for the current process (minimum of all values)
            working_fitness = 1
            
            # Run through all rules and apply them to the current process
            for rule in self.rules:
                working_fitness = min(working_fitness, rule(process, dynamic_knowledge.facts, course_info))
            
            # Check if the fitness value is different
            if dynamic_knowledge.fitness_mapping[process] != working_fitness:
                # Update the interation goal so that another cycle is completed
                iteration_goal = process_index
                # Update the fitness factor
                dynamic_knowledge.fitness_mapping[process] = working_fitness
            
                # Check if the course can be taken and note that fact in memory if so
                if working_fitness and 'Can_Take_' + process not in dynamic_knowledge.facts:
                    dynamic_knowledge.facts.add('Can_Take_' + process)
            
            # Update process index (iteration variables) by incrementing in modulo(process count)
            process_index = (process_index + 1) % len(dynamic_knowledge.process_list)
            
            # Check if the iteration goal has been met
            if process_index == iteration_goal:
                # Break from the loop if goal met
                break
            else:
                # Update iteration variables
                process = dynamic_knowledge.process_list[process_index]
                execution_count -= 1
    
    
    @confidencerule(confidence=1.0)
    def coreq_fitness(course, facts, course_info):
        # TODO: implement
        return 1 # False
    
    @confidencerule(confidence=1.0)
    def gatekeeper_fitness(course, facts, course_info):
        # TODO: implement
        #return course_info.get_weight(course) > 2
        return 1 # False
    



# ---------------------------------------- Testing ----------------------------------------

# Testing:
#es = ExpertSystem()
#kb = ScheduleDynamicMemory()
#courses = ['1301', '1302', '2105']
#kb.load_facts({'Needs_' + c for c in courses})
#kb.load_process(courses)
#path = [['1301'], ['1302']]
#
#def plan():
#    r = []
#    for s in es.run_on(kb, 9):
#        semester = []
#        for course in s:
#            semester.append(course)
#        r.append(semester)
#    return r
#plan()


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
