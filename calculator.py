import streamlit as st
import pandas as pd
import re
from typing import Dict, Optional

# ------------------------------------------------------------------------------
# Inject custom CSS styling for a clean, professional look
# ------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Global styling */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        background-color: #f8f9fa;
        color: #333333;
    }
    
    /* Main container */
    .main-container {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 2rem auto;
        max-width: 1000px;
    }
    
    /* Title & Subtitle styling */
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #007bff;
        border: none;
        color: #ffffff;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 1rem;
        transition: background-color 0.2s ease;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    
    /* Breakdown container styling */
    .breakdown-container {
        background-color: #f1f1f1;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    .breakdown-title {
        font-size: 1.75rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .breakdown-item {
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    hr {
        border: 0;
        border-top: 1px solid #e0e0e0;
        margin: 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------------------------
# Incentive Calculation Functions
# ------------------------------------------------------------------------------
def calculate_base_oi(loan_amount, borrower_type):
    if 10000 <= loan_amount <= 99999:
        if borrower_type == "New Borrower":
            return loan_amount * 0.10
        else:  # Returning or Repeat
            return loan_amount * 0.06
    elif 100000 <= loan_amount <= 199999:
        if borrower_type == "New Borrower":
            return 10000
        else:
            return 6000
    return 0

def calculate_impact_areas_bonus(loan_amount, borrower_type, impact_areas):
    if 10000 <= loan_amount <= 99999:
        if borrower_type == "New Borrower":
            rates = {0: 0, 1: 0.02, 2: 0.03, 3: 0.04, 4: 0.045, 5: 0.05, 6: 0.055, 7: 0.06}
            return loan_amount * rates[impact_areas]
        else:
            rates = {0: 0, 1: 0.01, 2: 0.015, 3: 0.02, 4: 0.0225, 5: 0.025, 6: 0.0275, 7: 0.03}
            return loan_amount * rates[impact_areas]
    elif 100000 <= loan_amount <= 500000:
        if borrower_type == "New Borrower":
            amounts = {0: 0, 1: 2000, 2: 3000, 3: 4000, 4: 4500, 5: 5000, 6: 5500, 7: 6000}
            return amounts[impact_areas]
        else:
            amounts = {0: 0, 1: 1000, 2: 1500, 3: 2000, 4: 2250, 5: 2500, 6: 2750, 7: 3000}
            return amounts[impact_areas]
    return 0

def calculate_additional_incentives(additional_impacts):
    return len(additional_impacts) * 1000

def calculate_flc(loan_amount, borrower_type, loan_type, impact_areas):
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

# ------------------------------------------------------------------------------
# Main Interface (No PDF Upload, Only Manual Inputs)
# ------------------------------------------------------------------------------
with st.container():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='title'>🌍 Aceli Incentives Calculator</h1>", unsafe_allow_html=True)
    
    # Input Fields: Two-column layout for clarity
    col1, col2 = st.columns(2)
    with col1:
        loan_amount = st.number_input('Loan Amount ($)', 
                                      min_value=10000,
                                      max_value=500000,
                                      step=1000,
                                      value=10000)
        borrower_type = st.selectbox('Borrower Type', 
                                     ['New Borrower', 'Returning Borrower', 'Repeat Borrower'])
    with col2:
        loan_type = st.selectbox('Loan Type', ['Formal', 'Informal'])
        impact_areas = st.slider('Number of Impact Areas', 0, 7, 0)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("<h2 class='subtitle'>Additional Impact Areas</h2>", unsafe_allow_html=True)
    wob = st.checkbox('Women-Owned Business (WOB)')
    yob = st.checkbox('Youth-Owned Business (YOB)')
    cne = st.checkbox('Climate & Environment (C&E)')
    climate_tech = st.checkbox('Climate Tech')
    
    additional_impacts = []
    if wob: additional_impacts.append('WOB')



