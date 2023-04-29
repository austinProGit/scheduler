# Smart Planner

[v2.0.1 Release Notes](https://github.com/austinProGit/scheduler/releases/latest)

A program to assist with scheduling a student's university courses.

![Preview](https://github.com/austinProGit/scheduler/blob/main/preview.JPG)

## Downloads
[smart-planner-setup-2.0.1.exe](https://github.com/austinProGit/scheduler/releases/download/v2.0.1/smart-planner-setup-2.0.1.exe) Platform: Windows  
[SmartPlanner-2.0.1 executable (zip)](https://github.com/austinProGit/scheduler/releases/download/v2.0.1/SmartPlanner-2.0.1.zip) Platform: macOS  
[Source code (zip)](https://github.com/austinProGit/scheduler/archive/refs/tags/v2.0.1.zip)  
[Source code (tar.gz)](https://github.com/austinProGit/scheduler/archive/refs/tags/v2.0.1.tar.gz)

## Installation
### Standard (Currently only available for Windows)
* Download the [installer](https://github.com/austinProGit/scheduler/releases/download/v2.0.1/smart-planner-setup-2.0.1.exe) and double-click to launch the installation wizard

*Note: Antivirus software will warn against downloading and launching the installer since we are not a known publisher*

### Zip file (Recommended for macOS)
* Download the [SmartPlanner](https://github.com/austinProGit/scheduler/releases/download/v2.0.1/SmartPlanner-2.0.1.zip) zip file
* Unzip and click on the SmartPlanner executable to launch the program

### Using the command line (Developer option)
This option requires that Python3 version 3.8 to be installed on the computer that will run the scheduler program. 
All program dependencies are found in requirements.txt. The user must have python (and pip) installed. To install the dependencies,
the user can use the terminal command 'pip install -r requirements.txt'. After the aforementioned installation is complete, entering
'python main.py' or 'python3 main.py' (depending on OS) from the terminal will launch the program. This can be done my moving to the
src directory or by just entering the path of the main file. The program will then lauch in either CLI or GUI mode.



## Project Description
### System metaphor
Administrators configure the scheduler for use by Students, who input 
their needed courses and Course Path/Info to generate their by-semester Path to Graduation.	
Students at Columbus State University are often challenged to correctly schedule their course Path to Graduation. 
The task of scheduling courses is complex. Course availability varies by course and semester. Moreover, both 
prerequisites and corequisites must be properly accounted for during the scheduling process. Should a student fail 
to complete their Path to Graduation properly, they risk delaying their graduation by semesters or even years. 
Furthermore, if a student fails a course, the student’s Path to Graduation must be recalculated. Manual construction 
of students’ Path to Graduation has proved unreliable; therefore, a more automated approach to scheduling is necessary.
The program that we design to solve this problem must accept the following as inputs: the courses that a student 
still must take prior to graduation, that student’s chosen major/track, the semesters that courses are offered, the 
prerequisites and corequisites for all courses, the required electives that the student wishes to take, and the maximum 
hours that the student is willing to take per semester. The output of the scheduler program must be a valid schedule 
that incorporates all aforementioned inputs. 

Our software is flexible and includes a robust Command Line Interface (CLI) that provides numerous commands and parameter 
options like. load <needed courses>, load-e (with file explorer), destination <output directory>, destination-e, set-hours 
<maximum hours per semester>, set-exports, parameters, schedule <output filename>, verify <schedule filename>, verify-e, 
help <keywords>, quit, etc. Because our program uses an excel document as its database, configuration of course offering 
information is familiar for any system administrator. For users unfamiliar with the command line, we provide a Graphical User Interface (GUI). For seamless future use, our software implements a web crawler that 
draws the most up-to-date course information from Columbus State University’s official website. Lastly, we automatically 
check for invalid inputs (including unsatisfiable prerequisite requirements), providing our users confidence in the 
validity of their computed path to graduation. Our software also incorporates an Expert System Artificial Intelligence module
that assesses a scheduled path to graduation and provides the user with an evaluation that simulates the objective or 
opinionated assessment that an expert (an academic advisor) would provide a student during an advising session. 

## Manual

### Administrator Familiarization and Program Configuration
fter launching, the administrator accesses the help menu with command 'help'. On the help menu, 
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
  
### Load Needed Courses
To generate a schedule, the Smart Planner requires a valid DegreeWorks PDF from a student's DegreeWorks 
		portal as an input. To load needed courses via the GUI, the user can click 'Open Needed Courses', then 
		select the DegreeWorks PDF, then click 'Open'. To load needed courses via the CLI, the administrator can 
		either enter "load [fileName]" where 'fileName' is the local or absolute path, or enter "load-e" to open a file browser.
  
### Set the Number of Hours Per Semester
To set the number of credit hours per semester, enter "hours[number]" where 'number' is the desired number 
		of hours per Fall or Spring semesters. Optionally, the user can enter the “summer-hours [number]” command to 
		set the hours per Summer semester.
  
### Adjusting Configuration Data
The configuration file (called "config") is located in the 'Smart Planner' directory  has the following 
		json format: the keys and values include "course_info_filename": the course info file path, "alias_filename": 
		the path of the file used for aliasing old course numbers, "is_graphical": true or false (whether using a GUI 
		or CLI), "initial_schedule_name": The default name used for path exports, "normal_hours_limit": 18 by default, 
		"strong_hours_limit": the hours upper limit that must be enforced (30 by default), "strong_hours_minimum": the 
		hours lower limit that must be enforced (4 by default)
  
### CLI Scheduling
The program will begin execution in the GUI environment by default. Click 'Enter Command Line' to enter the CLI. The user loads needed courses with syntax 'load [fileName]', where 'fileName' is the name of the DegreeWorks PDF containing all path to graduation requirements. The user should verify the parameters of the current configuration with the 'parameters' command, which will output the file destination, the maximum hours per semester, and all loaded courses. Then, the user will generate a schedule with the 'schedule' command, receiving a positive completion output message. The user can then access their schedule.

### GUI Scheduling
The program will begin execution in the GUI environment by default. If the user is currently in a CLI mode, enter 
	the GUI with command 'gui-i'. Once the GUI is launched, the user will have access to the following parameters: 
	load needed courses, set destination directory, set maximum hours per semester, set output format, and set output 
	file name. The help button is also available to assist with program execution. Pressing the return key after 
	entering the parameters is necessary. After the user modifies desired parameters, they press the 'generate schedule' 
	button. The schedule is now generated.
 
### Program Interface
The program will begin execution in the GUI environment by default. If the user is currently in a CLI mode, the user 
	can enter the GUI with command 'gui-i'. Entering 'cli' will configure the interface to open in command line 
	interface mode by default. The same is the case with the “gui” command.
 
### Validate Existing Path to Graduation
In order to assess a given path to graduation for correctness, the program must first have the relevant DegreeWorks 
		PDF as input. To validate an existing path to graduation in the GUI, the user first clicks the 'Verify Schedule' 
		button and selects the relevant DegreeWorks PDF. Then, if the Path to Graduation is valid, the program outputs 
		'path valid' and the confidence in the path. Otherwise, it outputs a list of the errors found in the path. The user 
		can also verify in the CLI by entering 'verify [filePath]'', where 'filePath' is the location of the Path to 
		Graduation Excel document.

### AI Output Interpretation
After scheduling, the user will receive an output in the form of a decimal value between 0 and 100, where 0 reflects that
		the Expert System is very unconfident in the goodness of the Path to Graduation, and 100 reflects absolute confidence. All 
		Paths to Graduation are valid and satisfy CSU graduation requirements; this measure reflects a subjective judgment based 
		on rules provided by human scheduling experts.

 ### Case Based Reasoning (CBR) Description
Case Based Reasoning – Overview
 
Case Based Reasoning (CBR) uses past experiences to solve new problems. Previous experiences are stored in the system as Problem-Solution pairs. In the instance of the SmartPlanner CBR, a Problem is a studnets degreeworks file (courses taken and courses needed) and the Solution is the recommended electives (specifically, higher level CPSC electives). A user will select their input file, and the CBR will retrieve the recommended electives that best fit the user’s degree plan. Then, the user has the option to “Adapt” the solution to their specific situation (i.e., if the system recommended three electives, but the student only needs two). After adaptation, the user can select an output file to overwrite the blank electives slots filled by the Rule Based Scheduler. The system will automatically write the input file and adapted solution back into the Case Base to be used in the future.

Case Based Reasoning – Step by Step
 
    • Generate a schedule by using the SmartPlanner Rule Based Scheduler 
    • Choose the “Run CBR for Elective Recommendation” option on the GUI main page 
    • Once the CBR menu is opened, select “Run CBR” again
    • Choose the corresponding input file (same name as your degreeworks) located in the directory ‘CBR Inputs”
    • CBR will automatically run, and show recommended electives in the display box
    • User can choose the ‘Adapt elective recommendation” to cater the recommendation more to their specific situation 
    • New electives will be shown in the display box. 
    • User can select ‘Give Reasoning for Recommendation” to show WHY the system recommended the retrieved electives.
    • User can finally select ‘Choose output file” to find their excel file created from the Rules Based Scheduler and overwrite the elective slots in said excel file

<h3>Format of Course Info Input File</h3>
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
<p>
 A complex logic structure of predictable format must be created to represent the complex requirements presented by a student's 
 DegreeWorks PDF. The complex logic arises from choices that are presented to the student by the DegreeWorks PDF. For example, 
 a student may be able to satisfy a certain graduation requirement by taking one of several combinations of different courses. 
 By creating this logic string while parsing an input DegreeWorks PDF, the Smart Planner is able to represent any possible 
 variation of graduation requirements and process them for scheduling and user interaction. This data structure is also used to 
 represent pre and co-requisites in the 'Course Info.xlsx' file. For more details on this topic, see the 'README_DEV.md'.
</p>

<h3>Navigating Requirements Tree</h3>
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
<p>
 The Smart Planner features automatic updates. When the program is launched, it will check the online repository for changes. 
 If changes are found, the user will be prompted to update the program accordingly. On the Windows OS, the Smart Planner will 
 install the new version of the software and close the program. On macOS, it will download a zip file containing the updated 
 executable to the user's downloads directory. The user must then extract the zip file and move it to their desired directory 
 for execution.
</p>

<h3>Alias Module</h3>
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

## Further Resources
Once the program installed, there is a "Help" button that will link to a webpage describing system behavior, step-by-step instruction, all in plain language. There is also a README file intended for devlopers who wish to continue the SmartPlanner project. 
