# ============================================================
# FILE: create_sample_docs.py
# PURPOSE: Generate 3 realistic sample insurance PDF documents
#          for testing CLAIMA
# LIBRARY USED: fpdf2 (free PDF creation library)
#   Install with: pip install fpdf2
# ============================================================

from fpdf import FPDF
import os

os.makedirs("sample_docs", exist_ok=True)


def create_auto_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "COMMERCIAL AUTO INSURANCE APPLICATION", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Submission Reference: CA-2024-00891", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "APPLICANT INFORMATION", ln=True)
    pdf.set_font("Helvetica", "", 11)

    fields = [
        ("Applicant Name",      "Rajesh Kumar Logistics Pvt Ltd"),
        ("Business Name",       "RK Transport & Logistics"),
        ("Contact Person",      "Rajesh Kumar"),
        ("Contact Email",       "rajesh.kumar@rktransport.in"),
        ("Contact Phone",       "+91-98765-43210"),
        ("Business Address",    "Plot 45, Industrial Area, Hyderabad, Telangana - 500032"),
        ("Agent Name",          "Suresh Mehta, Senior Insurance Agent"),
    ]
    for label, value in fields:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(70, 9, f"{label}:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 9, value, ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "POLICY DETAILS", ln=True)
    pdf.set_font("Helvetica", "", 11)

    policy_fields = [
        ("Policy Type",         "Commercial Auto Insurance"),
        ("Coverage Amount",     "$750,000"),
        ("Effective Date",      "01/01/2025"),
        ("Expiration Date",     "31/12/2025"),
        ("Number of Vehicles",  "12"),
        ("Vehicle Types",       "Trucks (6), Vans (4), Cars (2)"),
        ("Primary Use",         "Goods transportation across Telangana and Andhra Pradesh"),
    ]
    for label, value in policy_fields:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(70, 9, f"{label}:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 9, value, ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "DRIVER INFORMATION", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        "Total Drivers: 14\n"
        "All drivers hold valid commercial driving licenses.\n"
        "Average driving experience: 7 years.\n"
        "No drivers with DUI or major violations in past 3 years."
    )

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "LOSS HISTORY (PAST 3 YEARS)", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        "2022: 1 minor accident - Rear collision, Claim Amount: $4,200. Settled.\n"
        "2023: No claims filed.\n"
        "2024: 1 vehicle theft reported, Claim Amount: $18,000. Under review."
    )

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "SPECIAL NOTES", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        "Fleet GPS tracking installed on all vehicles.\n"
        "Driver training program conducted quarterly.\n"
        "Requesting comprehensive coverage including collision and theft."
    )

    pdf.output("sample_docs/sample_auto.pdf")
    print("Created: sample_docs/sample_auto.pdf")


def create_property_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "COMMERCIAL PROPERTY INSURANCE APPLICATION", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Submission Reference: PR-2024-00445", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "APPLICANT INFORMATION", ln=True)
    pdf.set_font("Helvetica", "", 11)

    fields = [
        ("Applicant Name",      "Priya Sharma"),
        ("Business Name",       "Sharma Tech Hub"),
        ("Contact Email",       "priya.sharma@sharmatechhub.com"),
        ("Contact Phone",       "+91-99887-76655"),
        ("Agent Name",          "Vikram Nair, Property Insurance Specialist"),
    ]
    for label, value in fields:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(70, 9, f"{label}:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 9, value, ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "PROPERTY DETAILS", ln=True)
    pdf.set_font("Helvetica", "", 11)

    property_fields = [
        ("Policy Type",         "Commercial Property Insurance"),
        ("Coverage Amount",     "$1,500,000"),
        ("Effective Date",      "15/02/2025"),
        ("Expiration Date",     "14/02/2026"),
        ("Property Value",      "$1,200,000"),
        ("Location",            "Building No. 7, HITEC City, Hyderabad, Telangana - 500081"),
        ("Property Type",       "Commercial Office Building"),
        ("Construction Type",   "Reinforced Concrete (RCC)"),
        ("Year Built",          "2018"),
        ("Total Area",          "12,500 square feet across 4 floors"),
        ("Occupancy",           "IT Services and Software Development Firm"),
    ]
    for label, value in property_fields:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(70, 9, f"{label}:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 9, value, ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "PROTECTION SYSTEMS", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        "Fire Protection: Sprinkler system installed on all floors. Fire extinguishers present.\n"
        "Security: 24/7 CCTV surveillance. Biometric access control on all entry points.\n"
        "Alarm Systems: Smoke and heat detectors connected to local fire station.\n"
        "Backup Power: Diesel generator with 72-hour fuel capacity."
    )

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "LOSS HISTORY", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        "No claims in the past 5 years. Property has clean record.\n"
        "Previous insurer: HDFC ERGO. Policy expired without claims."
    )

    pdf.output("sample_docs/sample_property.pdf")
    print("Created: sample_docs/sample_property.pdf")


def create_liability_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "GENERAL LIABILITY INSURANCE APPLICATION", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Submission Reference: GL-2024-01122", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "APPLICANT INFORMATION", ln=True)
    pdf.set_font("Helvetica", "", 11)

    fields = [
        ("Applicant Name",      "Anil Reddy"),
        ("Business Name",       "Reddy Construction & Interiors"),
        ("Contact Email",       "anil.reddy@reddyconstruction.com"),
        ("Contact Phone",       "+91-97654-32109"),
        ("Agent Name",          "Kavitha Rao, Commercial Lines Specialist"),
    ]
    for label, value in fields:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(70, 9, f"{label}:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 9, value, ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "POLICY DETAILS", ln=True)
    pdf.set_font("Helvetica", "", 11)

    policy_fields = [
        ("Policy Type",           "General Liability Insurance"),
        ("Coverage Amount",       "$500,000"),
        ("Effective Date",        "01/03/2025"),
        ("Expiration Date",       "28/02/2026"),
        ("Liability Limit",       "$500,000 per occurrence / $1,000,000 aggregate"),
        ("Bodily Injury Limit",   "$300,000 per person"),
        ("Property Damage Limit", "$200,000 per occurrence"),
    ]
    for label, value in policy_fields:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(80, 9, f"{label}:", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 9, value, ln=True)

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "BUSINESS OPERATIONS", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        "Business Type: Commercial construction and interior fit-out services.\n"
        "Annual Revenue: Rs. 3.2 Crores\n"
        "Number of Employees: 45 (including contract workers)\n"
        "Operating Locations: Hyderabad, Secunderabad, Warangal\n"
        "Primary Services: Civil construction, electrical, plumbing, interior design"
    )

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "LIABILITY HISTORY", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        "2022: One bodily injury claim filed by a site worker. Settled for $8,500.\n"
        "2023: No liability claims.\n"
        "2024: One property damage claim during renovation project. Amount: $12,000. Pending."
    )

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "SPECIAL NOTES", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8,
        "All workers are covered under Workmen Compensation separately.\n"
        "Safety officer appointed on all project sites.\n"
        "Completed operations coverage also requested."
    )

    pdf.output("sample_docs/sample_liability.pdf")
    print("Created: sample_docs/sample_liability.pdf")


# Run all three
create_auto_pdf()
create_property_pdf()
create_liability_pdf()

print("\nAll 3 sample documents created successfully in sample_docs/ folder!")