# Thomas Merino
# 9/21/22
# CPSC 4175 Group Project


# TO THOSE INTERESTED: place YES as the second line of the "config" file to try out the GUI. This has fewer features right now, but it should give you a taste of what QT can provide (or least the minimum). I would still need to add labels and instructions, of course.

# TODO: Maybe add help

# TODO: Add testing.
# TODO: Add drag and drop support
# TODO: Implement weakref into the GUI widgets to prevent strong reference cycles
# TODO: Maybe move the message label to the bottom

# TODO: Shorten the name of long directories/fillenames (for display purposes).
# TODO: Needed courses label does not source from the data model (fix)
# TODO: Finish the QT UI
# TODO: Add some meaningful comments/documentation

from PySide6 import QtCore, QtWidgets, QtGui
from os import path
from pathlib import Path
import weakref

# TODO: Add these to a constants file so they are not defined in both driver and here
PATH_TO_GRADUATION_EXPORT_TYPE = 0x00
PLAIN_TEXT_EXPORT_TYPE = 0x01

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
        
        # Set the controller's listeners to two of widget's output handlers
        controller.set_output_listener(self.widget.receive_process_output)
        controller.set_warning_listener(self.widget.receive_process_warning)
        

# This subclass of the QT text field clears its contenct when focus is changed or the user presses enter/return
# --this changes the contents to the placeholder text.
class TextField(QtWidgets.QLineEdit):
    
    def focusOutEvent(self, event):
        '''Custom override of QLineEdit's focusOutEvent that clears text.'''
        super().focusOutEvent(event)    # Invoke the super's implementation
        self.clear()                    # Remove all text (use splaceholder text)


# Graphical interface for the main menu
class MainMenuWidget(QtWidgets.QWidget):

    def __init__(self, controller):
        # Call the super's initialization
        super().__init__()
        
        # Initialize a reference to the program's controller
        self.controller = controller
        
        # Create a label for presenting recent messages
        self.message_label = QtWidgets.QLabel('Welcome to Smart Planner')
        self.message_label.setWordWrap(True)
        
        # Initialize the scheduling parameter widgets
        # This does not add them; it just initializes them and saves them as instance variables
        self.initialize_parameter_widgets()
        
        # Create a button that generate's the schedule
        self.generate_schedule_button = QtWidgets.QPushButton('Generate Schedule')
        self.generate_schedule_button.clicked.connect(self._generate_schedule_callback)
        
        # Create a horizontal box layout
        # This will hold scheduling parametes on the left and information on the right
        self.layout = QtWidgets.QHBoxLayout(self)
        
        # Create the form area for presenting the message label, parameters, scheduling button, etc.
        self.interaction_area = QtWidgets.QFormLayout()
        
        self.interaction_area.addWidget(self.message_label)
        self.interaction_area.addRow(self.needed_courses_load_label, self.needed_courses_load_button)
        self.interaction_area.addRow(self.hours_per_semester_label, self.hours_per_semester_field)
        self.interaction_area.addRow(self.destination_directory_label, self.change_directory_button)
        self.interaction_area.addWidget(self.path_to_graduation_checkbox)
        self.interaction_area.addWidget(self.plain_text_checkbox)
        self.interaction_area.addRow(self.schedule_name_label, self.schedule_name_field)
        self.interaction_area.addWidget(self.generate_schedule_button)
        
        # Add the form area to the horizontal box
        self.layout.addLayout(self.interaction_area)
        
    def initialize_parameter_widgets(self):
        '''Setup the widgets for scheduling parameters. This does not add them; it just initializes them
        and saves them as instance variables.'''
            
        # Create a button to load the needed courses file
        self.needed_courses_load_label = QtWidgets.QLabel('*No needed courses file loaded*')
        self.needed_courses_load_button = QtWidgets.QPushButton('Open Needed Courses')
        self.needed_courses_load_button.clicked.connect(self._needed_courses_load_callback)
        
        # Create a text field that sets hours per semester after pressing enter/return
        self.hours_per_semester_label = QtWidgets.QLabel('Hours per semester:')
        self.hours_per_semester_field = TextField()
        self.hours_per_semester_field.setValidator(QtGui.QIntValidator())
        self.hours_per_semester_field.returnPressed.connect(self._hours_per_semester_callback)
        self.hours_per_semester_field.setPlaceholderText(str(self.controller.get_hours_per_semester()))
        
        # Create a button to select the working directory for output
        self.destination_directory_label = QtWidgets.QLabel('*No destination directory selected*')
        self.set_destination_label(self.controller.get_destination_directory())
        self.change_directory_button = QtWidgets.QPushButton('Change Directory')
        self.change_directory_button.clicked.connect(self._change_directory_callback)
        
        # Create checkboxes for controlling the output types to generate
        self.path_to_graduation_checkbox = QtWidgets.QCheckBox('Export Path to Graduation Excel')
        self.path_to_graduation_checkbox.setChecked(self.controller.is_using_export_type(PATH_TO_GRADUATION_EXPORT_TYPE))
        self.path_to_graduation_checkbox.toggled.connect(self._toggle_export_type_callback)
        self.plain_text_checkbox = QtWidgets.QCheckBox('Export Simple txt')
        self.plain_text_checkbox.setChecked(self.controller.is_using_export_type(PLAIN_TEXT_EXPORT_TYPE))
        self.plain_text_checkbox.toggled.connect(self._toggle_export_type_callback)
        
        # Create a text field that set the schedule's name after pressing enter/return
        self.schedule_name_label = QtWidgets.QLabel('Schedule name:')
        self.schedule_name_field = TextField()
        self.schedule_name_field.returnPressed.connect(self._schedule_name_callback)
        self.schedule_name_field.setPlaceholderText(self.controller.get_destination_filename())
        
            
    def receive_process_output(self, message):
        '''Method to use for output listening. This methods just updates the message label.'''
        self.message_label.setText(message)
        
                
    def receive_process_warning(self, message):
        '''Method to use for warning listening. This methods presents a warning message box with the passed message.'''
        message_box = QtWidgets.QMessageBox()
        message_box.setIcon(QtWidgets.QMessageBox.Warning)
        message_box.setText(message)
        message_box.exec()
        
    def set_needed_courses_label(self, filename):
        description = Path(filename).stem
        self.needed_courses_load_label.setText('Needed Courses: {0}'.format(description))
                
    def _needed_courses_load_callback(self):
        
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
        '''Callback for when enter/return is pressed while editing the hours per semester text field.'''
        
        hours_text = self.hours_per_semester_field.text()
        
        if hours_text.isdigit():
            number = int(hours_text)                                # Cast the input to an integer
            self.controller.configure_hours_per_semester(number)    # Set the number of hours per semester
            self.hours_per_semester_field.setPlaceholderText(str(self.controller.get_hours_per_semester()))
        else:
            # The argument was not valid (report to the user)
            self.controller.output('Sorry, that is not a valid input (please use a number).')
        self.hours_per_semester_field.clear()
        self.hours_per_semester_field.clearFocus()
        
            
    def set_destination_label(self, directory_name):
        description = Path(directory_name).stem
        self.destination_directory_label.setText('Destination Directory: {0}'.format(description))
                
    def _change_directory_callback(self):
        
        file_loader_dialog = QtWidgets.QFileDialog()
        file_loader_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        directory_name = None
        
        if file_loader_dialog.exec():
            directory_name = file_loader_dialog.selectedFiles()[0]
            self.controller.configure_destination_directory(directory_name)
            self.set_destination_label(self.controller.get_destination_directory())
        if directory_name == None:
            self.controller.output('Load cancelled.')
        
    def _toggle_export_type_callback(self):
        export_types = []
        
        if self.path_to_graduation_checkbox.isChecked():
            export_types.append(PATH_TO_GRADUATION_EXPORT_TYPE)
                
        if self.plain_text_checkbox.isChecked():
            export_types.append(PLAIN_TEXT_EXPORT_TYPE)
            
        if not len(export_types):
            self.controller.output_warning('Make sure you have at least one export mode selected.')
        
        self.controller.set_export_types(export_types)
    
    def _schedule_name_callback(self):
        '''Callback for when enter/return is pressed while editing the schedule name text field.'''
        
        self.controller.configure_destination_filename(self.schedule_name_field.text().strip())
        self.schedule_name_field.clear()
        self.schedule_name_field.clearFocus()
        self.schedule_name_field.setPlaceholderText(self.controller.get_destination_filename())
        
    
    def _generate_schedule_callback(self):
        
        self.controller.generate_schedule()
    


# NOTE: this may be removed later; it is just a thought right now.
class ConfigurationMenuWidget(QtWidgets.QWidget):

    def __init__(self, controller):
        super().__init__()                      # Call the super's initialization
        
        self.controller = controller
        
        # Create a basic layout
        self.layout = QtWidgets.QFormLayout(self)
    
