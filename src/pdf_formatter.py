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

def pdf_export(filepath: Path, schedule: ScheduleInfoContainer) -> None:
    # Create a PDF object
    pdf: FPDF = FPDF()
    pdf.add_page()
        
    # Iterate over each semester
    semester: SemesterDescription
    for semester in schedule.get_schedule():
        current_semester_type: SemesterType = semester.semester_type
        curent_year: int = semester.year
        pdf.set_font("helvetica", "BU", size=12)
        pdf.cell(0, 5, f"{SEMESTER_DESCRIPTION_MAPPING[current_semester_type]} {curent_year}", ln=1)
        pdf.set_font("helvetica", size=12)
        pdf.multi_cell(0, 5, ", ".join(semester.str_iterator()) if semester else "-No Courses-", 1)
        pdf.ln(10)


    # Save the pdf
    pdf.output(filepath)
