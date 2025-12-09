#!/usr/bin/env python3
"""
Aesop Daily Absence Report Generator
Generates PDF reports based on teacher schedule and configurable rules.
"""

import csv
import random
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# Configuration
ABSENCE_RULES = {
    0: {"absences": (6, 8), "sub_coverage": 0.80},    # Monday
    1: {"absences": (3, 5), "sub_coverage": 0.90},    # Tuesday
    2: {"absences": (3, 5), "sub_coverage": 0.90},    # Wednesday
    3: {"absences": (3, 5), "sub_coverage": 0.90},    # Thursday
    4: {"absences": (10, 12), "sub_coverage": 0.775}, # Friday (avg of 75-80%)
}

DURATION_WEIGHTS = {
    "Full Day": 0.85,
    "Half Day AM": 0.075,
    "Half Day PM": 0.075,
}

DURATION_TIMES = {
    "Full Day": "7:00 - 2:20",
    "Half Day AM": "7:00 - 11:15",
    "Half Day PM": "11:15 - 2:20",
}

ABSENCE_REASONS = [
    "Family Illness",
    "Personal Day",
    "Sick Day",
    "Professional Day",
    "Medical Appointment",
    "Bereavement",
]

REASON_WEIGHTS = [0.25, 0.20, 0.30, 0.15, 0.05, 0.05]


def load_teachers(csv_path):
    """Load teachers from CSV file."""
    teachers = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            teacher_name = row.get('Teacher', '').strip()
            department = row.get('Department', '').strip()
            if teacher_name and teacher_name != 'Teacher':
                # Parse "LastName, FirstName" format
                teachers.append({
                    'name': teacher_name,
                    'department': department if department else 'General',
                })
    return teachers


def load_subs(txt_path):
    """Load substitute teachers from text file."""
    subs = []
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('---'):
                subs.append(line)
    return subs


def generate_conf_number():
    """Generate a random confirmation number."""
    return f"{random.randint(680000000, 689999999)}"


def generate_phone():
    """Generate a random phone number."""
    return f"({random.randint(201, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"


def select_duration():
    """Select a duration based on weights."""
    durations = list(DURATION_WEIGHTS.keys())
    weights = list(DURATION_WEIGHTS.values())
    return random.choices(durations, weights=weights, k=1)[0]


def select_reason():
    """Select an absence reason based on weights."""
    return random.choices(ABSENCE_REASONS, weights=REASON_WEIGHTS, k=1)[0]


def generate_absence_data(teachers, subs, report_date):
    """Generate absence data for a specific date."""
    day_of_week = report_date.weekday()
    rules = ABSENCE_RULES.get(day_of_week, ABSENCE_RULES[1])  # Default to Tue-Thu rules

    # Determine number of absences
    num_absences = random.randint(rules["absences"][0], rules["absences"][1])
    sub_coverage = rules["sub_coverage"]

    # Select random teachers
    absent_teachers = random.sample(teachers, min(num_absences, len(teachers)))

    # Generate absence records
    absences = []
    for teacher in absent_teachers:
        duration = select_duration()
        reason = select_reason()

        # Determine if this absence gets a sub
        has_sub = random.random() < sub_coverage

        # Generate entry timestamp (1-7 days before report date)
        days_ago = random.randint(1, 7)
        entry_time = report_date - timedelta(days=days_ago)
        entry_time = entry_time.replace(
            hour=random.randint(6, 20),
            minute=random.randint(0, 59)
        )

        absence = {
            'conf_number': generate_conf_number(),
            'entry_date': entry_time.strftime("%-m/%-d/%Y"),
            'entry_time': entry_time.strftime("%-I:%M %p"),
            'school': 'SBHS',  # Abbreviated from South Brunswick High School
            'teacher_name': teacher['name'],
            'department': teacher['department'],
            'employee_type': 'Teacher',
            'shift': 'Employee Times',
            'shift_times': DURATION_TIMES[duration],
            'duration': duration,
            'reason': reason,
            'status': random.choice(['Approved', 'No Appr.\nReq.']),  # Abbreviated with line break
            'has_sub': has_sub,
            'sub_name': None,
            'sub_phone': None,
        }

        if has_sub:
            sub = random.choice(subs)
            absence['sub_name'] = sub
            absence['sub_phone'] = generate_phone()

        absences.append(absence)

    return absences


def create_pdf_report(absences, report_date, output_path, username="Brian McManus"):
    """Create a PDF report matching the Aesop template."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
    )
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
    )
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.black,
        spaceBefore=12,
        spaceAfter=6,
    )

    elements = []

    # Header
    header_text = f"{datetime.now().strftime('%-m/%-d/%y, %-I:%M %p')}"
    elements.append(Paragraph(header_text, header_style))
    elements.append(Spacer(1, 6))

    # Title
    elements.append(Paragraph("Daily Report", title_style))
    elements.append(Spacer(1, 12))

    # Filter info box
    filter_data = [
        ['Filter Report:', '', report_date.strftime("%A, %B %-d, %Y"), '', 'Report Date:', report_date.strftime("%b. %-d, %Y")],
        ['Type:', 'Absences and Vacancies', '', '', 'Username:', username],
        ['School(s):', 'All Schools', '', '', '', ''],
        ['Employee Type(s):', 'All Employee Types', '', '', '', ''],
    ]

    filter_table = Table(filter_data, colWidths=[1.2*inch, 1.5*inch, 2*inch, 0.3*inch, 0.8*inch, 1.5*inch])
    filter_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('TEXTCOLOR', (4, 0), (4, -1), colors.HexColor('#666666')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(filter_table)
    elements.append(Spacer(1, 20))

    # Separate absences into categories
    filled = [a for a in absences if a['has_sub']]
    unfilled = [a for a in absences if not a['has_sub']]

    # Unfilled section
    elements.append(Paragraph(f"<b>{len(unfilled)}</b>&nbsp;&nbsp;&nbsp;Unfilled", section_style))

    if unfilled:
        unfilled_header = [['Conf #', 'School', 'Name', 'Employee\nType', 'Shift', 'Duration', 'Reason', 'Status']]
        unfilled_data = unfilled_header.copy()

        for absence in unfilled:
            unfilled_data.append([
                f"Absence\n{absence['conf_number']}\n{absence['entry_date']}\n{absence['entry_time']}",
                absence['school'],
                f"{absence['teacher_name']}\n{absence['department']}",
                absence['employee_type'],
                f"{absence['shift']}\n{absence['shift_times']}",
                absence['duration'],
                absence['reason'],
                absence['status'],
            ])

        unfilled_table = Table(unfilled_data, colWidths=[0.95*inch, 0.55*inch, 1.3*inch, 0.65*inch, 0.95*inch, 0.7*inch, 0.75*inch, 0.75*inch])
        unfilled_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(unfilled_table)
    else:
        elements.append(Paragraph("No unfilled absences.", header_style))

    elements.append(Spacer(1, 20))

    # Filled section
    elements.append(Paragraph(f"<b>{len(filled)}</b>&nbsp;&nbsp;&nbsp;Filled", section_style))

    if filled:
        filled_header = [['Conf #', 'School', 'Name', 'Employee\nType', 'Shift', 'Duration', 'Reason', 'Status', 'Substitute']]
        filled_data = filled_header.copy()

        for absence in filled:
            filled_data.append([
                f"Absence\n{absence['conf_number']}\n{absence['entry_date']}\n{absence['entry_time']}",
                absence['school'],
                f"{absence['teacher_name']}\n{absence['department']}",
                absence['employee_type'],
                f"{absence['shift']}\n{absence['shift_times']}",
                absence['duration'],
                absence['reason'],
                absence['status'],
                f"{absence['sub_name']}\nPhone:\n{absence['sub_phone']}",
            ])

        filled_table = Table(filled_data, colWidths=[0.85*inch, 0.5*inch, 1.1*inch, 0.6*inch, 0.85*inch, 0.6*inch, 0.7*inch, 0.6*inch, 1.0*inch])
        filled_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TEXTCOLOR', (7, 1), (7, -1), colors.HexColor('#28a745')),  # Green for Approved status
        ]))
        elements.append(filled_table)
    else:
        elements.append(Paragraph("No filled absences.", header_style))

    elements.append(Spacer(1, 20))

    # Footer
    footer_text = f"https://absenceadminweb.frontlineeducation.com/reports/absence/daily-report?date={report_date.strftime('%m%%2F%d%%2F%Y')}"
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', fontSize=8, textColor=colors.HexColor('#999999'))))

    doc.build(elements)
    return output_path


def create_csv_report(absences, output_path):
    """Create a CSV file with Name and Duration from absence data."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Duration'])
        for absence in absences:
            writer.writerow([absence['teacher_name'], absence['duration']])
    return output_path


def generate_reports(num_reports=3, start_date=None):
    """Generate multiple absence reports."""
    # Load data
    teachers = load_teachers('/home/user/cc_work/sbhs_master_schedule_COMPLETE.csv')
    subs = load_subs('/home/user/cc_work/List of Available Subs.txt')

    print(f"Loaded {len(teachers)} teachers and {len(subs)} substitutes")

    # Generate reports for consecutive weekdays
    if start_date is None:
        start_date = datetime.now()

    # Find next Monday
    days_until_monday = (7 - start_date.weekday()) % 7
    if days_until_monday == 0 and start_date.weekday() != 0:
        days_until_monday = 7
    current_date = start_date + timedelta(days=days_until_monday)

    reports = []
    weekday_count = 0

    while len(reports) < num_reports:
        # Skip weekends
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            absences = generate_absence_data(teachers, subs, current_date)

            pdf_path = f"/home/user/cc_work/absence_report_{current_date.strftime('%Y%m%d')}.pdf"
            csv_path = f"/home/user/cc_work/absence_report_{current_date.strftime('%Y%m%d')}.csv"
            create_pdf_report(absences, current_date, pdf_path)
            create_csv_report(absences, csv_path)

            day_name = current_date.strftime("%A")
            print(f"Generated report for {day_name}, {current_date.strftime('%B %d, %Y')}")
            print(f"  - Total absences: {len(absences)}")
            print(f"  - Filled: {len([a for a in absences if a['has_sub']])}")
            print(f"  - Unfilled: {len([a for a in absences if not a['has_sub']])}")
            print(f"  - PDF: {pdf_path}")
            print(f"  - CSV: {csv_path}")

            reports.append({
                'date': current_date,
                'pdf_path': pdf_path,
                'csv_path': csv_path,
                'absences': len(absences),
            })

        current_date += timedelta(days=1)

    return reports


if __name__ == "__main__":
    print("Aesop Daily Absence Report Generator")
    print("=" * 40)
    reports = generate_reports(num_reports=3)
    print("\n" + "=" * 40)
    print(f"Generated {len(reports)} reports successfully!")
