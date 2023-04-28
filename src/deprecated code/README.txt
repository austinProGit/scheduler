Version: 1.0

    Project Description:System metaphor: Administrators configure the scheduler for use by Students, who input 
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
information is simple and familiar for any system administrator. For users unfamiliar with the command line, we provide a 
simple, user-friendly Graphical User Interface (GUI). For seamless future use, our software implements a web crawler that 
draws the most up-to-date course information from Columbus State University’s official website. Lastly, we automatically 
check for invalid inputs (including unsatisfiable prerequisite requirements), providing our users confidence in the 
validity of their computed path to graduation. Our software also incorporates an Expert System Artificial Intelligence module
that assesses a scheduled path to graduation and provides the user with an evaluation that simulates the objective or 
opinionated assessment that an expert (an academic advisor) would provide a student during an advising session. 

Manual:

Launching
This project requires that Python3 version 3.8 or above and Java be installed on the computer that will run the scheduler program. 
All program dependencies are found in requirements.txt. The user must have python (and pip) installed. To install the dependencies,
the user can use the terminal command 'pip install -r requirements.txt'. After the aforementioned installation is complete, entering
'python main.py' or 'python3 main.py' (depending on OS) from the terminal will launch the program. This can be done my moving to the
src directory or by just entering the path of the main file. The program will then lauch in either CLI or GUI mode.

CLI Scheduling
From the command line, user launches main.py. User loads needed courses with syntax ‘load fileName’. The user should verify 
the parameters of the current configuration with the parameters command, syntax ‘parameters’, which will output the file 
destination, the maximum hours per semester, and all loaded courses. Then, the user will generate a schedule with the ‘schedule’
command, receiving a positive completion output message. The user can then access their schedule.

GUI Scheduling
From the command line, user launches main.py. If the program has been previously configured to open immediately to the GUI, 
then the GUI will launch automatically. If not, the user will then enter ‘gui-i’ to launch the GUI. Once the GUI is launched, 
the user will have access to the following parameters: load needed courses, set destination directory, set maximum hours per 
semester, set output format, and set output file name. After the user modifies desired parameters, they press the ‘generate 
schedule’ button. The schedule is now generated.
 
Scheduling with bad Course Information Input
The administrator has configured the program with a prerequisite that is definitionally unsatisfiable. As soon as the user 
launches the program, the user is notified that the catalog contains invalid data and is then redirected to an error menu. 
The user must seek the administrator’s assistance in creating a valid course information input. Once in the error menu, the 
administrator has the option to create a new default configuration file or attempt to reload. The user cannot access the GUI 
if there is an error.

Administrator Familiarization and Configuration
After launching, the administrator accesses the help menu with command ‘help’. On the help menu, the administrator sees a 
prompt to search by keywords for help articles. The administrator decides to instead see all help articles by entering the 
command ‘all’. The administrator learns about the main functions of the program, including loading courses needed, generating 
the hours, selecting the schedule export types, and many other functions. The administrator then begins configuration. The 
administrator configures the courses by editing the Course Info excel file. The administrator then changes the source directory 
for the Course Info file as desired by editing the config file. Next, the administrator sets the output format with the 
commands ‘exports [exportNum]’. Next, the administrator configures the destination path with the command ‘destination [path]’. 
The administrator then sets the default user interface to GUI with command ‘gui’. The program is now configured for student use.
 
User Submits Path to Graduation for Verification
User launches program in CLI and enters ‘verify [filePath]’, where filePath is the location of the Path to Graduation. If the 
Path to Graduation is valid, the program outputs ‘path valid’. Otherwise, it outputs a list of the errors found in the path.

Batch Processing
The administrator has a folder containing all of the Courses Needed PDF files. The admin enters the destination directory with 
command ‘destination [path]’. Then, he begins batch process execution with command ‘batch [directoryOfNeededCourseFiles],
[destinationDirectoryName]’. Valid results will be found in the destination folder. Invalid inputs will result in no corresponding
output, and an error message will be displayed.

AI Output Interpretation
After scheduling, the user will receive an output in the form of a decimal value between 0 and 1, where 0 reflects that the 
Expert System is very unconfident in the goodness of the Path to Graduation, and 1 reflects absolute confidence. All Path to 
Graduation are valid and satisfy CSU graduation requirements; this measure reflects a subjective judgment based on rules provided 
by human scheduling experts.
