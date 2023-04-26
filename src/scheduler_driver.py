# Thomas Merino
# 4/24/2023
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
from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from typing import Optional, Any
    from requirement_tree import RequirementsTree, SchedulableParameters
    from scheduling_parameters_container import ConstructiveSchedulingParametersContainers
    from course_info_container import CourseInfoContainer
    from courses_needed_container import CoursesNeededContainer
    from end_reports import ValidationReportResult
from end_reports import PathValidationReport, VALIDATION_REPORT_PARSED

from scheduling_parameters_container import ConstructiveSchedulingParametersContainers
from instance_identifiers import CourseIdentifier
from general_utilities import *

# Lew: Comment import below to prevent circular importation ERROR for isolation tests of schedule_inspector and expert_system_module to
# instantiate CourseIdentifier objects.
from expert_system_module import ExpertSystem, DynamicKnowledge

from schedule_info_container import *
from general_utilities import *

from bisect import insort
from math import inf
from random import choice, randint, shuffle, random


# TODO: THIS IS A TEST IMPORT (REMOVE)!!
from scheduler_driver_testing import CourseInfoContainer
from degree_extraction_container import DegreeExtractionContainer

# TODO: TEMP for testing part
from scheduling_parameters_container import SchedulerParameterContainer 
from pathlib import Path 

"""

============== Here are the types ==============

CourseIdentifier:
    This represents a single course or a unique pattern for a course.
    If the identifier is concrete/not a stub, then identifiers with the same course number/id are considered equivalent.
    If the identifier is not (the above), then no other identifier is consider equivalent.

Schedulable:
    This represents individual entities/entries that are entered into a schedule.
    A schedulable contains a CourseIdentifier to classify it.

NOTE: to differentiate between CourseIdentifiers and Schedulables, identifiers can be passed around/shared, duplicated,
recreated, etc., and each will work as expected. They serve as keys to identify courses or classes of courses.
Schedulables, on the other hand, represent entries in a schedule. Each schedulable should appear in a path only once--
a identifier may appear in multiple schedulables.


SemesterDescription:
    This stores a list of schedulables, representing a single scheduled semester
    
ScheduleInfoContainer:


PathValidationReport:
PathValidationReport.Error:
CourseInfoContainer:
ConstructiveScheduler:
GeneticScheduler:


============== Here are the methods ==============

rigorous_validate_schedule:
validate_user_submitted_schedule:


============== Here is the structure of the following ==============

============== Here is the gene sequence meaning ==============


An optimizer is passed a maybe-valid (depends on the particular courses) path.
This path is stored alongside another object with the same structure as the path but storing, instead of the courses, deltas
Each gene sequence represents the deltas (from the original schedule). Here is an example:


Original schedule:
FALL    SPRING  SUMMER
1101    1102    1103
1201    1202    1203
1301    1302
1401    1402


Deltas:
FALL    SPRING  SUMMER
1       -1      0
0       0       0
0       0
2       0


Result of applying deltas:
FALL    SPRING  SUMMER
1102    1101    1103
1201    1202    1203
1301    1302    1401
        1402

"""

class CreditHourInformer:

    @staticmethod
    def make_unlimited_generator() -> CreditHourInformer:
        result: CreditHourInformer = CreditHourInformer(None)
        result._generator = lambda s, y: inf
        return result

    def _invalid_generator(self, semester: SemesterType, year: int) -> int:
        raise ValueError('Illegal credit hour informer state encountered.')

    def __init__(self, meta_informer: Any):
        self._generator: Callable[[SemesterType, int], float] = self._invalid_generator
        if meta_informer is None:
            pass
        elif isinstance(meta_informer, ConstuctiveScheduler):
            self._generator = lambda s, y: meta_informer.get_hours_per_semester(s).stop

    def get(self, semester: SemesterType, year: int) -> int:
        return self._generator(semester, year)

    

def rigorous_validate_schedule(schedule: ScheduleInfoContainer,
        taken_courses: list[CourseIdentifier] = [],
        prequisite_ignored_courses: list[CourseIdentifier] = [],
        credit_hour_informer: CreditHourInformer = CreditHourInformer.make_unlimited_generator()) -> PathValidationReport:

    # TODO: implement checking for courses not appearing in course info container (unless signed off on)

    # TODO:
    # NOTE: there is a lot of longer than needed searches in this method.
    # It might be a good move to create a sometimes-hashed map for searching. There are 2 parts:
    # 1. hashed map for searching, 2. a shorter list for linear searching or no searching at all.

    running_taken_courses: list[CourseIdentifier] = taken_courses[:]
    error_list: list[PathValidationReport.Error] = []

    semester: SemesterDescription
    for semester in schedule:

        # Get the year and semester information
        working_year: int = semester.year
        working_semester: SemesterType = semester.semester_type

        # Create a tracker to determine if the limit is reached on credits for the semester 
        credits_left: int = credit_hour_informer.get(working_semester, working_year)

        # Create a list of schedulables to check (requirements)--the identifiers will be added to running_taken_courses
        currently_taking_courses: list[Schedulable] = []
        
        error_description: str
        course: Schedulable

        # Check for repeating course within a semester and update the coreq.s
        for course in semester:

            # Clear all the selections (this is the first time encountering the course)
            course.reset_all_selection()

            # Check for repeating course within a semester
            if course not in currently_taking_courses:
                
                

                # Check if the course was taken in another semester
                if course in running_taken_courses:
                    # Repeating course found in different semester (append an error report)
                    error_description = f'Taking {course} again in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                    error_list.append(PathValidationReport.Error(error_description))

                # Make each course recognize the coreq. relationship (bidirectional)
                taking_course: Schedulable
                for taking_course in currently_taking_courses:
                    course.sync_course_taking(taking_course.course_identifier)
                    taking_course.sync_course_taking(course.course_identifier)
                
                # Make each course recognize the prereq.s
                taken_course_identifier: CourseIdentifier
                for taken_course_identifier in running_taken_courses:
                    course.sync_course_taken(taken_course_identifier)

                # Append the course the to the list of currentlyt taking courses
                currently_taking_courses.append(course)

                # Record the credits
                credits_left -= course.hours
                # Check if going over credit limit per semester
                if credits_left < 0:
                    # The semester went over the limit of credits
                    error_description = f'Went over credit limit during {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                    error_list.append(PathValidationReport.Error(error_description))

            else:
                # Repeating course found in the same semester (append an error report)
                error_description = f'Taking {course} multiple times in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(PathValidationReport.Error(error_description))


        # Check for prereq.s/coreq.s and availability
        for course in currently_taking_courses:

            # Check prereq.s/coreq.s
            if not course.can_be_taken() and course not in prequisite_ignored_courses:
                # TODO: add a logic requirement print out to the report (prereq.s and coreq.s)
                # Inadequate fulfillment of requirements (append an error report)
                error_description = f'Not all requirements satisfied before taking {course} in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(PathValidationReport.Error(error_description))

            # Check availability
            if working_semester not in course.availability:
                # Inadequate fulfillment of requirements (append an error report)
                error_description = f'Availability for {course} not present in {SEMESTER_DESCRIPTION_MAPPING[working_semester]} {working_year}'
                error_list.append(PathValidationReport.Error(error_description))
        

        # Add the semester's courses to the list of courses taken
        for course in currently_taking_courses:

            # TODO: this check may be temp: >>>
            if course.can_be_taken():
                # <<<

                running_taken_courses.append(course.course_identifier)
                
                
        
    return PathValidationReport(error_list, VALIDATION_REPORT_PARSED)

    # processed_list = []
    # err_list = []
    # err_str = ''
    # current_semester = 'Su'
    
    # for semester in reversed(schedule):

    #     for course in semester:
    #         if current_semester not in container.get_availability(course):
    #             err_str = (f'{course} taken during the {USER_READABLE_SEMESTER_DESCRIPTION[current_semester]} term (not available).')
    #             err_list.append(err_str)

    #         #course_coreqs = container.get_coreqs(course)

    #         # TODO: this was added before presentation for demonstration
    #         requirements = container.get_coreqs(course) or ''
    #         tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
    #         course_coreqs = []#[i.course_number for i in tree.decision_tree.get_all_aggragate()]

    #         for coreq in course_coreqs:
    #             if coreq in processed_list:
    #                 err_str = (f'{course} taken before {coreq}.')
    #                 err_list.append(err_str)

    #     for course in semester:
    #         processed_list.append(course)
    #     for course in semester:
    #         # Check if the course is being scheduled multiple times
    #         if processed_list.count(course) > 1:
    #             err_str = (f'{course} scheduled multiple times.')
    #             if err_str not in err_list and 'XXX' not in course:
    #                 err_list.append(err_str)

    #         #course_prereqs = container.get_prereqs(course)
            
    #         # TODO: this was added before presentation for demonstration
    #         requirements = container.get_prereqs(course) or ''
    #         tree = RequirementsParser.make_from_course_selection_logic_string(requirements)
    #         course_prereqs = [i.course_number for i in tree.decision_tree.get_all_aggragate()]
            
    #         for prereq in course_prereqs:
    #             if prereq in processed_list:
    #                 err_str = (f'{course} taken before/during {prereq}.')
    #                 err_list.append(err_str)

    #     # Update the semester term
    #     current_semester = SEMESTER_TYPE_PREDECESSOR[current_semester]

    # return err_list

    # throw the semester's courses in big list
    # check to see if any of the prereqs for the courses 
    # for the semester you are 
    # on are in the big list. If the are, append to string.
    # If no problems return none

    # New comment to test branch



# Approach:
# Keep a list of courses for each semester in itself a list
# each list stores a list of course indices
# each evaluation only schedules those that can be scheduled (every other will not be pushed)
# if a schedule misses scheduling a course (not being scheduled at all), it is dead/zero fitness (strong rule)

# hyper parameter will be strong rule: how many extra course indices in a given semester allowed (either kill entire schedule (strong) or truncate (weak))


# Caching will become very important:
# this will be used to speed up determining which courses can be taken

# TODO: there needs to be fitness influence from the number of semesters taken

# Approach:
# Steps to initialization:
#   create a blank object
#   load the provided list of list of courses
#   for each semester, create a new gene semester
#       for each course, add it into the gene semester and register all schedulables with each other (taking)
#   



# Steps to judge a semester (fitness)



# Steps to mutate a course:

CACHE_SIZE: int = 10_000
MUTATION_SHIFTS = [-4, -3, -2, -1, 1, 2, 3]

CACHE = {'TEST_CACHE_T': 0, 'TEST_CACHE_F': 0}

class GeneticOptimizer:

    class Gene:

        # The process of "executing" genes will consist of pulling courses from the list of possibilities.
        # This will involve taking courses from a running list of courses based on availability.
        # The actual judging will be done seperately.

        # There are two reasons to check whether a course can be taken:
        #   1. to construct a one-dimensional list of courses to pull from as per the gene encoding.
        #       This is a dynamic schema that ensures better quality results.
        #   2. to find the validatity of the produced schedule.


        def __init__(self, cloned: Optional[GeneticOptimizer.Gene] = None):
            self.selections: list[int] = [] if cloned is None else cloned.selections[:]
            self.fitness: Optional[float] = None

        def __str__(self) -> str:
            return str(self.selections)
        
        def __ge__(self, rhs: GeneticOptimizer.Gene) -> bool:
            return self.fitness <= rhs.fitness
        
        def __gt__(self, rhs: GeneticOptimizer.Gene) -> bool:
            return self.fitness < rhs.fitness
        
        def __le__(self, rhs: GeneticOptimizer.Gene) -> bool:
            return self.fitness >= rhs.fitness

        def __lt__(self, rhs: GeneticOptimizer.Gene) -> bool:
            return self.fitness > rhs.fitness

        def set_selections_from_structure(self, raw_selections: list[list[Schedulable]]):
            
            self.selections = [[0 for _ in semester] for semester in raw_selections]

            # '''
            # NOTE: all courses in the raw selection must be in the optimizer's domain list (a value error raised otherwise).
            # '''
            
            # self.selections = []
            # domain: list[Schedulable] = optimizer.domain
            # for raw_semester in raw_selections:
            #     semester_selections: list[int] = []
            #     for raw_schedulable in raw_semester:
            #         working_index: int = 0
            #         found_course: bool = False
            #         for domain_course in domain:
            #             if domain_course is raw_schedulable:
            #                 found_course = True
            #                 break
            #             working_index += 1
            #         if found_course:
            #             semester_selections.append(working_index)
            #         else:
            #             raise ValueError(f'Could not find course "{str(raw_schedulable)}"')
            #     self.selections.append(semester_selections)
            # print("The good stuff:", self.selections)

        def make_schedule_info_container(self, optimizer: GeneticOptimizer) -> ScheduleInfoContainer:

            raw_list: list[list[Schedulable]] = [[]]

            if optimizer.prototype_schedule is not None:
                semester_index: int
                semester: list[Schedulable]
                for semester_index, semester in enumerate(optimizer.prototype_schedule):
                    schedulable_index: int
                    schedulable: Schedulable
                    for schedulable_index, schedulable in enumerate(semester):
                        
                        semester_to_place = semester_index + self.selections[semester_index][schedulable_index]

                        while len(raw_list) <= semester_to_place:
                            raw_list.append([])
                        
                        raw_list[semester_to_place].append(schedulable.create_stateless_copy())
                        

            #return ScheduleInfoContainer.make_from_schedulables_list(raw_list, starting_semester = optimizer.semester_start, starting_year =, confidence_level: float | None = None))
            schedule: ScheduleInfoContainer = ScheduleInfoContainer.make_from_schedulables_list(raw_list, optimizer.semester_start, optimizer.year_start)
            return schedule

    def __init__(self, course_info_container: CourseInfoContainer, degree_extraction: DegreeExtractionContainer,
            parameters_container: SchedulerParameterContainer, fiteness_function: ScheduleFitenessFunction,
            semester_start: SemesterType, year: int, credit_hour_informer: CreditHourInformer) -> None:
        
        self.course_info_container: CourseInfoContainer = course_info_container
        self.semester_start: SemesterType = semester_start
        self.year_start: int = year

        # The following will vary by student
        self.parameters_container: SchedulerParameterContainer = parameters_container

        # The following are derived from a degree extraction container
        self.degree_extraction: DegreeExtractionContainer = degree_extraction
        self.taken_course: list[CourseIdentifier] = \
            [CourseIdentifier(taken_course_string) for taken_course_string in degree_extraction.make_taken_courses_list()]
        self.schedulables: list[Schedulable] = []
        self.prequisite_ignored_courses: list[CourseIdentifier] = []

        # The fitness function for evolving the gene sequences
        self._fiteness_function = fiteness_function

        # TODO: remove this (not used I think)
        self.domain: list[Schedulable] = []

        self.credit_hour_informer = credit_hour_informer

        self.prototype_schedule: Optional[list[list[Schedulable]]] = None

        # Setup genetic algorithm variables
        self.setup_genetics(population_size=0, course_count=0, mutation_rate=0.25)


    
    def setup_genetics(self, population_size: int, course_count: int, mutation_rate: float = 0.25,\
            fitness_function: ScheduleFitenessFunction = None) -> None:
        '''Setup the gene algorithm relevant instance variables.'''
        
        # ------------------------ Populations Properties ------------------------ #

        # The number of gene sequences in the population
        self._population_size: int = population_size

        # The list of population gene sequences in no particular order
        self._population_gene_sequences: list[GeneticOptimizer.Gene] = []

        # The number of courses to schedule
        self._course_count: int = course_count

        # The chance (0 to 1) that a mutation will occur on a single bit for a new gene sequence
        self._mutation_rate: float = mutation_rate

        # TODO: add parameter to initializer
        self._make_swap_mutation_rate: float = 0.5
        
        # ------------------------ Training Properties ------------------------ #

        # The hard/maximum number of iterations left for training
        self._training_iterations_left: int = 0

        # The threshold for the fitness that when met terminates training
        self._fitness_threshold: Optional[float] = None
        
        # ------------------------ Cache Properties ------------------------ #

        # A simple cache queue that is used to determine which cached fitness values should be removed from the cache (does not sort by access, only by addition)
        self._fitness_cache_queue: list[str] = []

        # A cache of fitness values given a gene sequence (cleared when the fitness function is updated)
        self._fitness_cache: dict[str, float] = {}

        # The active size of the fitness value cache
        self._cache_size: int = 0

        # The maximum size of the fitness value cache
        self._max_cache_size: int = CACHE_SIZE

        # ------------------------ Fitness Function ------------------------ #

        self._fitness_function: ScheduleFitenessFunction = fitness_function
            
        
    # ------------------------ Fitness Function Property ------------------------ #

    def _get_fitness_function(self) -> ScheduleFitenessFunction:
        '''Getter for fitness function.'''
        return self._fitness_function
    
    def _set_fitness_function(self, value: ScheduleFitenessFunction):
        '''Setter for fitness function.'''
        self._fitness_function = value
        self._fitness_cache_queue = []
        self._fitness_cache = {}
        self._cache_size = 0
    
    fitness_function = property(_get_fitness_function, _set_fitness_function)

    # ------------------------ Setup/configuration ------------------------ #

    def set_ignored_prerequisites(self, prequisite_ignored_courses: list[CourseIdentifier]) -> None:
        self.prequisite_ignored_courses = prequisite_ignored_courses

    # def set_schedulable_mapping_from_constructive(self, domain: list[ConstuctiveScheduler.Schedulable]) -> None:
    #     self.domain = [schedulable.schedulable for schedulable in domain]

    def set_prototype_schedule_from_constructive(self, prototype_schedule: list[list[Schedulable]]) -> None:
        self.prototype_schedule = prototype_schedule

    def fill_population_with_model(self, possible_gene_sequence: list[Gene]) -> None:
        '''Fill the remaining space in the population with random gene sequences.'''

        while len(self._population_gene_sequences) < self._population_size:
            new_gene_sequence: GeneticOptimizer.Gene = GeneticOptimizer.Gene(choice(possible_gene_sequence))
            self._population_gene_sequences.append(new_gene_sequence)


    def set_to_track_session(self, maximum_iterations: int, fitness_threshold: Optional[float] = None) -> None:
        '''Set up the trainer to start performing evolution.'''
        self._training_iterations_left = maximum_iterations
        self._fitness_threshold = fitness_threshold

    # ------------------------ Gene Sequence Evaluation ------------------------ #

    def evaluate_gene_sequence_fitness(self, gene_sequence: Gene) -> float:
        '''Calculate the passed gene sequence's fitness.'''
        
        memo: str = str(gene_sequence)
        fitness: float = -inf
        
        # Check if the memo (gene) is already cached
        if memo not in self._fitness_cache:
            CACHE['TEST_CACHE_F'] += 1

            # The sequence is not cached
            schedule: ScheduleInfoContainer = gene_sequence.make_schedule_info_container(self)
            fitness: float = self.fitness_function(schedule, self)

            # Memoization management
            self._fitness_cache_queue.append(memo)
            self._fitness_cache[memo] = fitness
            self._cache_size += 1

            if self._cache_size > self._max_cache_size:
                cachedEntityToRemove = self._fitness_cache_queue.pop(0)
                del self._fitness_cache[cachedEntityToRemove]
                self._cache_size -= 1
        else:
            # The sequence is cached
            fitness = self._fitness_cache[memo]
            CACHE['TEST_CACHE_T'] += 1
            
        return fitness


    def best_genes(self, count: int) -> list[Gene]:
        '''Get a list of the (count)-many best gene sequences in order (using the current fitness function).'''

        best_genes: list[GeneticOptimizer.Gene] = []

        gene: GeneticOptimizer.Gene
        for gene in self._population_gene_sequences:
            if gene.fitness is None:
                gene.fitness = self.evaluate_gene_sequence_fitness(gene)
            insort(best_genes, gene)
        
        #return best_genes[:self._population_size-count-1:-1]
        return best_genes[:count]

    # ------------------------ Breeding ------------------------ #

    def crossover_gene_sequences(self, gene1: Gene, gene2: Gene) -> Gene:
        '''Get a single child from the passed parents, crossing over the genes randomly.
        The order of the parents does not matter.'''
        cross_index: int = randint(0, (len(gene1.selections) + len(gene2.selections)) // 2 - 1)
        first_gene: GeneticOptimizer.Gene
        second_gene: GeneticOptimizer.Gene
        first_gene, second_gene = (gene1, gene2) if randint(0, 1) else (gene2, gene1)
        new_gene: GeneticOptimizer.Gene = GeneticOptimizer.Gene()
        new_selections: list[list[int]] = first_gene.selections[:cross_index] + second_gene.selections[cross_index:]
        new_gene.selections = [semester[:] for semester in new_selections]
        return new_gene

    def mutate_genes(self, gene: Gene) -> Gene:
        '''Get a mutated version of the passed gene sequence. This applies an (near-) atomic mutation.'''
        
        semester_last_index = len(gene.selections) - 1
        semester_index = randint(0, semester_last_index)
        prototype_semester: list[int] = gene.selections[semester_index]
        while not prototype_semester:
            semester_index = randint(0, semester_last_index)
            prototype_semester = gene.selections[semester_index]
        
        mutation_course_index = randint(0, len(prototype_semester) - 1)
        old_delta = prototype_semester[mutation_course_index]
        new_delta: int = old_delta + choice(MUTATION_SHIFTS)
        # The following max method call ensure semester are not scheduled for the past (cannot go before immediate semester)
        new_delta = max(-semester_index, new_delta)
        gene.selections[semester_index][mutation_course_index] = new_delta

        if random() <= self._make_swap_mutation_rate:
            # TODO: test the heck out of this!!:

            destination_semester_index: int = semester_index + new_delta
            # start_semester_index: int = semester_index + old_delta

            searches_left: int = 5
            while searches_left > 0:
                searches_left -= 1

                semester_to_index = randint(0, semester_last_index)
                needed_swap_delta = destination_semester_index - semester_to_index
                prototype_to_semester: list[int] = gene.selections[semester_to_index]
                if needed_swap_delta in prototype_to_semester:
                    to_replace_index = prototype_to_semester.index(needed_swap_delta)
                    prototype_to_semester[to_replace_index] = semester_index - semester_to_index
                    searches_left = 0


        return gene

    def make_child_from(self, geneSequence1: Gene, geneSequence2: Gene) -> Gene:
        '''Get a child (gene sequence) from two parent (oder does not matter). This applies
        crossover and may flip any number of bits (less likely to be more).'''
        child = self.crossover_gene_sequences(geneSequence1, geneSequence2)
        should_mutate: bool = random() <= self._mutation_rate
        while should_mutate:
            child = self.mutate_genes(child)
            should_mutate = random() <= self._mutation_rate
        return child

    # ------------------------ Iteration training/evolution ------------------------ #

    def _reached_threshold(self, bestGeneSequences: list[str]) -> bool:
        '''Helper method for iteration method that updates the iteration count and determines if 
        any threshold has been met.'''

        self._training_iterations_left -= 1
        isFinishedTraining: bool = self._training_iterations_left <= 0
        
        # Check fitness
        if self._fitness_threshold is not None and \
                self.evaluate_gene_sequence_fitness(bestGeneSequences[0]) >= self._fitness_threshold:
            isFinishedTraining = True

        return isFinishedTraining


    def run_iteration(self, reduction_size: int, best_performer_maintain: int = 0) -> bool:
        '''Perform a single iteration/evolution over'''
        best_gene_sequences: list[GeneticOptimizer.Gene] = self.best_genes(reduction_size)

        # TODO: REMOVE!
        if self._training_iterations_left == -1:
            print(30*'-')
            print('LOOK AT THE GENES!!:')
            for g in best_gene_sequences[:]:
                print(str(g), g.fitness)
            print(30*'-')

        if self._reached_threshold(best_gene_sequences):
            return True
        
        number_of_parent_pairs: int = reduction_size//2
        new_population: list[GeneticOptimizer.Gene] = []
        
        for index in range(min(best_performer_maintain, self._population_size)):
            new_population.append(best_gene_sequences[index])

        children_per_pair: int = (self._population_size - len(new_population))//number_of_parent_pairs
        shuffle(best_gene_sequences)

        for index in range(number_of_parent_pairs):
            gene_sequence_1 = best_gene_sequences[2 * index]
            gene_sequence_2 = best_gene_sequences[2 * index + 1]

            for _ in range(children_per_pair):
                new_population.append(self.make_child_from(gene_sequence_1, gene_sequence_2))
        
        for index in range(self._population_size - len(new_population)):
            gene_sequence_1 = best_gene_sequences[2 * index]
            gene_sequence_2 = best_gene_sequences[2 * index + 1]
            new_population.append(self.make_child_from(gene_sequence_1, gene_sequence_2))

        self._population_gene_sequences = new_population
        
        return False


ScheduleFitenessFunction = Callable[[ScheduleInfoContainer, GeneticOptimizer], float]

SCHEDULE_SIZE_MULTIPLIER: float = 0.2

judge_path: ScheduleFitenessFunction
def judge_path(schedule_info_container: ScheduleInfoContainer, dummy_genetic_optimizer: GeneticOptimizer) -> float:
    # TODO: this is unfinished of course (implement)
    
    validation_report: PathValidationReport = rigorous_validate_schedule(
        schedule = schedule_info_container,
        taken_courses = dummy_genetic_optimizer.taken_course,
        prequisite_ignored_courses = dummy_genetic_optimizer.prequisite_ignored_courses,
        credit_hour_informer=dummy_genetic_optimizer.credit_hour_informer
    )

    # TODO: CLEAN THIS UP (BAD CODE) AND ADD MORE VARIANCE TO EXPERT SYSTEM 
    dynamic_knowledge = DynamicKnowledge()
    s = [[l.course_identifier.course_number or l.course_identifier.name for l in r] for r in schedule_info_container._semesters]
    dynamic_knowledge.set_schedule(s)
    confidence_factor = ExpertSystem().calculate_confidence(dynamic_knowledge, dummy_genetic_optimizer.course_info_container)


    # print([str(s) for s in dummy_genetic_optimizer.taken_course])
    # print([str(s) for s in dummy_genetic_optimizer.prequisite_ignored_courses])
    # print(schedule_info_container)
    # print([str(e) for e in validation_report.error_list])
    # print(validation_report.is_valid())
    return (1000 if validation_report.is_valid() else -len(validation_report.error_list)) + confidence_factor - SCHEDULE_SIZE_MULTIPLIER*schedule_info_container.semester_count()



DEFAULT_HOURS_PER_SEMESTER: int= 15

LOW_FITNESS: float = 1
MID_FITNESS: float = 5.5
HIGH_FITNESS: float = 10


NUMBER_COORDINATION: dict[str, float] = {
    "1": HIGH_FITNESS,
    "2": (HIGH_FITNESS + MID_FITNESS) / 2.0,
    "3": MID_FITNESS,
    "4": (MID_FITNESS + LOW_FITNESS) / 2.0
}

# TODO: implement this!
lower_number_rule: ConstuctiveScheduler.Rule
def lower_number_rule(course: ConstuctiveScheduler.Schedulable,
        courses_needed: list[ConstuctiveScheduler.Schedulable],
        course_info_container: CourseInfoContainer) -> float:
    
    # <<!
    # TODO: REMOVE THIS - it is to support old interfaces (course info protocol)
    # print(type(course))
    # print(type(course.schedulable.course_identifier))
    course_number = course
    if isinstance(course_number, ConstuctiveScheduler.Schedulable):
        course_number = course_number.schedulable
    if isinstance(course_number, Schedulable):
        course_number = course_number.course_identifier
    if isinstance(course_number, CourseIdentifier):
        course_number = course_number.course_number
    if course_number is None:
        course_number = '\0'
    first_number = course_number[course_number.find(' ') + 1]
    return NUMBER_COORDINATION[first_number] if first_number in NUMBER_COORDINATION else LOW_FITNESS
    # !>>

    # <<$
    #course_number: str = course.schedulable.course_identifier.course_number or ' \0'
    # first_number: str = course_number[course_number.find(' ') + 1]
    # return NUMBER_COORDINATION[first_number] if first_number in NUMBER_COORDINATION else LOW_FITNESS
    # $>>



# TODO: This needs to go!
TEST_GATEWAY_HARDSET_DICT: dict[str, float] = {
    "CPSC 1302": HIGH_FITNESS,
    "CPSC 1555": LOW_FITNESS
}

local_gatekeeper_rule: ConstuctiveScheduler.Rule
def local_gatekeeper_rule(course: ConstuctiveScheduler.Schedulable,
        courses_needed: list[ConstuctiveScheduler.Schedulable],
        course_info_container: CourseInfoContainer) -> float:
    # TODO: this was commented out for the demonstration
    # weight = course_info_container.get_weight(courseID)
    # if weight is None:
    #     weight = LOW_FITNESS
    # fitness = HIGH_FITNESS - (HIGH_FITNESS - LOW_FITNESS) / (weight + 1)
    # return fitness
    # TODO: this is a test!

    
    # <<!
    # TODO: REMOVE THIS - it is to support old interfaces (course info protocol)
    course_number = course
    if isinstance(course_number, ConstuctiveScheduler.Schedulable):
        course_number = course_number.schedulable
    if isinstance(course_number, Schedulable):
        course_number = course_number.course_identifier
    if isinstance(course_number, CourseIdentifier):
        course_number = course_number.course_number
    if course_number is None:
        course_number = '\0'
    # !>>

    return MID_FITNESS if course_number not in TEST_GATEWAY_HARDSET_DICT \
        else TEST_GATEWAY_HARDSET_DICT[course_number]
    course_id: str = course.schedulable.course_identifier.course_number
    count = 5
    other_course: ConstuctiveScheduler
    for other_course in courses_needed:
        pass
    return course.schedulable.get_prequisite_tree().has_deep_child_by_course_id()
    

FITNESS_LISTING: list[float] = [HIGH_FITNESS, MID_FITNESS, LOW_FITNESS]

availability_rule: ConstuctiveScheduler.Rule
def availability_rule(course: ConstuctiveScheduler.Schedulable,
        courses_needed: list[ConstuctiveScheduler.Schedulable],
        course_info_container: CourseInfoContainer) -> float:
    return FITNESS_LISTING[max(len(course.schedulable.availability) - 1, 2)]


class ConstuctiveScheduler:

    HARD_SEMESTER_LIMIT = 50
    
    class Schedulable:

        def __init__(self, schedulable: Schedulable) -> None:
            self.schedulable: Schedulable = schedulable
            self.first_take_fitness: Optional[float] = None

        def __str__(self) -> str:
            return str(self.schedulable)

        def __ge__(self, rhs: ConstuctiveScheduler.Schedulable) -> bool:
            return self.first_take_fitness <= rhs.first_take_fitness
        
        def __gt__(self, rhs: ConstuctiveScheduler.Schedulable) -> bool:
            return self.first_take_fitness < rhs.first_take_fitness
        
        def __le__(self, rhs: ConstuctiveScheduler.Schedulable) -> bool:
            return self.first_take_fitness >= rhs.first_take_fitness

        def __lt__(self, rhs: ConstuctiveScheduler.Schedulable) -> bool:
            return self.first_take_fitness > rhs.first_take_fitness
    
    class SortingDict:

        def __init__(self) -> None:
            self._keys: list[int] = [] # ordered low to high
            self._data: dict[int, list[ConstuctiveScheduler.Schedulable]] = {}
            self._set: set[ConstuctiveScheduler.Schedulable] = set()
        
        def has_course(self) -> bool:
            return len(self._keys) != 0

        def all(self) -> Iterator[ConstuctiveScheduler.Schedulable]:
            return self._set.__iter__()

        def get_top_key(self) -> Optional[int]:
            return self._keys[-1] if self._keys else None

        def get_next_key(self, key: int) -> Optional[int]:
            # NOTE: this is linear because of the domain
            next_key_index: int = len(self._keys) - 1
            while next_key_index >= 0 and self._keys[next_key_index] >= key:
                next_key_index -= 1
            return self._keys[next_key_index] if next_key_index >= 0 else None

        def get_schedulable(self, key: int, index: int) -> Optional[ConstuctiveScheduler.Schedulable]:
            result: Optional[ConstuctiveScheduler.Schedulable] = None
            if key in self._data:
                listing: list[ConstuctiveScheduler.Schedulable] = self._data[key]
                if index < len(listing):
                    result = listing[index]
            return result

        def add(self, schedulable: ConstuctiveScheduler.Schedulable) -> None:
            hours: int = schedulable.schedulable.hours
            if hours not in self._data:
                insort(self._keys, hours)
                self._data[hours] = []
            # Insert by Schedulable's "<", "<=", ">", and ">=" operator definitions
            insort(self._data[hours], schedulable)
            self._set.add(schedulable)
        
        def remove(self, key: int, index: int) -> None:
            if key in self._data:
                listing: list[ConstuctiveScheduler.Schedulable] = self._data[key]
                if index < len(listing):
                    self._set.remove(listing.pop(index)) # remove from both list and set
                # self._data[key] = listing[:index] + listing[index+1:]
                if not listing:
                    self._keys.remove(key)
                    del self._data[key]

        def remove_schedulable(self, schedulable: ConstuctiveScheduler.Schedulable) -> None:
            key: int = schedulable.schedulable.hours
            if key in self._data:
                listing: list[ConstuctiveScheduler.Schedulable] = self._data[key]
                if schedulable in listing:
                    listing.remove(schedulable)
                    if not listing:
                        self._keys.remove(key)
                        del self._data[key]

    

    Rule = Callable[[Schedulable, "list[Schedulable]", CourseInfoContainer], float]
    
    def __init__(self, course_info_container: Optional[CourseInfoContainer],
            parameters_container: SchedulerParameterContainer,
            semester_start: Optional[SemesterType] = None, year: Optional[int] = None) -> None:
        
        # TODO: implement some sort of time detection or pick up from the university website
        self.semester_start: SemesterType = semester_start if semester_start is not None else SPRING
        self.year_start: int = year if year is not None else 2023

        self._course_info_container: Optional[CourseInfoContainer] = course_info_container
        self.schedule_evaluator: ExpertSystem = ExpertSystem()
        
        # The following will vary by student
        self._parameters_container: Optional[SchedulerParameterContainer] = parameters_container
        self._degree_extraction: Optional[DegreeExtractionContainer] = None

        # The following are derived from a degree extraction container
        self._courses_needed_container: Optional[CoursesNeededContainer] = None
        self._taken_course: list[CourseIdentifier] = []
        self._schedulables: list[ConstuctiveScheduler.Schedulable] = []

        self._fitness_functions: list[ConstuctiveScheduler.Rule] = [
            lower_number_rule,
            local_gatekeeper_rule,
            availability_rule
        ]
    
    def get_schedulables(self) -> list[Schedulable]:
        return self._schedulables

    def get_parameter_container(self) -> Optional[SchedulerParameterContainer]:
        return self._parameters_container

    def get_course_info(self) -> Optional[CourseInfoContainer]:
        return self._course_info_container
        
    def get_schedule_evaluator(self) -> Optional[ExpertSystem]:
        return self.schedule_evaluator
        
    def get_courses_needed_container(self) -> Optional[CourseInfoContainer]:
        return self._courses_needed_container
    
    def get_hours_per_semester(self, semesterType: SemesterType = FALL) -> range:
        return self._parameters_container.get_hours_for(semesterType)
    
    def configure_parameters(self, parameters_containter: SchedulerParameterContainer) -> None:
        self._parameters_container = parameters_containter

    def configure_degree_extraction(self, degree_extraction: DegreeExtractionContainer) -> None:
        self._degree_extraction = degree_extraction
        self._courses_needed_container = degree_extraction.make_courses_needed_container()
        self._taken_course = []
        taken_course_string: str
        for taken_course_string in degree_extraction.make_taken_courses_list():
            # TODO: verify the name and number are checked
            self._taken_course.append(CourseIdentifier(taken_course_string))
    
    def configure_course_info(self, container: CourseInfoContainer) -> None:
        self._course_info_container = container

    def make_credit_hour_informer(self) -> CreditHourInformer:
        return CreditHourInformer(self)

        
    def prepare_schedulables(self) -> bool:

        courses_needed_root: RequirementsTree = self._courses_needed_container.get_decision_tree()

        if not courses_needed_root.is_deep_resolved():
            return False
        
        self._schedulables = []

        schedulable_parameters: list[SchedulableParameters] = courses_needed_root.get_aggregate()

        schedulable_parameters_item: SchedulableParameters
        for schedulable_parameters_item in schedulable_parameters:

            if not schedulable_parameters_item.is_stub:

                course_number: str = schedulable_parameters_item.course_number

                if course_number is None and self._course_info_container.validate_course(schedulable_parameters_item.course_name):
                    course_number = schedulable_parameters_item.course_name

                course_identifier: CourseIdentifier = \
                    CourseIdentifier(course_number, schedulable_parameters_item.course_name)

                # TODO: IMP NEW -> 

                # TODO: REMOVE THIS - it is to support old interfaces (course info protocol)
                FUNC_course_identifier = course_identifier if isinstance(self._course_info_container, CourseInfoContainer) else course_identifier.course_number
                FUNC_availabilities = self._course_info_container.get_availability(FUNC_course_identifier)
                if isinstance(FUNC_availabilities, list):
                    FUNC_availabilities = set(map(lambda x: {'Fa':FALL, 'Sp':SPRING, 'Su':SUMMER, '--':None}[x], FUNC_availabilities))

                schedulable: Schedulable = Schedulable(
                    course_identifier = course_identifier,
                    prerequisite_string = self._course_info_container.get_prereqs(FUNC_course_identifier) or " ",
                    corequisite_string = self._course_info_container.get_coreqs(FUNC_course_identifier) or " ",
                    hours = self._course_info_container.get_hours(FUNC_course_identifier),
                    availability = FUNC_availabilities,
                    recommended = self._course_info_container.get_recommended(FUNC_course_identifier)
                )
                self._schedulables.append(ConstuctiveScheduler.Schedulable(schedulable))

            else:
                schedulable: Schedulable = Schedulable(
                    course_identifier = CourseIdentifier(None, schedulable_parameters_item.course_name),
                    prerequisite_string = schedulable_parameters_item.stub_prereqs_logic_string,
                    corequisite_string = schedulable_parameters_item.stub_coreqs_logic_string,
                    hours = schedulable_parameters_item.stub_hours,
                    availability = schedulable_parameters_item.stub_availability,
                    recommended = schedulable_parameters_item.stub_availability
                )
                self._schedulables.append(ConstuctiveScheduler.Schedulable(schedulable))

        return True
        

    def configure_hours_per_semester(self, number_of_hours) -> None:
        # self.hours_per_semester = number_of_hours
        # TODO: this is hard set on using the Fall (update to use any given semester or take into account tbe parameter
        # container and its interface) 
        self._parameters_container.set_hours(FALL, number_of_hours)
    

    def _create_weighted_schedulables(self, prequisite_ignored_courses: list[CourseIdentifier]) -> ConstuctiveScheduler.SortingDict:

        courses_needed: list[ConstuctiveScheduler.Schedulable] = self._schedulables
        taken_courses: list[CourseIdentifier] = self._taken_course + prequisite_ignored_courses
        # print('Whats going into the scheduler:', [str(s) for s in courses_needed])

        course_info = self._course_info_container # Get the course info container

        schedulables_dictionary: ConstuctiveScheduler.SortingDict = ConstuctiveScheduler.SortingDict()

        schedulable: ConstuctiveScheduler.Schedulable
        for schedulable in courses_needed:

            new_fitness: float = 0
            fitness_function: ConstuctiveScheduler.Rule
            for fitness_function in self._fitness_functions:
                new_fitness += fitness_function(schedulable, courses_needed, course_info)
            schedulable.first_take_fitness = new_fitness

            schedulables_dictionary.add(schedulable)

            # Register all taken courses with the current schedule
            taken_course: CourseIdentifier
            for taken_course in taken_courses:
                schedulable.schedulable.sync_course_taken(taken_course)

        return schedulables_dictionary

    def _generate_simple_corequisite_pairs(self) -> dict[str, ConstuctiveScheduler.Schedulable]:

        result: dict[str, ConstuctiveScheduler.Schedulable] = {}
        courses_needed: list[ConstuctiveScheduler.Schedulable] = self._schedulables

        schedulable: ConstuctiveScheduler.Schedulable
        for schedulable in courses_needed:
            corequisite_tree: RequirementsTree = schedulable.schedulable.get_corequisite_tree()
            if corequisite_tree.get_all_deep_count() == 1:
                delivable: SchedulableParameters = corequisite_tree.get_all_aggragate()[0]
                if delivable.course_number:
                    result[delivable.course_number] = schedulable

        return result
    
    def _constructive_schedule_as_list(self, schedulables_dictionary: ConstuctiveScheduler.SortingDict,
            simple_corequisite_pairs: dict[str, ConstuctiveScheduler.Schedulable]) -> list[list[Schedulable]]:
        '''Create a path/schedule as a list of list of schedulables. NOTE: the passes schedulables collection will be mutated.'''

        # This scheduling method work constructively, adding new courses to a working semester.
        # When the semester is full or no courses can be taken, the semester is appended to the path.
        # As soon as no courses remain or the hard limit is met, the path is returned as a list of list.
        # Course will be scheduled first by the larger credit hours (for a given semester).
        # Tie breaking will be performed by the precalculated fitness scores for the class.

        # Create list of lists (each sublist is a semester and in each sublist are the schedulables)
        result_list: list[list[Schedulable]] = []

        # Create variables to track the working the semester type (Spring, Fall, Summer) and year (such as 2023)
        working_semester_type: SemesterType = self.semester_start
        working_year: int = self.year_start

        # The hours available for the current semester
        hours_available = self.get_parameter_container().get_hours_for(working_semester_type, working_year).stop

        # The hard limit of semesters for the schedule (this will be decremented as scheduling continues)
        hard_iteration_limit: int = ConstuctiveScheduler.HARD_SEMESTER_LIMIT

        # The current number of hours to try to use for scheduling (this is part of the dictionary key for schedulable look up)
        hours_key: int = schedulables_dictionary.get_top_key()

        course_index: int = 0
        working_semester_list: list[ConstuctiveScheduler.Schedulable] = []
        
        # While course are still left to be scheduled
        while schedulables_dictionary.has_course():
            if hours_available >= hours_key:
                course: Optional[ConstuctiveScheduler.Schedulable] = \
                    schedulables_dictionary.get_schedulable(hours_key, course_index)
                if course is not None:
                    
                    if working_semester_type in course.schedulable.availability:
                        if course.schedulable.can_be_taken():
                            working_semester_list.append(course)
                            hours_available -= hours_key
                            schedulables_dictionary.remove(hours_key, course_index)
                            remaining_course: ConstuctiveScheduler.Schedulable
                            for remaining_course in schedulables_dictionary.all():
                                remaining_course.schedulable.sync_course_taking(course.schedulable.course_identifier)
                        else:
                            course_number: str = course.schedulable.course_identifier.course_number
                            if course_number in simple_corequisite_pairs:
                                # There is an associated simple coreq. (see if it will work)
                                additional_schedulable: ConstuctiveScheduler.Schedulable = simple_corequisite_pairs[course_number]
                                if working_semester_type in additional_schedulable.schedulable.availability and \
                                        hours_available >= hours_key + additional_schedulable.schedulable.hours:
                                    working_semester_list.append(course)
                                    working_semester_list.append(additional_schedulable)
                                    hours_available -= hours_key + additional_schedulable.schedulable.hours
                                    schedulables_dictionary.remove(hours_key, course_index)
                                    schedulables_dictionary.remove_schedulable(additional_schedulable)
                                    remaining_course: ConstuctiveScheduler.Schedulable
                                    for remaining_course in schedulables_dictionary.all():
                                        remaining_course.schedulable.sync_course_taking(course.schedulable.course_identifier)
                                        remaining_course.schedulable.sync_course_taking(additional_schedulable.schedulable.course_identifier)
                                else:
                                    course_index += 1
                            else:
                                course_index += 1
                    else:
                        course_index += 1
                else:
                    hours_key = schedulables_dictionary.get_next_key(hours_key)
                    course_index = 0
            else:
                hours_key = schedulables_dictionary.get_next_key(hours_key)
                course_index = 0

            if hours_key is None:

                # Rotate all courses to recognize the course as "taken" instead of "taking"
                working_course: ConstuctiveScheduler.Schedulable
                for working_course in working_semester_list:
                    remaining_course: ConstuctiveScheduler.Schedulable
                    for remaining_course in schedulables_dictionary.all():
                        remaining_course.schedulable.sync_course_taken(working_course.schedulable.course_identifier) 
                # TODO: REMOVE THIS!
                # print(SEMESTER_DESCRIPTION_MAPPING[working_semester_type], working_year, [str(schedulable.schedulable) for schedulable in working_semester_list])
                result_list.append([schedulable.schedulable for schedulable in working_semester_list])
                working_semester_list = []

                hours_key = schedulables_dictionary.get_top_key()
                course_index = 0

                working_semester_type = SEMESTER_TYPE_SUCCESSOR[working_semester_type]
                if working_semester_type == SPRING:
                    working_year += 1
                
                hours_available = self.get_parameter_container().get_hours_for(working_semester_type, working_year).stop

                hard_iteration_limit -= 1
                if hard_iteration_limit <= 0:
                    # TODO: TEST REMOVE BY OVERRIDE OF EXCEPTION
                    #raise RuntimeError("Semester generating limit met")

                    #print("result_list at fault state", [[str(s) for s in l] for l in result_list])


                    while not result_list[-1]:
                        result_list.pop()
                    residue: list[Schedulable] = [schedulable.schedulable for schedulable in schedulables_dictionary.all()]
                    result_list.append(residue)
                    #result_list = list(filter(lambda x: x != [], result_list))
                    
                    
                    # for s in schedulables_dictionary.all():
                    #     print(str(s))
                    #     print(s.schedulable._prequisite_tree.get_deep_description()) 

                    return result_list

        if working_semester_list:
            result_list.append([schedulable.schedulable for schedulable in working_semester_list])
        
        return result_list

        
    # def generate_schedule(self, prequisite_ignored_courses: list[CourseIdentifier], optimizer: Optional[GeneticOptimizer] = None) -> ScheduleInfoContainer:

    def generate_schedule(self, prequisite_ignored_courses: list[CourseIdentifier], optimizer: bool = True) -> ScheduleInfoContainer:
        """Primary method to schedule a path to graduation
           Inputs: None, but requires course_info and courses_needed setup prior to running
           Returns: list of lists, inner list is one semester of courses, outer list is full schedule"""

        # Create a dictionary that indexed by a composite of the credits hours and the fitness index (0 is the most fit, 1 the second most fit, etc.)
        schedulables_dictionary: ConstuctiveScheduler.SortingDict = self._create_weighted_schedulables(prequisite_ignored_courses)
        
        simple_corequisite_pairs: dict[str, ConstuctiveScheduler.Schedulable] = self._generate_simple_corequisite_pairs()
        
        # Create a list of lists using the above schedulables
        result_list: list[list[Schedulable]] = self._constructive_schedule_as_list(schedulables_dictionary, simple_corequisite_pairs)

        # Perform optimizations here (if an optimizer was passes in)
        if optimizer is not None:

            # TODO: these values are not configurable yet
            population_size: int = 120#100
            mutation_rate: float = 0.6
            fitness_function: ScheduleFitenessFunction = judge_path
            maximum_iterations: int = 10
            fitness_threshold: Optional[float] = None
            reduction_size: int = population_size//4
            best_performer_maintain: Optional[int] = 5

            trainer: GeneticOptimizer = GeneticOptimizer(
                course_info_container=self._course_info_container,
                degree_extraction=self._degree_extraction,
                parameters_container=self._parameters_container,
                fiteness_function=fitness_function,
                semester_start=self.semester_start,
                year=self.year_start,
                credit_hour_informer=self.make_credit_hour_informer()
            )
            
            trainer.setup_genetics(
                population_size=population_size,
                course_count=len(self._schedulables),
                mutation_rate=mutation_rate,
                fitness_function=fitness_function
            )

            trainer.set_ignored_prerequisites(prequisite_ignored_courses)

            trainer.set_prototype_schedule_from_constructive(result_list)
            # trainer.set_schedulable_mapping_from_constructive(self._schedulables)
            
            model_gene: GeneticOptimizer.Gene = GeneticOptimizer.Gene()
            model_gene.set_selections_from_structure(result_list)

            trainer.fill_population_with_model([model_gene])

            trainer.set_to_track_session(maximum_iterations, fitness_threshold=fitness_threshold)
            
            while not trainer.run_iteration(reduction_size=reduction_size, \
                best_performer_maintain=best_performer_maintain): pass
                
            best_schedule: ScheduleInfoContainer = trainer.best_genes(1)[0].make_schedule_info_container(trainer)
            result_list = best_schedule.to_list_of_lists()
            
        
        # Calculate the confidence factor for the new schedule
        dynamic_knowledge = DynamicKnowledge()
        dynamic_knowledge.set_schedule([[l.course_identifier.course_number or l.course_identifier.name for l in r] for r in result_list])
        confidence_factor = self.schedule_evaluator.calculate_confidence(dynamic_knowledge, self._course_info_container)

        return ScheduleInfoContainer.make_from_schedulables_list(
            raw_list = result_list,
            starting_semester = self.semester_start,
            starting_year = self.year_start,
            confidence_level = confidence_factor
        )
    




def dummy_validation_unit_test():

    course_info_container: CourseInfoContainer = CourseInfoContainer()

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
    else:
        print('Passed path validation case 6')




if __name__ == '__main__':
        dummy_validation_unit_test()

        print('Test starting')
        print(80*'=')
        print(80*'=')

        course_info_container: CourseInfoContainer = CourseInfoContainer()

        course_set_a: list[set] = [
            'CPSC 1301K',
            'CPSC 1302',
            'CPSC 2105',
            'CPSC 2108',
            'CPSC 3111',
            'CPSC 3121',
            'CPSC 3125',
            'CPSC 3131',
            'CPSC 3165',
            'CPSC 3165',
            'CPSC 3175',
            'CPSC 4115',
            'CPSC 4127',
            'CPSC 4135',
        ]
        
        identifiers = {id : CourseIdentifier(id) for id in course_set_a}
        schedulables = Schedulable.create_schedulables(list(identifiers.values()), course_info_container)
        
        # for s in schedulables:
        #     print(40*'-')
        #     s.sync_prerequisites_taking(identifiers['CPSC 1301K'])
        #     s.sync_prerequisites_taking(CourseIdentifier('MATH 2125'))
        #     s.sync_prerequisites_taking(CourseIdentifier('MATH 1113'))
        #     s.sync_prerequisites_taking(CourseIdentifier('CPSC 3175'))
        #     s.sync_prerequisites_taking(CourseIdentifier('CYBR 2160'))
        #     s.sync_prerequisites_taking(CourseIdentifier('MISM 3145'))
        #     # s.reset_all_selection()
        #     print(s.can_be_taken())
        #     print(s.course_identifier.course_number)
        #     print(s.get_prequisite_tree().get_deep_description())

        test_path_a: ScheduleInfoContainer = ScheduleInfoContainer.make_from_string_list([
            ['CPSC 1301K'],
            ['CPSC 1302', 'CPSC 1555'],
            ['CPSC 2108'],
            ['CPSC 3175'],
            ['CPSC 2555', 'CPSC 3118'],
            [],
            ['CPSC 4111'],
            ['CPSC 4112', 'CPSC 4113']
        ], course_info_container, starting_semester=FALL, starting_year=2023)
        
        # print(test_path_a)

        

        report: PathValidationReport = rigorous_validate_schedule(
            test_path_a,
            taken_courses=[CourseIdentifier('MATH 2125'), CourseIdentifier('MATH 1113')],
            prequisite_ignored_courses=[],
            credit_hour_informer=CreditHourInformer.make_unlimited_generator()

        )
        # print('Errors:')
        # print(report.get_errors_printable())


        ##################################################################
        ##################################################################


        '''
        2023, Spring: CPSC 2115
        2023, Summer: CPSC 1302
        2023, Fall: CPSC 1105, Course XXXX, CPSC 2125, CPSC 3111
        2024, Spring: CPSC 1301K, CPSC 1555, CPSC 2105, CPSC 3105
        '''

        ##################################################################
        ##################################################################

        dcspc: ConstructiveSchedulingParametersContainers\
            = ConstructiveSchedulingParametersContainers(Path.home(), [],
            fall_spring_hours=15, summer_hours=6)
        scheduler: ConstuctiveScheduler = ConstuctiveScheduler(course_info_container, dcspc)


#         degree_extraction: DegreeExtractionContainer = DegreeExtractionContainer(taken_courses=['MATH 2125', 'MATH 1113'],\
#             courses_needed_constuction_string='''
# [e <n=The Things>[d <n=CPSC 1301K>][d <n=CPSC 1302>][d <n=CPSC 1555>][d <n=CPSC 2108>][d <n=CPSC 2555>]
#             ''')

        # degree_extraction: DegreeExtractionContainer = DegreeExtractionContainer(taken_courses=['MATH 2125', 'MATH 1113'],\
        #     courses_needed_constuction_string='''
        # (CPSC 1105, CPSC 2105, CPSC 2115,
        # CPSC 2125, CPSC 3105, CPSC 3111)
        
        # [e <n=The Things>[d <n=CPSC 1301K>][d <n=CPSC 1302>][d <n=CPSC 1555>][s <n=Take, c=1>[d <n=CPSC 2108>][d <n=CPSC 2555>]]]
        #  ''')


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


        # degree_extraction: DegreeExtractionContainer = DegreeExtractionContainer(taken_courses=['MATH 2125', 'MATH 1113', 'MATH 5125U'],\
        #     courses_needed_constuction_string='''
        # (CPSC 1105, CPSC 2105, CPSC 2115, CPSC 1555, CPSC 2108, CPSC 3118, CPSC 3175,
        # CPSC 2125, CPSC 3105, CPSC 3111, CPSC 1302, CPSC 4111,
        # CPSC 1301K, CPSC 4112, CPSC 4113
        # ) [p <n=COURSE A>][p <n=COURSE B>][p <n=COURSE C>]
        # ''')


        prequisite_ignored_courses: list[CourseIdentifier] = [
            CourseIdentifier('MATH 1113')
        ]
            
        #print('SCHED')
        scheduler.configure_degree_extraction(degree_extraction)
        scheduler.get_courses_needed_container().stub_all_unresolved_nodes()
        scheduler.prepare_schedulables()
        path: ScheduleInfoContainer = scheduler.generate_schedule(prequisite_ignored_courses=prequisite_ignored_courses)
        print(path)

        generated_report: PathValidationReport = rigorous_validate_schedule(
            path,
            taken_courses=[CourseIdentifier('MATH 2125'), CourseIdentifier('MATH 1113'), CourseIdentifier('MATH 5125U')],
            prequisite_ignored_courses=[],
            credit_hour_informer=scheduler.make_credit_hour_informer()
        )
        print('Errors:')
        print(generated_report.get_errors_printable())
        print('Caching usage:')
        print('Used Cache:', CACHE['TEST_CACHE_T'])
        print('Calculated:', CACHE['TEST_CACHE_F'])
        print('Ratio:', CACHE['TEST_CACHE_T']/(CACHE['TEST_CACHE_F']+CACHE['TEST_CACHE_T']))

        
