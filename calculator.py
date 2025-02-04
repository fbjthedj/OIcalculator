import streamlit as st
import pandas as pd
import pdfplumber
import re
from typing import Dict, Optional

# ---------------------------
# Inject custom CSS styling
# ---------------------------
st.markdown(
    """
    <style>
    /* Global styling */
    html, body, [class*="css"]  {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: #f8f9fa;
    }

    /* Main container styling */
    .main {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 2rem auto;
        max-width: 1200px;
    }

    /* Header styling */
    h1 {
        color: #333333;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    h2, h3, h4, h5, h6 {
        color: #333333;
        font-weight: 600;
    }

    /* Card styling for metrics (if you choose to wrap metrics in a container) */
    .metric {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    /* Button styling */
    .stButton button {
        background-color: #007bff;
        border: none;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 1rem;
        transition: background-color 0.2s ease;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }

    /* Additional spacing for Streamlit columns */
    [data-testid="stHorizontalBlock"] > div {
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Application Functions
# ---------------------------
def calculate_base_oi(loan_amount, borrower_type):
    # First table calculations
    if 10000 <= loan_amount <= 99999:
        if borrower_type == "New Borrower":
            return loan_amount * 0.10
        else:  # Returning or Repeat
            return loan_amount * 0.06
    elif 100000 <= loan_amount <= 199999:
        if borrower_type == "New Borrower":
            return 10000
        else:  # Returning or Repeat
            return 6000
    return 0

def calculate_impact_areas_bonus(loan_amount, borrower_type, impact_areas):
    # Second table calculations
    if 10000 <= loan_amount <= 99999:
        if borrower_type == "New Borrower":
            rates = {0: 0, 1: 0.02, 2: 0.03, 3: 0.04, 4: 0.045, 5: 0.05, 6: 0.055, 7: 0.06}
            return loan_amount * rates[impact_areas]
        else:  # Returning or Repeat
            rates = {0: 0, 1: 0.01, 2: 0.015, 3: 0.02, 4: 0.0225, 5: 0.025, 6: 0.0275, 7: 0.03}
            return loan_amount * rates[impact_areas]
    elif 100000 <= loan_amount <= 500000:
        if borrower_type == "New Borrower":
            amounts = {0: 0, 1: 2000, 2: 3000, 3: 4000, 4: 4500, 5: 5000, 6: 5500, 7: 6000}
            return amounts[impact_areas]
        else:  # Returning or Repeat
            amounts = {0: 0, 1: 1000, 2: 1500, 3: 2000, 4: 2250, 5: 2500, 6: 2750, 7: 3000}
            return amounts[impact_areas]
    return 0

def calculate_additional_incentives(additional_impacts):
    return len(additional_impacts) * 1000

def calculate_flc(loan_amount, borrower_type, loan_type, impact_areas):
    # FLC calculations based on loan ranges and types
    if loan_type == "Formal":
        if 25000 <= loan_amount <= 750000:
            base_rate = 0.04 if borrower_type == "New Borrower" else 0.02
            impact_rate = calculate_flc_impact_rate(loan_amount, borrower_type, impact_areas, "Formal")
            return loan_amount * (base_rate + impact_rate)
    else:  # Informal
        if 25000 <= loan_amount <= 1000000:
            base_rate = 0.06 if borrower_type == "New Borrower" else 0.04
            impact_rate = calculate_flc_impact_rate(loan_amount, borrower_type, impact_areas, "Informal")
            return loan_amount * (base_rate + impact_rate)
    return 0

def calculate_flc_impact_rate(loan_amount, borrower_type, impact_areas, loan_type):
    if impact_areas == 0:
        return 0
    
    is_new = borrower_type == "New Borrower"
    rates = {
        "Formal": {
            "New": {1: 0.01, 2: 0.015, 3: 0.02, 4: 0.0225, 5: 0.025, 6: 0.0275, 7: 0.03},
            "Returning": {1: 0.005, 2: 0.0075, 3: 0.01, 4: 0.0113, 5: 0.0125, 6: 0.0138, 7: 0.015}
        },
        "Informal": {
            "New": {1: 0.01, 2: 0.015, 3: 0.02, 4: 0.0225, 5: 0.025, 6: 0.0275, 7: 0.03},
            "Returning": {1: 0.005, 2: 0.0075, 3: 0.01, 4: 0.0113, 5: 0.0125, 6: 0.0138, 7: 0.015}
        }
    }
    
    borrower_category = "New" if is_new else "Returning"
    return rates[loan_type][borrower_category].get(impact_areas, 0)

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text content from uploaded PDF file."""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting PDF content: {str(e)}")
        return ""

def extract_loan_details(text: str) -> Dict[str, Optional[str]]:
    """Extract key loan details from text content."""
    patterns = {
        'loan_amount': r'(?:loan amount|amount requested|facility amount)[:\s]*([0-9,.]+)',
        'borrower_type': r'(?:borrower type|client type)[:\s]*(\w+)',
        'loan_type': r'(?:loan type|facility type)[:\s]*(\w+)',
        'impact_areas': r'(?:impact areas|social impact)[:\s]*(\d+)',
        'additional_impacts': r'(?:additional impacts|special category)[:\s]*([^\.]+)'
    }
    
    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text.lower())
        results[key] = match.group(1).strip() if match else None
    
    return results

# ---------------------------
# Streamlit Interface
# ---------------------------
# Wrap the content in a styled container
with st.container():
    st.title('🌍 Aceli Incentives Calculator')

    # Input fields arranged in two columns
    col1, col2 = st.columns(2)

    with col1:
        loan_amount = st.number_input('Loan Amount ($)', 
                                      min_value=10000,
                                      max_value=500000,
                                      step=1000,
                                      value=10000)
        borrower_type = st.selectbox('Borrower Type', 
                                     ['New Borrower', 'Returning Borrower', 'Repeat Borrower'])
        loan_type = st.selectbox('Loan Type',
                                 ['Formal', 'Informal'])
        impact_areas = st.slider('Number of Impact Areas', 0, 7, 0)

    with col2:
        st.write('Additional Impact Areas:')
        wob = st.checkbox('Women-Owned Business (WOB)')
        yob = st.checkbox('Youth-Owned Business (YOB)')
        cne = st.checkbox('Climate & Environment (C&E)')
        climate_tech = st.checkbox('Climate Tech')

    # Calculate additional impacts
    additional_impacts = []
    if wob: additional_impacts.append('WOB')
    if yob: additional_impacts.append('YOB')
    if cne: additional_impacts.append('C&E')
    if climate_tech: additional_impacts.append('Climate Tech')

    # Calculate incentives when button is clicked
    if st.button('Calculate Incentives'):
        if loan_amount < 10000:
            st.error('Loan amount must be at least $10,000')
        else:
            # Calculate Origination Incentive (OI)
            base_oi = calculate_base_oi(loan_amount, borrower_type)
            impact_bonus = calculate_impact_areas_bonus(loan_amount, borrower_type, impact_areas)
            additional_oi = calculate_additional_incentives(additional_impacts)
            total_oi = base_oi + impact_bonus + additional_oi

            # Calculate Financial Loss Cover (FLC)
            flc = calculate_flc(loan_amount, borrower_type, loan_type, impact_areas)
            
            # Combined Total Incentives
            combined_total = total_oi + flc

            # Display results
            st.header('Total Incentives')
            st.metric('Combined Total (OI + FLC)', f'${combined_total:,.2f}')
            
            st.subheader('Origination Incentive (OI)')
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric('Base OI', f'${base_oi:,.2f}')
            with col2:
                st.metric('Impact Areas Bonus', f'${impact_bonus:,.2f}')
            with col3:
                st.metric('Additional Impact OI', f'${additional_oi:,.2f}')
            with col4:
                st.metric('Total OI', f'${total_oi:,.2f}')

            st.subheader('Financial Loss Cover (FLC)')
            st.metric('Total FLC', f'${flc:,.2f}')

            st.subheader('Calculation Breakdown')
            st.write(f"""
            **Loan Details:**
            - Loan Amount: ${loan_amount:,.2f}
            - Borrower Type: {borrower_type}
            - Loan Type: {loan_type}
            - Number of Impact Areas: {impact_areas}
            - Additional Impact Areas: {', '.join(additional_impacts) if additional_impacts else 'None'}

            **Totals:**
            - Combined Incentives: ${combined_total:,.2f}
              - Origination Incentive (OI): ${total_oi:,.2f}
                - Base OI: ${base_oi:,.2f}
                - Impact Areas Bonus: ${impact_bonus:,.2f}
                - Additional Impact OI: ${additional_oi:,.2f}
              - Financial Loss Cover (FLC): ${flc:,.2f}
            """)

# ---------------------------
# Optional: Main function for additional workflow
# ---------------------------
def main():
    st.title("🌍 Aceli Incentives Calculator")
    
    # File uploader for PDF documents
    uploaded_file = st.file_uploader("Upload Loan Document (PDF)", type=['pdf'])
    
    if uploaded_file:
        # Extract text from PDF
        text_content = extract_text_from_pdf(uploaded_file)
        
        if text_content:
            # Extract loan details
            loan_details = extract_loan_details(text_content)
            
            st.subheader("Extracted Loan Details")
            st.write("Please verify the extracted information:")
            
            # Allow user to verify/modify extracted values
            loan_amount = st.number_input(
                "Loan Amount ($)", 
                value=float(loan_details['loan_amount'].replace(',', '')) if loan_details['loan_amount'] else 10000,
                min_value=10000,
                max_value=500000
            )
            
            borrower_type = st.selectbox(
                "Borrower Type",
                ["New Borrower", "Returning Borrower", "Repeat Borrower"],
                index=0 if not loan_details['borrower_type'] else None
            )
            
            # ... rest of your existing input fields ...

if __name__ == "__main__":
    main()


