import streamlit as st
import pandas as pd

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
            rates = {
                0: 0, 1: 0.02, 2: 0.03, 3: 0.04, 
                4: 0.045, 5: 0.05, 6: 0.055, 7: 0.06
            }
            return loan_amount * rates[impact_areas]
        else:  # Returning or Repeat
            rates = {
                0: 0, 1: 0.01, 2: 0.015, 3: 0.02, 
                4: 0.0225, 5: 0.025, 6: 0.0275, 7: 0.03
            }
            return loan_amount * rates[impact_areas]
    
    elif 100000 <= loan_amount <= 500000:
        if borrower_type == "New Borrower":
            amounts = {
                0: 0, 1: 2000, 2: 3000, 3: 4000, 
                4: 4500, 5: 5000, 6: 5500, 7: 6000
            }
            return amounts[impact_areas]
        else:  # Returning or Repeat
            amounts = {
                0: 0, 1: 1000, 2: 1500, 3: 2000, 
                4: 2250, 5: 2500, 6: 2750, 7: 3000
            }
            return amounts[impact_areas]
    return 0

def calculate_additional_incentives(additional_impacts):
    return len(additional_impacts) * 1000

# Set up the Streamlit interface
st.title('Aceli Africa Origination Incentives Calculator')

# Input fields
col1, col2 = st.columns(2)

with col1:
    loan_amount = st.number_input('Loan Amount ($)', 
                                 min_value=10000,
                                 max_value=500000,
                                 step=1000,
                                 value=10000)
    borrower_type = st.selectbox('Borrower Type', 
                                ['New Borrower', 'Returning Borrower', 'Repeat Borrower'])
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

# Calculate incentives
if st.button('Calculate Origination Incentive'):
    if loan_amount < 10000:
        st.error('Loan amount must be at least $10,000')
    else:
        base_oi = calculate_base_oi(loan_amount, borrower_type)
        impact_bonus = calculate_impact_areas_bonus(loan_amount, borrower_type, impact_areas)
        additional_oi = calculate_additional_incentives(additional_impacts)
        total_oi = base_oi + impact_bonus + additional_oi

        # Display results
        st.subheader('Calculation Results')
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric('Base OI', f'${base_oi:,.2f}')
        
        with col2:
            st.metric('Impact Areas Bonus', f'${impact_bonus:,.2f}')
            
        with col3:
            st.metric('Additional Impact OI', f'${additional_oi:,.2f}')
        
        with col4:
            st.metric('Total OI', f'${total_oi:,.2f}')

        # Display calculation breakdown
        st.subheader('Calculation Breakdown')
        st.write(f"""
        - Loan Amount: ${loan_amount:,.2f}
        - Borrower Type: {borrower_type}
        - Number of Impact Areas: {impact_areas}
        - Additional Impact Areas: {', '.join(additional_impacts) if additional_impacts else 'None'}
        - Base OI: ${base_oi:,.2f}
        - Impact Areas Bonus: ${impact_bonus:,.2f}
        - Additional Impact OI: ${additional_oi:,.2f}
        - Total OI: ${total_oi:,.2f}
        """)
