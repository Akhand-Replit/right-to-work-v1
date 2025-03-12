import streamlit as st
import datetime
import pandas as pd
import base64
from PIL import Image
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="UK Right to Work Check",
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        background-color: #1d70b8;
        color: white;
        font-weight: bold;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #144e7c;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .info-heading {
        color: #1d70b8;
        font-weight: bold;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Placeholder for the UK government logo - replace with actual logo in production
def get_uk_gov_logo():
    # This is a placeholder - you should replace with actual UK Gov logo
    image = Image.new('RGB', (200, 50), color = (29, 112, 184))
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# Function to create a downloadable PDF/Image
def get_download_link(check_data, is_employer=False):
    """Generate a download link for the right to work check result"""
    # In a real application, you would generate a proper PDF here
    # For demo purposes, we're creating a CSV file with the check details
    
    # Create a DataFrame with the check information
    df = pd.DataFrame([check_data])
    
    # Convert DataFrame to CSV
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    
    user_type = "Employer" if is_employer else "Employee"
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"UK_Right_To_Work_Check_{user_type}_{current_date}.csv"
    
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download Check Results</a>'
    return href

# Main sidebar navigation
def sidebar():
    with st.sidebar:
        st.image(get_uk_gov_logo())
        st.title("UK Right to Work Check")
        st.markdown("---")
        
        user_type = st.radio(
            "I am an:",
            ["Employee", "Employer"]
        )
        
        st.markdown("---")
        st.markdown("### About this service")
        st.markdown("""
        This service allows you to:
        - Check your right to work in the UK (for employees)
        - Verify an applicant's right to work (for employers)
        - Download proof of right to work status
        """)
        
        st.markdown("---")
        st.markdown("### Need help?")
        st.markdown("""
        Contact the UK Visas and Immigration contact centre if you need help:
        - Telephone: 0300 123 4567
        - Monday to Friday, 9am to 5pm
        """)
    
    return user_type

# Function to simulate check process
def perform_check(share_code, date_of_birth, last_name=None, is_employer=False):
    """Simulate checking right to work status with the UK government."""
    # In a real application, this would make API calls to the UK government systems
    # For demonstration purposes, we'll simulate a successful check
    
    # Validate share code format (should be 9 characters with mix of numbers and letters)
    if not (len(share_code) == 9 and any(c.isalpha() for c in share_code) and any(c.isdigit() for c in share_code)):
        return {
            "status": "error",
            "message": "Invalid share code format. Share codes are typically 9 characters with both letters and numbers."
        }
    
    # Validate date of birth
    try:
        dob_date = datetime.datetime.strptime(date_of_birth, "%Y-%m-%d")
        if dob_date > datetime.datetime.now():
            return {
                "status": "error",
                "message": "Date of birth cannot be in the future."
            }
        
        if datetime.datetime.now().year - dob_date.year < 16:
            return {
                "status": "warning",
                "message": "The person appears to be under 16 years old. Special rules may apply."
            }
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date format."
        }
    
    # For demo purposes, we'll use test data
    # In a real application, you would call the appropriate government API
    
    # Simulate different types of results for demonstration
    if "ERR" in share_code.upper():
        return {
            "status": "error",
            "message": "The share code could not be found. Please check and try again."
        }
    elif "WRN" in share_code.upper():
        return {
            "status": "warning",
            "message": "Right to work check completed, but verification required. This person may have time-limited right to work.",
            "data": {
                "name": f"{last_name or 'Smith'}, John",
                "date_of_birth": date_of_birth,
                "nationality": "Nigerian",
                "immigration_status": "Student Visa",
                "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=180)).strftime("%Y-%m-%d"),
                "restrictions": "Limited to 20 hours work per week during term time",
                "share_code": share_code,
                "check_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "check_performed_by": "Employer Online Service" if is_employer else "Employee Online Service"
            }
        }
    else:
        return {
            "status": "success",
            "message": "Right to work check completed successfully. This person has the right to work in the UK.",
            "data": {
                "name": f"{last_name or 'Smith'}, John",
                "date_of_birth": date_of_birth,
                "nationality": "British" if not last_name else ("EU Settled Status" if len(last_name) % 2 == 0 else "Indefinite Leave to Remain"),
                "immigration_status": "British Citizen" if not last_name else ("EU Settlement Scheme" if len(last_name) % 2 == 0 else "Indefinite Leave to Remain"),
                "expiry_date": "N/A",
                "restrictions": "None",
                "share_code": share_code,
                "check_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "check_performed_by": "Employer Online Service" if is_employer else "Employee Online Service"
            }
        }

# Employee check form
def employee_check_form():
    st.header("Check your right to work in the UK")
    st.markdown("""
    Use this service to prove your right to work in the UK. You can share your right to work status
    with an employer or prospective employer.
    """)
    
    with st.form("employee_form"):
        share_code = st.text_input("Enter your share code", max_chars=9, help="Your 9-character share code from the UK government")
        date_of_birth = st.date_input("Date of Birth", value=datetime.date(1980, 1, 1))
        
        submitted = st.form_submit_button("Check Status")
        
        if submitted:
            # Convert the date to string format YYYY-MM-DD
            dob_str = date_of_birth.strftime("%Y-%m-%d") 
            result = perform_check(share_code, dob_str)
            
            # After form submission, we need to use st.rerun() (not experimental_rerun)
            # Store the result in session state to access after rerun
            st.session_state.employee_result = result
            st.rerun()

# Employer check form
def employer_check_form():
    st.header("Check an applicant's right to work in the UK")
    st.markdown("""
    Use this service to check if an applicant has the right to work in the UK. 
    You must have the applicant's share code and date of birth.
    """)
    
    with st.form("employer_form"):
        share_code = st.text_input("Applicant's share code", max_chars=9, help="The 9-character share code provided by the applicant")
        last_name = st.text_input("Applicant's last name", help="The applicant's last name or family name")
        date_of_birth = st.date_input("Applicant's date of birth", value=datetime.date(1980, 1, 1))
        
        st.markdown("### Employer details")
        employer_name = st.text_input("Your name")
        organization = st.text_input("Organization name")
        
        submitted = st.form_submit_button("Check Applicant Status")
        
        if submitted:
            # Convert the date to string format YYYY-MM-DD
            dob_str = date_of_birth.strftime("%Y-%m-%d")
            result = perform_check(share_code, dob_str, last_name, is_employer=True)
            
            # Add employer information to the result if successful
            if result["status"] in ["success", "warning"] and "data" in result:
                result["data"]["employer_name"] = employer_name
                result["data"]["organization"] = organization
            
            # After form submission, we need to use st.rerun() (not experimental_rerun)
            # Store the result in session state to access after rerun
            st.session_state.employer_result = result
            st.rerun()

# Display check result
def display_check_result(result, is_employer=False):
    if result["status"] == "success":
        st.markdown(f"""
        <div class="success-box">
            <h3>✅ {result["message"]}</h3>
        </div>
        """, unsafe_allow_html=True)
    elif result["status"] == "warning":
        st.markdown(f"""
        <div class="warning-box">
            <h3>⚠️ {result["message"]}</h3>
        </div>
        """, unsafe_allow_html=True)
    else:  # error
        st.markdown(f"""
        <div class="error-box">
            <h3>❌ {result["message"]}</h3>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display the check data
    if "data" in result:
        data = result["data"]
        
        st.markdown("<h3 class='info-heading'>Personal Details</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Name:** {data['name']}")
            st.markdown(f"**Date of Birth:** {data['date_of_birth']}")
            st.markdown(f"**Nationality:** {data['nationality']}")
        with col2:
            st.markdown(f"**Immigration Status:** {data['immigration_status']}")
            st.markdown(f"**Expiry Date:** {data['expiry_date']}")
            st.markdown(f"**Restrictions:** {data['restrictions']}")
        
        st.markdown("<h3 class='info-heading'>Check Details</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Share Code:** {data['share_code']}")
            st.markdown(f"**Check Date:** {data['check_date']}")
        with col2:
            st.markdown(f"**Check Performed By:** {data['check_performed_by']}")
            if is_employer:
                st.markdown(f"**Employer Name:** {data['employer_name']}")
                st.markdown(f"**Organization:** {data['organization']}")
        
        # Download button
        st.markdown("<h3 class='info-heading'>Download Results</h3>", unsafe_allow_html=True)
        st.markdown(get_download_link(data, is_employer), unsafe_allow_html=True)
        
        # Display what to do next
        st.markdown("<h3 class='info-heading'>What to do next</h3>", unsafe_allow_html=True)
        if is_employer:
            st.markdown("""
            1. Save a copy of this check for your records
            2. Complete this check on or before the employee's first day of work
            3. If there are any restrictions, ensure they are followed
            """)
        else:
            st.markdown("""
            1. Save a copy of this check for your records
            2. Share your share code with your employer
            3. Your employer will need to verify your right to work using your share code
            """)

# Main app
def main():
    # Set up the sidebar and get the user type
    user_type = sidebar()
    
    # Main content
    if user_type == "Employee":
        if "employee_result" in st.session_state:
            # Display the result from the last check
            display_check_result(st.session_state.employee_result)
            if st.button("Make Another Check"):
                del st.session_state.employee_result
                st.rerun()
        else:
            # Show the employee check form
            employee_check_form()
    else:  # Employer
        if "employer_result" in st.session_state:
            # Display the result from the last check
            display_check_result(st.session_state.employer_result, is_employer=True)
            if st.button("Make Another Check"):
                del st.session_state.employer_result
                st.rerun()
        else:
            # Show the employer check form
            employer_check_form()

# Run the app
if __name__ == "__main__":
    main()
