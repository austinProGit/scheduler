# Thomas Merino
# 8/31/22
# CPSC 4175 Group Project

# Warning: this is full of a lot of doo-doo code


try:
    import tabula
    import pandas
    import networkx
    
except (ModuleNotFoundError):
    print("Missing modules. Please intall the following: lorem ipsum.")
    exit(1)
    
# Constants for denoting the types/formats for file output
EXCEL_OUTPUT_TYPE = 0x0
PDF_OUTPUT_TYPE = 0x1
TEXT_OUTPUT_TYPE = 0x2

class DummyCourseAvailabilityParser:
    
    def __init__(self):
        pass
        
    def parseFile(self, filename):
        pass

class DummyCourseAvailabilityParser:
    
    def __init__(self):
        pass
        
    def parseFile(self, filename):
        pass

class DummyScheduler:
    '''A dummy scheduler class for testing the program.'''
    
    def __init__(self):
        pass
        
    def loadAvailability(self, container):
        ''''Load data from an availability container into the scheduler. These is how prerequisites and course availabiliities are set.'''
        print("Loaded availability: " + str(container))
        
    def loadNeededCourses(self, container):
        '''Load data from a needed courses container into the scheduler. These is how the to-be-scheduled courses are set.'''
        print("Loaded needed courses: " + str(container))
    
    def setNumberOfCourses(self, number):
        ''''Set the number of courses to be scheduled per semester.'''
        print("Number of courses per semester set to " + str(number))
    
    def generateSchedule(self, filename, outputMethods):
        ''''Generate a schedule.'''
        
        for outputMethod in outputMethods:
            pass
        
        print("Schedule Generated!")
        return filename + ".dummy"


class SmartPlannerController:
    
    def __init__(self):
        self.setup()
    
    def setup(self):
        '''Perform setup for scheduling, general configuration, and user interface'''
        self._interfaceStack = [MainMenuInteface()]
        self._scheduler = DummyScheduler()
        
        try:
            # Perform setup of DAG here
            parser = DummyCourseAvailabilityParser()
            
        except(FileNotFoundError):
            # Perform error handling here
            print("Invalid course catalog file")
            exit(2)
    
    def pushInterface(self, interface):
        '''Push a given interface to the top of the interface stack.'''
        self._interfaceStack.append(interface)
    
    def popInterface(self, interface):
        '''Pop the provided interface if it on top of the interface stack.'''
        
        # Check if the passed interface resides on the top of the stack
        if interface == self._interfaceStack[-1]:
            topInterface = self._interfaceStack.pop()
            # Call the interface's deconstruct method
            topInterface.deconstruct(self)
            return topInterface
            
        else:
            # The passed interface is not on the top (return None explicitly)
            return None
    
    def _getCurrentInterface(self):
        '''Get the interface on top of the interface stack'''
        return self._interfaceStack[-1]
    
    def _setCurrentInterface(self, interface):
        '''Replace the top interface on the stack with a given interface'''
        self.popInterface(self._interfaceStack[-1])
        self.pushInterface(interface)
    
    # Property for the top-most interface
    currentInterface = property(_getCurrentInterface, _setCurrentInterface)
    
    def output(self, message):
        '''Output a message to the user.'''
        print(message)
        
    def reportInputError(self, message):
        '''Output an error message to the user.'''
        self.output("ERROR: " + message)
    
    def loadNeededCourses(self, filename):
        '''Load the courses that must be scheduled into the scheduler (from a filename).'''
        parsedStuff = ("Data parsed from " + filename)
        self._scheduler.loadNeededCourses(parsedStuff)
    
    def setNumberOfCourses(self, numberOfCourses):
        '''Set the number of courses that are scheduled per semester.'''
        self._scheduler.setNumberOfCourses(numberOfCourses)
        self.output("The number of courses has been set")
        
            
    def generateSchedule(self, filename, outputMethods):
        '''Generate the schedule with a given filename.'''
        resuleFileNames = self._scheduler.generateSchedule(filename, outputMethods)
        self.output("The schedule has been saved as:\n" + resuleFileNames)
        
        
    def dummyLoop(self, iterations):
        '''Test loop'''
        for _ in range(iterations):
            currentInterface = self.currentInterface
            inp = input(currentInterface.name + ": ")
            self.currentInterface.parseInput(self, inp)
            
            if len(self._interfaceStack) == 0:
                exit(0)

    

class MainMenuInteface:
    
    def __init__(self):
        self.name = "main menu"
        self._commands = {
            "load": loadNeededCoursesCommand,
            "courses": setNumberOfCoursesCommand,
            "schedule": generateScheduleCommand,
            "help": helpCommand,
            "quit": quitCommand
        }
        
    def parseInput(self, caller, input):
        '''Handler input on behalf of the passed caller (controller).'''
        
        # Get the position of the first space in the input string
        firstSpaceIndex = input.find(' ')
        commandKey = input
        argument = ""
        
        # Check if the input has multiple words
        if firstSpaceIndex != -1:
            # Set the command key to just the first word and the arguements to the rest
            commandKey = input[0:firstSpaceIndex]
            argument = input[firstSpaceIndex:].strip()
        
        # Check if the command key is valid
        if commandKey in self._commands:
            # Get and execute the command (function)
            command = self._commands[commandKey]
            command(caller, argument)
        else:
            # Report invalid input
            caller.reportInputError("Sorry, no command matching \"" + commandKey+ "\" was found. Enter \"help\" to find the command you are looking for.")
        
    def deconstruct(self, caller):
        print("MAIN MENU BYE BYE!")


class HelpInterface:
    
    def __init__(self):
        self.name = "help menu"
        
    def parseInput(self, caller, input):
        '''Handler input on behalf of the passed caller (controller).'''
        
        # TEST -> IMP
        if "exit" in input:
            caller.popInterface(self)
        else:
            caller.output("Now searching for \"" + input + "\"")
    
    def deconstruct(self, caller):
        print("HELP MENU BYE BYE!")


def loadNeededCoursesCommand(caller, filename):
    if filename != "":
        caller.loadNeededCourses(filename)
    else:
        caller.reportInputError("No filename entered.")
        
def setNumberOfCoursesCommand(caller, argument):
    try:
        number = int(argument)
        caller.setNumberOfCourses(number)
    except(ValueError):
        caller.reportInputError("Sorry, that is not a valid input (pleas use a number)")
    

def generateScheduleCommand(caller, filename):
    if filename != "":
        caller.generateSchedule(filename, [EXCEL_OUTPUT_TYPE])
    else:
        caller.reportInputError("No filename entered.")

def helpCommand(caller, argument):
    caller.output("Welcome to the help menu")
    newHelpInterface = HelpInterface()
    caller.pushInterface(newHelpInterface)
    
    # Check to see if the an
    if argument != "":
        newHelpInterface.parseInput(caller, argument)
        
    
def quitCommand(caller, argument):
    caller.output("Good bye!")
    caller.popInterface(caller.currentInterface)
        

s = SmartPlannerController()
s.dummyLoop(100)
