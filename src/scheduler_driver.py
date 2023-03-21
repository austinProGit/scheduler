# Thomas Merino
# 3/15/2023
# CPSC 4176 Project


from __future__ import annotations
from requirement_parser import RequirementsParser


class DummySchedulable:

    def __init__(self, course_number: str, prerequisite_string: str):
        self._course_number: str = course_number
        self._prequisite_tree_string: str = prerequisite_string

    def __str__(self):
        return self._course_number
    
    def get_prequisite_tree(self):
        return RequirementsParser.make_from_course_selection_logic_string(self._prequisite_tree_string)



class GeneticScheduler:

    def __init__(self, schedulables: list[DummySchedulable]):
        self._schedulables = schedulables






if __name__ == '__main__':


        print('Test starting')







# REFERNCE FROM OTHER ASSIGNMENT (aided by Ryan Zimmerman):

# Two Guys and a Duck (Thomas Merino and Ryan Zimmerman)
# 3/11/23
# Assignment 4 - CPSC 4185 - R. Abid - Spring, 2023

# The third dataset works better with random start
# Mutations are programmed to apply either no change, one change, or more changes
#   This is then larger leaps are possible
# We check for the value threshold only in the top k-many according to the fitness
#   ranking because it is more efficient and the fitness function is suppossed to
#   be highly correlated with the sum of the value.


from typing import Callable, Optional, Union
from math import inf
from random import choice, randint, shuffle, random
from time import perf_counter
import sys

SHOULD_PRINT_THRESHOLD_MEET = False
'''Whether meeting the threshold is printed.'''

SHOULD_PRINT_FITNESS = True
'''Whether meeting the running is printed.'''

class Valuable:
    '''A representation of a valuable item that can be stored in a knapsack. This contanins
    a value and a weight.'''
    
    def __init__(self, value: float, weight: float, name: str = None) -> None:
        self.value: float = value
        self.weight: float = weight
        self.name: str = name if name is not None else \
            f'Valuable with value {value} and weight {weight}'

    def __str__(self):
        return self.name

# ---------------------------------- Valuable Stores ---------------------------------- #

# The following are some stores (that sell valuables).
# Each is just a list of Valuable instances and are used for testing the program.
# The top three appear in the assignment details.

assignmentStore1: list[Valuable] = [
     Valuable(value=5, weight=2),
     Valuable(value=5, weight=3),
     Valuable(value=1, weight=5),
     Valuable(value=5, weight=1),
     Valuable(value=1, weight=2)
]

assignmentStore2: list[Valuable] = [
     Valuable(value=92, weight=23),
     Valuable(value=57, weight=31),
     Valuable(value=49, weight=29),
     Valuable(value=68, weight=44),
     Valuable(value=60, weight=53),
     Valuable(value=43, weight=38),
     Valuable(value=67, weight=63),
     Valuable(value=84, weight=85),
     Valuable(value=87, weight=89),
     Valuable(value=72, weight=82),
]

assignmentStore3: list[Valuable] = [
    Valuable(value=135, weight=70),
    Valuable(value=139, weight=73),
    Valuable(value=149, weight=77),
    Valuable(value=150, weight=80),
    Valuable(value=156, weight=82),
    Valuable(value=163, weight=87),
    Valuable(value=173, weight=90),
    Valuable(value=184, weight=94),
    Valuable(value=192, weight=98),
    Valuable(value=201, weight=106),
    Valuable(value=210, weight=110),
    Valuable(value=214, weight=113),
    Valuable(value=221, weight=115),
    Valuable(value=229, weight=118),
    Valuable(value=240, weight=120),
]

store: list[Valuable] = [
    Valuable(value=30, weight=5),
    Valuable(value=35, weight=7),
    Valuable(value=30, weight=5),
    Valuable(value=20, weight=5),
    Valuable(value=20, weight=5),
    Valuable(value=20, weight=5),
    Valuable(value=10, weight=10),
    Valuable(value=10, weight=5),
    Valuable(value=20, weight=10),
    Valuable(value=5, weight=10),
    Valuable(value=5, weight=10),
    Valuable(value=1, weight=1),
    Valuable(value=1, weight=2),
]


# ---------------------------------- Fitness Functions ---------------------------------- #

# The following are fitness functions: (list of Valuable) -> fitness float
# These can be 

FitenessFunction = "Callable[[set[Valuable]], float]"
'''Fitness calculation method given a list of valuables (for annotations)'''

ratioOfSums: FitenessFunction
def ratioOfSums(valuables: set[Valuable]) -> float:
    '''The ratio between the some of the values and the sum of the weights (0 is empty list passed).'''
    if valuables:
        weightsSum: float = sum(valuable.weight for valuable in valuables)
        valuesSum: float = sum(valuable.value for valuable in valuables)
        return valuesSum / weightsSum
    else:
        return 0 

sumOfRatios: FitenessFunction
def sumOfRatios(valuables: set[Valuable]) -> float:
    '''The sum of the ratios between the values and the weights (0 is empty list passed).'''
    result = 0
    for valuable in valuables:
        result += valuable.value / valuable.weight
    return result


sumsDifference: FitenessFunction
def sumsDifference(valuables: set[Valuable]) -> float:
    '''The sum of the values minus the sum of the weights (0 is empty list passed).'''
    if valuables:
        return sum(valuable.value - valuable.weight for valuable in valuables)
    else:
        return 0

# The sum of the values (0 is empty list passed).
justValue: FitenessFunction = lambda valuables: \
    sum(valuable.value for valuable in valuables) if valuables else 0

# ---------------------------------- Trainer ---------------------------------- #

CACHE_SIZE: int = 1000
'''The max size of the cache for caching calculated fitness values'''

class Trainer:
    '''A trainer that manages a population (gene sequence strings) and the evolution of that population.'''

    def __init__(self, populationSize: int, maximumWeight: float, store: list[Valuable] = store, \
            mutationRate: float = 0.25, fitnessFunction: FitenessFunction = sumsDifference) -> None:
        
        # ------------------------ Populations Properties ------------------------ #

        self.populationSize: int = populationSize
        '''The number of gene sequences in the population.'''

        self.populationGeneSequences: list[str] = []
        '''The list of population gene sequences in no particular order.'''

        self.maximumWeight: float = maximumWeight
        '''The maximum weight a knapsack can hold.'''

        self.store: list[Valuable] = store
        '''The list of Valuable objects in the problem (order matters).'''

        self.bitLength: int = len(store)
        '''The size of the bit strings that make up each gene sequence. This should be the same
        as the length store.'''

        self.mutationRate: float = mutationRate
        '''The chance (0 to 1) that a mutation will occur on a single bit for a new gene sequence.'''
        
        # ------------------------ Training Properties ------------------------ #

        self.trainingIterationsLeft: int = 0
        '''the hard/maximum number of iterations left for training.'''

        self.valueThreshold: Optional[float] = None
        '''The threshold for the value that when met terminates training.'''

        self.valueCheckingSetSize: Optional[float] = None 
        '''The number of top n-many genes (when sorting the genes by fitness) to check
        when applying the valueThreshold check.'''

        self.fitnessThreshold: Optional[float] = None
        '''The threshold for the fitness that when met terminates training.'''
        
        # ------------------------ Cache Properties ------------------------ #
        
        self.fitnessCacheQueue: list[str] = []
        '''A simple cache queue that is used to determine which cached fitness values
        should be removed from the cache (does not sort by access, only by addition).'''

        self.fitnessCache: dict[str, float] = {}
        '''A cache of fitness values given a gene sequence (cleared when the fitness
        function is updated).'''

        self.cacheSize: int = 0
        '''The active size of the fitness value cache.'''

        self.maxCacheSize: int = CACHE_SIZE
        '''The maximum size of the fitness value cache.'''

        # ------------------------ Fitness Function ------------------------ #

        self._fitnessFunction: FitenessFunction = fitnessFunction
        '''The fitness function for evolving the gene sequences.'''


    # ------------------------ Fitness Function Property ------------------------ #

    def _get_fitnessFunction(self) -> FitenessFunction:
        '''Getter for fitness function.'''
        return self._fitnessFunction
    
    def _set_fitnessFunction(self, value: FitenessFunction):
        '''Setter for fitness function.'''
        self._fitnessFunction = value
        self.fitnessCacheQueue = []
        self.fitnessCache = {}
        self.cacheSize = 0
    
    fitnessFunction = property(_get_fitnessFunction, _set_fitnessFunction)

    # ------------------------ Setup/configuration ------------------------ #

    def setUpRandomPopulation(self) -> None:
        '''Set up the population using random gene sequences.'''
        self.populationGeneSequences = []
        self.fillRandomPopulation()

    def fillRandomPopulation(self) -> None:
        '''Fill the remaining space in the population with random gene sequences.'''
        choices: list[str] = ['0', '1']
        while len(self.populationGeneSequences) < self.populationSize:
            newGeneSequence: str = ''.join(choice(choices) for _ in range(self.bitLength))
            self.populationGeneSequences.append(newGeneSequence)

    def setUpSchemaPopulation(self, fillCap: Optional[int] = None) -> None:
        '''Set up the population using schema-based gene sequences. If fillCap is passed,
        only fillCap-many genes will be schema-based and the rest will be random.'''
        
        self.populationGeneSequences = []
        prototype: str = self.generatePrototype()
        prototypeCount = self.populationSize

        if fillCap is not None and fillCap < self.populationSize:
            prototypeCount = fillCap

        for _ in range(prototypeCount):
            self.populationGeneSequences.append(prototype)

        # Fill the rest with random
        self.fillRandomPopulation()
            

    def setToTrackSession(self, maximumIterations: int, valueThreshold: Union[float, None, str] = None, \
            fitnessThreshold: Optional[float] = None, valueCheckSize: Optional[int] = None) -> None:
        '''Set up the trainer to start performing evolution.'''

        self.trainingIterationsLeft = maximumIterations

        # Calculate or set the value threshold
        if isinstance(valueThreshold, str):
            if valueThreshold == 'guess':
                self.valueThreshold = self.generateValueApproximateThreshold()
            else:
                raise ValueError('Illegal value threshold calculation method.')
        else:
            self.valueThreshold = valueThreshold
        
        self.fitnessThreshold = fitnessThreshold
        self.valueCheckingSetSize = valueCheckSize
    

    # ------------------------ Heuristics ------------------------ #

    def generatePrototype(self) -> str:
        '''Generate a prototype by including 1s in all available places (don't exceed max weight),
        filling in order of best bang-for-buck (best value-to-weight ratio).'''

        # Create a list of store item indices ranked from best bang-for-buck to worst
        sortingLambda = lambda bitIndex: self.fitnessFunction({self.store[bitIndex]})
        itemIndicesRanking: list[int] = list(range(self.bitLength))
        itemIndicesRanking.sort(key=sortingLambda, reverse=True)
        
        resultBitSet: set[int] = set()
        workingResultWeight: float = 0
        for itemIndex in itemIndicesRanking:
            candidateItem: Valuable = self.store[itemIndex]
            
            if candidateItem.weight + workingResultWeight <= self.maximumWeight:
                resultBitSet.add(itemIndex)
                workingResultWeight += candidateItem.weight
        
        result: str = ''.join('1' if index in resultBitSet else '0' for index in range(self.bitLength))
        return result

    def generateValueApproximateThreshold(self) -> float:
        '''Calculate the threshold value by generating a prototype and adding to its value sum
        the smallest possible amount (0 if the prototype's remaining weight is 0).'''
        
        prototype: str = self.generatePrototype()
        prototypeValue: float = self.evaluateGeneSequenceValue(prototype)
        prototypeWeight: float = self.evaluateGeneSequenceWeight(prototype)
        
        # Check if the prototype's remaining weight is 0
        if self.maximumWeight - prototypeWeight == 0:
            return prototypeValue
        
        workingSmallestDifference = inf

        for lhsIndex in range(self.bitLength - 1):
            for rhsIndex in range(lhsIndex + 1, self.bitLength):
                difference: float = abs(self.store[lhsIndex].value - self.store[rhsIndex].value)
                if difference != 0 and difference < workingSmallestDifference:
                    workingSmallestDifference = difference

        return prototypeValue + workingSmallestDifference / 2.0

    
    # ------------------------ Gene Sequence Evaluation ------------------------ #

    def evaluateGeneSequenceWeight(self, geneSequence: str) -> float:
        '''Calculate the passed gene sequence's weight.'''
        weightSum: float = 0
        for bitIndex, bitValue in enumerate(geneSequence):
            if bitValue != '0':
                valuable: Valuable = self.store[bitIndex]
                weightSum += valuable.weight
        return weightSum

    def evaluateGeneSequenceValue(self, geneSequence: str) -> float:
        '''Calculate the passed gene sequence's value.'''
        valueSum: float = 0
        for bitIndex, bitValue in enumerate(geneSequence):
            if bitValue != '0':
                valuable: Valuable = self.store[bitIndex]
                valueSum += valuable.value
        return valueSum
    
    def evaluateGeneSequenceFitness(self, geneSequence: str) -> float:
        '''Calculate the passed gene sequence's fitness.'''
        
        memo: str = geneSequence
        fitness: float = -inf
        
        # Check if the memo (gene) is already cached
        if memo not in self.fitnessCache:
            # The sequence is not cached

            valuables: set[Valuable] = set()
            weightSum: float = 0

            for bitIndex, bitValue in enumerate(geneSequence):
                if bitValue != '0':
                    valuable: Valuable = self.store[bitIndex]
                    valuables.add(valuable)
                    weightSum += valuable.weight

                    if weightSum > self.maximumWeight:
                        break

            if weightSum <= self.maximumWeight:
                fitness = self.fitnessFunction(valuables)
            
            # Memoization management
            
            self.fitnessCacheQueue.append(memo)
            self.fitnessCache[memo] = fitness
            self.cacheSize += 1

            if self.cacheSize > self.maxCacheSize:
                cachedEntityToRemove = self.fitnessCacheQueue.pop(0)
                del self.fitnessCache[cachedEntityToRemove]
                self.cacheSize -= 1
        else:
            # The sequence is cached
            fitness = self.fitnessCache[memo]
            
        return fitness


    def bestGenes(self, count: int, silencePrint: bool = False) -> list[str]:
        '''Get a list of the (count)-many best gene sequences in order (using the
        current fitness function).'''

        bestGenes: list[(float, str)] = []
        highestFitness: float = -inf
        fitnessSum: float = 0

        gene: str
        for gene in self.populationGeneSequences:
            fitness: float = self.evaluateGeneSequenceFitness(gene)
            bestGenes.append((fitness, gene))
            highestFitness = max(highestFitness, fitness)
            if fitness != -inf:
                fitnessSum += fitness
        
        bestGenes.sort(key=lambda tuple: tuple[0], reverse=True)

        if SHOULD_PRINT_FITNESS and not silencePrint:
            print(f'Highest: {highestFitness:.2f},    Average: {fitnessSum/self.populationSize:.2f}')

        return [entry for _, entry in bestGenes[:count]]

    # ------------------------ Breeding ------------------------ #

    def crossoverGeneSequences(self, gene1: str, gene2: str) -> str:
        '''Get a single child from the passed parents, crossing over the genes randomly.
        The order of the parents does not matter.'''

        crossIndex: int = randint(0, self.bitLength)
        firstGene: str
        secondGene: str
        firstGene, secondGene = (gene1, gene2) if randint(0, 1) else (gene2, gene1)
        return firstGene[:crossIndex] + secondGene[crossIndex:]

    def mutateGenes(self, gene: str) -> str:
        '''Get a mutated version of the passed gene sequence. This applies one bit flips
        for a random bit.'''

        flippedIndex: int = randint(0, self.bitLength - 1)
        newBit: str = '1' if gene[flippedIndex] == '0' else '0'
        newGene: str = gene[:flippedIndex] + newBit + gene[flippedIndex+1:]
        return newGene

    def makeChildFrom(self, geneSequence1: str, geneSequence2: str) -> str:
        '''Get a child (gene sequence) from two parent (oder does not matter). This applies
        crossover and may flip any number of bits (less likely to be more).'''
        child = self.crossoverGeneSequences(geneSequence1, geneSequence2)
        should_mutate: bool = random() <= self.mutationRate
        while should_mutate:
            child = self.mutateGenes(child)
            should_mutate = random() <= self.mutationRate
        return child

    # ------------------------ Iteration training/evolution ------------------------ #

    def _reachedThreshold(self, bestGeneSequences: list[str]) -> bool:
        '''Helper method for iteration method that updates the iteration count and determines if 
        any threshold has been met.'''

        self.trainingIterationsLeft -= 1
        isFinishedTraining: bool = self.trainingIterationsLeft <= 0

        # Make the set/list of genes to perform a value check over 
        valueCheckingSet: list[str] = bestGeneSequences if self.valueCheckingSetSize is None \
            else bestGeneSequences[:self.valueCheckingSetSize]

        # Check value
        if self.valueThreshold is not None and \
                any(self.evaluateGeneSequenceValue(geneSequence) >= self.valueThreshold \
                for geneSequence in valueCheckingSet \
                if self.evaluateGeneSequenceWeight(geneSequence) <= self.maximumWeight):
            isFinishedTraining = True
            if SHOULD_PRINT_THRESHOLD_MEET:
                print('Reached the value threshold')
        
        # Check fitness
        if self.fitnessThreshold is not None and \
                self.evaluateGeneSequenceFitness(bestGeneSequences[0]) >= self.fitnessThreshold:
            isFinishedTraining = True
            if SHOULD_PRINT_THRESHOLD_MEET:
                print('Reached the fitness threshold')

        return isFinishedTraining


    def runIteration(self, reductionSize: int, bestPerformerMaintain: int = 0) -> bool:
        '''Perform a single iteration/evolution over'''
        bestGeneSequences: list[str] = self.bestGenes(reductionSize)

        if self._reachedThreshold(bestGeneSequences):
            return True
        
        numberOfParentPairs: int = reductionSize//2
        newPopulation: list[str] = []

        for index in range(min(bestPerformerMaintain, self.populationSize)):
            newPopulation.append(bestGeneSequences[index])

        childrenPerPair: int = (self.populationSize - len(newPopulation))//numberOfParentPairs
        shuffle(bestGeneSequences)

        for index in range(numberOfParentPairs):
            geneSequence1 = bestGeneSequences[2 * index]
            geneSequence2 = bestGeneSequences[2 * index + 1]

            for _ in range(childrenPerPair):
                newPopulation.append(self.makeChildFrom(geneSequence1, geneSequence2))
        
        for index in range(self.populationSize - len(newPopulation)):
            geneSequence1 = bestGeneSequences[2 * index]
            geneSequence2 = bestGeneSequences[2 * index + 1]
            newPopulation.append(self.makeChildFrom(geneSequence1, geneSequence2))

        self.populationGeneSequences = newPopulation

        return False
        

# ---------------------------------- Analysis ---------------------------------- #

def performanceTest(maximumWeight: float, store: list[Valuable]) -> None:

    # *ADJUST THIS TO ADJUST THE BEHAVIOR OF WHAT APPEARS IN MAIN*
    # More test parameters:
    populationSize: int = 100
    mutationRate: float = 0.25
    fitnessFunction: fitnessFunction = justValue
    initialSchemaPopulationFillCap: int = 0
    maximumIterations: int = 10
    # Use 'guess' to approximate the value threshold (just beyond what the schema gives)
    valueThrehold: Union[str, None, int] = None
    fitnessThreshold: Optional[float] = None
    reductionSize: int = populationSize//2
    bestPerformerMaintain: Optional[int] = 10

    # Testing:
    startTime = perf_counter()

    trainer = Trainer(populationSize=populationSize, maximumWeight=maximumWeight,\
        mutationRate=mutationRate, store=store, fitnessFunction=fitnessFunction)
    trainer.setUpSchemaPopulation(fillCap=initialSchemaPopulationFillCap)
    trainer.setToTrackSession(maximumIterations, valueThreshold=valueThrehold, \
        fitnessThreshold=fitnessThreshold)
    
    while not trainer.runIteration(reductionSize=reductionSize, \
        bestPerformerMaintain=bestPerformerMaintain): pass

    endTime = perf_counter()
    trainingTimeDelta = endTime - startTime

    # Return the trainer and the time to train
    return trainer, trainingTimeDelta


# ---------------------------------- Main ---------------------------------- #

if __name__ == '__main__':

    # Get the arguments passed in via the terminal
    commandArguments = sys.argv[1:]

    if len(commandArguments) > 0 and commandArguments[0] == 'test':
        # trainer, trainingTime = performanceTest(10, assignmentStore1)
        # trainer, trainingTime = performanceTest(165, assignmentStore2)
        trainer, trainingTime = performanceTest(750, assignmentStore3)

        trainer.fitnessFunction = justValue
        geneSequences = trainer.bestGenes(10, silencePrint=True)
        print('Top 10 value-gene pairings:', [(trainer.evaluateGeneSequenceFitness(gene), gene) for gene in geneSequences])
        print(f'Training time: {trainingTime:.4f}')

    else:

        # Attempt to open a file and read the contents (for input)
        fileInputs: list[str] = []
        if len(commandArguments) > 0 and commandArguments[0] != '-t':
            with open(commandArguments[0], 'r') as f:
                fileInputs = f.readlines()

        # Get the input from the file (if available) or from the user
        def pullInput() -> str:
            result = None
            if fileInputs:
                result = fileInputs.pop(0)
            else:
                result = input()
            return result

        # Get the user-entered max weight and number of valuables
        userParmeters: list[str] = pullInput().split(' ')
        filter(lambda entry: entry != '', userParmeters)
        maxWeight: float = int(userParmeters[0])
        numberOfValuables: float = int(userParmeters[1])

        # Creata a list of the user-configured valuables
        usersStore: list[Valuable] = []

        for _ in range(numberOfValuables):
            # Add a valuable
            valuableParmeters: list[str] = pullInput().split(' ')
            filter(lambda entry: entry != '', valuableParmeters)
            usersStore.append(Valuable(value=int(valuableParmeters[1]), weight=int(valuableParmeters[0])))

        # Perform the training
        trainer, trainingTime = performanceTest(maxWeight, usersStore)

        # Get and print the best results by total value (new fitness function)
        trainer.fitnessFunction = justValue
        bestGeneSequence: str = trainer.bestGenes(1, silencePrint=True)[0]
        print(' '.join(bestGeneSequence))
        print(trainer.evaluateGeneSequenceFitness(bestGeneSequence), \
            trainer.evaluateGeneSequenceWeight(bestGeneSequence))
        print(f'Training time: {trainingTime:.4f}')





