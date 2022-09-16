# Thomas Merino
# 9/16/22
# CPSC 4175 Group Project

# NOTE: you will need to install QT PySide6 to use this.

# TO THOSE INTERESTED: place YES as the second line of the "config" file to try out the GUI. This has fewer features right now, but it should give you a taste of what QT can provide (or least the minimum). I would still need to add labels and instructions, of course.

# TODO: Finish the QT UI
# TODO: Add testing.
# TODO: Maybe make the name of the help file included in config
# TODO: Ensure exception raising is implemented in other modules (e.g. NonDAGCourseInfoError)
# TODO: Create the driver-level interface for getting item selection (e.g. for selecting electives)

from PySide6 import QtCore, QtWidgets, QtGui
from os import getcwd, path

## --------------------------------------------------------------------- ##
## ---------------------- Graphical User Interface --------------------- ##
## --------------------------------------------------------------------- ##


# This is a subclass of the QT text field that clears when focus is changed or the user presses enter/return
class TextField(QtWidgets.QLineEdit):
    
    def focusOutEvent(self, event):
        '''Custom override of QLineEdit's focusOutEvent that clears text.'''
        super().focusOutEvent(event)
        self.clear()

# Graphical interface for the main menu
class MainMenuWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()                      # Call the super's initialization
        self.working_directory = getcwd()       # Get the program's working directory and set it as the output directory

        # Create a label for presenting recent messages
        self.message_label = QtWidgets.QLabel('Welcome to Smart Planner')
        
        # Create a button to load the needed courses file
        self.needed_courses_load_button = QtWidgets.QPushButton('Load Needed Courses')
        self.needed_courses_load_button.clicked.connect(self._needed_courses_load_callback)

        # Create a text field that sets hours per semester after pressing enter/return
        self.hours_per_semester_field = TextField()
        self.hours_per_semester_field.setValidator(QtGui.QIntValidator())
        self.hours_per_semester_field.returnPressed.connect(self._hours_per_semester_callback)

        # Create a button to select the working directory for output
        self.change_directory_button = QtWidgets.QPushButton('Change Directory')
        self.change_directory_button.clicked.connect(self._change_directory_callback)

        # Create a text field that generate's the schedule after pressing enter/return
        self.generate_schedule_field = TextField()
        self.generate_schedule_field.returnPressed.connect(self._generate_schedule_callback)
        self.generate_schedule_field.setPlaceholderText('Schedule Name')

        # Create a basic layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.message_label)
        self.layout.addWidget(self.needed_courses_load_button)
        self.layout.addWidget(self.hours_per_semester_field)
        self.layout.addWidget(self.change_directory_button)
        self.layout.addWidget(self.generate_schedule_field)
        
                
    def _needed_courses_load_callback(self):
        print('_needed_courses_load_callback')
        file_loader_dialog = QtWidgets.QFileDialog()
        file_loader_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        #dlg.setFilter(PySide6.QtCore.QDir.)
        filename = None

        if file_loader_dialog.exec():
            filename = file_loader_dialog.selectedFiles()[0]
            self.controller.load_courses_needed(filename)
        if filename == None:
            self.controller.output('Load cancelled.')
        
    def _hours_per_semester_callback(self):
        print('_hours_per_semester_callback')
        try:
            number = int(self.hours_per_semester_field.text())      # Attempt to cast the input to an integer
            self.controller.configure_hours_per_semester(number)    # If successful, set the number of
        except ValueError:
            # The argument was not valid (report to the user)
            self.controller.output('Sorry, that is not a valid input (please use a number).')
        self.hours_per_semester_field.setPlaceholderText(self.hours_per_semester_field.text())
        self.hours_per_semester_field.clear()
        self.hours_per_semester_field.clearFocus()
        
        
    def _change_directory_callback(self):
        print('_change_directory_callback')
        file_loader_dialog = QtWidgets.QFileDialog()
        file_loader_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        directory_name = None

        if file_loader_dialog.exec():
            directory_name = file_loader_dialog.selectedFiles()[0]
            self.working_directory = directory_name
        if directory_name == None:
            self.controller.output('Load cancelled.')
        
    def _generate_schedule_callback(self):
        print('_generate_schedule_callback')
        self.controller.generate_schedule(path.join(self.working_directory, self.generate_schedule_field.text()))
        
        self.generate_schedule_field.clear()
        self.generate_schedule_field.clearFocus()
                
        self.message_label.setText('Schedule Generated')
    
