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

<h3>Administrator Familiarization and Program Configuration</h3>
	<!-- admin administrator familiarization configuration -->
<p>
    After launching, the administrator accesses the help menu with command 'help'. On the help menu, 
    the administrator sees a prompt to search by keywords for help articles. The administrator decides 
    to instead see all help articles by entering the command 'all'. The administrator learns about the main 
    functions of the program, including loading courses needed, setting maximum hours per semester, 
    selecting the schedule export types, and other functions. The administrator then begins configuration. 
    The administrator configures the course records by editing the 'Course Info' excel file, which is found 
    within the 'Smart Planner/input_files' directory. The administrator then changes the source directory for 
    the 'Course Info' file as desired by editing the 'config' file located in the 'Smart Planner' directory. 
    Next, the administrator sets the output format with the commands 'exports [exportNum]'. Next, the 
    administrator configures the destination path with the command 'destination [path]'. The administrator 
    then sets the default user interface to GUI with command 'gui'. The program is now configured for student use.
</p>
<h3>Load Needed Courses</h3>
<!--load needed courses course classes class schedule input-->
<p>
    To generate a schedule, the Smart Planner requires a valid DegreeWorks PDF from a student's DegreeWorks 
    portal as an input. To load needed courses via the GUI, the user can click 'Open Needed Courses', then 
    select the DegreeWorks PDF, then click 'Open'. To load needed courses via the CLI, the administrator can 
    either enter "load [fileName]" where 'fileName' is the local or absolute path, or enter "load-e" to open a file browser.
</p>
<h3>Set the Number of Hours Per Semester</h3>
<!--hours set parameter per semester setup configure summer-->
<p>
    To set the number of credit hours per semester, enter "hours[number]" where 'number' is the desired number 
    of hours per Fall or Spring semesters. Optionally, the user can enter the “summer-hours [number]” command to 
    set the hours per Summer semester.
</p>
<h3>Adjusting Configuration Data</h3>
<!--config configuration setup settings administrate files custom customize-->
<p>
    The configuration file (called "config") is located in the 'Smart Planner' directory  has the following 
    json format: the keys and values include "course_info_filename": the course info file path, "alias_filename": 
    the path of the file used for aliasing old course numbers, "is_graphical": true or false (whether using a GUI 
    or CLI), "initial_schedule_name": The default name used for path exports, "normal_hours_limit": 18 by default, 
    "strong_hours_limit": the hours upper limit that must be enforced (30 by default), "strong_hours_minimum": the 
    hours lower limit that must be enforced (4 by default)
</p>
<h3>CLI Scheduling</h3>
<!-- generate run execute schedule create scheduling cli -->
<p>
    The program will begin execution in the GUI environment by default. Click 'Enter Command Line' to enter the 
    CLI. The user loads needed courses with syntax 'load [fileName]', where 'fileName' is the name of the 
    DegreeWorks PDF containing all path to graduation requirements. The user should verify the parameters of 
    the current configuration with the 'parameters' command, which will output the file destination, the maximum 
    hours per semester, and all loaded courses. Then, the user will generate a schedule with the 'schedule' 
    command, receiving a positive completion output message. The user can then access their schedule.
</p>
<h3>GUI Scheduling</h3>
<!-- graphical GUI schedule scheduling userstory -->
<p>
The program will begin execution in the GUI environment by default. If the user is currently in a CLI mode, enter 
the GUI with command 'gui-i'. Once the GUI is launched, the user will have access to the following parameters: 
load needed courses, set destination directory, set maximum hours per semester, set output format, and set output 
file name. The help button is also available to assist with program execution. Pressing the return key after 
entering the parameters is necessary. After the user modifies desired parameters, they press the 'generate schedule' 
button. The schedule is now generated.
</p>
<h3>Program Interface</h3>
<!-- graphical GUI CLI program view look interface -->
<p>
The program will begin execution in the GUI environment by default. If the user is currently in a CLI mode, the user 
can enter the GUI with command 'gui-i'. Entering 'cli' will configure the interface to open in command line 
interface mode by default. The same is the case with the “gui” command.
</p>
<h3>Validate Existing Path to Graduation</h3>
<!-- existing validate user submit path -->
<p>
    In order to assess a given path to graduation for correctness, the program must first have the relevant DegreeWorks 
    PDF as input. To validate an existing path to graduation in the GUI, the user first clicks the 'Verify Schedule' 
    button and selects the relevant DegreeWorks PDF. Then, if the Path to Graduation is valid, the program outputs 
    'path valid' and the confidence in the path. Otherwise, it outputs a list of the errors found in the path. The user 
    can also verify in the CLI by entering 'verify [filePath]'', where 'filePath' is the location of the Path to 
    Graduation Excel document.
</p>
<h3>AI Output Interpretation</h3>
<!-- ai es artificial intelligence expert system interpretation confidence -->
<p>
    After scheduling, the user will receive an output in the form of a decimal value between 0 and 100, where 0 reflects that
    the Expert System is very unconfident in the goodness of the Path to Graduation, and 100 reflects absolute confidence. All 
    Paths to Graduation are valid and satisfy CSU graduation requirements; this measure reflects a subjective judgment based 
    on rules provided by human scheduling experts.
</p>
<h3>Case Based Reasoning Overview</h3>
<!-- ai case based reasoning cbr overview elective scheduling assistance -->
<p>                
Case Based Reasoning (CBR) uses past experiences to solve new problems. Previous experiences are stored in the system as 
Problem-Solution pairs. In the instance of the SmartPlanner CBR, a Problem is a students degreeworks file (courses taken 
and courses needed) and the Solution is the recommended electives (specifically, higher level CPSC electives). A user will 
select their input file, and the CBR will retrieve the recommended electives that best fit the user's degree plan. Then, 
the user has the option to “Adapt” the solution to their specific situation (i.e., if the system recommended three electives, 
but the student only needs two). After adaptation, the user can select an output file to overwrite the blank electives slots 
filled by the Rule Based Scheduler. The system will automatically write the input file and adapted solution back into the Case 
Base to be used in the future.
</p>
<h3>Case Based Reasoning/Elective Recommendations - Step by Step</h3>
	<!-- ai case based reasoning cbr overview elective scheduling assistance -->
	<p>
		<ol id="cbr-steps-list">
			<li>Generate a schedule by using the SmartPlanner Rule Based Scheduler.</li>
			<li>Choose the “Run CBR for Elective Recommendations” option on the GUI main page.</li>
			<li>Once the CBR menu is opened, select “Run CBR” again.</li>
			<li>Choose the corresponding input file (same name as your degreeworks file) located in the directory 'CBR Inputs'. CBR will automatically run and show recommended electives in the display box.</li>
			<li>User can choose the 'Adapt elective recommendation' to tailor the recommendation more to their specific situation. New electives will be shown in the display box.</li>
			<li>The user can select "Give Reasoning for Recommendation” to show WHY the system recommended the retrieved electives.</li>
			<li>The user can finally select 'Choose output file' to find their scheduled path to graduation excel file created from the Rules Based Scheduler and overwrite the elective slots in said file.</li>
		</ol>
	</p>


<h3>Format of Course Info Input File</h3>
	<!-- format course info input columns -->
	<p>
		<ul id="format-course-info-file-list">
			<li>courseID: Unique identifier for courses.</li>
			<li>courseName: Common name for course.</li>
			<li>hours: Hours by semester.</li>
			<li>availability: When a course is offered during the year by season.</li>
			<li>prerequisites: Courses required to be taken before a given course. Uses a logic tree string to represent all possible ways to satisfy prerequisite requirements. See ‘README_DEV.md’ or module ‘Logic Tree Overview’ in this help module documentation for further details.</li>
			<li>co-requisites: Courses that must be taken concurrently with a given course. Stored like a prerequisite in a logic tree string.</li>
			<li>recommended: Courses recommended to take together.</li>
			<li>restrictions: Restrictions on when a course can be taken, ex: must be senior.</li>
			<li>note: Misc notes.</li>
			<li>importance: Importance that a class be taken sooner than other courses from 1 to 100. Previously implemented but deprecated pending future development.</li>
		</ul>
	</p>


<h3>Logic Tree Overview</h3>
	<!-- logic tree string node -->
	<p>
		A complex logic structure of predictable format must be created to represent the complex requirements presented by a student's 
		DegreeWorks PDF. The complex logic arises from choices that are presented to the student by the DegreeWorks PDF. For example, 
		a student may be able to satisfy a certain graduation requirement by taking one of several combinations of different courses. 
		By creating this logic string while parsing an input DegreeWorks PDF, the Smart Planner is able to represent any possible 
		variation of graduation requirements and process them for scheduling and user interaction. This data structure is also used to 
		represent pre and co-requisites in the 'Course Info.xlsx' file. For more details on this topic, see the 'README_DEV.md'.
	</p>


<h3>Navigating Requirements Tree</h3>
	<!-- logic tree node navigate requirements -->
	<p>
		After the logic tree string has been generated for a given DegreeWorks PDF, the user must be able to navigate the resulting 
		logical tree structure. The user enters the command “tree” from the main menu to enter the course selection menu. From the 
		course selection menu, the user navigates the structure of the tree by using the "show" command. "show-all" shows the entire 
		tree structure; “show-info [node]” shows the information for a given node. The user uses “move [node]”, “back”, “root”, and 
		“exit” to navigate. The “select [node]”, “deselect [node]”, “stub [node]”, and “unstub [node]” to change the selection and 
		stubbing status of the nodes. There are also administrative (can edit tree structure) and user modes (cannot edit tree structure) 
		that can be toggled with “admin” and “user” commands respectively. “Fill [node]” puts the user in the fill menu that fills out 
		protocol nodes. As an administrator, the “add-exhaustive”, “add-exhaustive”, “add-deliverable”, “add-protocol”, “add-shallow-count”, 
		“add-deep-count”, “add-deep-credit”, and “add-inserter” commands add new and empty nodes to the working node. The “delete [node]”, 
		“edit [node]”, “validate”, “copy [node]”, “cut [node]”, “paste” commands are also available. The user enters “commands” to see all 
		available commands. Note that all commands have a few aliases and shorthands. For more details on this topic, see the 
		'README_DEV.md'.
	</p>


<h3>Database Updating</h3>
	<!-- fetch update database excel course info xlsx storage web crawler crawling -->
	<p>
		Our program database is an Excel document called 'Course Info.xlsx' located in the '/src/input_files' directory. For a full list 
		of what the database contains, see the 'Format of Course Info Input File' section of this help module. Using the CLI and the 
		'fetch' command, the administrator can update the entire database with an automated web crawler, which scrapes all relevant 
		information from the Columbus State University website. This ensures that all course information is up to date. Because the 
		database stores the information for each department on a different Excel sheet, the administrator can choose to update only 
		select department information by entering command 'fetch [departmentNomenclature]'. Ex: 'fetch CPSC'. Reference the CSU website 
		at <a>https://catalog.columbusstate.edu/course-descriptions/</a> for a full list of department nomenclatures. This functionality is 
		not available via the GUI. It is advised that all departments are updated concurrently.
	</p>


<h3>Program Updates</h3>
	<!-- updates automatic version versioning  -->
	<p>
		The Smart Planner features automatic updates. When the program is launched, it will check the online repository for changes. 
		If changes are found, the user will be prompted to update the program accordingly. On the Windows OS, the Smart Planner will 
		install the new version of the software and close the program. On macOS, it will download a zip file containing the updated 
		executable to the user's downloads directory. The user must then extract the zip file and move it to their desired directory 
		for execution.
	</p>


<h3>Alias Module</h3>
	<!-- course alias update renamed rename xlsx -->
	<p>
		The University will periodically rename courses during curriculum refactors/updates. For example, 'CPSC 5150' could be renamed 
		to 'CPSC 4150'. As such, aliasing is required to prevent such changes from breaking the Smart Planner. To add a course to be 
		aliased after such a change, the administrator navigates to the 'alias.xlsx' file, puts the outdated course ID under the 'old_id' 
		column, and puts the updated course ID in the 'new_id' column.
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
        <td>Courses required to be taken before a given course. Uses a logic tree string to represent all possible ways to satisfy prerequisite requirements. See ‘README_DEV.md’ or module ‘Logic Tree Overview’ in this help module documentation for further details.</td>
    </tr>
    <tr>
        <td>co-requisites</td>
        <td>Courses that must be taken concurrently with a given course. Stored like a prerequisite in a logic tree string.</td>
    </tr>
    <tr>
        <td>recommended</td>
        <td>Courses recommended to take together.</td>
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
        <td>Importance that a class be taken sooner than other courses from 1 to 100. Previously implemented but deprecated pending future development.</td>
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

### Utilities:
* Module: 'general_utilities'
    * This module has basic definitions for constant and semester successors.
* Module: 'driver_fs_functions'
    * The driver_fs_functions provides high level functions for interfacing with the file system, including ready made path methods.
* Module: 'dataframe_io'
    * It contains helper functions for reading and writing pandas DataFrames.
* Module: 'alias_module'
    * This module updates course IDs as needed. The default file for construction is Aliases.xlsx.
* Module: 'configuration_manager'
    * It handles reading and writing for easy program configuration through a JSON file.

### Scheduling:
* Module: 'scheduler_driver'
    * It contains the constructive scheduler, which uses a greedy algorithm to generate a valid or nearly valid Path To Graduation. The genetic optimizer works over greedy and applies a genetic algorithm, which bases its outputs on the highest possible confidence factor. 

* Module: 'expert_system_module'
    * This is a rules based expert system that judges the fitness of the schedule using soft rules. 

* Module: 'schedule_inspector'
    * The schedule_inspector applies soft rules to the generated schedule. Most of the rules consist of high level and low level courses being scheduled in the same semester or too close together.  

* Module: 'scheduling_parameters_container'
    * It has containers that store all of the needed information for the scheduler to run and export given a DegreeExtractionContainer.  
	
* Module: 'user_submitted_validator'
    * The user_submitted_validator provides functions for determining the validity for a schedule/Path To Graduation.

### Not in Use:
* batch_configuration
* batch_process
* batch_process_schedules
* batch_validation
* program_generated_evaluator
* scheduler_driver_testing

### Deprecated:
* degreeworks_parser
* scheduler
* catalog_parser
* course_info_parser
* scheduling_assistant

### CBR Contents:
* Non-Python Files:
    * CBR Inputs – sample input files, contains courses and gpa
    * Case Base – similar to input files, contains courses and gpa of cases. These have a solution (I.e, recommended electives) that is present in the solutions text file
    * Solutions.txt – solutions to the respective case base files
* Python Files:
    * adaptation.py – adaptation module. Fits retrieved electives to input case. In other words, if a student needs only two electives but the closest case recommends three, it will ask for a case to be removed and edit the Result object accordingly. Input is handled by the Adaptation Window in graphical_interface.py
    * case_creator.py – fetches the data from the cbr_parser and uses the Case class to create case objects
    * Case.py – Case class used to store case file_nae, gpa, and course_list (note, this is the entire courses needed list)
    * cbr_driver.py – when in stand alone, this acts as the main menu and driver. When integrated, it calls the function to run the CBR and give reasoning for the recommended case.
    * cbr_excel_output_hanlder – simple excel overwriter. Currently, I have it so the CBR just overwrites the excel file outputted by the scheduler directly. Looks for Course XXXX – NAME UNAVAILABLE and replaces that cell data with the recommended electives
    * cbr_parser – parses the text files in the case base / input folder and sends information to the case_creator module
    * graphical_interface.py – added two new windows to this file, Adaptation and CBR Main Menu
    * insertion.py – used to insert the input case with recommended solution back into the case base. Currently not integrated due to testing and demonstration reasons. Given the small size of the  * input case base, you would have to manually delete the solutions from the case base to re-demo the system
    * output_fetch.py – acts as a middle man between CBR driver and similarity-measure class. Calls similarity_measure functions and creates/returns a Result type object to the cbr_driver
    * Result.py – Result class that holds target Case object, retrieved Case object, recommended electives, and the similarity measure. NOTE: These are case objects, so you can call getters on these (eg, get filename, get gpa, etc)
    * similarity_measure.py – runs the similarity function to compare how similar cases are. Currently, the highest weighted feature is GPA, followed by how many “programming courses” have been taken (1301, 1302, 2108 are the specific ones).
    * program_driver – added a Result variable to the constructor. New functions are down at the very bottom under the James CBR stuff comment
    * PDF_to_CBR_Formatter – takes parsed info from the degreeworks parser and uses it to create a text file that is easily read by the CBR


## Known Bugs
1. The DegreeWorks parser is currently somewhat tightly coupled to the 
sample inputs that the Smart Planner team was initially given. Parsing 
live DegreeWorks documents will take minor refactoring/reworking of the 
DegreeWorks parsing module. For example, assumptions were made about the 
ability to rely on key phrases as 'backstops' to trim course names. As 
those key phrases appear differently in the real DegreeWorks than they did 
in sample inputs, new key phrases would need to be added.

## Further Resources
The help file located in the program explains more of the system behavior in plain language. This document is intended as a technical overview rather than a how-to. The SmartPlanner Github page is also updated regularly with release notes, history etc. Separate from this document is the README file intended for the average user. Like the Help page, this file will explain system behavior in a more digestible way. 
