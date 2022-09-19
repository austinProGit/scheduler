# Thomas Merino
# 9/19/22
# CPSC 4175 Group Project

# NOTE: you will need to install QT PySide6 to use this.

# TO THOSE INTERESTED: place YES as the second line of the "config" file to try out the GUI. This has fewer features right now, but it should give you a taste of what QT can provide (or least the minimum). I would still need to add labels and instructions, of course.

# TODO: Finish the QT UI
# TODO: Add testing.
# TODO: Maybe add help
# TODO: Create the driver-level interface for getting item selection (e.g. for selecting electives)
# TODO: Shorten the name of long directories (for display purposes).


from PySide6 import QtCore, QtWidgets, QtGui
from os import path
from pathlib import Path

## --------------------------------------------------------------------- ##
## ---------------------- Graphical User Interface --------------------- ##
## --------------------------------------------------------------------- ##

# This is the window for presenting the all graphical UI
class MainProgramWindow(QtWidgets.QMainWindow):
    
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle('Smart Planner')
        self.widget = MainMenuWidget(controller)
        self.setCentralWidget(self.widget)
        

# This is a subclass of the QT text field that clears when focus is changed or the user presses enter/return
class TextField(QtWidgets.QLineEdit):
    
    def focusOutEvent(self, event):
        '''Custom override of QLineEdit's focusOutEvent that clears text.'''
        super().focusOutEvent(event)
        self.clear()


# Graphical interface for the main menu
class MainMenuWidget(QtWidgets.QWidget):

    def __init__(self, controller):
        super().__init__()                      # Call the super's initialization
        
        self.controller = controller
        
        # Create a label for presenting recent messages
        self.message_label = QtWidgets.QLabel('Welcome to Smart Planner')
        
        # Create a button to load the needed courses file
        self.needed_courses_load_label = QtWidgets.QLabel('*No needed courses file loaded*')
        self.needed_courses_load_button = QtWidgets.QPushButton('Open Needed Courses')
        self.needed_courses_load_button.clicked.connect(self._needed_courses_load_callback)

        # Create a text field that sets hours per semester after pressing enter/return
        self.hours_per_semester_label = QtWidgets.QLabel("Hours per semester:")
        self.hours_per_semester_field = TextField()
        self.hours_per_semester_field.setValidator(QtGui.QIntValidator())
        self.hours_per_semester_field.returnPressed.connect(self._hours_per_semester_callback)
        self.hours_per_semester_field.setPlaceholderText(str(self.controller.get_hours_per_semester()))

        # Create a button to select the working directory for output
        self.destination_directory_label = QtWidgets.QLabel('*No destination directory selected*')
        self.set_destination_label(self.controller.get_destination_directory())
        self.change_directory_button = QtWidgets.QPushButton('Change Directory')
        self.change_directory_button.clicked.connect(self._change_directory_callback)

        # Create a text field that set the schedule's name after pressing enter/return
        self.schedule_name_label = QtWidgets.QLabel("Schedule name:")
        self.schedule_name_field = TextField()
        self.schedule_name_field.returnPressed.connect(self._schedule_name_callback)
        self.schedule_name_field.setPlaceholderText(self.controller.get_destination_filename())
        
        # Create a button that generate's the schedule
        self.generate_schedule_button = QtWidgets.QPushButton('Generate Schedule')
        self.generate_schedule_button.clicked.connect(self._generate_schedule_callback)
        

        # Create a basic layout
        self.layout = QtWidgets.QFormLayout(self)
        self.layout.addWidget(self.message_label)
        self.layout.addRow(self.needed_courses_load_label, self.needed_courses_load_button)
        self.layout.addRow(self.hours_per_semester_label, self.hours_per_semester_field)
        self.layout.addRow(self.destination_directory_label, self.change_directory_button)
        self.layout.addRow(self.schedule_name_label, self.schedule_name_field)
        self.layout.addWidget(self.generate_schedule_button)
        
        
    def set_needed_courses_label(self, filename):
        description = Path(filename).stem
        self.needed_courses_load_label.setText('Needed Courses: {0}'.format(description))
                
    def _needed_courses_load_callback(self):
        print('_needed_courses_load_callback')
        file_loader_dialog = QtWidgets.QFileDialog()
        file_loader_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        #dlg.setFilter(PySide6.QtCore.QDir.)
        filename = None

        if file_loader_dialog.exec():
            filename = file_loader_dialog.selectedFiles()[0]
            load_success = self.controller.load_courses_needed(filename)
            if load_success:
                # TODO: Test this for absolute and relative paths
                self.set_needed_courses_label(filename)
        if filename == None:
            self.controller.output('Load cancelled.')
        
    def _hours_per_semester_callback(self):
        print('_hours_per_semester_callback')
        try:
            number = int(self.hours_per_semester_field.text())      # Attempt to cast the input to an integer
            self.controller.configure_hours_per_semester(number)    # If successful, set the number of
            self.hours_per_semester_field.setPlaceholderText(str(self.controller.get_hours_per_semester()))
        except ValueError:
            # The argument was not valid (report to the user)
            self.controller.output('Sorry, that is not a valid input (please use a number).')
        self.hours_per_semester_field.clear()
        self.hours_per_semester_field.clearFocus()
        
            
    def set_destination_label(self, directory_name):
        description = Path(directory_name).stem
        self.destination_directory_label.setText('Destination Directory: {0}'.format(description))
                
    def _change_directory_callback(self):
        print('_change_directory_callback')
        file_loader_dialog = QtWidgets.QFileDialog()
        file_loader_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        directory_name = None
        
        if file_loader_dialog.exec():
            directory_name = file_loader_dialog.selectedFiles()[0]
            self.controller.configure_destination_directory(directory_name)
            self.set_destination_label(self.controller.get_destination_directory())
        if directory_name == None:
            self.controller.output('Load cancelled.')
        
        
    def _schedule_name_callback(self):
        self.controller.configure_destination_filename(self.schedule_name_field.text().strip())
        self.schedule_name_field.clear()
        self.schedule_name_field.clearFocus()
        self.schedule_name_field.setPlaceholderText(self.controller.get_destination_filename())
        
    
    def _generate_schedule_callback(self):
        print('_generate_schedule_callback')
        self.controller.generate_schedule(path.join(self.controller.get_destination_directory(),
                                                    self.controller.get_destination_filename()))
        self.message_label.setText('Schedule Generated')
        self.controller.enter_error_menu()
    
