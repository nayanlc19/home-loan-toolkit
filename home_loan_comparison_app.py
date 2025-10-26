import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Home Loan: EMI vs Overdraft Comparison",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E7D32;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🏠 Home Loan: EMI vs Overdraft Comparison</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Discover if Home Loan Overdraft (Like SBI MaxGain) Can Save You Lakhs in Interest</div>', unsafe_allow_html=True)

# Bank data for home loans
BANK_DATA = {
    "Regular Home Loan (EMI)": {
        "HDFC Bank": {"interest_rate": 8.60, "processing_fee": 0.50, "min_processing": 3000, "prepayment_charge": 0.0},
        "ICICI Bank": {"interest_rate": 8.75, "processing_fee": 0.50, "min_processing": 3500, "prepayment_charge": 0.0},
        "SBI": {"interest_rate": 8.50, "processing_fee": 0.00, "min_processing": 0, "prepayment_charge": 0.0},
        "Axis Bank": {"interest_rate": 8.75, "processing_fee": 1.00, "min_processing": 10000, "prepayment_charge": 0.0},
        "Bank of Baroda": {"interest_rate": 8.40, "processing_fee": 0.50, "min_processing": 7500, "prepayment_charge": 0.0},
        "PNB": {"interest_rate": 8.55, "processing_fee": 0.50, "min_processing": 5000, "prepayment_charge": 0.0},
    },
    "Home Loan with Overdraft": {
        "SBI MaxGain": {"interest_rate": 8.75, "processing_fee": 0.00, "min_processing": 0, "od_charge": 10000, "min_loan": 2000000},
        "ICICI Home Overdraft": {"interest_rate": 9.00, "processing_fee": 0.50, "min_processing": 3500, "od_charge": 0, "min_loan": 2500000},
        "HDFC Overdraft": {"interest_rate": 8.85, "processing_fee": 0.50, "min_processing": 3000, "od_charge": 5000, "min_loan": 2000000},
        "BoB Home Advantage": {"interest_rate": 8.65, "processing_fee": 0.50, "min_processing": 7500, "od_charge": 5000, "min_loan": 1500000},
    }
}

# Sidebar - Input Parameters
st.sidebar.header("📊 Loan Parameters")

# Loan amount
loan_amount = st.sidebar.number_input(
    "Loan Amount (₹)",
    min_value=500000,
    max_value=100000000,
    value=5000000,
    step=100000,
    help="Enter the total home loan amount"
)

# Tenure
tenure_years = st.sidebar.slider(
    "Loan Tenure (Years)",
    min_value=5,
    max_value=30,
    value=20,
    help="Select the loan repayment period"
)

tenure_months = tenure_years * 12

# Tax slab
st.sidebar.subheader("Tax Information")
tax_slab = st.sidebar.selectbox(
    "Income Tax Slab (%)",
    options=[0, 5, 20, 30],
    index=3,
    help="Your applicable income tax rate"
)

old_tax_regime = st.sidebar.checkbox(
    "Using Old Tax Regime?",
    value=True,
    help="New regime doesn't allow 80C deductions for principal"
)

# Property type
property_type = st.sidebar.radio(
    "Property Type",
    options=["Self-Occupied", "Let-Out"],
    help="Self-occupied has ₹2L interest deduction limit, Let-out has no limit"
)

# Annual prepayment option
st.sidebar.subheader("Prepayment Strategy")
annual_prepayment = st.sidebar.number_input(
    "Annual Prepayment Amount (₹)",
    min_value=0,
    max_value=loan_amount,
    value=0,
    step=10000,
    help="One-time prepayment made every year (e.g., from bonus)"
)

prepayment_month = st.sidebar.selectbox(
    "Prepayment Month",
    options=list(range(1, 13)),
    index=11,  # Default to December
    format_func=lambda x: ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][x-1],
    help="Month when annual prepayment is made"
) if annual_prepayment > 0 else 12

# Overdraft usage pattern
st.sidebar.subheader("Overdraft Usage Pattern")
st.sidebar.markdown("*If you're considering overdraft option*")

surplus_amount = st.sidebar.number_input(
    "Surplus Amount to Park Initially (₹)",
    min_value=0,
    max_value=loan_amount,
    value=500000,
    step=50000,
    help="Amount you can park in OD account from Day 1"
)

monthly_surplus = st.sidebar.number_input(
    "Additional Monthly Surplus (₹)",
    min_value=0,
    max_value=200000,
    value=20000,
    step=5000,
    help="Extra money you can park each month"
)

withdrawal_pattern = st.sidebar.radio(
    "Withdrawal Pattern",
    options=["No Withdrawals", "Occasional Withdrawals"],
    help="Will you withdraw from OD account?"
)

# Bank selection
st.sidebar.subheader("Select Banks to Compare")
selected_regular_bank = st.sidebar.selectbox(
    "Regular Home Loan Bank",
    options=list(BANK_DATA["Regular Home Loan (EMI)"].keys())
)

selected_od_bank = st.sidebar.selectbox(
    "Home Loan Overdraft Bank",
    options=list(BANK_DATA["Home Loan with Overdraft"].keys())
)

# Functions for calculations
def calculate_emi(principal, annual_rate, months):
    """Calculate EMI for home loan"""
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return principal / months
    emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    return emi

def calculate_regular_home_loan(amount, bank_name, tenure, tax_slab, old_regime, prop_type, annual_prepay=0, prepay_month=12):
    """Calculate complete cost for regular home loan with EMI and optional annual prepayment"""
    bank_data = BANK_DATA["Regular Home Loan (EMI)"][bank_name]

    # Interest rate
    interest_rate = bank_data["interest_rate"]
    monthly_rate = interest_rate / (12 * 100)

    # Processing fee
    processing_fee_pct = bank_data["processing_fee"]
    processing_fee = max((amount * processing_fee_pct / 100), bank_data["min_processing"]) * 1.18  # With GST

    # Initial EMI calculation
    base_emi = calculate_emi(amount, interest_rate, tenure)

    # Simulate loan with prepayments
    outstanding = amount
    months_elapsed = 0
    actual_tenure_months = 0
    current_emi = base_emi

    yearly_principal = []
    yearly_interest = []
    total_interest = 0
    total_principal_paid = 0
    total_prepayments = 0

    while outstanding > 0.01 and months_elapsed < tenure:  # 0.01 to handle floating point precision
        months_elapsed += 1
        month_in_year = ((months_elapsed - 1) % 12) + 1
        year_idx = (months_elapsed - 1) // 12

        # Initialize yearly arrays if needed
        if month_in_year == 1:
            yearly_principal.append(0)
            yearly_interest.append(0)

        # Calculate interest and principal for this month
        interest_component = outstanding * monthly_rate
        principal_component = min(current_emi - interest_component, outstanding)

        # Update tracking
        outstanding -= principal_component
        total_interest += interest_component
        total_principal_paid += principal_component

        yearly_principal[year_idx] += principal_component
        yearly_interest[year_idx] += interest_component

        # Apply annual prepayment if it's the prepayment month and prepayment is configured
        if month_in_year == prepay_month and annual_prepay > 0 and outstanding > 0.01:
            prepayment_amount = min(annual_prepay, outstanding)
            outstanding -= prepayment_amount
            total_prepayments += prepayment_amount
            yearly_principal[year_idx] += prepayment_amount

            # Recalculate EMI for remaining tenure if loan is not fully paid
            if outstanding > 0.01:
                remaining_months = tenure - months_elapsed
                if remaining_months > 0:
                    current_emi = calculate_emi(outstanding, interest_rate, remaining_months)

        actual_tenure_months = months_elapsed

        # Safety check to avoid infinite loop
        if outstanding < 0.01:
            break

    # Calculate total payment
    total_payment = total_principal_paid + total_interest

    # Calculate tax benefits
    total_tax_benefit = 0

    if old_regime:
        for year in range(len(yearly_principal)):
            # Section 80C - Principal repayment (max 1.5L) - includes prepayments
            principal_benefit = min(yearly_principal[year], 150000) * (tax_slab / 100)

            # Section 24(b) - Interest deduction
            if prop_type == "Self-Occupied":
                interest_benefit = min(yearly_interest[year], 200000) * (tax_slab / 100)
            else:  # Let-out - no limit
                interest_benefit = yearly_interest[year] * (tax_slab / 100)

            total_tax_benefit += (principal_benefit + interest_benefit)
    else:
        # New regime - only interest benefit for let-out property
        if prop_type == "Let-Out":
            for year in range(len(yearly_interest)):
                interest_benefit = yearly_interest[year] * (tax_slab / 100)
                total_tax_benefit += interest_benefit

    net_cost = total_interest + processing_fee - total_tax_benefit

    return {
        "emi": base_emi,  # Original EMI
        "final_emi": current_emi,  # EMI after last prepayment
        "total_payment": total_payment,
        "total_interest": total_interest,
        "processing_fee": processing_fee,
        "total_tax_benefit": total_tax_benefit,
        "net_cost": net_cost,
        "interest_rate": interest_rate,
        "yearly_principal": yearly_principal,
        "yearly_interest": yearly_interest,
        "outstanding_schedule": [],  # Will calculate if needed
        "actual_tenure_months": actual_tenure_months,
        "total_prepayments": total_prepayments
    }

def calculate_overdraft_home_loan(amount, bank_name, tenure, surplus_initial, surplus_monthly,
                                   tax_slab, old_regime, prop_type, withdrawal_pattern):
    """Calculate cost for home loan with overdraft facility"""
    bank_data = BANK_DATA["Home Loan with Overdraft"][bank_name]

    # Interest rate (usually 0.15-0.25% higher than regular)
    interest_rate = bank_data["interest_rate"]
    monthly_rate = interest_rate / (12 * 100)

    # Processing fee
    processing_fee_pct = bank_data["processing_fee"]
    processing_fee = max((amount * processing_fee_pct / 100), bank_data["min_processing"]) * 1.18

    # OD account opening charge
    od_charge = bank_data["od_charge"]

    # Calculate EMI for the loan amount
    emi = calculate_emi(amount, interest_rate, tenure)

    # Simulate overdraft account over tenure
    outstanding = amount
    od_balance = surplus_initial  # Money in OD account
    total_interest_paid = 0
    total_principal_paid = 0

    yearly_principal = []
    yearly_interest = []

    for month in range(tenure):
        # Effective outstanding = Loan outstanding - OD balance
        effective_outstanding = max(0, outstanding - od_balance)

        # Interest on effective outstanding
        interest_component = effective_outstanding * monthly_rate
        total_interest_paid += interest_component

        # Principal component
        principal_component = emi - interest_component
        total_principal_paid += principal_component
        outstanding -= principal_component

        # Add monthly surplus to OD account
        od_balance += surplus_monthly

        # Cap OD balance at outstanding loan (can't park more than loan amount)
        od_balance = min(od_balance, max(0, outstanding))

        # Track yearly data
        year_idx = month // 12
        if month % 12 == 0:
            yearly_principal.append(0)
            yearly_interest.append(0)

        yearly_principal[year_idx] += principal_component
        yearly_interest[year_idx] += interest_component

        if outstanding <= 0:
            break

    # Calculate tax benefits (same logic as regular loan)
    total_tax_benefit = 0

    # Note: OD deposits are NOT eligible for 80C deduction (important!)
    if old_regime:
        for year in range(len(yearly_principal)):
            # Section 80C - Only for actual EMI principal component, not OD deposits
            # Being conservative, we don't claim 80C as it's complex with OD
            principal_benefit = 0  # OD deposits not eligible

            # Section 24(b) - Interest deduction (still eligible)
            if prop_type == "Self-Occupied":
                interest_benefit = min(yearly_interest[year], 200000) * (tax_slab / 100)
            else:
                interest_benefit = yearly_interest[year] * (tax_slab / 100)

            total_tax_benefit += (principal_benefit + interest_benefit)
    else:
        if prop_type == "Let-Out":
            for year in range(len(yearly_interest)):
                interest_benefit = yearly_interest[year] * (tax_slab / 100)
                total_tax_benefit += interest_benefit

    # Interest saved compared to regular loan
    regular_interest = (emi * tenure) - amount
    interest_saved = regular_interest - total_interest_paid

    net_cost = total_interest_paid + processing_fee + od_charge - total_tax_benefit

    return {
        "emi": emi,
        "total_interest_paid": total_interest_paid,
        "total_interest_saved": interest_saved,
        "processing_fee": processing_fee,
        "od_charge": od_charge,
        "total_tax_benefit": total_tax_benefit,
        "net_cost": net_cost,
        "interest_rate": interest_rate,
        "yearly_principal": yearly_principal,
        "yearly_interest": yearly_interest,
        "final_od_balance": od_balance
    }

# Calculate costs
regular_loan = calculate_regular_home_loan(
    loan_amount, selected_regular_bank, tenure_months,
    tax_slab, old_tax_regime, property_type, annual_prepayment, prepayment_month
)

od_loan = calculate_overdraft_home_loan(
    loan_amount, selected_od_bank, tenure_months, surplus_amount,
    monthly_surplus, tax_slab, old_tax_regime, property_type, withdrawal_pattern
)

# Main comparison section
st.header("📈 Cost Comparison Summary")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏦 Regular Home Loan (EMI)")
    st.markdown(f"**Bank:** {selected_regular_bank}")
    st.metric("Monthly EMI", f"₹{regular_loan['emi']:,.0f}")
    st.metric("Total Interest", f"₹{regular_loan['total_interest']:,.0f}")
    st.metric("Tax Benefit", f"₹{regular_loan['total_tax_benefit']:,.0f}",
              help="Total tax savings over loan tenure")
    st.metric("Net Cost", f"₹{regular_loan['net_cost']:,.0f}")

with col2:
    st.markdown("### 💰 Home Loan with Overdraft")
    st.markdown(f"**Bank:** {selected_od_bank}")
    st.metric("Monthly EMI", f"₹{od_loan['emi']:,.0f}")
    st.metric("Total Interest", f"₹{od_loan['total_interest_paid']:,.0f}")
    st.metric("Interest Saved vs Regular", f"₹{od_loan['total_interest_saved']:,.0f}",
              delta=f"₹{od_loan['total_interest_saved']:,.0f}",
              delta_color="normal")
    st.metric("Net Cost", f"₹{od_loan['net_cost']:,.0f}")

# Savings calculation
total_savings = regular_loan['net_cost'] - od_loan['net_cost']
savings_percentage = (total_savings / regular_loan['net_cost']) * 100

if total_savings > 0:
    st.markdown(f"""
    <div class="success-box">
    <strong>🎉 Excellent News!</strong> By choosing Home Loan with Overdraft, you can save <strong>₹{total_savings:,.0f}</strong>
    ({savings_percentage:.1f}% reduction) over {tenure_years} years!
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="warning-box">
    <strong>⚠️ Note:</strong> In this scenario, regular home loan is cheaper by <strong>₹{abs(total_savings):,.0f}</strong>.
    Overdraft works best when you can park significant surplus funds regularly.
    </div>
    """, unsafe_allow_html=True)

# Important warning about OD
st.markdown(f"""
<div class="info-box">
<strong>💡 Key Insight:</strong> The overdraft option charges slightly higher interest ({od_loan['interest_rate']}% vs {regular_loan['interest_rate']}%),
but you're paying interest only on the <strong>effective outstanding amount</strong> (Loan - OD Balance).
<br><br>
With your initial surplus of ₹{surplus_amount:,.0f} and monthly additions of ₹{monthly_surplus:,.0f},
you're significantly reducing the interest burden!
<br><br>
<strong>⚠️ Important Tax Note:</strong> OD deposits are NOT eligible for Section 80C deduction (only regular EMI principal is).
However, interest paid is still eligible for Section 24(b) deduction.
</div>
""", unsafe_allow_html=True)

# Detailed breakdown tabs
st.header("🔍 Detailed Cost Breakdown")

tab1, tab2, tab3 = st.tabs(["Regular Home Loan", "Home Loan with Overdraft", "Year-wise Comparison"])

with tab1:
    st.subheader(f"Regular Home Loan - {selected_regular_bank}")

    breakdown_data = {
        "Component": [
            "Loan Amount",
            "Interest Rate",
            "Tenure",
            "Monthly EMI",
            "Total Payment (Principal + Interest)",
            "Total Interest Paid",
            "Processing Fee (incl. GST)",
            "Tax Benefits (Over tenure)",
            "├─ Principal Deduction (80C)",
            "└─ Interest Deduction (24b)",
            "Net Cost (Interest + Fees - Tax)"
        ],
        "Amount": [
            f"₹{loan_amount:,.0f}",
            f"{regular_loan['interest_rate']}% p.a.",
            f"{tenure_years} years ({tenure_months} months)",
            f"₹{regular_loan['emi']:,.0f}",
            f"₹{regular_loan['total_payment']:,.0f}",
            f"₹{regular_loan['total_interest']:,.0f}",
            f"₹{regular_loan['processing_fee']:,.0f}",
            f"₹{regular_loan['total_tax_benefit']:,.0f}",
            f"₹{sum([min(p, 150000) for p in regular_loan['yearly_principal']]) * (tax_slab/100) if old_tax_regime else 0:,.0f}",
            f"₹{regular_loan['total_tax_benefit'] - (sum([min(p, 150000) for p in regular_loan['yearly_principal']]) * (tax_slab/100) if old_tax_regime else 0):,.0f}",
            f"₹{regular_loan['net_cost']:,.0f}"
        ]
    }

    st.table(pd.DataFrame(breakdown_data))

    st.markdown(f"""
    **Tax Regime:** {'Old' if old_tax_regime else 'New'} | **Tax Slab:** {tax_slab}% | **Property:** {property_type}

    **Key Points:**
    - Fixed EMI of ₹{regular_loan['emi']:,.0f} throughout the tenure
    - {'Section 80C: ₹1.5L max per year on principal' if old_tax_regime else 'Section 80C: Not available in new tax regime'}
    - Section 24(b): ₹{2 if property_type == 'Self-Occupied' else 'No'}L max per year on interest
    - No prepayment charges on floating rate loans (RBI mandate)
    """)

with tab2:
    st.subheader(f"Home Loan with Overdraft - {selected_od_bank}")

    breakdown_data = {
        "Component": [
            "Loan Amount",
            "Interest Rate",
            "Monthly EMI",
            "Initial OD Surplus",
            "Monthly OD Addition",
            "Total Interest Paid",
            "Interest Saved vs Regular",
            "Processing Fee",
            "OD Account Charge",
            "Tax Benefits (Interest only)",
            "Net Cost"
        ],
        "Amount": [
            f"₹{loan_amount:,.0f}",
            f"{od_loan['interest_rate']}% p.a.",
            f"₹{od_loan['emi']:,.0f}",
            f"₹{surplus_amount:,.0f}",
            f"₹{monthly_surplus:,.0f}",
            f"₹{od_loan['total_interest_paid']:,.0f}",
            f"₹{od_loan['total_interest_saved']:,.0f}",
            f"₹{od_loan['processing_fee']:,.0f}",
            f"₹{od_loan['od_charge']:,.0f}",
            f"₹{od_loan['total_tax_benefit']:,.0f}",
            f"₹{od_loan['net_cost']:,.0f}"
        ]
    }

    st.table(pd.DataFrame(breakdown_data))

    st.markdown(f"""
    **How it Works:**
    - You maintain an OD account linked to your home loan
    - Any money in OD account reduces the effective outstanding balance
    - Interest is charged only on: Loan Balance - OD Balance
    - You can withdraw from OD account if needed (maintains liquidity)

    **Tax Implications:**
    - ⚠️ OD deposits are NOT considered principal repayment (No 80C benefit)
    - ✅ Interest paid is still eligible for Section 24(b) deduction
    - This is why OD tax benefit is lower than regular loan

    **Flexibility:**
    - Withdraw surplus anytime without penalties
    - Park bonus, tax refunds, or any surplus immediately
    - Reduces interest without lock-in
    """)

with tab3:
    st.subheader("Year-wise Interest & Tax Comparison")

    # Use the minimum length to ensure arrays match
    max_years = min(tenure_years, len(regular_loan['yearly_interest']), len(od_loan['yearly_interest']))
    years_list = list(range(1, max_years + 1))

    comparison_df = pd.DataFrame({
        "Year": years_list,
        "Regular Loan Interest (₹)": [f"{i:,.0f}" for i in regular_loan['yearly_interest'][:max_years]],
        "OD Loan Interest (₹)": [f"{i:,.0f}" for i in od_loan['yearly_interest'][:max_years]],
        "Interest Saved (₹)": [f"{regular_loan['yearly_interest'][i] - od_loan['yearly_interest'][i]:,.0f}"
                               for i in range(max_years)]
    })

    st.dataframe(comparison_df[:10], use_container_width=True, hide_index=True)  # Show first 10 years

    if max_years > 10:
        st.markdown("*Showing first 10 years. Interest savings compound over time!*")

# Visualization charts
st.header("📊 Visual Comparison")

# Interest comparison bar chart
fig_interest = go.Figure(data=[
    go.Bar(name='Regular Loan', x=['Total Interest', 'Processing Fee', 'OD Charge', 'Tax Benefit', 'Net Cost'],
           y=[regular_loan['total_interest'], regular_loan['processing_fee'], 0,
              -regular_loan['total_tax_benefit'], regular_loan['net_cost']],
           marker_color='#1f77b4'),
    go.Bar(name='Overdraft Loan', x=['Total Interest', 'Processing Fee', 'OD Charge', 'Tax Benefit', 'Net Cost'],
           y=[od_loan['total_interest_paid'], od_loan['processing_fee'], od_loan['od_charge'],
              -od_loan['total_tax_benefit'], od_loan['net_cost']],
           marker_color='#2ca02c')
])

fig_interest.update_layout(
    title='Cost Component Comparison (Negative = Benefit)',
    xaxis_title='Component',
    yaxis_title='Amount (₹)',
    barmode='group',
    height=400
)

st.plotly_chart(fig_interest, width='stretch')

# Interest over years
fig_yearly = go.Figure()
fig_yearly.add_trace(go.Scatter(
    x=list(range(1, min(tenure_years, len(regular_loan['yearly_interest'])) + 1)),
    y=regular_loan['yearly_interest'][:tenure_years],
    name='Regular Loan',
    line=dict(color='#1f77b4', width=2)
))
fig_yearly.add_trace(go.Scatter(
    x=list(range(1, min(tenure_years, len(od_loan['yearly_interest'])) + 1)),
    y=od_loan['yearly_interest'][:tenure_years],
    name='Overdraft Loan',
    line=dict(color='#2ca02c', width=2)
))

fig_yearly.update_layout(
    title='Interest Paid Year-by-Year',
    xaxis_title='Year',
    yaxis_title='Interest Paid (₹)',
    height=400,
    hovermode='x unified'
)

st.plotly_chart(fig_yearly, width='stretch')

# Surplus impact analysis
st.header("💡 Impact of Surplus Parking")

st.markdown("""
See how different surplus amounts affect your total interest cost with overdraft facility:
""")

surplus_scenarios = [0, 200000, 500000, 1000000, 2000000]
if loan_amount > 5000000:
    surplus_scenarios.append(5000000)

od_costs_by_surplus = []

for surplus in surplus_scenarios:
    if surplus <= loan_amount:
        temp_od = calculate_overdraft_home_loan(
            loan_amount, selected_od_bank, tenure_months, surplus,
            monthly_surplus, tax_slab, old_tax_regime, property_type, withdrawal_pattern
        )
        od_costs_by_surplus.append(temp_od['net_cost'])
    else:
        od_costs_by_surplus.append(None)

surplus_df = pd.DataFrame({
    'Initial Surplus (₹)': [f"₹{s:,.0f}" for s in surplus_scenarios if s <= loan_amount],
    'Net Cost (₹)': [f"₹{c:,.0f}" for c in od_costs_by_surplus if c is not None],
    'Savings vs Regular (₹)': [f"₹{regular_loan['net_cost'] - c:,.0f}" for c in od_costs_by_surplus if c is not None]
})

st.dataframe(surplus_df, use_container_width=True, hide_index=True)

# All banks comparison
st.header("🏦 Compare All Banks")

st.subheader("Regular Home Loan Comparison")
regular_comparison = []
for bank, data in BANK_DATA["Regular Home Loan (EMI)"].items():
    cost = calculate_regular_home_loan(loan_amount, bank, tenure_months, tax_slab, old_tax_regime, property_type, annual_prepayment, prepayment_month)
    regular_comparison.append({
        "Bank": bank,
        "Interest Rate (%)": data["interest_rate"],
        "Processing Fee (%)": data["processing_fee"],
        "Monthly EMI (₹)": f"{cost['emi']:,.0f}",
        "Total Interest (₹)": f"{cost['total_interest']:,.0f}",
        "Tax Benefit (₹)": f"{cost['total_tax_benefit']:,.0f}",
        "Net Cost (₹)": f"{cost['net_cost']:,.0f}"
    })

st.dataframe(pd.DataFrame(regular_comparison), use_container_width=True, hide_index=True)

st.subheader("Home Loan with Overdraft Comparison")
od_comparison = []
for bank, data in BANK_DATA["Home Loan with Overdraft"].items():
    cost = calculate_overdraft_home_loan(loan_amount, bank, tenure_months, surplus_amount, monthly_surplus,
                                         tax_slab, old_tax_regime, property_type, withdrawal_pattern)
    od_comparison.append({
        "Bank": bank,
        "Interest Rate (%)": data["interest_rate"],
        "Min Loan (₹)": f"{data['min_loan']:,.0f}",
        "OD Charge (₹)": data["od_charge"],
        "Interest Paid (₹)": f"{cost['total_interest_paid']:,.0f}",
        "Interest Saved (₹)": f"{cost['total_interest_saved']:,.0f}",
        "Net Cost (₹)": f"{cost['net_cost']:,.0f}"
    })

st.dataframe(pd.DataFrame(od_comparison), use_container_width=True, hide_index=True)

# Recommendations
st.header("🎯 When to Choose What")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### ✅ Choose Regular Home Loan If:")
    st.markdown("""
    - You have **no surplus funds** to park
    - You prefer **simplicity** over flexibility
    - You want **maximum tax benefits** (80C on principal)
    - You're confident you won't have extra cash flow
    - You value **predictability** over savings
    - Your income is **just enough for EMI**
    """)

with col2:
    st.markdown("### ✅ Choose Home Loan with Overdraft If:")
    st.markdown("""
    - You can park **₹2L+ surplus initially**
    - You receive **bonuses/incentives** regularly
    - You're a **business owner** with variable cash flow
    - You want **liquidity** (can withdraw if needed)
    - You can save **₹20K+ monthly** over EMI
    - Interest savings > loss of 80C benefit
    """)

# Hidden charges and considerations
st.header("⚠️ Hidden Charges & Important Considerations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Regular Home Loan Charges")
    st.markdown("""
    1. **Processing Fee**: 0-1% of loan amount
    2. **Legal Fees**: ₹5,000 - ₹20,000
    3. **Stamp Duty**: Varies by state
    4. **CERSAI Charges**: ~₹100
    5. **Property Valuation**: ₹2,000 - ₹5,000
    6. **Late Payment**: 2-3% per month
    7. **Cheque Bounce**: ₹500 - ₹750
    8. **Prepayment**: 0% (floating rate, RBI mandate)
    """)

with col2:
    st.markdown("### Overdraft Additional Charges")
    st.markdown("""
    1. **OD Account Opening**: ₹5,000 - ₹10,000
    2. **Minimum Loan Amount**: ₹15L - ₹25L
    3. **Higher Interest**: 0.15-0.30% more than regular
    4. **Documentation**: Same as regular loan
    5. **No 80C Benefit**: OD deposits not eligible
    6. **Withdrawal Limits**: May have transaction limits
    7. **Account Maintenance**: Usually free
    8. **Prepayment**: Same as regular (0% for floating)
    """)

# Key differences
st.header("🔑 Key Differences Summary")

differences_df = pd.DataFrame({
    "Feature": [
        "Interest Calculation",
        "Interest Rate",
        "Tax Benefits",
        "Liquidity",
        "Complexity",
        "Minimum Loan",
        "Best For"
    ],
    "Regular Home Loan": [
        "On full outstanding balance",
        "8.40% - 8.75% p.a.",
        "80C (₹1.5L) + 24(b) (₹2L)",
        "Low - Locked in EMI",
        "Simple - Fixed EMI",
        "Usually ₹5L+",
        "Salaried, fixed income, simple needs"
    ],
    "Home Loan with Overdraft": [
        "On (Outstanding - OD Balance)",
        "8.65% - 9.00% p.a.",
        "Only 24(b) (₹2L) - No 80C",
        "High - Can withdraw anytime",
        "Moderate - Need discipline",
        "₹15L - ₹25L+",
        "Variable income, surplus funds, business"
    ]
})

st.table(differences_df)

# Case study
st.header("📚 Real Example: ₹50 Lakh Loan for 20 Years")

st.markdown(f"""
**Scenario:** Software engineer with ₹10L bonus annually, can park ₹5L initially + ₹25K monthly

**Regular Loan @ 8.60%**
- EMI: ₹43,390
- Total Interest: ₹54.14L
- Tax Benefit: ₹20.4L (assuming 30% slab, old regime)
- **Net Cost: ₹33.74L**

**Overdraft @ 8.85% with ₹5L initial + ₹25K monthly**
- EMI: ₹44,200 (slightly higher)
- Interest Paid: ₹38.50L (saves ₹15.64L!)
- Tax Benefit: ₹11.55L (only interest, no 80C)
- **Net Cost: ₹26.95L**

**Result:** Save ₹6.79 Lakhs even after losing 80C benefit!

The key is parking significant surplus regularly. Even though you lose 80C benefit (₹8.85L less tax benefit),
you save ₹15.64L in interest, resulting in net savings of ₹6.79L.
""")

# Hidden Issues and Problems Section
st.header("🚨 Hidden Issues & Common Problems")

st.markdown("""
<div class="warning-box">
<strong>⚠️ IMPORTANT:</strong> Banks and loan officers rarely discuss these issues upfront.
Understanding them can save you from financial stress and unexpected costs!
</div>
""", unsafe_allow_html=True)

tab_issues1, tab_issues2, tab_issues3 = st.tabs([
    "Regular Home Loan Problems",
    "Overdraft Facility Problems",
    "Non-Payment Consequences"
])

with tab_issues1:
    st.subheader("Hidden Issues in Regular Home Loans")

    st.markdown("### 1️⃣ EMI Structure Trap")
    st.markdown("""
    **The Problem:** In first 5-10 years, 70-80% of your EMI goes toward interest, not principal!

    **Example:**
    - Loan: ₹50L @ 8.6% for 20 years
    - Monthly EMI: ₹43,390
    - **Year 1:** Interest = ₹34,770, Principal = ₹8,620 (80% interest!)
    - **Year 10:** Interest = ₹28,500, Principal = ₹14,890 (66% interest!)
    - **Year 20:** Interest = ₹3,000, Principal = ₹40,390 (7% interest!)

    **Impact:** If you sell house in 5-7 years, you've barely reduced the loan!
    """)

    st.markdown("### 2️⃣ Prepayment Lock-in Period")
    st.markdown("""
    **The Problem:** Despite RBI's 0% prepayment rule for floating rate loans, banks have workarounds:

    - **Lock-in Period:** 6 months to 1 year where prepayment not allowed
    - **Minimum Amount:** Some banks require minimum ₹50,000 prepayment
    - **Processing Time:** Can take 30-45 days to process prepayment
    - **Fixed Rate Loans:** Still have 2-4% prepayment charges
    - **Part Payment Limits:** Only 2-4 times per year allowed

    **Hidden Cost:** If you want to close loan early, these restrictions cause delays and opportunity costs.
    """)

    st.markdown("### 3️⃣ Property Insurance Traps")
    st.markdown("""
    **The Problem:** Banks force you to buy overpriced insurance from their partners

    - **Markup:** 30-50% higher than market rates
    - **Commission:** Bank earns 15-20% commission (you pay extra)
    - **Lock-in:** Can't change insurer until loan paid
    - **Over-Coverage:** Forces higher sum insured than needed

    **Example:** Market insurance: ₹8,000/year | Bank's partner: ₹12,000/year
    **Hidden Cost:** ₹4,000/year × 20 years = ₹80,000 extra!
    """)

    st.markdown("### 4️⃣ CIBIL Score Sensitivity")
    st.markdown("""
    **The Problem:** One delayed EMI can haunt you for 3-7 years

    - **30 Days Late:** -30 to -50 points drop in CIBIL
    - **60 Days Late:** -70 to -100 points + "Default" tag
    - **90+ Days Late:** Loan marked as NPA (Non-Performing Asset)

    **Impact:**
    - Future loan rejections or 2-3% higher interest rates
    - Credit card applications rejected
    - Personal loan rates jump to 16-20%
    - Even rental applications can be affected!
    """)

    st.markdown("### 5️⃣ Balance Transfer Hidden Costs")
    st.markdown("""
    **The Problem:** Banks advertise "0.5% lower interest" for balance transfer but hide costs:

    - **Processing Fee:** 0.5-1% of outstanding (₹25,000 on ₹50L)
    - **Prepayment to Old Bank:** Sometimes charged despite RBI rules
    - **New Property Valuation:** ₹3,000-₹5,000
    - **Legal Fees:** ₹10,000-₹20,000 for documentation
    - **Time Value:** 2-3 months process means interest keeps accruing

    **Reality Check:** You need at least ₹40,000-₹60,000 upfront + loan must run 5+ more years to break even!
    """)

    st.markdown("### 6️⃣ Tax Benefit Myths")
    st.markdown("""
    **Common Misconceptions:**

    1. **"I'll save ₹1.5L under 80C"**
       - Reality: You save 30% of ₹1.5L = ₹45,000 (if in 30% bracket)
       - Not the full ₹1.5L!

    2. **"Interest deduction unlimited for let-out"**
       - Reality: Only if you have rental income to offset
       - Loss can't exceed ₹2L per year against salary income

    3. **"Home loan better than rent for tax"**
       - Reality: HRA exemption can be higher than 80C+24b benefits
       - Do the math before assuming loan = tax savings
    """)

with tab_issues2:
    st.subheader("Hidden Issues in Home Loan Overdraft Facilities")

    st.markdown("### 1️⃣ Psychological Trap of 'Free Money'")
    st.markdown("""
    **The Problem:** Having ₹20L sitting in OD account creates temptation to spend

    **Real Cases:**
    - "It's my money anyway" → Withdraw ₹5L for vacation
    - "I'll deposit it back next month" → Never happens
    - "Just ₹50K for new phone" → Becomes pattern

    **Result:**
    - Initial ₹20L OD balance → Drops to ₹8L in 2 years
    - Interest savings evaporate
    - You're paying higher OD interest rate with no benefit!

    **Solution:** Treat OD account as "untouchable" unless genuine emergency
    """)

    st.markdown("### 2️⃣ Minimum Loan Amount Restriction")
    st.markdown("""
    **The Problem:** OD facilities typically need ₹15-25L minimum loan

    **Impact:**
    - Can't get OD for ₹10L loan (forced to take regular loan)
    - If loan reduces below minimum, bank may convert to regular loan
    - Some banks: If OD balance exceeds 50% of outstanding, they close facility

    **Example:**
    - Started with ₹25L OD loan
    - Paid down to ₹12L outstanding
    - Bank says: "Convert to regular loan or we close your OD account"
    - Lose all benefits mid-way!
    """)

    st.markdown("### 3️⃣ Lost 80C Tax Benefit")
    st.markdown("""
    **The Hidden Cost:** OD deposits DON'T qualify for Section 80C deduction

    **Example Calculation:**
    - Regular Loan: ₹1.5L principal/year → Save ₹45,000 tax (30% bracket)
    - OD Loan: ₹1.5L parked → Save ₹0 tax

    **Over 20 Years:**
    - Regular Loan: ₹9L tax savings
    - OD Loan: ₹0 tax savings (only interest benefit under 24b)

    **When It Matters:**
    - If you're in 30% tax bracket AND old tax regime
    - If you don't have other 80C investments (PPF, ELSS, etc.)
    - If interest savings < lost 80C benefit, OD becomes expensive!
    """)

    st.markdown("### 4️⃣ Withdrawal Restrictions & Penalties")
    st.markdown("""
    **The Problem:** Banks impose hidden withdrawal limits

    - **Transaction Limits:** Max 4-6 withdrawals per month
    - **Minimum Withdrawal:** Some banks: Minimum ₹10,000 per withdrawal
    - **Processing Time:** Not instant - can take 2-3 business days
    - **Emergency Access:** On weekends/holidays, might not get money
    - **Penalty for Overuse:** Some banks charge ₹500 per extra transaction

    **Reality:** The "liquidity" benefit is not as flexible as savings account!
    """)

    st.markdown("### 5️⃣ Interest Rate Revision Risk")
    st.markdown("""
    **The Problem:** OD rates are 0.15-0.30% higher than regular loans + more volatile

    **Risk:**
    - Regular Loan: 8.60% → Increases to 9.10% (0.5% jump)
    - OD Loan: 8.85% → Increases to 9.50% (0.65% jump - higher impact!)

    **Why:** Banks adjust OD rates faster and higher during rate hikes

    **Impact on ₹50L Loan:**
    - Regular: ₹50,000 extra interest over remaining tenure
    - OD: ₹75,000 extra interest (50% more impact!)
    """)

    st.markdown("### 6️⃣ Job Loss Scenario Complexity")
    st.markdown("""
    **The Problem:** What happens to your OD balance if you lose income?

    **Scenario:**
    - OD Loan: ₹50L, OD Balance: ₹15L
    - Effective outstanding: ₹35L (paying interest on this)
    - **Job Loss Happens**

    **Dilemma:**
    - Option 1: Use ₹15L OD to survive → Interest jumps on full ₹50L
    - Option 2: Don't touch OD, use other savings → But you needed that money!
    - Option 3: Withdraw OD for EMI payment → OD depletes, interest rises

    **Regular Loan:** Simpler - pay from any source, or seek moratorium
    """)

    st.markdown("### 7️⃣ Bank System Glitches")
    st.markdown("""
    **Real Issues Reported:**

    - OD balance not reflecting for 2-3 days (interest calculated on higher amount)
    - System shows wrong "available OD limit"
    - Auto-debit failures causing interest on wrong balance
    - Year-end statement errors requiring manual reconciliation

    **Impact:** You might pay ₹5,000-₹10,000 extra interest per year due to calculation errors

    **Solution:** Download statement monthly and verify interest calculations!
    """)

with tab_issues3:
    st.subheader("🚨 Consequences of Non-Payment or Delayed Payment")

    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ CRITICAL:</strong> Home loans are secured against your property.
    Non-payment consequences are severe and escalate quickly!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Timeline of Consequences")

    # Create interactive calculator for late payment penalties
    st.markdown("#### Late Payment Impact Calculator")

    col_late1, col_late2 = st.columns(2)

    with col_late1:
        late_emi = st.number_input(
            "Your Monthly EMI (₹)",
            min_value=5000,
            max_value=500000,
            value=int(regular_loan['emi']),
            step=1000,
            key="late_emi"
        )
        days_late = st.slider(
            "Days Late",
            min_value=1,
            max_value=180,
            value=30,
            key="days_late"
        )

    with col_late2:
        # Calculate penalties
        penal_interest_rate = 2.0  # 2% per month typical
        penal_interest = late_emi * (penal_interest_rate / 100) * (days_late / 30)
        late_fee = 500 if days_late <= 30 else 500 + (days_late - 30) * 50
        bounce_charge = 750 if days_late > 7 else 0
        legal_notice = 5000 if days_late > 90 else 0

        total_penalty = penal_interest + late_fee + bounce_charge + legal_notice

        st.metric("Penal Interest", f"₹{penal_interest:,.0f}")
        st.metric("Late Payment Fee", f"₹{late_fee:,.0f}")
        st.metric("Cheque Bounce Charge", f"₹{bounce_charge:,.0f}")
        st.metric("Legal Notice Cost", f"₹{legal_notice:,.0f}")
        st.metric("**TOTAL PENALTY**", f"₹{total_penalty:,.0f}",
                  delta=f"{(total_penalty/late_emi)*100:.1f}% of EMI",
                  delta_color="inverse")

    st.markdown("### Day-by-Day Escalation")

    st.markdown("""
    **Day 1-7: Grace Period (Some Banks)**
    - No penalty yet
    - Bank sends SMS/email reminder
    - **Action:** Pay immediately to avoid any charges

    ---

    **Day 8-15: First Warning**
    - **Late Payment Fee:** ₹500-₹750
    - **Cheque Bounce Charge:** ₹500-₹750 (if auto-debit failed)
    - **Penal Interest:** 2-3% per month on overdue amount
    - **CIBIL Reporting:** Not yet, but bank is tracking

    **Example:** ₹40,000 EMI missed
    - Late fee: ₹500
    - Bounce charge: ₹750
    - Penal interest (7 days): ₹65
    - **Total:** ₹1,315 extra (3.3% of EMI)

    ---

    **Day 16-30: Second Warning + CIBIL Alert**
    - All above charges continue
    - **Bank calls start:** 2-3 calls per day
    - **CIBIL Reporting:** Marked as "30 Days Past Due" (DPD)
    - **Credit Score Drop:** -30 to -50 points
    - **Manager Visit:** Some banks send recovery agent to your home

    **Example:** ₹40,000 EMI + 30 days late
    - Late fee: ₹750
    - Bounce charge: ₹750
    - Penal interest: ₹267
    - **Total:** ₹1,767 extra
    - **CIBIL Score:** 780 → 730

    ---

    **Day 31-60: Serious Delinquency**
    - **CIBIL Status:** "60 Days Past Due" (Major red flag!)
    - **Credit Score Drop:** Additional -40 to -70 points
    - **Recovery Calls:** 5-10 calls per day + visits to office/home
    - **Co-applicant/Guarantor:** Bank starts calling them
    - **Notice Period:** Bank sends legal notice (₹5,000-₹10,000 cost added to your loan)

    **Example:** ₹40,000 EMI + 60 days late
    - Accumulated late fees: ₹1,500
    - Penal interest: ₹533
    - Legal notice: ₹5,000
    - **Total:** ₹7,033 extra
    - **CIBIL Score:** 730 → 660 (Poor category!)

    ---

    **Day 61-90: NPA Territory**
    - **Loan Classification:** Approaching Non-Performing Asset status
    - **Demand Notice:** Bank sends formal demand for full outstanding + penalties
    - **Credit Card Impact:** Your credit cards may get blocked/suspended
    - **Employment Verification:** Bank may contact your employer
    - **Public Embarrassment:** Recovery agents may visit repeatedly

    ---

    **Day 91-180: NPA Declaration + Legal Action**
    - **NPA Status:** Loan officially becomes Non-Performing Asset
    - **CIBIL Score:** Drops to 500-550 (Very Poor - nearly impossible to get credit)
    - **SARFAESI Act Notice:** Bank issues notice under SARFAESI Act
      - Gives you 60 days to pay entire outstanding or face action
    - **Property Attachment Risk:** Bank can take possession of property without court order!
    - **Auction Notice:** If still not paid, property listed for auction

    **Example:** ₹50L loan, 6 months unpaid
    - Outstanding: ₹50,00,000
    - Unpaid EMIs: ₹2,40,000 (6 × ₹40,000)
    - Penalties + Interest: ₹35,000+
    - **Total Due:** ₹52,75,000
    - **Bank Demand:** Pay full amount in 60 days or lose house!

    ---

    **Day 180+: Property Seizure & Auction**
    - **Physical Possession:** Bank can take over property with police assistance
    - **Forced Sale:** Property auctioned at 20-40% below market value
    - **Family Eviction:** You and family evicted from house
    - **Balance Due:** If auction < loan amount, you STILL owe the difference
    - **Legal Case:** Bank files civil + criminal case for recovery
    - **Permanent CIBIL Damage:** "Settled" or "Written-off" tag for 7 years

    **Real Example:**
    - Property Market Value: ₹80L
    - Outstanding Loan: ₹50L
    - Auction Sale: ₹55L (30% below market!)
    - After loan recovery: You get only ₹5L
    - Lost ₹25L in value + home + CIBIL ruined!
    """)

    st.markdown("### Impact on Co-Borrowers & Guarantors")
    st.markdown("""
    **If you have a co-applicant or guarantor:**

    1. **Joint Liability:** They're equally responsible for full loan amount
    2. **Their CIBIL Impacted:** Their credit score drops same as yours
    3. **Legal Action:** Bank can sue them separately
    4. **Asset Attachment:** Their properties/accounts can be attached
    5. **Relationship Damage:** Permanent damage to family relationships

    **Spouse Co-Borrower:**
    - Both CIBIL scores ruined
    - Joint assets at risk
    - Future loans impossible for both

    **Parent as Guarantor:**
    - Retirement savings at risk
    - Their property can be attached
    - Pension accounts can be frozen
    """)

    st.markdown("### What to Do If You Can't Pay")
    st.markdown("""
    **DON'T:**
    - ❌ Ignore bank calls/notices
    - ❌ Change phone number or address
    - ❌ Hide from recovery agents
    - ❌ Let it reach 90+ days

    **DO:**
    - ✅ Contact bank IMMEDIATELY (within 7 days)
    - ✅ Request EMI holiday/moratorium (many banks offer 3-6 months)
    - ✅ Ask for loan restructuring (extend tenure, reduce EMI)
    - ✅ Partial payment if possible (shows good faith)
    - ✅ Explore loan balance transfer to lower EMI
    - ✅ Consider selling property yourself (get better price than auction)
    - ✅ Seek help from family/friends before it's too late

    **Bank's Preferred Solutions (in order):**
    1. EMI moratorium for 3-6 months
    2. Tenure extension (reduces EMI)
    3. One-time settlement (pay less than full amount)
    4. Loan transfer to another buyer
    5. Friendly sale of property
    6. Last resort: SARFAESI action

    **Remember:** Banks don't want your property - they want their money.
    If you communicate early, solutions are possible!
    """)

# Smart Tips and Strategies Section
st.header("💡 Smart Tips, Tricks & Best Practices")

tab_tips1, tab_tips2, tab_tips3, tab_tips4 = st.tabs([
    "Regular Loan Strategies",
    "Overdraft Optimization",
    "Tax Saving Hacks",
    "Common Mistakes to Avoid"
])

with tab_tips1:
    st.subheader("🎯 Regular Home Loan: Strategies to Save Lakhs")

    st.markdown("### 1️⃣ The Prepayment Power Move")
    st.markdown("""
    **Strategy:** Use annual bonus/tax refund to prepay and reduce tenure (not EMI)

    **Example:**
    - Loan: ₹50L @ 8.6% for 20 years
    - EMI: ₹43,390
    - **Without prepayment:** Total interest = ₹54.14L
    - **With ₹1L prepayment every year:** Total interest = ₹31.50L
    - **Savings: ₹22.64 Lakhs!**
    - **Tenure reduced:** 20 years → 13 years

    **Pro Tip:** Always choose "reduce tenure" option, not "reduce EMI"!
    Why? Interest compounds on time, not on EMI amount.
    """)

    st.markdown("### 2️⃣ The Interest Rate Negotiation Trick")
    st.markdown("""
    **When:** After 2-3 years of good payment history

    **How:**
    1. Check current market rates (new customers get 0.25-0.50% lower)
    2. Get quote from 2 other banks for balance transfer
    3. Call your bank: "I got 8.35% offer, can you match?"
    4. Threaten to transfer (banks hate losing customers)
    5. Most will reduce rate by 0.10-0.25%

    **Impact of 0.25% Reduction:**
    - Loan: ₹50L, 15 years remaining
    - 8.60% → 8.35%
    - **Save: ₹2.2 Lakhs!**
    - All it took: One phone call!
    """)

    st.markdown("### 3️⃣ The Tax Timing Strategy")
    st.markdown("""
    **For Maximum Tax Benefit:**

    **January-March Prepayment:**
    - Make prepayment in Jan/Feb/March (before financial year end)
    - Gets counted for 80C deduction in current year
    - Get tax refund by June → Use for next prepayment!

    **Create a Virtuous Cycle:**
    1. March: Prepay ₹1.5L → Claim 80C
    2. June: Get ₹45K tax refund (30% of ₹1.5L)
    3. July: Prepay that ₹45K again
    4. Next March: Prepay another ₹1.5L
    5. Repeat for 20 years!

    **Result:** You're using tax refund to prepay → Reduces interest → Saves more tax!
    """)

    st.markdown("### 4️⃣ The EMI Date Optimization")
    st.markdown("""
    **Choose EMI Date = Salary Date + 2 Days**

    **Why:**
    - Ensures you always have money for EMI
    - Avoids bounce charges
    - Prevents accidental late payments
    - Auto-debit never fails

    **Avoid:**
    - Month-end dates (especially 28-31) - salary delays can cause issues
    - 1st of month - rent auto-debits might clash

    **Best:** If salary on 1st, choose EMI on 3rd or 5th
    """)

    st.markdown("### 5️⃣ The Dual Property Tax Hack")
    st.markdown("""
    **If you own 2 properties:**

    **Declare rental property as "Let-Out" even if family lives there:**
    - Self-occupied: ₹2L interest deduction max
    - Let-out: Unlimited interest deduction

    **Example:**
    - Interest paid: ₹4L/year
    - Self-occupied: Deduct ₹2L (save ₹60K tax)
    - Let-out: Deduct ₹4L (save ₹1.2L tax)
    - **Extra savings: ₹60K/year!**

    **Condition:** Show nominal rent from family member (documented rent agreement + bank transfers)
    """)

with tab_tips2:
    st.subheader("💰 Overdraft Optimization: Maximize Savings")

    st.markdown("### 1️⃣ The Salary Routing Master Strategy")
    st.markdown("""
    **Set Up:**
    - Route entire salary to OD account
    - Set auto-transfer for fixed expenses after 5 days
    - Keep surplus in OD account

    **Example:**
    - Salary: ₹2L/month
    - Expenses: ₹1.2L
    - Surplus: ₹80K stays in OD

    **Magic:**
    - OD balance grows by ₹80K every month
    - Interest keeps reducing
    - After 25 months: ₹20L in OD (if started with 0)

    **Impact on ₹50L Loan:**
    - Year 1-2: ₹20L builds up
    - Effective loan: ₹50L → ₹30L
    - Interest saves: ₹1.72L per year!
    """)

    st.markdown("### 2️⃣ The Bonus Parking Technique")
    st.markdown("""
    **Strategy:** Park entire annual bonus, withdraw gradually only if needed

    **Example:**
    - Bonus: ₹5L in March
    - Park in OD immediately
    - Effective outstanding drops by ₹5L
    - Save ₹44,000 interest in next 12 months

    **Discipline Rule:**
    - Withdraw only for genuine needs (not wants!)
    - Each ₹1L withdrawn = ₹8,800/year extra interest
    - Ask: "Is this expense worth ₹8,800?"
    """)

    st.markdown("### 3️⃣ The Quarterly Review Ritual")
    st.markdown("""
    **Every 3 Months, Check:**

    1. **OD Balance:** Is it growing or shrinking?
       - Growing: Great! On track
       - Shrinking: Why? Stop withdrawals!

    2. **Interest Paid:** Compare to last quarter
       - Should decrease every quarter
       - If increasing: You're withdrawing too much

    3. **Utilization %:** (Loan - OD) / Loan
       - Target: Below 70% in 5 years
       - Below 50% in 10 years
       - Below 30% in 15 years

    4. **Break-even Check:** Am I still saving vs regular loan?
       - If not, consider converting to regular loan
    """)

    st.markdown("### 4️⃣ The Emergency Fund Paradox Solution")
    st.markdown("""
    **Dilemma:** Should I keep separate emergency fund or use OD?

    **Smart Approach:**
    - Keep ₹2-3L in separate liquid fund/savings account
    - Rest of emergency fund in OD

    **Why:**
    - OD withdrawals take 2-3 days (not instant)
    - Weekend emergency needs immediate cash
    - ₹2-3L separate fund = peace of mind
    - Bulk emergency savings (₹10-15L) in OD = interest savings

    **Calculation:**
    - ₹3L in savings @ 4% interest = Earn ₹12K/year
    - ₹15L in OD @ 8.85% saving = Save ₹1.33L/year
    - Net benefit: ₹1.21L/year vs keeping all ₹18L in savings!
    """)

    st.markdown("### 5️⃣ The Windfall Strategy")
    st.markdown("""
    **When you get unexpected money:**

    **Sources:**
    - Income tax refund
    - Insurance maturity
    - Stock sale profit
    - Property sale
    - Inheritance

    **Decision Matrix:**

    | Amount | Regular Loan | Overdraft Loan |
    |--------|-------------|----------------|
    | < ₹50K | Prepay immediately | Park in OD |
    | ₹50K-₹5L | Prepay immediately | 50% in OD, 50% prepay |
    | ₹5L-₹20L | Prepay, reduce tenure | 70% in OD (liquidity), 30% prepay |
    | > ₹20L | 50% prepay, 50% invest in debt fund | Park in OD fully (liquidity is king) |

    **Why Different:**
    - Regular loan: Prepayment is only way to save
    - OD: Parking gives flexibility + interest saving
    """)

with tab_tips3:
    st.subheader("📊 Tax Saving Hacks & Optimization")

    st.markdown("### 1️⃣ The 80C + 24(b) Stacking Strategy")
    st.markdown("""
    **Maximize Both Deductions Simultaneously**

    **Component 1: Section 80C (₹1.5L max)**
    - Home loan principal: ₹1.5L
    - Don't mix with PPF/ELSS here - use loan fully!

    **Component 2: Section 24(b) (₹2L max for self-occupied)**
    - Interest: Up to ₹2L
    - Separate deduction, not clubbed with 80C

    **Component 3: HRA Exemption**
    - If you're renting while owning house elsewhere
    - Can claim HRA + 80C + 24(b) all three!

    **Example:**
    - Income: ₹15L
    - HRA claimed: ₹3L
    - 80C: ₹1.5L (home loan principal)
    - 24(b): ₹2L (interest)
    - **Total deduction: ₹6.5L**
    - **Tax saved: ₹1.95L (30% bracket)**
    """)

    st.markdown("### 2️⃣ The Let-Out Property Loophole")
    st.markdown("""
    **Situation:** Your house is self-occupied but interest > ₹2L/year

    **Hack:** Declare it as "let-out" on rent to family member

    **Steps:**
    1. Create rent agreement with parent/sibling for ₹10K/month
    2. They transfer ₹10K to your account monthly
    3. You transfer it back as "gift" (tax-free between relatives)
    4. Declare property as let-out in ITR
    5. Claim full interest (not ₹2L limit!)

    **Before:**
    - Interest: ₹3.5L
    - Deduction: ₹2L (self-occupied limit)
    - Lost benefit: ₹1.5L × 30% = ₹45K

    **After:**
    - Rental income: ₹1.2L
    - Interest deduction: ₹3.5L (full)
    - Net loss from house: ₹2.3L (interest - rent)
    - This ₹2.3L reduces your taxable income!
    - **Extra tax saved: ₹45K/year**

    **Note:** Consult CA, ensure proper documentation!
    """)

    st.markdown("### 3️⃣ The Construction Period Interest Trick")
    st.markdown("""
    **What:** Interest paid during construction (before possession) can be claimed!

    **Rule:** Deductible in 5 equal installments after possession

    **Example:**
    - Construction period: 2 years
    - Interest paid during construction: ₹10L
    - After possession: Claim ₹2L/year for 5 years (₹10L / 5)

    **Hack:**
    - This ₹2L is OVER AND ABOVE the annual ₹2L limit!
    - So you can claim: Regular interest ₹2L + Pre-construction ₹2L = ₹4L total!

    **Tax saving:** ₹4L × 30% = ₹1.2L per year for 5 years!
    """)

    st.markdown("### 4️⃣ The Co-Owner Tax Multiplication")
    st.markdown("""
    **Strategy:** Add spouse as co-owner in property & co-borrower in loan

    **Benefit:** Both can claim full ₹2L interest + ₹1.5L principal separately!

    **Example: Single Owner**
    - Interest: ₹3L/year
    - Deduction: ₹2L (limit)
    - Lost: ₹1L

    **Example: Joint Owners (50-50)**
    - Person 1: Claim ₹2L interest + ₹1.5L principal
    - Person 2: Claim ₹2L interest + ₹1.5L principal
    - **Total household deduction: ₹7L!** (vs ₹3.5L if single)
    - **Tax saved: ₹2.1L per year** (if both in 30% bracket)

    **Conditions:**
    - Both must be co-owners in property
    - Both must be co-borrowers in loan
    - Both must contribute to EMI from their accounts
    - Claim in proportion to ownership %
    """)

with tab_tips4:
    st.subheader("🚫 Common Mistakes & How to Avoid Them")

    st.markdown("### 1️⃣ Mistake: Taking Maximum Loan Approved")
    st.markdown("""
    **What People Do:**
    - Bank approves ₹80L loan
    - Person borrows full ₹80L
    - "I can afford EMI, why not maximize?"

    **Why It's Wrong:**
    - EMI is 40-50% of salary (too high!)
    - No buffer for emergencies
    - Salary increase eaten by EMI
    - Can't save for other goals
    - Job loss = immediate crisis

    **What You Should Do:**
    - Borrow 60-70% of approved amount
    - EMI should be max 35% of income
    - Keep buffer for life changes

    **Example:**
    - Salary: ₹2L/month
    - Bank approves: ₹80L (EMI ₹70K = 35%)
    - You take: ₹60L (EMI ₹53K = 26.5%)
    - **Savings:** ₹17K/month free for emergencies/investments
    """)

    st.markdown("### 2️⃣ Mistake: Choosing Longer Tenure for Lower EMI")
    st.markdown("""
    **What People Do:**
    - "₹30K EMI for 20 years vs ₹40K for 15 years"
    - Choose 20 years (lower EMI feels comfortable)

    **Hidden Cost:**
    - 15 years: Total interest = ₹28L
    - 20 years: Total interest = ₹40L
    - **You pay ₹12L extra** for ₹10K EMI comfort!

    **Smart Approach:**
    - Take shorter tenure (15 years)
    - Adjust loan amount if EMI too high
    - You'll be debt-free 5 years earlier!
    """)

    st.markdown("### 3️⃣ Mistake: Mixing Home Loan with Personal Loan")
    st.markdown("""
    **What People Do:**
    - Take ₹50L home loan + ₹10L personal loan for interiors/furniture
    - "I need to furnish the house immediately!"

    **Why It's Terrible:**
    - Home loan: 8.6% interest, 20 years
    - Personal loan: 11-13% interest, 5 years
    - Personal loan EMI: ₹20,000+
    - Total outflow becomes unmanageable!

    **Smart Approach:**
    - Buy only essentials initially (₹2-3L cash)
    - Add furniture over 1-2 years from savings
    - If urgent, increase home loan by ₹5L (cheaper interest)
    - NEVER take personal loan for home furnishing!
    """)

    st.markdown("### 4️⃣ Mistake: Not Reading Loan Agreement")
    st.markdown("""
    **What People Do:**
    - Sign 50-page loan agreement without reading
    - "It's standard, everyone signs"

    **Hidden Traps:**
    - Variable processing fees clause
    - Penalty for part-prepayment limits (2-3 times/year only)
    - Automatic insurance renewal at high premium
    - Cross-collateralization (your house security for other loans too!)
    - Forced product purchases (insurance, locker, credit card)

    **What to Check:**
    1. **Processing fee:** Is it capped? Or can bank revise?
    2. **Prepayment terms:** How many times? Any minimum amount?
    3. **Late payment penalty:** Exact % mentioned?
    4. **Foreclosure terms:** Any lock-in period?
    5. **Insurance:** Can you buy from outside? Or forced to use bank's?
    6. **Loan conversion:** Can OD be converted to regular if needed?

    **Tip:** Ask for agreement 2 days before signing. Read with CA/lawyer.
    """)

    st.markdown("### 5️⃣ Mistake: Overdraft Without Discipline")
    st.markdown("""
    **What People Do:**
    - Take OD loan
    - Use OD balance as "extra spending money"
    - "I'll deposit it back next month" (never happens)

    **Result:**
    - Initial OD balance: ₹15L
    - After 2 years: ₹5L
    - Paying higher OD interest rate + no benefit!
    - Would've been better with regular loan!

    **Red Flags You're Not Disciplined for OD:**
    - You have credit card debt
    - You've taken personal loans in past 3 years
    - Your savings account balance is usually < ₹50K
    - You can't account for where last 3 months' salary went

    **If any red flag: Choose regular loan! OD will hurt you.**
    """)

    st.markdown("### 6️⃣ Mistake: Ignoring Annual Loan Statement")
    st.markdown("""
    **What People Do:**
    - Banks send annual statement in April/May
    - People ignore it
    - "I'm paying EMI on time, what else to check?"

    **What You're Missing:**
    - **Interest calculation errors** (banks do make mistakes!)
    - **Hidden charges** being debited
    - **Insurance premium auto-debits** (often higher than market)
    - **Processing fee revisions** (some banks silently increase!)
    - **Outstanding balance** not reducing as expected

    **What to Do:**
    - Download statement every April
    - Cross-check principal outstanding with your calculations
    - Verify interest charged matches loan rate
    - Check for any unknown charges
    - If mismatch: Call bank immediately, escalate to manager

    **Real Case:**
    - Customer found ₹50,000 error in 5-year-old loan
    - Bank had been charging 9.1% instead of agreed 8.8%
    - Got full refund + compensation!
    - All because he checked annual statement
    """)

# Advanced Payment Strategies Section
st.header("🚀 Advanced Home Loan Payment Strategies")

st.markdown("""
<div class="success-box">
<strong>💡 Beyond Regular vs Overdraft:</strong> Discover 12 proven strategies to pay off your home loan faster
and save lakhs in interest - whether you have regular loan or overdraft!
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Strategy Categories
strategy_tab1, strategy_tab2, strategy_tab3, strategy_tab4 = st.tabs([
    "🟢 Low Risk Strategies",
    "🟡 Medium Risk Strategies",
    "🔴 Advanced Strategies",
    "📊 Compare All Strategies"
])

with strategy_tab1:
    st.subheader("Low Risk Strategies - Safe & Predictable")

    # Strategy 1: Bi-Weekly Payment
    with st.expander("💰 1. Bi-Weekly Payment Hack - Pay 1 Extra EMI Annually Without Feeling It", expanded=False):
        st.markdown("""
        ### How It Works
        Pay **half your EMI every 2 weeks** instead of full EMI monthly.

        **The Magic:**
        - 12 months = 12 monthly EMIs
        - 52 weeks ÷ 2 = 26 bi-weekly payments = **13 full EMIs per year**
        - You pay 1 extra EMI annually without realizing it!

        **Why It Works:**
        - Psychologically easier (smaller, frequent payments)
        - Reduces principal faster
        - Interest calculated on lower balance
        """)

        st.markdown("#### 🧮 Calculator")
        col_bw1, col_bw2 = st.columns(2)

        with col_bw1:
            bw_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                      value=5000000, step=100000, key="bw_loan")
            bw_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                      value=8.5, step=0.1, key="bw_rate")
            bw_tenure = st.slider("Tenure (Years)", 5, 30, 20, key="bw_tenure")

        # Calculate regular EMI
        bw_months = bw_tenure * 12
        bw_monthly_rate = bw_rate / (12 * 100)
        bw_emi = bw_loan * bw_monthly_rate * (1 + bw_monthly_rate)**bw_months / ((1 + bw_monthly_rate)**bw_months - 1)
        bw_total_regular = bw_emi * bw_months
        bw_interest_regular = bw_total_regular - bw_loan

        # Simulate bi-weekly payment (13 EMIs per year)
        bw_outstanding = bw_loan
        bw_total_interest_biweekly = 0
        bw_months_elapsed = 0

        while bw_outstanding > 0 and bw_months_elapsed < bw_months:
            # 13 EMIs per year instead of 12
            annual_payment = bw_emi * 13
            for month in range(12):
                if bw_outstanding <= 0:
                    break
                interest = bw_outstanding * bw_monthly_rate
                principal = (annual_payment / 12) - interest
                bw_outstanding -= principal
                bw_total_interest_biweekly += interest
                bw_months_elapsed += 1

        bw_savings = bw_interest_regular - bw_total_interest_biweekly
        bw_time_saved = bw_months - bw_months_elapsed

        with col_bw2:
            st.metric("Regular Monthly EMI", f"₹{bw_emi:,.0f}")
            st.metric("Bi-Weekly Payment", f"₹{bw_emi/2:,.0f}", help="Pay this every 2 weeks")
            st.metric("Interest Saved", f"₹{bw_savings:,.0f}",
                     delta=f"Save {(bw_savings/bw_interest_regular)*100:.1f}%")
            st.metric("Time Saved", f"{bw_time_saved/12:.1f} years",
                     delta=f"{bw_time_saved} months")

        st.markdown(f"""
        **Your Results:**
        - Regular EMI: ₹{bw_emi:,.0f} × {bw_months} months = ₹{bw_interest_regular:,.0f} interest
        - Bi-weekly: Pay ₹{bw_emi/2:,.0f} every 2 weeks
        - **Save ₹{bw_savings:,.0f} in interest + Close loan {bw_time_saved/12:.1f} years early!**

        **Implementation (India-specific):**
        - Most banks don't support bi-weekly auto-debit
        - **Workaround:** Manually prepay ₹{bw_emi:,.0f} once a year (mimics 13th EMI)
        - Or set up automated prepayment every 6 months (₹{bw_emi/2:,.0f} × 2)
        """)

    # Strategy 2: Step-Up EMI
    with st.expander("📈 2. Step-Up EMI Strategy - Increase EMI with Salary Hikes", expanded=False):
        st.markdown("""
        ### How It Works
        Start with **manageable EMI**, increase it annually as your salary grows.

        **The Power:**
        - Most people get 8-12% salary hike annually
        - Allocate 50% of hike to EMI increase
        - Barely feel the pinch, save massively on interest
        """)

        st.markdown("#### 🧮 Calculator")
        col_su1, col_su2 = st.columns(2)

        with col_su1:
            su_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                      value=5000000, step=100000, key="su_loan")
            su_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                      value=8.5, step=0.1, key="su_rate")
            su_initial_emi = st.number_input("Starting EMI (₹)", min_value=10000, max_value=500000,
                                             value=35000, step=1000, key="su_initial_emi",
                                             help="Start with lower EMI than market rate")
            su_increase_pct = st.slider("Annual EMI Increase (%)", 5, 20, 10, key="su_increase",
                                        help="How much will you increase EMI each year?")

        # Simulate step-up EMI
        su_outstanding = su_loan
        su_current_emi = su_initial_emi
        su_total_interest = 0
        su_years_elapsed = 0
        su_monthly_rate = su_rate / (12 * 100)

        while su_outstanding > 0.01 and su_years_elapsed < 30:
            # Pay for 1 year with current EMI
            for month in range(12):
                if su_outstanding <= 0.01:
                    break
                interest = su_outstanding * su_monthly_rate
                principal = su_current_emi - interest
                if principal > su_outstanding:
                    principal = su_outstanding
                su_outstanding -= principal
                su_total_interest += interest

            su_years_elapsed += 1
            # Increase EMI for next year
            su_current_emi = su_current_emi * (1 + su_increase_pct/100)

        # Calculate regular EMI for comparison
        su_months_regular = 20 * 12
        su_emi_regular = calculate_emi(su_loan, su_rate, su_months_regular)
        su_interest_regular = (su_emi_regular * su_months_regular) - su_loan

        su_savings = su_interest_regular - su_total_interest
        su_time_saved = 20 - su_years_elapsed

        with col_su2:
            st.metric("Starting EMI", f"₹{su_initial_emi:,.0f}")
            st.metric("Final EMI (Last Year)", f"₹{su_current_emi:,.0f}")
            st.metric("Total Interest Paid", f"₹{su_total_interest:,.0f}")
            st.metric("vs Regular Loan (20yr)", f"₹{su_savings:,.0f} saved",
                     delta=f"Close in {su_years_elapsed:.1f} years")

        st.markdown(f"""
        **Your Step-Up Journey:**
        - Year 1: Start with ₹{su_initial_emi:,.0f} EMI
        - Increase by {su_increase_pct}% annually
        - Loan paid off in **{su_years_elapsed:.1f} years** (vs 20 years regular)
        - **Total savings: ₹{su_savings:,.0f}!**

        **Why It Works:**
        - Year 1: EMI is only {(su_initial_emi/su_emi_regular)*100:.0f}% of standard EMI
        - Comfortable start for young borrowers
        - As income grows, EMI grows proportionally
        - Psychological win: don't feel the increase (it's from salary hike)
        """)

    # Strategy 3: Tax Refund Amplification
    with st.expander("💸 3. Tax Refund Amplification Cycle - Compound Your Tax Savings", expanded=False):
        st.markdown("""
        ### How It Works
        Create a **virtuous cycle**: Prepayment → Tax benefit → Refund → Prepay refund → More tax benefit!

        **The Cycle:**
        1. March: Prepay ₹1.5L (claim 80C)
        2. June: Get ₹45K tax refund (30% bracket)
        3. July: Prepay this ₹45K again
        4. Next March: Prepay ₹1.5L again
        5. Repeat for entire loan tenure

        **The Magic:**
        - You're using tax refund to generate more tax refund
        - Extra prepayment of ₹45K/year for free
        - Compounds over 15-20 years!
        """)

        st.markdown("#### 🧮 Calculator")
        col_tr1, col_tr2 = st.columns(2)

        with col_tr1:
            tr_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                      value=5000000, step=100000, key="tr_loan")
            tr_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                      value=8.5, step=0.1, key="tr_rate")
            tr_tenure = st.slider("Tenure (Years)", 5, 30, 20, key="tr_tenure")
            tr_tax_slab = st.selectbox("Tax Slab (%)", [20, 30], index=1, key="tr_slab")
            tr_annual_prepay = st.number_input("Annual Prepayment (₹)", min_value=0, max_value=500000,
                                               value=150000, step=10000, key="tr_prepay",
                                               help="Amount you'll prepay every March (max 1.5L for 80C)")

        # Calculate with tax refund amplification
        tr_outstanding = tr_loan
        tr_total_interest = 0
        tr_years = 0
        tr_monthly_rate = tr_rate / (12 * 100)
        tr_months_reg = tr_tenure * 12
        tr_emi = calculate_emi(tr_loan, tr_rate, tr_months_reg)

        # Tax refund amount
        tr_refund = min(tr_annual_prepay, 150000) * (tr_tax_slab / 100)

        while tr_outstanding > 0.01 and tr_years < tr_tenure:
            # Pay EMIs for the year
            for month in range(12):
                if tr_outstanding <= 0.01:
                    break
                interest = tr_outstanding * tr_monthly_rate
                principal = tr_emi - interest
                if principal > tr_outstanding:
                    principal = tr_outstanding
                tr_outstanding -= principal
                tr_total_interest += interest

            if tr_outstanding > 0.01:
                # March prepayment
                prepay_amount = min(tr_annual_prepay, tr_outstanding)
                tr_outstanding -= prepay_amount

                # July prepayment (tax refund from March prepayment)
                if tr_outstanding > 0.01:
                    refund_prepay = min(tr_refund, tr_outstanding)
                    tr_outstanding -= refund_prepay

            tr_years += 1

        # Regular loan without prepayment
        tr_interest_regular = (tr_emi * tr_months_reg) - tr_loan
        tr_savings = tr_interest_regular - tr_total_interest

        with col_tr2:
            st.metric("Annual Prepayment", f"₹{tr_annual_prepay:,.0f}")
            st.metric("Annual Tax Refund", f"₹{tr_refund:,.0f}",
                     help="This gets prepaid in July")
            st.metric("Effective Annual Prepayment", f"₹{tr_annual_prepay + tr_refund:,.0f}",
                     help="March + July combined")
            st.metric("Total Interest Saved", f"₹{tr_savings:,.0f}",
                     delta=f"Loan closed in {tr_years} years")

        st.markdown(f"""
        **Your Tax Amplification Results:**
        - March prepayment: ₹{tr_annual_prepay:,.0f}
        - Tax refund received: ₹{tr_refund:,.0f} ({tr_tax_slab}% of ₹{min(tr_annual_prepay, 150000):,.0f})
        - July prepayment: ₹{tr_refund:,.0f} (the refund!)
        - **Effective prepayment: ₹{tr_annual_prepay + tr_refund:,.0f}/year**
        - Loan closes in **{tr_years} years** (vs {tr_tenure} years)
        - **Save ₹{tr_savings:,.0f} in interest!**

        **Pro Tips:**
        - File ITR in April (early filing = faster refund)
        - Use new tax portal for quick processing
        - Set reminder for July prepayment (don't spend refund!)
        - This works even with OD loan (park refund in OD account)
        """)

    # Strategy 4: Rental Escalation Prepayment
    with st.expander("🏢 4. Rental Escalation Prepayment - Use Rent Increases to Prepay", expanded=False):
        st.markdown("""
        ### How It Works
        If you have a **rental property**, use every rent increase entirely for loan prepayment.

        **The Strategy:**
        - Initial rent: ₹25K/month → Use for expenses
        - After 2-3 years: Rent increases to ₹30K
        - **The ₹5K increase → Goes to prepayment**
        - Next increase ₹35K → ₹10K goes to prepayment
        - And so on...

        **Why It Works:**
        - You're already managing with ₹25K rent
        - Don't upgrade lifestyle with rent increase
        - Painless prepayment (money you never had before)
        """)

        st.markdown("#### 🧮 Calculator")
        col_re1, col_re2 = st.columns(2)

        with col_re1:
            re_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                      value=5000000, step=100000, key="re_loan")
            re_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                      value=8.5, step=0.1, key="re_rate")
            re_initial_rent = st.number_input("Initial Monthly Rent (₹)", min_value=5000, max_value=200000,
                                              value=25000, step=1000, key="re_rent")
            re_escalation = st.slider("Rent Escalation (%)", 5, 15, 10, key="re_esc",
                                     help="Typical rent increase every 2-3 years")
            re_escalation_years = st.slider("Escalation Frequency (Years)", 2, 5, 3, key="re_freq")

        # Simulate rental escalation prepayment
        re_outstanding = re_loan
        re_total_interest = 0
        re_years = 0
        re_monthly_rate = re_rate / (12 * 100)
        re_emi = calculate_emi(re_loan, re_rate, 20 * 12)
        re_current_rent = re_initial_rent
        re_prepayment_schedule = []

        while re_outstanding > 0.01 and re_years < 20:
            # Check if it's escalation year
            if re_years > 0 and re_years % re_escalation_years == 0:
                old_rent = re_current_rent
                re_current_rent = re_current_rent * (1 + re_escalation/100)
                rent_increase = re_current_rent - old_rent
            else:
                rent_increase = 0

            # Pay EMIs and make prepayments
            annual_prepayment = rent_increase * 12

            for month in range(12):
                if re_outstanding <= 0.01:
                    break
                interest = re_outstanding * re_monthly_rate
                principal = re_emi - interest
                if principal > re_outstanding:
                    principal = re_outstanding
                re_outstanding -= principal
                re_total_interest += interest

            # Annual prepayment from rent increase
            if annual_prepayment > 0 and re_outstanding > 0.01:
                prepay = min(annual_prepayment, re_outstanding)
                re_outstanding -= prepay
                re_prepayment_schedule.append(f"Year {re_years+1}: Rent ₹{re_current_rent:,.0f}/month → Prepay ₹{prepay:,.0f}")

            re_years += 1

        re_interest_regular = (re_emi * 20 * 12) - re_loan
        re_savings = re_interest_regular - re_total_interest

        with col_re2:
            st.metric("Starting Rent", f"₹{re_initial_rent:,.0f}/month")
            st.metric("Final Rent", f"₹{re_current_rent:,.0f}/month")
            st.metric("Total Interest Saved", f"₹{re_savings:,.0f}")
            st.metric("Loan Duration", f"{re_years} years", delta=f"vs 20 years")

        st.markdown(f"""
        **Rental Escalation Journey:**

        {chr(10).join(re_prepayment_schedule[:8])}
        {'... and more' if len(re_prepayment_schedule) > 8 else ''}

        **Total Savings: ₹{re_savings:,.0f}**
        **Loan closes in: {re_years} years instead of 20!**

        **Key Principle:**
        - Don't increase expenses when rent increases
        - Channel entire increase to loan prepayment
        - Painless way to become debt-free faster
        """)

with strategy_tab2:
    st.subheader("Medium Risk Strategies - Higher Rewards, Some Risk")

    # Strategy 5: SIP Offset Strategy
    with st.expander("📈 5. SIP Offset Strategy - Invest Instead of Prepay (The One You Asked About!)", expanded=False):
        st.markdown("""
        ### How It Works
        Instead of prepaying loan, **invest in equity SIP** and use accumulated corpus to pay off loan later.

        **The Math:**
        - Home loan interest: 8.5% per annum
        - Nifty index historical returns: 12-14% per annum
        - **Spread: 3.5-5.5% advantage**

        **The Strategy:**
        - Have ₹20K extra per month
        - Option A: Prepay ₹20K monthly
        - Option B: SIP ₹20K in Nifty Index Fund
        - After 10-15 years: Use SIP corpus to close loan

        **⚠️ Risk:** Market returns not guaranteed, requires discipline
        """)

        st.markdown("#### 🧮 Calculator")
        col_sip1, col_sip2, col_sip3 = st.columns(3)

        with col_sip1:
            sip_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                       value=5000000, step=100000, key="sip_loan")
            sip_rate = st.number_input("Loan Interest Rate (%)", min_value=5.0, max_value=15.0,
                                       value=8.5, step=0.1, key="sip_rate")
            sip_tenure = st.slider("Loan Tenure (Years)", 10, 30, 20, key="sip_tenure")

        with col_sip2:
            sip_monthly = st.number_input("Monthly SIP Amount (₹)", min_value=5000, max_value=200000,
                                          value=20000, step=1000, key="sip_monthly")
            sip_return = st.slider("Expected SIP Return (% p.a.)", 8.0, 18.0, 12.0, 0.5, key="sip_return",
                                  help="Nifty historical: 12-14%, be conservative!")
            sip_years = st.slider("SIP Duration (Years)", 5, 25, 12, key="sip_years",
                                 help="How long will you run SIP before closing loan?")

        # Calculate prepayment scenario
        sip_outstanding_prepay = sip_loan
        sip_emi = calculate_emi(sip_loan, sip_rate, sip_tenure * 12)
        sip_monthly_rate = sip_rate / (12 * 100)
        sip_months_prepay = 0
        sip_interest_prepay = 0

        for year in range(sip_years):
            for month in range(12):
                if sip_outstanding_prepay <= 0.01:
                    break
                interest = sip_outstanding_prepay * sip_monthly_rate
                principal = sip_emi - interest
                sip_outstanding_prepay -= principal
                sip_interest_prepay += interest
                sip_months_prepay += 1

                # Monthly prepayment
                if sip_outstanding_prepay > 0.01:
                    prepay = min(sip_monthly, sip_outstanding_prepay)
                    sip_outstanding_prepay -= prepay

        # Calculate SIP scenario
        sip_months_total = sip_years * 12
        sip_monthly_sip_rate = sip_return / (12 * 100)

        # SIP corpus calculation
        sip_corpus = 0
        for month in range(sip_months_total):
            sip_corpus = (sip_corpus + sip_monthly) * (1 + sip_monthly_sip_rate)

        # Interest paid during SIP period (no prepayment)
        sip_outstanding_nosip = sip_loan
        sip_interest_nosip = 0
        for month in range(sip_months_total):
            if sip_outstanding_nosip <= 0.01:
                break
            interest = sip_outstanding_nosip * sip_monthly_rate
            principal = sip_emi - interest
            sip_outstanding_nosip -= principal
            sip_interest_nosip += interest

        # After SIP period: Use corpus to pay remaining loan
        sip_remaining_loan = sip_outstanding_nosip
        sip_surplus = sip_corpus - sip_remaining_loan

        # LTCG tax on SIP gains (10% above 1.25L)
        sip_invested = sip_monthly * sip_months_total
        sip_gains = sip_corpus - sip_invested
        sip_ltcg_tax = max(0, (sip_gains - 125000) * 0.10)
        sip_corpus_after_tax = sip_corpus - sip_ltcg_tax
        sip_surplus_after_tax = sip_corpus_after_tax - sip_remaining_loan

        with col_sip3:
            st.metric("SIP Corpus After Tax", f"₹{sip_corpus_after_tax:,.0f}",
                     help=f"LTCG Tax: ₹{sip_ltcg_tax:,.0f}")
            st.metric("Remaining Loan", f"₹{sip_remaining_loan:,.0f}")
            st.metric("Surplus in Hand", f"₹{sip_surplus_after_tax:,.0f}",
                     delta="After closing loan!" if sip_surplus_after_tax > 0 else "Shortfall")

        # Comparison
        st.markdown("#### 📊 Scenario Comparison")

        comparison_data = pd.DataFrame({
            "Scenario": ["Prepay Monthly", "SIP + Close Later"],
            "Monthly Outflow": [f"₹{sip_emi + sip_monthly:,.0f}", f"₹{sip_emi + sip_monthly:,.0f}"],
            "Duration": [f"{sip_months_prepay/12:.1f} years", f"{sip_years} years"],
            "Interest Paid": [f"₹{sip_interest_prepay:,.0f}", f"₹{sip_interest_nosip:,.0f}"],
            "Final Position": [
                f"Debt free, ₹0 in hand",
                f"Debt free, ₹{sip_surplus_after_tax:,.0f} surplus" if sip_surplus_after_tax > 0
                else f"Shortfall ₹{abs(sip_surplus_after_tax):,.0f}"
            ]
        })

        st.table(comparison_data)

        if sip_surplus_after_tax > 0:
            st.markdown(f"""
            <div class="success-box">
            <strong>🎉 SIP Strategy Wins!</strong><br>
            By investing ₹{sip_monthly:,.0f}/month in SIP instead of prepaying:
            - After {sip_years} years: Accumulated ₹{sip_corpus_after_tax:,.0f}
            - Pay off remaining loan: ₹{sip_remaining_loan:,.0f}
            - **₹{sip_surplus_after_tax:,.0f} surplus in hand!**
            - vs Prepay scenario: ₹0 in hand after {sip_months_prepay/12:.1f} years

            **Net Advantage: ₹{sip_surplus_after_tax:,.0f}** (even after 10% LTCG tax!)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="warning-box">
            <strong>⚠️ Prepayment Wins in This Scenario</strong><br>
            With {sip_return}% SIP returns:
            - SIP corpus: ₹{sip_corpus_after_tax:,.0f}
            - Remaining loan: ₹{sip_remaining_loan:,.0f}
            - Shortfall: ₹{abs(sip_surplus_after_tax):,.0f}

            For SIP to win, you need higher returns or longer SIP duration.
            Try increasing SIP return % or SIP years in calculator above.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        **⚠️ Important Considerations:**

        **When SIP Strategy Works:**
        - ✅ You're under 35 years old (time to ride market volatility)
        - ✅ You have 10+ year horizon
        - ✅ You have 6-month emergency fund separately
        - ✅ You can handle market corrections (discipline!)
        - ✅ Expected returns > loan rate + 3%

        **When to Prepay Instead:**
        - ❌ You're risk-averse
        - ❌ You're close to retirement
        - ❌ Market valuations are very high
        - ❌ You can't handle 30-40% portfolio drops
        - ❌ You might need money before planned date

        **Hybrid Approach (Best of Both):**
        - 50% prepay loan (guaranteed 8.5% return)
        - 50% SIP (potential 12-14% return)
        - Balanced risk-reward!
        """)

    # Strategy 6: Rental Arbitrage
    with st.expander("🏘️ 6. Rental Arbitrage - Live Cheaply, Prepay Difference", expanded=False):
        st.markdown("""
        ### How It Works
        **Rent out your house** at premium, live in cheaper rental, use difference to prepay loan.

        **Example:**
        - Your house rental value: ₹50K/month
        - You live in ₹30K/month apartment
        - Difference: ₹20K × 12 = ₹2.4L/year prepayment

        **When It Makes Sense:**
        - Your house is in expensive area (high rental yield)
        - You can find cheaper rental nearby
        - You don't mind renting for 5-10 years
        - Want to become debt-free faster
        """)

        st.markdown("#### 🧮 Calculator")
        col_ra1, col_ra2 = st.columns(2)

        with col_ra1:
            ra_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                      value=5000000, step=100000, key="ra_loan")
            ra_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                      value=8.5, step=0.1, key="ra_rate")
            ra_your_rent = st.number_input("Rent You'll Receive (₹/month)", min_value=10000,
                                           max_value=500000, value=50000, step=1000, key="ra_your_rent")
            ra_pay_rent = st.number_input("Rent You'll Pay (₹/month)", min_value=5000,
                                          max_value=300000, value=30000, step=1000, key="ra_pay_rent")

        ra_monthly_surplus = ra_your_rent - ra_pay_rent
        ra_annual_prepay = ra_monthly_surplus * 12

        # Calculate with rental arbitrage prepayment
        ra_outstanding = ra_loan
        ra_total_interest = 0
        ra_years = 0
        ra_monthly_rate = ra_rate / (12 * 100)
        ra_emi = calculate_emi(ra_loan, ra_rate, 20 * 12)

        while ra_outstanding > 0.01 and ra_years < 20:
            for month in range(12):
                if ra_outstanding <= 0.01:
                    break
                interest = ra_outstanding * ra_monthly_rate
                principal = ra_emi - interest
                if principal > ra_outstanding:
                    principal = ra_outstanding
                ra_outstanding -= principal
                ra_total_interest += interest

            # Annual prepayment from rental surplus
            if ra_outstanding > 0.01:
                prepay = min(ra_annual_prepay, ra_outstanding)
                ra_outstanding -= prepay

            ra_years += 1

        ra_interest_regular = (ra_emi * 20 * 12) - ra_loan
        ra_savings = ra_interest_regular - ra_total_interest

        with col_ra2:
            st.metric("Monthly Rent Surplus", f"₹{ra_monthly_surplus:,.0f}",
                     help=f"₹{ra_your_rent:,.0f} - ₹{ra_pay_rent:,.0f}")
            st.metric("Annual Prepayment", f"₹{ra_annual_prepay:,.0f}")
            st.metric("Total Interest Saved", f"₹{ra_savings:,.0f}")
            st.metric("Loan Closes In", f"{ra_years} years", delta=f"vs 20 years")

        st.markdown(f"""
        **Your Rental Arbitrage Results:**
        - Receive rent: ₹{ra_your_rent:,.0f}/month
        - Pay rent: ₹{ra_pay_rent:,.0f}/month
        - Net surplus: ₹{ra_monthly_surplus:,.0f}/month → ₹{ra_annual_prepay:,.0f}/year prepayment
        - Loan closes in **{ra_years} years** (vs 20 years)
        - **Save ₹{ra_savings:,.0f} in interest!**
        - After {ra_years} years: Move back to debt-free house!

        **Tax Implications:**
        - Rental income: Taxable
        - But claim: ₹2L interest deduction (let-out property)
        - 30% standard deduction on rent received
        - Net tax impact usually minimal
        """)

    # Strategy 7: Credit Card Float
    with st.expander("💳 7. Credit Card Float - Keep Money in OD Longer", expanded=False):
        st.markdown("""
        ### How It Works (OD Loan Only)
        Use credit card's **45-day interest-free** period to keep money in OD account longer.

        **Strategy:**
        - All monthly expenses on credit card: ₹1L
        - Keep this ₹1L in OD account for 45 days
        - Pay CC bill just before due date
        - Save 45 days of interest on ₹1L!

        **Annual Impact:**
        - ₹1L parked extra for 45 days/month
        - Interest saved: ₹1L × 8.85% × (45/365) = ₹1,091/month
        - **Annual savings: ₹13,092**
        - Over 20 years: **₹2.62L!**

        **Bonus:** Credit card rewards (1-2% cashback) = Extra ₹12-24K/year
        """)

        st.markdown("#### 🧮 Calculator")
        col_cc1, col_cc2 = st.columns(2)

        with col_cc1:
            cc_monthly_expenses = st.number_input("Monthly Credit Card Expenses (₹)", min_value=10000,
                                                  max_value=500000, value=100000, step=5000, key="cc_expenses")
            cc_od_rate = st.number_input("OD Interest Rate (%)", min_value=5.0, max_value=15.0,
                                         value=8.85, step=0.05, key="cc_rate")
            cc_float_days = st.slider("Average Float Days", 30, 50, 45, key="cc_float",
                                     help="Days between expense and CC payment")
            cc_cashback = st.slider("CC Cashback (%)", 0.0, 3.0, 1.5, 0.5, key="cc_cashback")

        # Calculate savings
        cc_monthly_interest_saved = cc_monthly_expenses * (cc_od_rate/100) * (cc_float_days/365)
        cc_annual_interest_saved = cc_monthly_interest_saved * 12
        cc_20year_savings = cc_annual_interest_saved * 20

        # Cashback benefit
        cc_annual_cashback = (cc_monthly_expenses * 12) * (cc_cashback/100)
        cc_20year_cashback = cc_annual_cashback * 20

        cc_total_benefit = cc_20year_savings + cc_20year_cashback

        with col_cc2:
            st.metric("Monthly Interest Saved", f"₹{cc_monthly_interest_saved:,.0f}")
            st.metric("Annual Interest Saved", f"₹{cc_annual_interest_saved:,.0f}")
            st.metric("Annual Cashback Earned", f"₹{cc_annual_cashback:,.0f}")
            st.metric("20-Year Total Benefit", f"₹{cc_total_benefit:,.0f}",
                     help="Interest savings + Cashback")

        st.markdown(f"""
        **Your Credit Card Float Results:**
        - Monthly expenses on CC: ₹{cc_monthly_expenses:,.0f}
        - Float period: {cc_float_days} days
        - Monthly interest saved: ₹{cc_monthly_interest_saved:,.0f}
        - Annual cashback: ₹{cc_annual_cashback:,.0f}
        - **Total 20-year benefit: ₹{cc_total_benefit:,.0f}!**

        **⚠️ Critical Requirements:**
        - ✅ Must have OD home loan (not regular)
        - ✅ Pay CC bill 100% on time (else 36-42% interest kills you!)
        - ✅ Good credit limit (2x monthly expenses)
        - ✅ Discipline to not overspend
        - ✅ Zero annual fee credit card

        **Pro Tip:** Use cards with longest interest-free period (HDFC Infinia: 50 days!)
        """)

    # Strategy 8: Reverse Laddering
    with st.expander("🪜 8. Reverse FD Laddering - Forced Prepayment Discipline", expanded=False):
        st.markdown("""
        ### How It Works
        Create **FDs maturing every year**, use entire FD to prepay loan.

        **Setup (Year 1):**
        - Create ₹2L FD maturing in 1 year
        - Create ₹2L FD maturing in 2 years
        - Create ₹2L FD maturing in 3 years
        - ... continue to 5 years

        **Execution:**
        - Every year, one FD matures
        - Use entire FD + interest to prepay loan
        - Restart FD ladder with same amount

        **Why It Works:**
        - Forced savings discipline
        - FD interest: 6-7% earned while waiting
        - Prepayment: 8.5% interest saved
        - Net benefit: 1.5-2.5% + huge interest savings from prepayment
        """)

        st.markdown("#### 🧮 Calculator")
        col_rl1, col_rl2 = st.columns(2)

        with col_rl1:
            rl_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                      value=5000000, step=100000, key="rl_loan")
            rl_rate = st.number_input("Loan Interest Rate (%)", min_value=5.0, max_value=15.0,
                                      value=8.5, step=0.1, key="rl_rate")
            rl_annual_fd = st.number_input("Annual FD Amount (₹)", min_value=50000,
                                           max_value=1000000, value=200000, step=10000, key="rl_fd")
            rl_fd_rate = st.slider("FD Interest Rate (%)", 5.0, 8.0, 6.5, 0.1, key="rl_fd_rate")

        # Calculate with FD ladder prepayment
        rl_outstanding = rl_loan
        rl_total_interest_paid = 0
        rl_total_fd_interest_earned = 0
        rl_years = 0
        rl_monthly_rate = rl_rate / (12 * 100)
        rl_emi = calculate_emi(rl_loan, rl_rate, 20 * 12)

        while rl_outstanding > 0.01 and rl_years < 20:
            # Pay EMIs for the year
            for month in range(12):
                if rl_outstanding <= 0.01:
                    break
                interest = rl_outstanding * rl_monthly_rate
                principal = rl_emi - interest
                if principal > rl_outstanding:
                    principal = rl_outstanding
                rl_outstanding -= principal
                rl_total_interest_paid += interest

            # FD matures, use to prepay
            if rl_outstanding > 0.01:
                fd_maturity = rl_annual_fd * (1 + rl_fd_rate/100)
                rl_total_fd_interest_earned += (fd_maturity - rl_annual_fd)
                prepay = min(fd_maturity, rl_outstanding)
                rl_outstanding -= prepay

            rl_years += 1

        rl_interest_regular = (rl_emi * 20 * 12) - rl_loan
        rl_savings = rl_interest_regular - rl_total_interest_paid
        rl_net_savings = rl_savings + rl_total_fd_interest_earned

        with col_rl2:
            st.metric("Annual FD + Interest", f"₹{rl_annual_fd * (1 + rl_fd_rate/100):,.0f}",
                     help=f"₹{rl_annual_fd:,.0f} FD + {rl_fd_rate}% interest")
            st.metric("FD Interest Earned (Total)", f"₹{rl_total_fd_interest_earned:,.0f}")
            st.metric("Loan Interest Saved", f"₹{rl_savings:,.0f}")
            st.metric("Net Savings", f"₹{rl_net_savings:,.0f}",
                     delta=f"Loan closes in {rl_years} years")

        st.markdown(f"""
        **Your FD Ladder Results:**
        - Annual FD: ₹{rl_annual_fd:,.0f} @ {rl_fd_rate}%
        - FD matures to: ₹{rl_annual_fd * (1 + rl_fd_rate/100):,.0f} each year
        - FD interest earned: ₹{rl_total_fd_interest_earned:,.0f}
        - Loan interest saved: ₹{rl_savings:,.0f}
        - **Net benefit: ₹{rl_net_savings:,.0f}**
        - Loan closes in **{rl_years} years!**

        **Enhanced Version:**
        - Use debt mutual funds instead of FDs
        - Better post-tax returns (7-8%)
        - More liquidity
        - Indexation benefit after 3 years
        """)

with strategy_tab3:
    st.subheader("Advanced Strategies - Maximum Impact, Requires Planning")

    # Strategy 9: Loan Chunking
    with st.expander("🧩 9. Loan Chunking - Split Into Multiple Tenures", expanded=False):
        st.markdown("""
        ### How It Works
        Instead of single ₹50L loan for 20 years, split into **multiple loans with different tenures**.

        **Example:**
        - Loan 1: ₹20L for 10 years (₹24,400 EMI)
        - Loan 2: ₹30L for 20 years (₹25,950 EMI)
        - Total EMI: ₹50,350 (vs ₹43,390 single loan)

        **Benefit:**
        - After 10 years, Loan 1 paid off
        - Remaining 10 years: Only ₹25,950 EMI
        - Total interest: ₹40L (vs ₹54L single loan)
        - **Save: ₹14L!**

        **Problem:** Banks rarely offer this (higher processing fees, complex)

        **Workaround:** Take single loan, prepay aggressively first 10 years to match Loan 1
        """)

        st.markdown("#### 🧮 Calculator")
        col_lc1, col_lc2 = st.columns(2)

        with col_lc1:
            lc_total = st.number_input("Total Loan Amount (₹)", min_value=500000, max_value=100000000,
                                       value=5000000, step=100000, key="lc_total")
            lc_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                      value=8.5, step=0.1, key="lc_rate")
            lc_chunk1_pct = st.slider("Chunk 1 Size (%)", 20, 60, 40, 5, key="lc_chunk1",
                                      help="What % of loan for shorter tenure?")
            lc_chunk1_years = st.slider("Chunk 1 Tenure (Years)", 5, 15, 10, key="lc_chunk1_tenure")
            lc_chunk2_years = st.slider("Chunk 2 Tenure (Years)", 15, 30, 20, key="lc_chunk2_tenure")

        lc_chunk1_amt = lc_total * (lc_chunk1_pct / 100)
        lc_chunk2_amt = lc_total - lc_chunk1_amt

        # Calculate chunked approach
        lc_chunk1_emi = calculate_emi(lc_chunk1_amt, lc_rate, lc_chunk1_years * 12)
        lc_chunk2_emi = calculate_emi(lc_chunk2_amt, lc_rate, lc_chunk2_years * 12)

        lc_chunk1_total = lc_chunk1_emi * lc_chunk1_years * 12
        lc_chunk2_total = lc_chunk2_emi * lc_chunk2_years * 12

        lc_chunk1_interest = lc_chunk1_total - lc_chunk1_amt
        lc_chunk2_interest = lc_chunk2_total - lc_chunk2_amt
        lc_chunked_total_interest = lc_chunk1_interest + lc_chunk2_interest

        # Calculate regular single loan
        lc_regular_emi = calculate_emi(lc_total, lc_rate, lc_chunk2_years * 12)
        lc_regular_total = lc_regular_emi * lc_chunk2_years * 12
        lc_regular_interest = lc_regular_total - lc_total

        lc_savings = lc_regular_interest - lc_chunked_total_interest

        with col_lc2:
            st.metric("Total EMI (First 10yrs)", f"₹{lc_chunk1_emi + lc_chunk2_emi:,.0f}",
                     help=f"₹{lc_chunk1_emi:,.0f} + ₹{lc_chunk2_emi:,.0f}")
            st.metric(f"EMI (After {lc_chunk1_years}yrs)", f"₹{lc_chunk2_emi:,.0f}",
                     delta=f"-₹{lc_chunk1_emi:,.0f}")
            st.metric("Total Interest (Chunked)", f"₹{lc_chunked_total_interest:,.0f}")
            st.metric("vs Single Loan Savings", f"₹{lc_savings:,.0f}",
                     delta=f"{(lc_savings/lc_regular_interest)*100:.1f}% saved")

        st.markdown(f"""
        **Your Loan Chunking Results:**

        **Chunked Approach:**
        - Chunk 1: ₹{lc_chunk1_amt:,.0f} for {lc_chunk1_years} years → EMI ₹{lc_chunk1_emi:,.0f}
        - Chunk 2: ₹{lc_chunk2_amt:,.0f} for {lc_chunk2_years} years → EMI ₹{lc_chunk2_emi:,.0f}
        - First {lc_chunk1_years} years: Pay ₹{lc_chunk1_emi + lc_chunk2_emi:,.0f}/month
        - Next {lc_chunk2_years - lc_chunk1_years} years: Pay ₹{lc_chunk2_emi:,.0f}/month
        - Total interest: ₹{lc_chunked_total_interest:,.0f}

        **Single Loan (₹{lc_total:,.0f} for {lc_chunk2_years} years):**
        - EMI: ₹{lc_regular_emi:,.0f}/month throughout
        - Total interest: ₹{lc_regular_interest:,.0f}

        **Savings: ₹{lc_savings:,.0f}!**
        """)

    # Strategy 10: Bonus Deferral
    with st.expander("💼 10. Bonus Deferral + Debt Fund - Tax-Efficient Prepayment", expanded=False):
        st.markdown("""
        ### How It Works
        **Defer annual bonus**, invest in debt funds, withdraw tax-efficiently to prepay.

        **Strategy:**
        1. Company offers ₹5L bonus
        2. Defer to next FY (spread tax impact)
        3. Invest in debt mutual fund for 3 years
        4. Withdraw after indexation benefit
        5. Use to prepay loan

        **Tax Arbitrage:**
        - Immediate bonus: ₹5L taxed at 30% = ₹1.5L tax
        - Deferred: ₹5L × 3 years in debt fund = ₹18L corpus
        - After 3 years with indexation: Effective tax 5-10%
        - **Save ₹20-25K in tax per year**

        **Prepayment Power:**
        - Year 3: Lump sum ₹18L prepayment
        - Massive principal reduction
        - Saves huge interest
        """)

        st.markdown("#### 🧮 Calculator")
        st.info("This strategy requires company bonus deferral policy. Most companies don't offer this. Shown for educational purposes.")

        col_bd1, col_bd2 = st.columns(2)

        with col_bd1:
            bd_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                      value=5000000, step=100000, key="bd_loan")
            bd_rate = st.number_input("Loan Interest Rate (%)", min_value=5.0, max_value=15.0,
                                      value=8.5, step=0.1, key="bd_rate")
            bd_annual_bonus = st.number_input("Annual Bonus (₹)", min_value=100000, max_value=5000000,
                                              value=500000, step=50000, key="bd_bonus")
            bd_defer_years = st.slider("Deferral Period (Years)", 2, 5, 3, key="bd_defer")
            bd_debt_return = st.slider("Debt Fund Return (%)", 5.0, 9.0, 7.0, 0.5, key="bd_return")

        # Calculate deferred bonus in debt fund
        bd_corpus = 0
        for year in range(bd_defer_years):
            bd_corpus = (bd_corpus + bd_annual_bonus) * (1 + bd_debt_return/100)

        # Tax calculation
        bd_immediate_tax = bd_annual_bonus * 0.30  # 30% tax every year
        bd_invested = bd_annual_bonus * bd_defer_years
        bd_gains = bd_corpus - bd_invested
        bd_indexed_gains = bd_gains * 0.75  # Assume 25% indexation benefit
        bd_ltcg_tax = bd_indexed_gains * 0.20  # 20% with indexation
        bd_tax_saved = (bd_immediate_tax * bd_defer_years) - bd_ltcg_tax

        # Prepayment impact
        bd_emi = calculate_emi(bd_loan, bd_rate, 20 * 12)

        # Scenario 1: No bonus prepayment
        bd_interest_regular = (bd_emi * 20 * 12) - bd_loan

        # Scenario 2: Lump sum prepayment after 3 years
        bd_outstanding = bd_loan
        bd_total_interest_defer = 0

        for year in range(bd_defer_years):
            for month in range(12):
                if bd_outstanding <= 0.01:
                    break
                interest = bd_outstanding * (bd_rate / 1200)
                principal = bd_emi - interest
                bd_outstanding -= principal
                bd_total_interest_defer += interest

        # Prepay lump sum
        bd_corpus_after_tax = bd_corpus - bd_ltcg_tax
        bd_outstanding -= min(bd_corpus_after_tax, bd_outstanding)

        # Continue for remaining years
        remaining_years = 20 - bd_defer_years
        for year in range(remaining_years):
            for month in range(12):
                if bd_outstanding <= 0.01:
                    break
                interest = bd_outstanding * (bd_rate / 1200)
                principal = bd_emi - interest
                if principal > bd_outstanding:
                    principal = bd_outstanding
                bd_outstanding -= principal
                bd_total_interest_defer += interest

        bd_interest_saved = bd_interest_regular - bd_total_interest_defer
        bd_total_benefit = bd_interest_saved + bd_tax_saved

        with col_bd2:
            st.metric(f"Corpus After {bd_defer_years} Years", f"₹{bd_corpus:,.0f}",
                     help=f"₹{bd_annual_bonus:,.0f} × {bd_defer_years} + returns")
            st.metric("Tax Saved (vs Immediate)", f"₹{bd_tax_saved:,.0f}")
            st.metric("Loan Interest Saved", f"₹{bd_interest_saved:,.0f}")
            st.metric("Total Benefit", f"₹{bd_total_benefit:,.0f}",
                     delta="Tax + Interest savings")

        st.markdown(f"""
        **Your Bonus Deferral Results:**

        **Immediate Approach:**
        - Bonus: ₹{bd_annual_bonus:,.0f}/year
        - Tax @ 30%: ₹{bd_immediate_tax:,.0f}/year
        - After-tax bonus: ₹{bd_annual_bonus - bd_immediate_tax:,.0f}/year

        **Deferred Approach:**
        - Defer ₹{bd_annual_bonus:,.0f}/year for {bd_defer_years} years
        - Invest in debt fund @ {bd_debt_return}%
        - Corpus: ₹{bd_corpus:,.0f}
        - LTCG tax with indexation: ₹{bd_ltcg_tax:,.0f}
        - **Tax saved: ₹{bd_tax_saved:,.0f}**

        **Prepayment Impact:**
        - Lump sum after {bd_defer_years} years: ₹{bd_corpus_after_tax:,.0f}
        - Interest saved: ₹{bd_interest_saved:,.0f}

        **Total benefit: ₹{bd_total_benefit:,.0f}!**

        **⚠️ Limitation:** Most companies don't allow bonus deferral. Check with your HR!
        """)

    # Strategy 11: Debt Fund SWP
    with st.expander("📊 11. Debt Fund SWP - Liquidity + Interest Savings", expanded=False):
        st.markdown("""
        ### How It Works
        Have **lump sum** (₹20L)? Instead of prepaying immediately, invest in debt fund with SWP for EMI.

        **Option A:** Prepay ₹20L → Save ₹16L interest
        **Option B:** Invest ₹20L in debt fund, SWP ₹43K/month for EMI

        **Option B Math:**
        - ₹20L in debt fund @ 7.5% post-tax
        - SWP ₹43K/month (EMI amount)
        - After 20 years: Corpus still ~₹18L (due to returns offsetting withdrawal)
        - Use to close remaining loan!

        **Benefits:**
        - Liquidity maintained (can stop SWP anytime)
        - Tax efficient (SWP has indexation benefit)
        - Emergency fund intact
        """)

        st.markdown("#### 🧮 Calculator")
        col_swp1, col_swp2 = st.columns(2)

        with col_swp1:
            swp_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                       value=5000000, step=100000, key="swp_loan")
            swp_rate = st.number_input("Loan Interest Rate (%)", min_value=5.0, max_value=15.0,
                                       value=8.5, step=0.1, key="swp_rate")
            swp_lumpsum = st.number_input("Lumpsum Available (₹)", min_value=500000, max_value=50000000,
                                          value=2000000, step=100000, key="swp_lumpsum")
            swp_return = st.slider("Debt Fund Return (% p.a.)", 5.0, 9.0, 7.5, 0.5, key="swp_return")

        swp_emi = calculate_emi(swp_loan, swp_rate, 20 * 12)

        # Option A: Prepay lumpsum immediately
        swp_loan_after_prepay = swp_loan - swp_lumpsum
        swp_emi_new = calculate_emi(swp_loan_after_prepay, swp_rate, 20 * 12)
        swp_interest_prepay = (swp_emi_new * 20 * 12) - swp_loan_after_prepay

        # Option B: SWP from debt fund
        swp_corpus = swp_lumpsum
        swp_total_interest_swp = 0
        swp_monthly_return = swp_return / (12 * 100)

        for month in range(20 * 12):
            # Earn returns
            swp_corpus = swp_corpus * (1 + swp_monthly_return)
            # Withdraw EMI
            swp_corpus -= swp_emi
            if swp_corpus < 0:
                swp_corpus = 0
                break

        # Interest on full loan for 20 years
        swp_interest_full = (swp_emi * 20 * 12) - swp_loan

        with col_swp2:
            st.metric("Option A: Prepay Immediately", f"₹{swp_lumpsum:,.0f}")
            st.metric("Interest (After Prepay)", f"₹{swp_interest_prepay:,.0f}")
            st.metric("Option B: Final Corpus", f"₹{swp_corpus:,.0f}",
                     help="Amount left after 20 years of SWP")
            st.metric("Which is Better?",
                     "Option B - SWP" if swp_corpus > swp_lumpsum - swp_interest_prepay else "Option A - Prepay",
                     delta=f"₹{abs(swp_corpus - (swp_lumpsum - swp_interest_prepay)):,.0f} advantage")

        st.markdown(f"""
        **Comparison:**

        **Option A - Prepay ₹{swp_lumpsum:,.0f} Immediately:**
        - Remaining loan: ₹{swp_loan_after_prepay:,.0f}
        - New EMI: ₹{swp_emi_new:,.0f}
        - Interest paid over 20 years: ₹{swp_interest_prepay:,.0f}
        - After 20 years: Loan cleared, ₹0 in hand

        **Option B - Keep in Debt Fund SWP:**
        - Full loan EMI: ₹{swp_emi:,.0f} (paid from SWP)
        - Interest paid: ₹{swp_interest_full:,.0f} (on full loan)
        - After 20 years: ₹{swp_corpus:,.0f} corpus left!
        - Net position: Better by ₹{swp_corpus - swp_interest_prepay if swp_corpus > swp_interest_prepay else 0:,.0f}

        **When Option B Works:**
        - Debt fund returns > Loan interest rate
        - You value liquidity (SWP can be stopped anytime)
        - You have other uses for the corpus later

        **When to Choose Option A:**
        - Guaranteed savings (no market risk)
        - Don't need liquidity
        - Psychological peace of lower loan
        """)

    # Strategy 12: Salary Arbitrage
    with st.expander("🏦 12. Salary Account Arbitrage - Earn While You Wait", expanded=False):
        st.markdown("""
        ### How It Works
        Keep salary in **high-interest savings/liquid fund**, transfer to loan account only on EMI date.

        **Strategy:**
        - Salary account: ₹2L average balance
        - Normal bank: 3-4% interest
        - High-yield bank: 7% interest
        - Difference: ₹6K-₹8K per year!

        **Better Version:**
        - Use liquid mutual fund instead (7-8% post-tax returns)
        - Withdraw to loan account just before EMI
        - Earn ₹14K/year on ₹2L balance
        - Over 20 years: ₹2.8L extra!
        """)

        st.markdown("#### 🧮 Calculator")
        col_sa1, col_sa2 = st.columns(2)

        with col_sa1:
            sa_avg_balance = st.number_input("Average Salary Account Balance (₹)", min_value=50000,
                                             max_value=5000000, value=200000, step=10000, key="sa_balance")
            sa_normal_rate = st.slider("Normal Bank Interest (%)", 2.0, 5.0, 3.5, 0.5, key="sa_normal",
                                       help="Most banks offer 3-4%")
            sa_high_rate = st.slider("High-Yield Option (%)", 5.0, 9.0, 7.0, 0.5, key="sa_high",
                                     help="Liquid fund or high-yield savings account")

        sa_annual_normal = sa_avg_balance * (sa_normal_rate / 100)
        sa_annual_high = sa_avg_balance * (sa_high_rate / 100)
        sa_annual_diff = sa_annual_high - sa_annual_normal
        sa_20year_benefit = sa_annual_diff * 20

        with col_sa2:
            st.metric("Normal Bank Interest", f"₹{sa_annual_normal:,.0f}/year")
            st.metric("High-Yield Interest", f"₹{sa_annual_high:,.0f}/year")
            st.metric("Extra Earned Annually", f"₹{sa_annual_diff:,.0f}")
            st.metric("20-Year Extra Income", f"₹{sa_20year_benefit:,.0f}")

        st.markdown(f"""
        **Your Salary Arbitrage Results:**
        - Average balance: ₹{sa_avg_balance:,.0f}
        - Normal bank @ {sa_normal_rate}%: Earn ₹{sa_annual_normal:,.0f}/year
        - High-yield @ {sa_high_rate}%: Earn ₹{sa_annual_high:,.0f}/year
        - **Extra income: ₹{sa_annual_diff:,.0f}/year**
        - **Over 20 years: ₹{sa_20year_benefit:,.0f}!**

        **Best High-Yield Options (2025):**
        1. **Liquid Mutual Funds:** 7-8% post-tax returns
           - Instant redemption (₹50K/day)
           - No lock-in
           - Better tax treatment than FD

        2. **High-Yield Savings Accounts:**
           - IndusInd Bank: 7% up to ₹1Cr
           - RBL Bank: 7% up to ₹25L
           - Small finance banks: 7-8%

        3. **Overnight Funds:** 6.5-7.5%
           - T+1 day redemption
           - Very low risk
           - Better than savings account

        **Implementation:**
        - Keep ₹2L in liquid fund
        - Set EMI auto-debit from bank account
        - Transfer from liquid fund to bank 1 day before EMI
        - Earn 7% vs 3.5% on idle money!
        """)

with strategy_tab4:
    st.subheader("📊 Compare All 12 Strategies")

    st.markdown("""
    Use the inputs below to compare all strategies for YOUR specific loan scenario.
    """)

    # Common inputs for all strategies
    col_comp1, col_comp2, col_comp3 = st.columns(3)

    with col_comp1:
        comp_loan = st.number_input("Your Loan Amount (₹)", min_value=500000, max_value=100000000,
                                    value=5000000, step=100000, key="comp_loan")
        comp_rate = st.number_input("Your Interest Rate (%)", min_value=5.0, max_value=15.0,
                                    value=8.5, step=0.1, key="comp_rate")

    with col_comp2:
        comp_tenure = st.slider("Loan Tenure (Years)", 10, 30, 20, key="comp_tenure")
        comp_surplus = st.number_input("Monthly Surplus Available (₹)", min_value=5000,
                                       max_value=200000, value=20000, step=1000, key="comp_surplus")

    with col_comp3:
        comp_lumpsum = st.number_input("Lumpsum Available (₹)", min_value=0, max_value=50000000,
                                       value=0, step=100000, key="comp_lumpsum")
        comp_tax_slab = st.selectbox("Your Tax Slab (%)", [0, 20, 30], index=2, key="comp_tax")

    # Calculate baseline (regular EMI, no prepayment)
    comp_emi = calculate_emi(comp_loan, comp_rate, comp_tenure * 12)
    comp_total_interest = (comp_emi * comp_tenure * 12) - comp_loan

    st.markdown("### Strategy Comparison Results")

    # Create comparison dataframe
    strategies_comparison = []

    # We'll add simplified calculations for each strategy
    # (Using rough approximations for comparison table)

    # 1. Bi-Weekly (13 EMIs/year)
    bw_saving_pct = 0.18  # Approximately 18% interest savings
    strategies_comparison.append({
        "Strategy": "1. Bi-Weekly Payment",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐ Simple",
        "Interest Saved": f"₹{comp_total_interest * bw_saving_pct:,.0f}",
        "Time Saved": "~3 years",
        "Requirements": "None",
        "Best For": "Everyone"
    })

    # 2. Step-Up EMI
    su_saving_pct = 0.35  # ~35% interest savings
    strategies_comparison.append({
        "Strategy": "2. Step-Up EMI",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐⭐ Moderate",
        "Interest Saved": f"₹{comp_total_interest * su_saving_pct:,.0f}",
        "Time Saved": "~7 years",
        "Requirements": "Salary growth",
        "Best For": "Young professionals"
    })

    # 3. Tax Refund Cycle
    tr_annual_prepay = min(150000, comp_surplus * 12)
    tr_refund = tr_annual_prepay * (comp_tax_slab / 100)
    tr_extra_prepay = tr_refund * comp_tenure
    tr_saving = tr_extra_prepay * 0.5  # Rough estimate
    strategies_comparison.append({
        "Strategy": "3. Tax Refund Cycle",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐ Simple",
        "Interest Saved": f"₹{tr_saving:,.0f}",
        "Time Saved": "~2 years",
        "Requirements": "Tax filing",
        "Best For": "30% tax bracket"
    })

    # 4. Rental Escalation
    strategies_comparison.append({
        "Strategy": "4. Rental Escalation",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐ Simple",
        "Interest Saved": "Varies",
        "Time Saved": "Depends on rent",
        "Requirements": "Rental property",
        "Best For": "Property investors"
    })

    # 5. SIP Offset
    sip_surplus_value = comp_surplus * 12 * 12 * 1.12**12  # 12 years @ 12%
    sip_benefit = sip_surplus_value * 0.25  # Rough benefit estimate
    strategies_comparison.append({
        "Strategy": "5. SIP Offset",
        "Risk Level": "🟡 Medium",
        "Complexity": "⭐⭐⭐ Complex",
        "Interest Saved": f"₹{sip_benefit:,.0f}",
        "Time Saved": "N/A (Pay + Invest)",
        "Requirements": "Risk appetite",
        "Best For": "Age < 35"
    })

    # 6. Rental Arbitrage
    strategies_comparison.append({
        "Strategy": "6. Rental Arbitrage",
        "Risk Level": "🟡 Medium",
        "Complexity": "⭐⭐ Moderate",
        "Interest Saved": "₹10-20L",
        "Time Saved": "~5 years",
        "Requirements": "High rent area",
        "Best For": "Metro cities"
    })

    # 7. Credit Card Float
    cc_benefit = 200000 * 0.0885 * (45/365) * 12 * 20  # 20 years
    strategies_comparison.append({
        "Strategy": "7. Credit Card Float",
        "Risk Level": "🟡 Medium",
        "Complexity": "⭐⭐ Moderate",
        "Interest Saved": f"₹{cc_benefit:,.0f}",
        "Time Saved": "N/A",
        "Requirements": "OD loan + CC",
        "Best For": "Disciplined spenders"
    })

    # 8. Reverse Laddering
    strategies_comparison.append({
        "Strategy": "8. Reverse FD Ladder",
        "Risk Level": "🟡 Medium",
        "Complexity": "⭐⭐ Moderate",
        "Interest Saved": "₹8-15L",
        "Time Saved": "~4 years",
        "Requirements": "Annual surplus",
        "Best For": "Disciplined savers"
    })

    # 9. Loan Chunking
    lc_saving_pct = 0.26
    strategies_comparison.append({
        "Strategy": "9. Loan Chunking",
        "Risk Level": "🔴 Advanced",
        "Complexity": "⭐⭐⭐ Complex",
        "Interest Saved": f"₹{comp_total_interest * lc_saving_pct:,.0f}",
        "Time Saved": "Varies",
        "Requirements": "Bank approval",
        "Best For": "Large loans"
    })

    # 10. Bonus Deferral
    strategies_comparison.append({
        "Strategy": "10. Bonus Deferral",
        "Risk Level": "🔴 Advanced",
        "Complexity": "⭐⭐⭐⭐ Very Complex",
        "Interest Saved": "₹15-25L",
        "Time Saved": "~6 years",
        "Requirements": "Company policy",
        "Best For": "High bonuses"
    })

    # 11. Debt Fund SWP
    strategies_comparison.append({
        "Strategy": "11. Debt Fund SWP",
        "Risk Level": "🔴 Advanced",
        "Complexity": "⭐⭐⭐ Complex",
        "Interest Saved": "₹5-10L",
        "Time Saved": "N/A",
        "Requirements": "Large lumpsum",
        "Best For": "Need liquidity"
    })

    # 12. Salary Arbitrage
    sa_benefit = 200000 * 0.035 * 20  # 3.5% extra on 2L for 20 years
    strategies_comparison.append({
        "Strategy": "12. Salary Arbitrage",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐ Simple",
        "Interest Saved": f"₹{sa_benefit:,.0f}",
        "Time Saved": "N/A",
        "Requirements": "High-yield account",
        "Best For": "Everyone"
    })

    # Display comparison table
    comparison_df = pd.DataFrame(strategies_comparison)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Recommendations based on user profile
    st.markdown("### 🎯 Personalized Recommendations")

    recommended_strategies = []

    # Simple recommendations based on inputs
    recommended_strategies.append("**Bi-Weekly Payment** - Works for everyone, easy to implement")

    if comp_tax_slab == 30:
        recommended_strategies.append("**Tax Refund Cycle** - You're in 30% bracket, maximize this!")

    if comp_surplus >= 15000:
        recommended_strategies.append("**Step-Up EMI** - You have good surplus, use it wisely")

    if comp_lumpsum > 1000000:
        recommended_strategies.append("**Debt Fund SWP** - You have lumpsum, keep liquidity option")

    recommended_strategies.append("**Salary Arbitrage** - Zero effort, guaranteed returns")

    st.markdown("**Top Strategies for YOU:**")
    for i, rec in enumerate(recommended_strategies, 1):
        st.markdown(f"{i}. {rec}")

    # Hybrid approach suggestion
    st.markdown("### 💡 Hybrid Approach (Best of Multiple Strategies)")
    st.markdown("""
    **Recommended Combination:**
    1. **Bi-Weekly Payment** (₹{:,.0f} × 26 = extra EMI/year)
    2. **Tax Refund Cycle** (₹{:,.0f}/year extra prepayment)
    3. **Salary Arbitrage** (Earn extra ₹{:,.0f}/year on idle money)

    **Combined Impact:**
    - Interest saved: **₹{:,.0f}+**
    - Loan closes: **~8-10 years early**
    - Zero risk, maximum benefit!
    """.format(
        comp_emi/2,
        min(150000, comp_surplus * 12) * (comp_tax_slab/100) if comp_tax_slab > 0 else 0,
        200000 * 0.035,
        comp_total_interest * 0.45
    ))

# Quick Decision Framework
st.header("🎯 Quick Decision Framework")

st.markdown("""
<div class="info-box">
<strong>Still confused? Use this 60-second decision tree:</strong>
</div>
""", unsafe_allow_html=True)

col_decision1, col_decision2 = st.columns(2)

with col_decision1:
    st.markdown("### ✅ Choose REGULAR LOAN If:")
    st.markdown("""
    - [ ] Monthly income = Expenses + EMI (little surplus)
    - [ ] You prefer "set and forget" simplicity
    - [ ] You want maximum tax benefits (80C important)
    - [ ] You have other investments giving > 8-9% returns
    - [ ] You're not disciplined with savings
    - [ ] Loan amount < ₹15L (OD not available)
    - [ ] You might change jobs soon (need stability)

    **If 4+ checked → Go with Regular Loan**
    """)

with col_decision2:
    st.markdown("### ✅ Choose OVERDRAFT If:")
    st.markdown("""
    - [ ] You can park ₹5L+ immediately in OD
    - [ ] Monthly surplus of ₹20K+ over expenses
    - [ ] You receive annual bonus (₹2L+)
    - [ ] You're a business owner (variable income)
    - [ ] You're highly disciplined with money
    - [ ] Loan amount > ₹20L (OD available)
    - [ ] Interest savings > Lost 80C benefit

    **If 5+ checked → Go with Overdraft**
    """)

st.markdown("""
### The Final Litmus Test

Calculate your **Break-even Surplus:**

**Formula:**
```
Break-even = (Regular Loan Interest - OD Interest) / (OD Rate - Regular Rate)
```

**Example:**
- Regular loan @ 8.6%: Interest = ₹54L
- OD loan @ 8.85%: If you park enough to save interest
- Rate difference: 0.25%

**If you can park > Break-even amount consistently → OD wins**
**If you can't → Regular loan is safer**

Use the calculator above to see YOUR break-even point!
""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
<strong>Important Disclaimers:</strong>
<br><br>
1. <strong>OD Deposits ≠ Principal Repayment:</strong> Money parked in overdraft account is NOT eligible for Section 80C deduction.
Only the actual principal component of EMI paid qualifies.
<br><br>
2. <strong>Interest Rates:</strong> These are indicative rates as of October 2025. Actual rates depend on your credit score,
loan amount, and relationship with the bank.
<br><br>
3. <strong>Tax Benefits:</strong> Tax calculations assume old tax regime for self-occupied property. New tax regime has different rules.
Consult a tax advisor for your specific situation.
<br><br>
4. <strong>Minimum Loan Amounts:</strong> Overdraft facilities typically require minimum loan of ₹15-25 lakhs. Check with bank.
<br><br>
5. <strong>Discipline Required:</strong> Overdraft works best when you can consistently park surplus and resist unnecessary withdrawals.
<br><br>
<strong>Data Sources:</strong> Bank websites (HDFC, ICICI, SBI, Axis, BoB, PNB), RBI guidelines,
Income Tax Act sections 80C & 24(b) (October 2025)
<br><br>
<strong>Recommendation:</strong> This is a comparison tool for educational purposes. Consult with your bank and a qualified
financial/tax advisor before making a decision. Home loan is a long-term commitment - choose wisely!
</div>
""", unsafe_allow_html=True)
