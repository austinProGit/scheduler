# Thomas Merino
# 3/01/23
# CPSC 4175 Group Project

# TODO: MISSING ANOTTATIONS!

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from typing import Optional, Any
    from program_driver import SmartPlannerController as Controller
    from courses_needed_container import CoursesNeededContainer
    from general_utilities import *

# TODO: Add some meaningful comments/documentation
# TODO: Needed courses label and listing box do not source from the data model (fix)
# TODO: Get @QtCore.Slot decorator to work
# TODO: (ORGANIZE) remove overuse of self.*widget*

# from msilib.schema import Control

from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, \
    QGroupBox, QFormLayout, QLineEdit, QTextEdit, QCheckBox, QMessageBox, QFileDialog

from pathlib import Path

from driver_fs_functions import *


## --------------------------------------------------------------------- ##
## ---------------------- Graphical User Interface --------------------- ##
## --------------------------------------------------------------------- ##


# This is the window for presenting the all graphical UI
class MainProgramWindow(QMainWindow):
    
    def __init__(self, controller: Controller) -> None:
        super().__init__()
        self.setWindowTitle('Smart Planner')
        self.widget: MainMenuWidget = MainMenuWidget(controller)
        self.setCentralWidget(self.widget)
        
        # Set the controller's listeners to two of widget's output handlers
        controller.add_output_listener("GUIOutput", self.widget.receive_process_output)
        controller.add_warning_listener("GUIWarning", self.widget.receive_process_warning)
        

# This subclass of the QT text field clears its contenct when focus is changed or the user presses enter/return
# --this changes the contents to the placeholder text.
class TextField(QLineEdit):
    
    def focusOutEvent(self, event: Any) -> None:
        '''Custom override of QLineEdit's focusOutEvent that clears text.'''
        super().focusOutEvent(event) # Invoke the super's implementation
        self.clear() # Remove all text (use splaceholder text)


class ListingField(QTextEdit):
    
    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)


# Graphical interface for the main menu
class MainMenuWidget(QWidget):
    
    
    def __init__(self, controller) -> None:
        # Call the super's initialization
        super().__init__()
        
        # Initialize a reference to the program's controller
        self.controller: Controller = controller
        
        # Create a label for presenting recent messages
        self.message_label: QLabel = QLabel('Welcome to Smart Planner')
        self.message_label.setWordWrap(True)
        
        # Row at the bottom to place miscellaneous buttons
        self.bottom_bar: QHBoxLayout = QHBoxLayout()
        
        # Create a button to switch to the command line (interface)
        self.command_line_button: QPushButton = QPushButton('Enter Command Line')
        self.command_line_button.clicked.connect(self._reload_in_cli_callback)
        self.bottom_bar.addWidget(self.command_line_button)
        
        # Create a button to verify a schedule
        self.verify_schedule_button: QPushButton = QPushButton('Verify Schedule')
        self.verify_schedule_button.clicked.connect(self._verify_schedule_callback)
        self.bottom_bar.addWidget(self.verify_schedule_button)
        
        # Add spacer to bottom bar
        self.bottom_bar.addItem(QtWidgets.QSpacerItem(1, 1, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        # Initialize the scheduling parameter widgets
        # This does not add them; it just initializes them and saves them as instance variables
        self.initialize_parameter_widgets()
        
        # Create a button that generate's the schedule
        self.generate_schedule_button: QPushButton = QPushButton('Generate Schedule')
        self.generate_schedule_button.clicked.connect(self._generate_schedule_callback)
        self.bottom_bar.addWidget(self.generate_schedule_button)
        
        # Create a vertical layout to store all UI elements
        self.layout: QVBoxLayout = QVBoxLayout(self)
        
        # Create a horizontal box layout
        # This will hold scheduling parametes on the left and listing/information on the right
        self.main_area: QHBoxLayout = QHBoxLayout()
        
        # Create the form area for presenting the message label, parameters, scheduling button, etc.
        self.interaction_area: QFormLayout = QFormLayout()
        
        #self.interaction_area.addWidget(self.message_label)
        self.interaction_area.addRow(self.needed_courses_load_label, self.needed_courses_load_button)
        self.interaction_area.addRow(self.destination_directory_label, self.change_directory_button)
        self.interaction_area.addRow(self.hours_per_semester_label, self.hours_per_semester_field)
        self.interaction_area.addWidget(self.path_to_graduation_checkbox)
        self.interaction_area.addWidget(self.plain_text_checkbox)
        self.interaction_area.addWidget(self.pdf_checkbox)
        self.interaction_area.addRow(self.schedule_name_label, self.schedule_name_field)
        
        # Create the area for presenting large amounts of data
        self.listing_box: ListingField = ListingField()
        
        # Add the form area to the horizontal box
        self.group_box: QGroupBox = QGroupBox()
        self.group_box.setTitle('Scheduling Parameters')
        self.group_box.setLayout(self.interaction_area)
        self.main_area.addWidget(self.group_box)
        self.main_area.addWidget(self.listing_box)
        
        # Add the main area and the message label
        self.layout.addLayout(self.main_area)
        self.layout.addWidget(self.message_label)
        self.layout.addLayout(self.bottom_bar)
        
        # Update if courses are loaded

        # TODO: this access of the courses list might be slow
        self.needed_courses: Optional[CoursesNeededContainer] = controller.get_courses_needed()
        if self.needed_courses is not None and self.needed_courses.is_resolved():
            self.needed_courses_load_label.setText('Courses loaded')
            self.listing_box.setText('\n'.join(self.needed_courses.get_courses_string_list()))
        

    def initialize_parameter_widgets(self) -> None:
        '''Setup the widgets for scheduling parameters. This does not add them; it just initializes them
        and saves them as instance variables.'''
            
        # Create a button to load the needed courses file
        self.needed_courses_load_label: QLabel = QLabel('No needed courses file loaded')
        self.needed_courses_load_button: QtWidgets = QPushButton('Open Needed Courses')
        self.needed_courses_load_button.clicked.connect(self._needed_courses_load_callback)
                
        # Create a button to select the working directory for output
        self.destination_directory_label: QLabel = QLabel('*No destination directory selected*')
        self._update_destination_label()
        self.change_directory_button: QtWidgets = QPushButton('Change Directory')
        self.change_directory_button.clicked.connect(self._change_directory_callback)
        
        # Create a text field that sets hours per semester after pressing enter/return
        self.hours_per_semester_label: QLabel = QLabel('Hours per semester:')
        self.hours_per_semester_field: TextField = TextField()
        self.hours_per_semester_field.setValidator(QtGui.QIntValidator())
        self.hours_per_semester_field.returnPressed.connect(self._hours_per_semester_callback)
        
        hours_range: Optional[range] = self.controller.get_hours_per_semester()
        if hours_range is not None:
            self.hours_per_semester_field.setPlaceholderText(f'{hours_range.start} to {hours_range.stop}')
        else:
            self.hours_per_semester_field.setPlaceholderText('Unspecified')
        
        # Create checkboxes for controlling the output types to generate
        self.path_to_graduation_checkbox: QCheckBox = QCheckBox('Export Path to Graduation Excel')
        active_export_types: list[ExportType] = self.controller.get_export_type()
        self.path_to_graduation_checkbox.setChecked(PATH_TO_GRADUATION_EXPORT_TYPE in active_export_types)
        self.path_to_graduation_checkbox.toggled.connect(self._toggle_export_type_callback)
        self.plain_text_checkbox: QCheckBox = QCheckBox('Export Simple txt')
        self.plain_text_checkbox.setChecked(PLAIN_TEXT_EXPORT_TYPE in active_export_types)
        self.plain_text_checkbox.toggled.connect(self._toggle_export_type_callback)
        self.pdf_checkbox: QCheckBox = QCheckBox('Export PDF')
        self.pdf_checkbox.setChecked(PDF_EXPORT_TYPE in active_export_types)
        self.pdf_checkbox.toggled.connect(self._toggle_export_type_callback)
        
        # Create a text field that set the schedule's name after pressing enter/return
        self.schedule_name_label: QLabel = QLabel('Schedule name:')
        self.schedule_name_field: TextField = TextField()
        self.schedule_name_field.returnPressed.connect(self._schedule_name_callback)
        self.schedule_name_field.setPlaceholderText(self.controller.get_destination_filename())
        
            
    def receive_process_output(self, message: str) -> None:
        '''Method to use for output listening. This methods just updates the message label.'''
        self.message_label.setText(message)
        
                
    def receive_process_warning(self, message: str) -> None:
        '''Method to use for warning listening. This methods presents a warning message box with the passed message.'''
        message_box: QMessageBox = QMessageBox()
        message_box.setIcon(QMessageBox.Warning)
        message_box.setText(message)
        message_box.exec()
    
    
    def _update_needed_courses_label(self, filename: str) -> None:
        '''Set the needed course label to reflect what the controller has loaded and list those courses in the listing box.'''
        # Get the file's description and set the label to the description
        description: str = Path(filename).stem
        self.needed_courses_load_label.setText(f'Needed Courses: {description}')

        self.needed_courses = self.controller.get_courses_needed()

        # TODO: fix this (possibly bad get-update)
        if self.needed_courses.is_resolved():
            self.listing_box.setText('\n'.join([str(s) for s in self.needed_courses.get_courses_list()]))
        else:
            self.listing_box.setText('*NOT RESOLVED*')
    
    
    def _needed_courses_load_callback(self) -> None:
        
        file_loader_dialog: QFileDialog = QFileDialog()
        file_loader_dialog.setFileMode(QFileDialog.ExistingFile)
        filename: Optional[str] = None

        if file_loader_dialog.exec():
            filename = file_loader_dialog.selectedFiles()[0]
            load_success: bool = self.controller.load_courses_needed(filename)
            if load_success:
                self._update_needed_courses_label(filename) 
        if filename is None:
            self.controller.output('Load cancelled.')
        
    def _verify_schedule_callback(self) -> None:
        
        file_loader_dialog: QFileDialog = QFileDialog()
        file_loader_dialog.setFileMode(QFileDialog.ExistingFile)
        filename: Optional[str] = None
        
        # TODO: ADD TYPE ANNOTATIONS ->

        if file_loader_dialog.exec():
            filename = file_loader_dialog.selectedFiles()[0]
            error_report = self.controller.check_schedule(filename)
            
            if error_report:
                self.listing_box.setText('\n'.join(error_report))
            elif error_report is not None:
                message_box = QtWidgets.QMessageBox()
                message_box.setIcon(QtWidgets.QMessageBox.Information)
                message_box.setText('The loaded schedule appears to valid.')
                message_box.exec()
        if filename is None:
            self.controller.output('Load cancelled.')
    
    def _update_destination_label(self):
        description = Path(self.controller.get_destination_directory()).stem
        self.destination_directory_label.setText('Destination Directory: {0}'.format(description))
        
    
    def _change_directory_callback(self) -> None:
        
        file_loader_dialog: QFileDialog = QFileDialog()
        file_loader_dialog.setFileMode(QFileDialog.Directory)
        directory_name = None
        
        if file_loader_dialog.exec():
            directory_name = file_loader_dialog.selectedFiles()[0]
            self.controller.configure_destination_directory(directory_name)
            self._update_destination_label()
        if directory_name is None:
            self.controller.output('Load cancelled.')
    
    
    def _hours_per_semester_callback(self):
        '''Callback for when enter/return is pressed while editing the hours per semester text field.'''
        
        hours_text = self.hours_per_semester_field.text()
        
        if hours_text.isdigit():
            number = int(hours_text)                                # Cast the input to an integer
            self.controller.configure_hours_per_semester(number)    # Set the number of hours per semester
            hours_range: Optional[range] = self.controller.get_hours_per_semester()
            if hours_range is not None:
                self.hours_per_semester_field.setPlaceholderText(f'{hours_range.start} to {hours_range.stop}')
            else:
                self.hours_per_semester_field.setPlaceholderText('Unspecified')
        else:
            # The argument was not valid (report to the user)
            self.controller.output('Sorry, that is not a valid input (please use a number).')
        self.hours_per_semester_field.clear()
        self.hours_per_semester_field.clearFocus()
        
            
    def _toggle_export_type_callback(self):
        '''Callback for when any export type checkbox changes state. This checks to see if all methods are unchecked (inform
        the user if so) and updates the controller with the new selection.'''
        
        export_types = []
        
        if self.path_to_graduation_checkbox.isChecked():
            export_types.append(PATH_TO_GRADUATION_EXPORT_TYPE)
                
        if self.plain_text_checkbox.isChecked():
            export_types.append(PLAIN_TEXT_EXPORT_TYPE)

        if self.pdf_checkbox.isChecked():
            export_types.append(PDF_EXPORT_TYPE)
            
        if not len(export_types):
            self.controller.output_warning('Make sure you have at least one export mode selected.')
        
        self.controller.set_export_types(export_types)
    
    def _schedule_name_callback(self):
        '''Callback for when enter/return is pressed while editing the schedule name text field.'''
        
        filename = self.schedule_name_field.text().strip()
        
        # Check if filename is not empty
        if filename:
            self.controller.configure_destination_filename(filename)
            self.schedule_name_field.clear()
            self.schedule_name_field.clearFocus()
            self.schedule_name_field.setPlaceholderText(self.controller.get_destination_filename())
        else:
            self.controller.output_error('Please enter a filename.')
            self.schedule_name_field.clearFocus()
        
    
    def _generate_schedule_callback(self):
        
        confidence_factor = self.controller.generate_schedule()
        
        if confidence_factor != -1:
            message_box = QtWidgets.QMessageBox()
            message_box.setIcon(QtWidgets.QMessageBox.Information)
            message_box.setText('Schedule generated with confidence value of {0:.1f}%.'.format(confidence_factor*100))
            message_box.exec()
        
    
    def _reload_in_cli_callback(self):
        '''Callback for entering the CLI. This sends the user immediately into the CLI, but outputs instructions on
        how to get back to the GUI.'''
        self.controller.reload_in_cli()
        self.controller.output('Interface mode changed to command line. Enter "gui-i" to change back.')
    
