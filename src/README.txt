Version: Pre-Beta

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
validity of their computed path to graduation.

Manual:

How to Load Needed Courses
In order for Smart Planner to generate a schedule, it needs the a list of courses required before graduation. Courses 
should be listed in a PDF document. To load the courses into the program you can either enter "load FILENAME" where 
FILENAME is the local or absolute path, or enter "browse" to open a file browser.

How to Generate a Schedule
To generate a schedule, first make sure all needed courses are loaded and all scheduling parameters are set correctly 
(see other help pages for more information). Then, enter "schedule FILENAME" where FILENAME is the name of the output file.

How to Set the Number of Hours Per Semester
To set the number of credit hours per semester, enter "hours NUMBER" where NUMBER is the desired number of hours per semester.

Adjusting Configuration Data
The configuration file (called "config") has the following format: the first line is the filename of the catalog file. 
This is expected to be an xslx file in the working directory and follows the format in the instruction manual (see manual). 
The second line is whether the program launches in GUI mode (either "YES" or "NO").