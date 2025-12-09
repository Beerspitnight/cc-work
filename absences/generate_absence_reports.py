#!/usr/bin/env python3
"""
Generate daily absence report PDFs for December 9-22, 2025 (weekdays only)
"""

import random
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Teacher roster from fifty_teacher_roster.csv
TEACHERS = [
    ("Abdelhamed, Brittany", "General"),
    ("Ayala, Amaya", "General"),
    ("Doshi, Chetna", "General"),
    ("Durbhakula, Vyjayanti", "General"),
    ("Elvy, Mary", "General"),
    ("Kivowitz, Melissa", "General"),
    ("Zinsmeister, James", "General"),
    ("Biggs, Francesca", "Business"),
    ("Bogert, Janet", "Business"),
    ("Galaro, Annette", "Business"),
    ("Ganguzza, Amanda", "Business"),
    ("Hunte, Karen", "Business"),
    ("Lolli, John", "Business"),
    ("Maitland, Austin", "Business"),
    ("McGrath, Ailish", "Business"),
    ("Peart, Kimeka", "Business"),
    ("Becker, Matthew", "English / Language Arts"),
    ("Bergamotto, Lisa", "English / Language Arts"),
    ("Brancato, Kyle", "English / Language Arts"),
    ("Ciccone, Marisol", "English / Language Arts"),
    ("Duryea-Lojko, Janelle", "English / Language Arts"),
    ("Friedman, Joseph", "English / Language Arts"),
    ("Fritsche, Jessica", "English / Language Arts"),
    ("Grande, Christine", "English / Language Arts"),
    ("Halaw, Andre", "English / Language Arts"),
    ("Hines, Kristen", "English / Language Arts"),
    ("Honig, Peter", "English / Language Arts"),
    ("Lehre, Anna", "English / Language Arts"),
    ("Liguori, Monique", "English / Language Arts"),
    ("Marchetti, Stefanie", "English / Language Arts"),
    ("Mathe, Csilla", "English / Language Arts"),
    ("Noebels, James", "English / Language Arts"),
    ("Ramos, Ariana", "English / Language Arts"),
    ("Rivera, Wilfredo", "English / Language Arts"),
    ("Robinson, Darlene", "English / Language Arts"),
    ("Rossi, Collin", "English / Language Arts"),
    ("Schwartz, Shauna", "English / Language Arts"),
    ("Sincoff, Shara", "English / Language Arts"),
    ("Trader, Jillian", "English / Language Arts"),
    ("Bullen, Andria", "Family and Consumer Sciences"),
    ("Taranto, Natalie", "Family and Consumer Sciences"),
    ("Budhu, Laurie", "Fine Arts"),
    ("Bufis, Rebecca", "Fine Arts"),
    ("Chow, Norman", "Fine Arts"),
    ("McMillan, Kathleen", "Fine Arts"),
    ("McCuen, Justin", "James Kimple Center"),
    ("Akella, Aparna", "Mathematics"),
    ("Arnold, Briton", "Mathematics"),
    ("Barnes, Gordon", "Mathematics"),
    ("Budhu, Jared", "Mathematics"),
]

# Available substitutes
SUBS = [
    ("Chloe Bennett", "(555) 101-2001"),
    ("Hannah Rodriguez", "(555) 102-2002"),
    ("Natalie Chen", "(555) 103-2003"),
    ("Zoe Hayes", "(555) 104-2004"),
    ("Grace Patterson", "(555) 105-2005"),
    ("Savannah Flores", "(555) 106-2006"),
    ("Layla Morgan", "(555) 107-2007"),
    ("Stella Kim", "(555) 108-2008"),
    ("Aubrey Wallace", "(555) 109-2009"),
    ("Penelope Rhodes", "(555) 110-2010"),
    ("Eleanor Sullivan", "(555) 111-2011"),
    ("Maya Fitzgerald", "(555) 112-2012"),
    ("Claire Dawson", "(555) 113-2013"),
    ("Sadie Gallagher", "(555) 114-2014"),
    ("Violet Lawson", "(555) 115-2015"),
    ("Naomi Bauer", "(555) 116-2016"),
    ("Elena Rivera", "(555) 117-2017"),
    ("Isabelle Chu", "(555) 118-2018"),
    ("Caleb Murphy", "(555) 119-2019"),
    ("Gavin Holt", "(555) 120-2020"),
    ("Jordan Beck", "(555) 121-2021"),
    ("Nathaniel Pierce", "(555) 122-2022"),
    ("Wesley Jennings", "(555) 123-2023"),
    ("Miles O'Donnell", "(555) 124-2024"),
]

# Absence reasons
REASONS = ["Sick Day", "Family Illness", "Personal Day", "Professional Day", "Medical Appointment"]

# Absence durations
DURATIONS = [
    ("Full Day", "7:00 - 2:20"),
    ("Half Day AM", "7:00 - 11:15"),
    ("Half Day PM", "11:15 - 2:20"),
]

# Status options
STATUSES = ["Approved", "No Appr. Req."]


def generate_conf_number():
    """Generate a random 9-digit confirmation number"""
    return str(random.randint(680000000, 699999999))


def generate_conf_datetime(report_date):
    """Generate a random datetime 1-5 days before the report date"""
    days_before = random.randint(1, 5)
    conf_date = report_date - timedelta(days=days_before)
    hour = random.randint(5, 22)
    minute = random.randint(0, 59)
    am_pm = "AM" if hour < 12 else "PM"
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0:
        display_hour = 12
    return conf_date.strftime("%m/%d/%Y"), f"{display_hour}:{minute:02d} {am_pm}"


def get_day_type(date):
    """Return the day type: 0=Mon, 4=Fri are high absence days"""
    weekday = date.weekday()
    if weekday == 0 or weekday == 4:  # Monday or Friday
        return "high"
    return "normal"


def generate_absences_for_day(report_date, used_teachers_week):
    """Generate random absences for a given day"""
    day_type = get_day_type(report_date)

    # Determine number of absences based on day type
    if day_type == "high":
        num_absences = random.randint(8, 12)
    else:
        num_absences = random.randint(3, 6)

    # Select random teachers (avoid repeats within week if possible)
    available_teachers = [t for t in TEACHERS if t not in used_teachers_week]
    if len(available_teachers) < num_absences:
        available_teachers = TEACHERS.copy()

    absent_teachers = random.sample(available_teachers, num_absences)

    # Determine filled percentage (45-80%)
    filled_pct = random.uniform(0.45, 0.80)
    num_filled = int(num_absences * filled_pct)
    num_unfilled = num_absences - num_filled

    # Shuffle and split into filled/unfilled
    random.shuffle(absent_teachers)
    unfilled_teachers = absent_teachers[:num_unfilled]
    filled_teachers = absent_teachers[num_unfilled:]

    # Select subs for filled absences
    available_subs = random.sample(SUBS, min(len(filled_teachers), len(SUBS)))

    absences = []

    # Generate unfilled absences
    for teacher in unfilled_teachers:
        conf_date, conf_time = generate_conf_datetime(report_date)
        duration_info = random.choice(DURATIONS)
        absences.append({
            "type": "unfilled",
            "conf_num": generate_conf_number(),
            "conf_date": conf_date,
            "conf_time": conf_time,
            "name": teacher[0],
            "department": teacher[1],
            "duration": duration_info[0],
            "shift": duration_info[1],
            "reason": random.choice(REASONS),
            "status": random.choice(STATUSES),
            "substitute": None,
            "sub_phone": None,
        })

    # Generate filled absences
    for i, teacher in enumerate(filled_teachers):
        conf_date, conf_time = generate_conf_datetime(report_date)
        duration_info = random.choice(DURATIONS)
        sub = available_subs[i] if i < len(available_subs) else random.choice(SUBS)
        absences.append({
            "type": "filled",
            "conf_num": generate_conf_number(),
            "conf_date": conf_date,
            "conf_time": conf_time,
            "name": teacher[0],
            "department": teacher[1],
            "duration": duration_info[0],
            "shift": duration_info[1],
            "reason": random.choice(REASONS),
            "status": random.choice(STATUSES),
            "substitute": sub[0],
            "sub_phone": sub[1],
        })

    # Add to used teachers
    used_teachers_week.extend(absent_teachers)

    return absences


def create_pdf_report(report_date, absences, output_path):
    """Create a PDF report for the given date"""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    elements = []

    # Header timestamp
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey
    )

    # Format dates
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_name = day_names[report_date.weekday()]
    formatted_date = f"{day_name}, {report_date.strftime('%B')} {report_date.day}, {report_date.year}"
    short_date = f"{report_date.strftime('%b')}. {report_date.day}, {report_date.year}"

    # Header with timestamp
    timestamp = f"{report_date.strftime('%m/%d/%y')}, 12:00 AM"
    elements.append(Paragraph(timestamp, header_style))
    elements.append(Spacer(1, 0.1*inch))

    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20
    )
    elements.append(Paragraph("Daily Report", title_style))

    # Filter info table
    filter_data = [
        ["Filter Report:", formatted_date, f"Report Date: {short_date}"],
        ["Type:", "Absences and Vacancies", "Username: Brian McManus"],
        ["School(s):", "All Schools", ""],
        ["Employee Type(s):", "All Employee Types", ""],
    ]

    filter_table = Table(filter_data, colWidths=[1.5*inch, 3*inch, 2.5*inch])
    filter_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.lightgrey),
    ]))
    elements.append(filter_table)
    elements.append(Spacer(1, 0.3*inch))

    # Separate absences
    unfilled = [a for a in absences if a["type"] == "unfilled"]
    filled = [a for a in absences if a["type"] == "filled"]

    # Section header style
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=10,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )

    # Cell styles
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10
    )

    green_style = ParagraphStyle(
        'GreenCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.Color(0.2, 0.6, 0.2)
    )

    # Unfilled section
    elements.append(Paragraph(f"<b>{len(unfilled)}</b>&nbsp;&nbsp;Unfilled", section_style))

    if unfilled:
        unfilled_header = [
            Paragraph("<b>Conf #</b>", cell_style),
            Paragraph("<b>School</b>", cell_style),
            Paragraph("<b>Name</b>", cell_style),
            Paragraph("<b>Employee Type</b>", cell_style),
            Paragraph("<b>Shift</b>", cell_style),
            Paragraph("<b>Duration</b>", cell_style),
            Paragraph("<b>Reason</b>", cell_style),
            Paragraph("<b>Status</b>", cell_style),
        ]

        unfilled_data = [unfilled_header]
        for a in unfilled:
            row = [
                Paragraph(f"Absence<br/>{a['conf_num']}<br/>{a['conf_date']}<br/>{a['conf_time']}", cell_style),
                Paragraph("SBHS", cell_style),
                Paragraph(f"{a['name']}<br/>{a['department']}", cell_style),
                Paragraph("Teacher", cell_style),
                Paragraph(f"Employee Times<br/>{a['shift']}", cell_style),
                Paragraph(a['duration'], cell_style),
                Paragraph(a['reason'], cell_style),
                Paragraph(a['status'], cell_style),
            ]
            unfilled_data.append(row)

        unfilled_table = Table(unfilled_data, colWidths=[0.9*inch, 0.5*inch, 1.1*inch, 0.7*inch, 0.9*inch, 0.7*inch, 0.9*inch, 0.6*inch])
        unfilled_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),
        ]))
        elements.append(unfilled_table)

    elements.append(Spacer(1, 0.3*inch))

    # Filled section
    elements.append(Paragraph(f"<b>{len(filled)}</b>&nbsp;&nbsp;Filled", section_style))

    if filled:
        filled_header = [
            Paragraph("<b>Conf #</b>", cell_style),
            Paragraph("<b>School</b>", cell_style),
            Paragraph("<b>Name</b>", cell_style),
            Paragraph("<b>Employee Type</b>", cell_style),
            Paragraph("<b>Shift</b>", cell_style),
            Paragraph("<b>Duration</b>", cell_style),
            Paragraph("<b>Reason</b>", cell_style),
            Paragraph("<b>Status</b>", cell_style),
            Paragraph("<b>Substitute</b>", cell_style),
        ]

        filled_data = [filled_header]
        for a in filled:
            row = [
                Paragraph(f"Absence<br/>{a['conf_num']}<br/>{a['conf_date']}<br/>{a['conf_time']}", cell_style),
                Paragraph("SBHS", cell_style),
                Paragraph(f"{a['name']}<br/>{a['department']}", cell_style),
                Paragraph("Teacher", cell_style),
                Paragraph(f"Employee Times<br/>{a['shift']}", cell_style),
                Paragraph(a['duration'], cell_style),
                Paragraph(a['reason'], cell_style),
                Paragraph(a['status'], green_style),
                Paragraph(f"{a['substitute']}<br/>Phone:<br/>{a['sub_phone']}", green_style),
            ]
            filled_data.append(row)

        filled_table = Table(filled_data, colWidths=[0.85*inch, 0.45*inch, 1.0*inch, 0.65*inch, 0.85*inch, 0.65*inch, 0.8*inch, 0.55*inch, 0.9*inch])
        filled_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),
        ]))
        elements.append(filled_table)

    # Build PDF
    doc.build(elements)
    print(f"Created: {output_path}")


def main():
    # Set random seed for reproducibility (optional - remove for true randomness)
    random.seed(42)

    # Define date range: December 9-22, 2025 (weekdays only)
    start_date = datetime(2025, 12, 9)
    end_date = datetime(2025, 12, 22)

    output_dir = "/home/user/cc-work/absences/aesop"

    current_date = start_date
    used_teachers_week = []
    week_start = start_date

    dates_processed = []

    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            current_date += timedelta(days=1)
            continue

        # Reset used teachers at start of new week
        if current_date.weekday() == 0 and current_date != week_start:
            used_teachers_week = []
            week_start = current_date

        # Generate absences
        absences = generate_absences_for_day(current_date, used_teachers_week)

        # Create PDF
        filename = f"absence_report_{current_date.strftime('%Y%m%d')}.pdf"
        output_path = f"{output_dir}/{filename}"
        create_pdf_report(current_date, absences, output_path)

        dates_processed.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

    print(f"\nGenerated {len(dates_processed)} reports:")
    for d in dates_processed:
        print(f"  - {d}")


if __name__ == "__main__":
    main()
