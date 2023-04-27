# CPSC 4175 Group Project

# The following are imported for type annotations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from schedule_info_container import ScheduleInfoContainer, SemesterDescription
    from pathlib import Path

from fpdf import FPDF
from general_utilities import *


# SEMESTER_TYPE_SUCCESSOR = {'Fall': 'Spring', 'Spring':'Summer', 'Summer':'Fall'}    # Translation map from semester K to the next

def pdf_export(filepath: Path, schedule: ScheduleInfoContainer, starting_semester_type: SemesterType, starting_year: int) -> None:
    # Create a PDF object
    pdf: FPDF = FPDF()
    pdf.add_page()
    
    current_semester_type: SemesterType = starting_semester_type
    curent_year: int = starting_year
        
    # Iterate over each semester
    semester: SemesterDescription
    for semester in schedule.get_schedule():
        pdf.set_font("helvetica", "BU", size=12)
        pdf.cell(0, 5, f"{SEMESTER_DESCRIPTION_MAPPING[current_semester_type]} {curent_year}", ln=1)
        pdf.set_font("helvetica", size=12)
        pdf.multi_cell(0, 5, ", ".join(semester.str_iterator()) if semester else "-No Courses-", ln=1)
        pdf.ln(10)

        # Rotate the semester type and year if entering the spring
        current_semester_type = SEMESTER_TYPE_SUCCESSOR[current_semester_type]
        if current_semester_type == SPRING:
            curent_year += 1

    # Save the pdf
    pdf.output(filepath)
