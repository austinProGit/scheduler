from fpdf import FPDF

SEMESTER_TYPE_SUCCESSOR = {'Fall': 'Spring', 'Spring':'Summer', 'Summer':'Fall'}    # Translation map from semester K to the next

def pdf_export(filepath, schedule, starting_semester_type, starting_year):
    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()
    
    current_semester_type = starting_semester_type
    curent_year = starting_year
        
    # Iterate over each semester
    for semester in schedule:
        pdf.set_font("helvetica", "BU", size=12)
        pdf.cell(0, 5, f"{current_semester_type} {curent_year}", ln=1)
        pdf.set_font("helvetica", size=12)
        pdf.multi_cell(0, 5, ", ".join(semester) if semester else "-No Course-", ln=1)
        pdf.ln(10)

        # Rotate the semester type and year if entering the spring
        current_semester_type = SEMESTER_TYPE_SUCCESSOR[current_semester_type]
        if current_semester_type == 'Spring':
            curent_year += 1

    # Save the pdf
    pdf.output(filepath)