# Smart Planner: Developer README

## Software Overview
The program driver is at the core of Smart Planner. The program driver retains a copy of:
* a scheduler object, which defines and performs the scheduling algorithms
* a parameter container, which stores the parameters for creating a schedule including the destinations directories and file name (for general use)
* an interface stack, which tracks the state of the program and the available interaction options for the user
* a session configuration object, which records the global settings for the application

It should be noted that there are two parts to a schedule’s parameters: the schedule specific parameters and the output parameters. A schedule can be produced given the schedule specific parameters, but these parameters do not specify what to do with the resulting schedule. The output parameters specify the output methods destinations and I/O handling. Because both of these parameters are specific to an individual student, a pair will be needed to generate a schedule for each student.

Every process is orchestrated by the driver. The driver is responsible for handling I/O and orchestrating the applications functionality. The driver is broken up into a few sections, which includes:
* initialization
    * This is responsible for instantiating a driver object and orchestrating process and/or program configuration
* process configuration
    * Configures the individual process based on then config file
* program configuration
    * Configures the long-term behavior of the program
* user interface atoms
    * Defines the basic operations involved in presenting the user interface
* user interface management
    * Provides high-level user interface management functionality
* schedule parameter configuration
    * Sets the scheduling parameters, which are funneled into the perimeter container, scheduler object, or session configuration object
* schedule parameter retrieval
    * Get the scheduling parameters
* scheduling
    * Performs scheduling via the scheduling object and exports the results to the interface and/or the file system through formatter
The program driver is built on an interface stack. To interface with the driver, a component submits requests to the top interface of the stack. 


## Assumed Background
This document assumes that the reader is at least a junior level Computer Science student. Readers should be proficient in python and familiar with libraries like pandas, pyside6, and pypdf. This system touches on topics such as artificial intelligence (in the form of Rules Based expert system and Case Based Reasoning) and genetic algorithms, but the code should be somewhat self-explanatory. 

## Step-by-Step Usage

<h3>Load Needed Courses</h3>
<p>
    In order for Smart Planner to generate a schedule, it needs the a list of courses required before graduation. 
    Courses should be listed in a PDF document. To load the courses into the program you can either enter 
    "load FILENAME" where FILENAME is the local or absolute path, or enter "browse" to open a file browser.
</p>

<h3>Set the Number of Hours Per Semester</h3>
<p>
    To set the number of credit hours per semester, enter "hours NUMBER" where NUMBER is the desired number of hours 
    per semester.
</p>

<h3>Adjusting Configuration Data</h3>
<p>
    The configuration file (called "config") has the following format: the first line is the filename of the catalog 
    file. This is expected to be an xslx file in the working directory and follows the format in the instruction 
    manual (see manual). The second line is whether the program launches in GUI mode (either "YES" or "NO").
</p>

<h3>CLI Scheduling</h3>
<p>
    From the command line, user launches main.py. User loads needed courses with syntax 'load fileName'. The user 
    should verify the parameters of the current configuration with the parameters command, syntax 'parameters', which 
    will output the file destination, the maximum hours per semester, and all loaded courses. Then, the user will 
    generate a schedule with the 'schedule' command, receiving a positive completion output message. The user can then 
    access their schedule.
</p>

<h3>GUI Scheduling</h3>
<p>
    From the command line, user launches main.py. If the program has been previously configured to open immediately to 
    the GUI, then the GUI will launch automatically. If not, the user will then enter 'gui-i' to launch the GUI. Once 
    the GUI is launched, the user will have access to the following parameters: load needed courses, set destination 
    directory, set maximum hours per semester, set output format, and set output file name. After the user modifies 
    desired parameters, they press the 'generate schedule' button. The schedule is now generated.
</p>

<h3>Handling Bad Course Info Input</h3>
<p>
    The administrator has configured the program with a prerequisite that is definitionally unsatisfiable. As soon as 
    the user launches the program, the user is notified that the catalog contains invalid data and is then redirected 
    to an error menu. The user must seek the administrator's assistance in creating a valid course information input. 
    Once in the error menu, the administrator has the option to create a new default configuration file or attempt to 
    reload. The user cannot access the GUI if there is an error.
</p>

<h3>Administrator Familiarization and Program Configuration</h3>
<p>
    After launching, the administrator accesses the help menu with command 'help'. On the help menu, the administrator 
    sees a prompt to search by keywords for help articles. The administrator decides to instead see all help articles 
    by entering the command 'all'. The administrator learns about the main functions of the program, including loading 
    courses needed, generating the hours, selecting the schedule export types, and many other functions. The administrator 
    then begins configuration. The administrator configures the courses by editing the Course Info excel file. The 
    administrator then changes the source directory for the Course Info file as desired by editing the config file. Next, 
    the administrator sets the output format with the commands 'exports [exportNum]'. Next, the administrator configures 
    the destination path with the command 'destination [path]'. The administrator then sets the default user interface 
    to GUI with command 'gui'. The program is now configured for student use.
</p>

<h3>Validate Existing Path to Graduation</h3>
<p>
    User launches program in CLI and enters 'verify [filePath]'', where filePath is the location of the Path to Graduation. 
    If the Path to Graduation is valid, the program outputs 'path valid'. Otherwise, it outputs a list of the errors 
    found in the path.
</p>

<h3>Batch Processing</h3>
<p>
    The administrator has a folder containing all of the Courses Needed PDF files. The admin enters the destination directory 
    with command 'destination [path]'. Then, he enters the hours per semester with command 'hours [numberOfHoursPerSemester]'. 
    Then, he begins batch process execution with command 'batch [directoryOfNeededCourseFiles], [destinationDirectoryName]'. 
    Valid results will be found in the destination folder. Invalid inputs will result in no corresponding output, and an error 
    message will be displayed.
</p>

<h3>AI Output Interpretation</h3>
<p>
    After scheduling, the user will receive an output in the form of a decimal value between 0 and 100, where 0 reflects that
    the Expert System is very unconfident in the goodness of the Path to Graduation, and 100 reflects absolute confidence. All 
    Paths to Graduation are valid and satisfy CSU graduation requirements; this measure reflects a subjective judgment based 
    on rules provided by human scheduling experts.
</p>

<h3>Configure Course Importance</h3>
<p>
    Course importance is used to prioritize some classes over others in scheduling, provided that the importance does not conflict 
    with existing scheduling rules. The aministrator accesses the Importance column in the Course Info Excel file. For a given class, 
    a rating of 0 to 100 can be given.
</p>

<h3>Format of Course Info Input File</h3>
<p>
    courseID: Unique identifier for courses.
    courseName: Common name for course.
    hours: Hours by semester.
    availability: When a course is offered during the year by season.
    prerequisites: Courses required to be taken before a given course.
    co-requisites: Courses that must be taken before or concurrently with a given course.
    recommended: Courses recommended to take together.
    isElective: 1 if a course is an elective, 0 otherwise.
    restrictions: Restrictions on when a course can be taken, ex: must be senior.
    note: Misc notes.
    importance: Importance that a class be taken sooner than other courses from 1 to 100.
</p>
<table>
    <tr class="table_title">
        <th colspan="2">Course Info Column Descriptions</th>
    </tr>
    <tr>
        <th>Column Name</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>courseID</td>
        <td>Unique identifier for courses.</td>
    </tr>
    <tr>
        <td>courseName</td>
        <td>Common name for course.</td>
    </tr>
    <tr>
        <td>hours</td>
        <td>Hours by semester.</td>
    </tr>
    <tr>
        <td>availability</td>
        <td>When a course is offered during the year by season.</td>
    </tr>
    <tr>
        <td>prerequisites</td>
        <td>Courses required to be taken before a given course.</td>
    </tr>
    <tr>
        <td>co-requisites</td>
        <td>Courses that must be taken before or concurrently with a given course.</td>
    </tr>
    <tr>
        <td>recommended</td>
        <td>Courses recommended to take together.</td>
    </tr>
    <tr>
        <td>isElective</td>
        <td>1 if a course is an elective, 0 otherwise.</td>
    </tr>
    <tr>
        <td>restrictions</td>
        <td>Restrictions on when a course can be taken, ex: must be senior.</td>
    </tr>
    <tr>
        <td>note</td>
        <td>Misc notes.</td>
    </tr>
    <tr>
        <td>importance</td>
        <td>Importance that a class be taken sooner than other courses from 1 to 100.</td>
    </tr>
</table>

## Modules Overview

### Orchestrators
* main
    *This is the launching point of the program.
* program_driver
    * The driver is the  controller of the program that interfaces between the components. This stores the scheduler and scheduling parameters. This also stores and manages the interface stack.
* auto_update
    * The auto_update is a service that manages updating, including update checking, update downloading, and program status after updating.

### Identifiers and Data Types:
* Module 'course_info_container'
    * Types:
        * CourseInfoContainer: This container is a dictionary of DataFrames using the Pandas library. It is a reflection of course information found in our Course Info.xlsx. Any module that imports this module and/or class has access to contents/methods of the database.

        * CourseReport: There is a method 'get_course_report(CourseIdentifier)' that creates an instance of CourseReport.  Once instantiated the course ID is accessed from Course Identifier.  If the course is valid, this method automatically populates its attributes with all the course information in Course Info.xlsx. There is also an option to stub courses, meaning allowing courses to be validated if they are electives.
* Module 'instance_identifiers'
    * Types:
        * CourseIdentifier: These objects are disposable, replicable, identifiers for a course. While these are objects, they are best understood as a simple course ID with a small amount of wrapping (to include a printable name and whether the ID is a stub). Two CourseIdentifier objects are considered equivalent if their course IDs are the same unless they are stubbed, in which case they are always considered different.

        * Schedulable: These stateful objects serve as instances of courses that can be scheduled. For example, an object instance of the course ‘CPSC 1234’ can be instantiated and scheduled into an actual slot in an open schedule.

        * StudentIdentifier: During DegreeWorks parsing, this object wraps Student IDs. Currently not used.
* Module: 'degree_extraction_container'
    * This object holds Degreeworks PDF file student information, including: student name, student number, degree plan name, GPA, and current/taken courses after PDF file parsing. 
* Module: 'courses_needed_container'
    * This container encapsulates a requirement tree implementing methods to interface.
* Module: 'schedule_info_container'
    * SemesterDescription - Holds information including current year, semester type, course list. ScheduleInfoContainer - starting semester, starting year, confidence value
* Module: 'end_reports'
    * This is a class for representing a path to graduation validation report. It stores path’s file description, confidence factor and all errors.

### Tree Files:
* Module: 'requirement_tree'
    * A course selection tree represents not the course plan, but also the current students course selection (the courses they plan to take over other courses). Each node in the tree may store several or no selections. Those selections indicate which nodes directly below are to be choses/taken. Each node will have class-defined rules for satisfiability that depend on the selection. That is, to meet the requirements of the node, the user must select nodes below that satisfy its particular resolution function. Resolution functions are only aware of nodes below them and may query properties of nodes many layers below them (through recursive calls).
    * In the current version, there are eight types/classes of node:
        1. Shallow count node: requires n-many courses to be selected directly below it
        2. Deep count node: requires n-many courses to be selected anywhere below it
        3. Deep credit node: requires n-many credits to be selected anywhere below it
        4. Exhaustive node: a node suited for requiring all nodes directly below it
        5. List node: a node suited for requiring all courses directly below it (no groups)
        6. Deliverable course: an explicit instance of a course with a name and credits
        7. Course protocol node: a regex form that may be filled out to become any course matching that regex pattern (protocol)
        8. Inserter node: a node that, when selected, adds another node of a given form (for sections that have variable number of selections).
    * A consequence of this structure is that a tree can be in one of many satisfaction states. Each state is node-dependent, and there is an overall satisfaction state that is slightly related to this.
    
    * Each node can be in one of four states:
        1. Unresolved: selections directly below need to be made
        2. Discovery resolved: all selections made directly below are adequate for satisfying the node (even if more selections need to be made further below). 
        3. Resolved: The node is satisfied and all other nodes below it are in the resolved state (fully satisfied)
        4. Stubbed: The node has been set to a special state where all requirements are voided and the output courses (when requesting selected courses) are stand-in courses (substitutes). These substitutes are returned as a special kind of deliverable item when requests are made.

	* The whole tree can then be in one of three states:
        1. Unresolved: The tree is not in an outputting state. This means some more courses need to be selected or stubbed before a schedule can be generated.
        2. Resolved: The tree has all adequate selections and contains no active stubs. This can be used to generate a schedule.
        3. Partially resolved: The tree contains all adequate selections and some active stubs. This can be used to generate a schedule
* Module: 'requirement_container'
    * It is an encapsulation of a requirement tree, which provides methods to interface with the requirement tree.
* Module: 'requirement_parser'  
    * This module is used to parse over a tree logic string and generate a requirement tree.  

### Parsers:
* Module: 'degreeworks_parser_v2'
    * This module parses Degreeworks PDF documents to create a DegreeExtractionContainer that contains current taken courses, courses needed, degree plan name, student number, and gpa
* Module: 'path_to_grad_parser'
    * The path_to_grad_parser parses a filled Path To Graduation.xlsx file for verification.
* Module: 'CSU_public_data_parser'
    * This module fetches current data from CSU’s website and updates Course Info.xlsx.  
* Module: 'recursive_descent_parser'
    * This module uses the concept of context free grammar to parse logic with ordered precedence of parentheses, “and”, and  “or”.  By using a hierarchy of expressions, terms, and factors we are able to create nodes for the logic string used later on in the program.

### Formatters:
* Module: 'excel_formatter'
    * This module places the courses in the desired semester and year format of an empty Path To Graduation.xlsx template.   
* Module: 'pdf_formatter'
    * This formatter outputs the schedule as a PDF as opposed to default excel file output.
* Module: 'plain_text_formatter'
    * The plain_text_formatter outputs the schedule as a plain text document.

### Interface:
* Module: 'menu_interface_base'
    * It provides a super class for interface objects allocating basic functionality such as adding commands and parsing input.
* Module: 'cli_interface'
	* This is an object that takes user input, processes those inputs, determines the appropriate action per input, and sends requests to the program driver.  
* Module: 'graphical_interface'
    * It is just like any other interface layer except it constructs a pyside build user interface that has near to complete functionality.  
* Module: 'help_interface'
    * The  help_interface is an interface object that has searching and article displaying functionality, which pulls its content from the help.html.
* Module: 'item_selection_interface'
    * It serves as a type of CLI interface that performs item selections with functions via callbacks.
* Module: 'requirement_interface'
    * The requirement_interface acts as the interface for the requirements tree. Handles prerequisite, course selection, and other tree configurations management. 


## Errors

## Support

## Further Resources
The help file located in the program explains more of the system behavior in plain language. This document is intended as a technical overview rather than a how-to. The SmartPlanner Github page is also updated regularly with release notes, history etc. Separate from this document is the README file intended for the average user. Like the Help page, this file will explain system behavior in a more digestible way. 
