import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Aceli Incentives Calculator",
    page_icon="💰",
    layout="wide"
)

# Custom CSS Styling
st.markdown("""
    <style>
    /* Global Styling */
    body {
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
        background-color: #f4f6f9;
    }

    /* Main Container */
    .main-content {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
    }

    /* Headings */
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .subtitle {
        font-size: 1.6rem;
        font-weight: 600;
        color: #34495e;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Form Inputs */
    .stNumberInput, .stSelectbox, .stSlider {
        margin-bottom: 1rem;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-size: 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    /* Results Container */
    .result-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1.5rem;
    }

    .result-container hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Calculation Functions (Unchanged from previous code)
def calculate_base_oi(loan_amount, borrower_type):
    if 10000 <= loan_amount <= 99999:
        if borrower_type == "New Borrower":
            return loan_amount * 0.10
        else:
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
    is_new = (borrower_type == "New Borrower")
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

# Main Application
def main():
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    # Title
    st.markdown("<h1 class='title'>Aceli Incentives Calculator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d; margin-bottom: 1.5rem;'>Calculate your loan incentives with ease</p>", unsafe_allow_html=True)

    # Input Columns
    col1, col2 = st.columns(2)
    with col1:
        loan_amount = st.number_input(
            'Loan Amount ($)', 
            min_value=10000, 
            max_value=1000000, 
            step=1000, 
            value=10000,
            help="Enter the total loan amount between $10,000 and $1,000,000"
        )
        borrower_type = st.selectbox(
            'Borrower Type', 
            ['New Borrower', 'Returning Borrower', 'Repeat Borrower'],
            help="Select the type of borrower based on your lending history"
        )

    with col2:
        loan_type = st.selectbox(
            'Loan Type', 
            ['Formal', 'Informal'],
            help="Choose between Formal and Informal loan types"
        )
        impact_areas = st.slider(
            'Number of Impact Areas', 
            0, 7, 0,
            help="Select the number of impact areas (0-7) to increase your incentives"
        )

    # Additional Impact Areas
    st.markdown("<h2 class='subtitle'>Additional Impact Areas</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        wob = st.checkbox('Women-Owned Business (WOB)')
        yob = st.checkbox('Youth-Owned Business (YOB)')
    
    with col2:
        cne = st.checkbox('Climate & Environment (C&E)')
        climate_tech = st.checkbox('Climate Tech')

    additional_impacts = []
    if wob: additional_impacts.append('WOB')
    if yob: additional_impacts.append('YOB')
    if cne: additional_impacts.append('C&E')
    if climate_tech: additional_impacts.append('Climate Tech')

    # Calculate Button
    if st.button("Calculate Incentives"):
        # Perform calculations
        base_oi = calculate_base_oi(loan_amount, borrower_type)
        impact_bonus = calculate_impact_areas_bonus(loan_amount, borrower_type, impact_areas)
        additional_oi = calculate_additional_incentives(additional_impacts)
        total_oi = base_oi + impact_bonus + additional_oi
        flc = calculate_flc(loan_amount, borrower_type, loan_type, impact_areas)
        combined_total = total_oi + flc

        # Results Display
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        
        # Loan Details Section
        st.markdown("<h3 style='color: #2c3e50; margin-bottom: 1rem;'>🔍 Loan Details</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
            st.write(f"**Borrower Type:** {borrower_type}")
        with col2:
            st.write(f"**Loan Type:** {loan_type}")
            st.write(f"**Impact Areas:** {impact_areas}")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Incentives Breakdown
        st.markdown("<h3 style='color: #2c3e50; margin-bottom: 1rem;'>📊 Incentives Breakdown</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Base OI:** ${base_oi:,.2f}")
            st.write(f"**Impact Areas Bonus:** ${impact_bonus:,.2f}")
        with col2:
            st.write(f"**Additional Impact OI:** ${additional_oi:,.2f}")
            st.write(f"**Total OI:** ${total_oi:,.2f}")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # FLC and Total
        st.markdown("<h3 style='color: #2c3e50; margin-bottom: 1rem;'>💰 Final Calculation</h3>", unsafe_allow_html=True)
        st.write(f"**Total FLC:** ${flc:,.2f}")
        st.markdown(f"<h2 style='color: #27ae60; text-align: center;'>Total Incentives: ${combined_total:,.2f}</h2>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()




