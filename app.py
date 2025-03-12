import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import base64
import io
# Add ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set page configuration
st.set_page_config(
    page_title="UK Right to Work Checker",
    page_icon="🇬🇧",
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        background-color: #1e3d59;
        color: white;
    }
    .download-btn {
        margin-top: 1rem;
    }
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .result-container {
        background-color: #f6f6f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success {
        color: green;
        font-weight: bold;
    }
    .error {
        color: red;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Function to make API request
def check_right_to_work(code, forename, surname, dob, company_name, allow_student, allow_sponsorship):
    url = "https://api.ukrtwchecker.co.uk/rtw"
    
    # Get API key from Streamlit secrets or use a placeholder for development
    api_key = st.secrets.get("UKRTWAPI_SECRET", "YOUR_API_KEY")
    
    headers = {
        "X-UKRTWAPI-SECRET": api_key
    }
    
    params = {
        "code": code,
        "forename": forename,
        "surname": surname,
        "dob": dob,
        "company_name": company_name,
        "allow_student": str(allow_student).lower(),
        "allow_sponsorship": str(allow_sponsorship).lower()
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Error connecting to API: {str(e)}"

# Function to generate downloadable PDF
def generate_download_file(data, user_type):
    # Import required libraries for PDF generation
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    # Create a buffer
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=12
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=6
    )
    
    normal_style = styles["Normal"]
    
    # Create the elements list to build the PDF
    elements = []
    
    # Add title
    if user_type == "employee":
        elements.append(Paragraph("UK Right to Work Check - Employee Report", title_style))
    else:
        elements.append(Paragraph("UK Right to Work Check - Employer Verification", title_style))
    
    elements.append(Spacer(1, 12))
    
    # Add check details
    elements.append(Paragraph("Check Details:", header_style))
    
    # Convert check data to table format
    table_data = []
    if user_type == "employee":
        table_data = [
            ["Name:", data["status"]["name"]],
            ["Right to Work Status:", data["status"]["outcome"]],
            ["Valid From:", data["status"]["start_date"]],
            ["Expiry Date:", data["status"]["expiry_date"] or "No expiry"],
            ["Conditions:", data["status"]["conditions"]],
            ["Checked On:", datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
        ]
    else:  # employer
        table_data = [
            ["Employee Name:", data["status"]["name"]],
            ["Right to Work Status:", data["status"]["outcome"]],
            ["Valid From:", data["status"]["start_date"]],
            ["Expiry Date:", data["status"]["expiry_date"] or "No expiry"],
            ["Conditions:", data["status"]["conditions"]],
            ["Verification Date:", datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
            ["Verified By:", st.session_state.get("company_name", "Employer")]
        ]
    
    # Create the table
    table = Table(table_data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, len(table_data)//2), (0, len(table_data)//2), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    
    elements.append(Spacer(1, 12))
    
    # Add details section
    elements.append(Paragraph("Additional Details:", header_style))
    elements.append(Paragraph(data["status"]["details"], normal_style))
    
    elements.append(Spacer(1, 24))
    
    # Add disclaimer
    elements.append(Paragraph("Disclaimer:", header_style))
    elements.append(Paragraph("This document is a record of a right to work check performed through the UK Right to Work Checker application. For official verification, please visit the GOV.UK website.", normal_style))
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Return the base64 encoded PDF
    b64 = base64.b64encode(buffer.read()).decode()
    
    filename = f"right_to_work_{user_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    return b64, filename

# Initialize session state for result storage
if 'check_result' not in st.session_state:
    st.session_state.check_result = None

# Sidebar for user type selection
st.sidebar.title("User Type")
user_type = st.sidebar.radio("Select your role:", ["Employee", "Employer"])

# Main app title
st.title("UK Right to Work Checker")
st.markdown("Verify right to work eligibility based on share code")

# Different forms based on user type
if user_type == "Employee":
    with st.form("employee_check_form"):
        st.subheader("Employee Right to Work Check")
        
        col1, col2 = st.columns(2)
        with col1:
            share_code = st.text_input("Share Code", placeholder="Enter your share code")
            dob = st.date_input("Date of Birth", format="DD/MM/YYYY")
            dob_formatted = dob.strftime("%d-%m-%Y")
        
        with col2:
            st.write("This check is for your personal records.")
            # Default values for name fields
            forename = "John"
            surname = "Doe"
        
        # Hidden fields with default values for employee check
        company_name = "Self Check"
        allow_student = True
        allow_sponsorship = True
        
        submitted = st.form_submit_button("Check Right to Work Status")
        
        if submitted:
            # Store in session state for company name reference
            st.session_state.company_name = company_name
            
            result, error = check_right_to_work(
                share_code, forename, surname, dob_formatted, 
                company_name, allow_student, allow_sponsorship
            )
            
            st.session_state.check_result = result
            st.session_state.check_error = error
            st.session_state.user_type = "employee"
            
            # Use rerun instead of experimental_rerun
            st.rerun()

else:  # Employer
    with st.form("employer_check_form"):
        st.subheader("Employer Right to Work Verification")
        
        col1, col2 = st.columns(2)
        with col1:
            share_code = st.text_input("Employee Share Code", placeholder="Enter employee share code")
            dob = st.date_input("Employee Date of Birth", format="DD/MM/YYYY")
            dob_formatted = dob.strftime("%d-%m-%Y")
        
        with col2:
            company_name = st.text_input("Company Name", placeholder="Enter your company name")
            # Default values for name fields
            forename = "John"
            surname = "Doe"
        
        # Set default values for additional options
        allow_student = True
        allow_sponsorship = True
        
        submitted = st.form_submit_button("Verify Employee Status")
        
        if submitted:
            # Store in session state for company name reference
            st.session_state.company_name = company_name
            
            result, error = check_right_to_work(
                share_code, forename, surname, dob_formatted, 
                company_name, allow_student, allow_sponsorship
            )
            
            st.session_state.check_result = result
            st.session_state.check_error = error
            st.session_state.user_type = "employer"
            
            # Use rerun instead of experimental_rerun
            st.rerun()

# Display the result if available
if st.session_state.get('check_result'):
    st.markdown("## Check Results")
    
    result = st.session_state.check_result
    status = result["status"]
    
    st.markdown(f"""
    <div class="result-container">
        <h3>{status["title"]}</h3>
        <p><strong>Name:</strong> {status["name"]}</p>
        <p><strong>Status:</strong> <span class="{'success' if status['outcome'] == 'ACCEPTED' else 'error'}">{status["outcome"]}</span></p>
        <p><strong>Valid From:</strong> {status["start_date"]}</p>
        <p><strong>Expiry:</strong> {status["expiry_date"] or "No expiry date"}</p>
        <p><strong>Conditions:</strong> {status["conditions"]}</p>
        <p><strong>Details:</strong> {status["details"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate downloadable file
    b64, filename = generate_download_file(result, st.session_state.user_type)
    
    # Create download button for PDF
    download_button_str = f'<div class="download-btn"><a href="data:application/pdf;base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;font-size:16px;width:100%;">Download PDF Report</button></a></div>'
    st.markdown(download_button_str, unsafe_allow_html=True)
    
    # Add a clear results button
    if st.button("Start New Check"):
        st.session_state.check_result = None
        st.session_state.check_error = None
        st.rerun()

elif st.session_state.get('check_error'):
    st.error(f"Error: {st.session_state.check_error}")
    if st.button("Try Again"):
        st.session_state.check_error = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center">
    <p>This application helps verify UK right to work eligibility based on share codes.</p>
    <p>For official verification, please visit <a href="https://www.gov.uk/prove-right-to-work" target="_blank">GOV.UK Right to Work</a></p>
</div>
""", unsafe_allow_html=True)
