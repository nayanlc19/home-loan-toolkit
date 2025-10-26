import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Loan vs Overdraft Comparison Tool",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
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
        border-left: 4px solid #1f77b4;
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
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">💰 Loan vs Overdraft: Comprehensive Cost Comparison</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Make informed borrowing decisions based on actual costs, not marketing claims</div>', unsafe_allow_html=True)

# Bank data - Based on research
BANK_DATA = {
    "Personal Loans": {
        "HDFC Bank": {"interest_rate": 10.50, "processing_fee": 2.0, "prepayment_charge": 4.0},
        "ICICI Bank": {"interest_rate": 10.60, "processing_fee": 2.0, "prepayment_charge": 5.0},
        "Axis Bank": {"interest_rate": 10.49, "processing_fee": 2.0, "prepayment_charge": 4.0},
        "SBI": {"interest_rate": 11.15, "processing_fee": 1.5, "prepayment_charge": 3.0},
        "Bajaj Finserv": {"interest_rate": 13.00, "processing_fee": 3.5, "prepayment_charge": 5.0},
        "IDFC First Bank": {"interest_rate": 10.49, "processing_fee": 2.0, "prepayment_charge": 0.0},
        "Tata Capital": {"interest_rate": 11.50, "processing_fee": 3.5, "prepayment_charge": 4.0},
    },
    "Overdraft Against Salary": {
        "HDFC Bank": {"interest_rate": 14.00, "processing_fee": 0.0, "renewal_fee": 250},
        "ICICI Bank": {"interest_rate": 13.86, "processing_fee": 0.0, "renewal_fee": 300},
        "Axis Bank": {"interest_rate": 14.50, "processing_fee": 0.5, "renewal_fee": 500},
        "SBI": {"interest_rate": 13.50, "processing_fee": 0.0, "renewal_fee": 300},
    },
    "Overdraft Against FD": {
        "HDFC Bank": {"fd_rate": 6.50, "spread": 2.0, "processing_fee": 0.0},
        "ICICI Bank": {"fd_rate": 6.60, "spread": 2.0, "processing_fee": 0.0},
        "Axis Bank": {"fd_rate": 7.00, "spread": 2.0, "processing_fee": 0.0},
        "SBI": {"fd_rate": 6.50, "spread": 1.5, "processing_fee": 0.0},
    }
}

# Sidebar - Input Parameters
st.sidebar.header("📊 Input Parameters")

# Loan amount
loan_amount = st.sidebar.number_input(
    "Amount Required (₹)",
    min_value=10000,
    max_value=10000000,
    value=100000,
    step=10000,
    help="Enter the total amount you need to borrow"
)

# Tenure
tenure_months = st.sidebar.slider(
    "Tenure (Months)",
    min_value=3,
    max_value=60,
    value=12,
    help="Select the repayment period"
)

# Usage pattern for overdraft
st.sidebar.subheader("Overdraft Usage Pattern")
utilization_percentage = st.sidebar.slider(
    "Average Utilization (%)",
    min_value=10,
    max_value=100,
    value=50,
    help="What percentage of the overdraft limit will you use on average?"
)

utilization_days = st.sidebar.slider(
    "Days Used Per Month",
    min_value=1,
    max_value=30,
    value=15,
    help="How many days per month will you use the overdraft?"
)

# Bank selection
st.sidebar.subheader("Select Banks to Compare")
selected_loan_bank = st.sidebar.selectbox(
    "Personal Loan Bank",
    options=list(BANK_DATA["Personal Loans"].keys())
)

selected_od_salary_bank = st.sidebar.selectbox(
    "Overdraft Against Salary Bank",
    options=list(BANK_DATA["Overdraft Against Salary"].keys())
)

selected_od_fd_bank = st.sidebar.selectbox(
    "Overdraft Against FD Bank",
    options=list(BANK_DATA["Overdraft Against FD"].keys())
)

# Functions for calculations
def calculate_emi(principal, annual_rate, months):
    """Calculate EMI for personal loan"""
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return principal / months
    emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    return emi

def calculate_personal_loan_cost(amount, bank_name, tenure):
    """Calculate total cost of personal loan"""
    bank_data = BANK_DATA["Personal Loans"][bank_name]

    # Interest rate
    interest_rate = bank_data["interest_rate"]

    # Processing fee
    processing_fee = (amount * bank_data["processing_fee"] / 100) * 1.18  # Including GST

    # EMI calculation
    emi = calculate_emi(amount, interest_rate, tenure)
    total_payment = emi * tenure
    total_interest = total_payment - amount

    return {
        "emi": emi,
        "total_payment": total_payment,
        "total_interest": total_interest,
        "processing_fee": processing_fee,
        "total_cost": total_payment - amount + processing_fee,
        "interest_rate": interest_rate,
        "effective_interest_rate": ((total_payment - amount + processing_fee) / amount) * (12 / tenure) * 100
    }

def calculate_overdraft_salary_cost(limit, bank_name, tenure, util_pct, days_per_month):
    """Calculate total cost of overdraft against salary"""
    bank_data = BANK_DATA["Overdraft Against Salary"][bank_name]

    # Interest rate
    interest_rate = bank_data["interest_rate"]

    # Processing fee
    processing_fee = (limit * bank_data["processing_fee"] / 100) * 1.18 if bank_data["processing_fee"] > 0 else 0

    # Average utilized amount
    avg_utilized = limit * (util_pct / 100)

    # Daily interest rate
    daily_rate = interest_rate / 365

    # Monthly interest
    monthly_interest = avg_utilized * (daily_rate / 100) * days_per_month

    # Total interest over tenure
    total_interest = monthly_interest * tenure

    # Renewal fees (once per year)
    years = tenure / 12
    renewal_fees = bank_data["renewal_fee"] * years

    return {
        "monthly_interest": monthly_interest,
        "total_interest": total_interest,
        "processing_fee": processing_fee,
        "renewal_fees": renewal_fees,
        "total_cost": total_interest + processing_fee + renewal_fees,
        "interest_rate": interest_rate,
        "avg_utilized": avg_utilized,
        "effective_interest_rate": (total_interest / avg_utilized / tenure) * 12 * 100 if avg_utilized > 0 else 0
    }

def calculate_overdraft_fd_cost(limit, bank_name, tenure, util_pct, days_per_month, fd_amount):
    """Calculate total cost of overdraft against FD"""
    bank_data = BANK_DATA["Overdraft Against FD"][bank_name]

    # Interest rate (FD rate + spread)
    od_interest_rate = bank_data["fd_rate"] + bank_data["spread"]
    fd_interest_rate = bank_data["fd_rate"]

    # Processing fee
    processing_fee = (limit * bank_data["processing_fee"] / 100) * 1.18 if bank_data["processing_fee"] > 0 else 0

    # Average utilized amount
    avg_utilized = limit * (util_pct / 100)

    # Daily interest rate
    daily_rate = od_interest_rate / 365

    # Monthly interest on OD
    monthly_interest = avg_utilized * (daily_rate / 100) * days_per_month

    # Total interest on OD over tenure
    total_od_interest = monthly_interest * tenure

    # FD interest earned (opportunity cost considered)
    fd_interest_earned = fd_amount * (fd_interest_rate / 100) * (tenure / 12)

    # Net cost (OD interest - FD interest earned)
    net_interest = total_od_interest - fd_interest_earned

    return {
        "monthly_interest": monthly_interest,
        "total_od_interest": total_od_interest,
        "fd_interest_earned": fd_interest_earned,
        "net_interest": net_interest,
        "processing_fee": processing_fee,
        "total_cost": net_interest + processing_fee,
        "od_interest_rate": od_interest_rate,
        "fd_interest_rate": fd_interest_rate,
        "avg_utilized": avg_utilized,
        "effective_interest_rate": (total_od_interest / avg_utilized / tenure) * 12 * 100 if avg_utilized > 0 else 0
    }

# Calculate costs
loan_cost = calculate_personal_loan_cost(loan_amount, selected_loan_bank, tenure_months)
od_salary_cost = calculate_overdraft_salary_cost(loan_amount, selected_od_salary_bank, tenure_months, utilization_percentage, utilization_days)

# For FD-backed OD, we need FD amount (typically 90% OD limit means FD should be ~111% of OD limit)
required_fd = loan_amount / 0.9
od_fd_cost = calculate_overdraft_fd_cost(loan_amount, selected_od_fd_bank, tenure_months, utilization_percentage, utilization_days, required_fd)

# Main comparison section
st.header("📈 Cost Comparison Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏦 Personal Loan")
    st.markdown(f"**Bank:** {selected_loan_bank}")
    st.metric("Total Cost", f"₹{loan_cost['total_cost']:,.2f}")
    st.metric("Monthly EMI", f"₹{loan_cost['emi']:,.2f}")
    st.metric("Interest Rate", f"{loan_cost['interest_rate']}%")

with col2:
    st.markdown("### 💳 Overdraft (Salary)")
    st.markdown(f"**Bank:** {selected_od_salary_bank}")
    st.metric("Total Cost", f"₹{od_salary_cost['total_cost']:,.2f}")
    st.metric("Avg Monthly Interest", f"₹{od_salary_cost['monthly_interest']:,.2f}")
    st.metric("Interest Rate", f"{od_salary_cost['interest_rate']}%")

with col3:
    st.markdown("### 💰 Overdraft (FD)")
    st.markdown(f"**Bank:** {selected_od_fd_bank}")
    st.metric("Total Cost", f"₹{od_fd_cost['total_cost']:,.2f}")
    st.metric("Avg Monthly Interest", f"₹{od_fd_cost['monthly_interest']:,.2f}")
    st.metric("OD Interest Rate", f"{od_fd_cost['od_interest_rate']}%")

# Warning box
st.markdown(f"""
<div class="warning-box">
<strong>⚠️ Reality Check:</strong> While overdraft may have higher interest rates ({od_salary_cost['interest_rate']}% vs {loan_cost['interest_rate']}%),
you're only paying interest on ₹{od_salary_cost['avg_utilized']:,.0f} (your average utilization) for {utilization_days} days/month,
not on the full ₹{loan_amount:,.0f} for the entire month like in a personal loan.
</div>
""", unsafe_allow_html=True)

# Detailed cost breakdown
st.header("🔍 Detailed Cost Breakdown")

tab1, tab2, tab3 = st.tabs(["Personal Loan", "Overdraft Against Salary", "Overdraft Against FD"])

with tab1:
    st.subheader(f"Personal Loan - {selected_loan_bank}")

    breakdown_data = {
        "Component": [
            "Principal Amount",
            "Processing Fee (incl. GST)",
            "Total Interest",
            "Total Repayment",
            "Total Cost (Fees + Interest)"
        ],
        "Amount (₹)": [
            f"{loan_amount:,.2f}",
            f"{loan_cost['processing_fee']:,.2f}",
            f"{loan_cost['total_interest']:,.2f}",
            f"{loan_cost['total_payment']:,.2f}",
            f"{loan_cost['total_cost']:,.2f}"
        ]
    }

    st.table(pd.DataFrame(breakdown_data))

    st.markdown(f"""
    **Key Points:**
    - Fixed EMI of ₹{loan_cost['emi']:,.2f} for {tenure_months} months
    - Interest charged on entire amount from day 1
    - Effective interest rate: {loan_cost['effective_interest_rate']:.2f}%
    - Prepayment charges: {BANK_DATA['Personal Loans'][selected_loan_bank]['prepayment_charge']}% (will be 0% from Jan 2026 as per RBI)
    """)

with tab2:
    st.subheader(f"Overdraft Against Salary - {selected_od_salary_bank}")

    breakdown_data = {
        "Component": [
            "Overdraft Limit",
            "Average Utilized Amount",
            "Processing Fee (incl. GST)",
            "Total Interest",
            "Renewal Fees",
            "Total Cost"
        ],
        "Amount (₹)": [
            f"{loan_amount:,.2f}",
            f"{od_salary_cost['avg_utilized']:,.2f}",
            f"{od_salary_cost['processing_fee']:,.2f}",
            f"{od_salary_cost['total_interest']:,.2f}",
            f"{od_salary_cost['renewal_fees']:,.2f}",
            f"{od_salary_cost['total_cost']:,.2f}"
        ]
    }

    st.table(pd.DataFrame(breakdown_data))

    st.markdown(f"""
    **Key Points:**
    - Interest charged only on utilized amount (₹{od_salary_cost['avg_utilized']:,.2f})
    - Interest calculated daily for {utilization_days} days/month
    - Flexible withdrawals and repayments
    - Renewal fee: ₹{BANK_DATA['Overdraft Against Salary'][selected_od_salary_bank]['renewal_fee']} per year
    - No prepayment charges
    """)

with tab3:
    st.subheader(f"Overdraft Against FD - {selected_od_fd_bank}")

    breakdown_data = {
        "Component": [
            "Required FD Amount (for 90% OD)",
            "Overdraft Limit",
            "Average Utilized Amount",
            "Processing Fee",
            "Total OD Interest Paid",
            "FD Interest Earned",
            "Net Interest Cost",
            "Total Cost"
        ],
        "Amount (₹)": [
            f"{required_fd:,.2f}",
            f"{loan_amount:,.2f}",
            f"{od_fd_cost['avg_utilized']:,.2f}",
            f"{od_fd_cost['processing_fee']:,.2f}",
            f"{od_fd_cost['total_od_interest']:,.2f}",
            f"{od_fd_cost['fd_interest_earned']:,.2f}",
            f"{od_fd_cost['net_interest']:,.2f}",
            f"{od_fd_cost['total_cost']:,.2f}"
        ]
    }

    st.table(pd.DataFrame(breakdown_data))

    st.markdown(f"""
    **Key Points:**
    - Requires FD of ₹{required_fd:,.2f} to get ₹{loan_amount:,.2f} OD limit
    - OD Interest: {od_fd_cost['od_interest_rate']:.2f}% (FD rate {od_fd_cost['fd_interest_rate']:.2f}% + {BANK_DATA['Overdraft Against FD'][selected_od_fd_bank]['spread']:.2f}% spread)
    - Your FD continues to earn interest at {od_fd_cost['fd_interest_rate']:.2f}%
    - Net cost is lower due to FD interest earnings
    - No renewal or processing fees
    - FD remains intact (can be used after loan closure)
    """)

# Comparison chart
st.header("📊 Visual Comparison")

# Total cost comparison
fig_cost = go.Figure(data=[
    go.Bar(name='Personal Loan', x=['Processing Fee', 'Interest', 'Other Charges', 'Total Cost'],
           y=[loan_cost['processing_fee'], loan_cost['total_interest'], 0, loan_cost['total_cost']],
           marker_color='#1f77b4'),
    go.Bar(name='OD Against Salary', x=['Processing Fee', 'Interest', 'Other Charges', 'Total Cost'],
           y=[od_salary_cost['processing_fee'], od_salary_cost['total_interest'],
              od_salary_cost['renewal_fees'], od_salary_cost['total_cost']],
           marker_color='#ff7f0e'),
    go.Bar(name='OD Against FD', x=['Processing Fee', 'Interest', 'Other Charges', 'Total Cost'],
           y=[od_fd_cost['processing_fee'], od_fd_cost['net_interest'], 0, od_fd_cost['total_cost']],
           marker_color='#2ca02c')
])

fig_cost.update_layout(
    title='Cost Component Breakdown',
    xaxis_title='Component',
    yaxis_title='Amount (₹)',
    barmode='group',
    height=400
)

st.plotly_chart(fig_cost, use_container_width=True)

# Monthly cash flow comparison
months = list(range(1, tenure_months + 1))
loan_monthly = [-loan_cost['emi']] * tenure_months
od_salary_monthly = [-od_salary_cost['monthly_interest']] * tenure_months
od_fd_monthly = [-od_fd_cost['monthly_interest']] * tenure_months

fig_cashflow = go.Figure()
fig_cashflow.add_trace(go.Scatter(x=months, y=loan_monthly, name='Personal Loan',
                                   line=dict(color='#1f77b4', width=2)))
fig_cashflow.add_trace(go.Scatter(x=months, y=od_salary_monthly, name='OD Against Salary',
                                   line=dict(color='#ff7f0e', width=2)))
fig_cashflow.add_trace(go.Scatter(x=months, y=od_fd_monthly, name='OD Against FD',
                                   line=dict(color='#2ca02c', width=2)))

fig_cashflow.update_layout(
    title='Monthly Outflow Comparison',
    xaxis_title='Month',
    yaxis_title='Monthly Outflow (₹)',
    height=400,
    hovermode='x unified'
)

st.plotly_chart(fig_cashflow, use_container_width=True)

# Scenario Analysis
st.header("🎯 Scenario-Based Recommendations")

# Calculate savings
if od_salary_cost['total_cost'] < loan_cost['total_cost']:
    od_salary_savings = loan_cost['total_cost'] - od_salary_cost['total_cost']
    od_salary_savings_pct = (od_salary_savings / loan_cost['total_cost']) * 100
else:
    od_salary_savings = 0
    od_salary_savings_pct = 0

if od_fd_cost['total_cost'] < loan_cost['total_cost']:
    od_fd_savings = loan_cost['total_cost'] - od_fd_cost['total_cost']
    od_fd_savings_pct = (od_fd_savings / loan_cost['total_cost']) * 100
else:
    od_fd_savings = 0
    od_fd_savings_pct = 0

# Determine best option
costs = {
    "Personal Loan": loan_cost['total_cost'],
    "Overdraft Against Salary": od_salary_cost['total_cost'],
    "Overdraft Against FD": od_fd_cost['total_cost']
}
best_option = min(costs, key=costs.get)

st.markdown(f"""
<div class="info-box">
<strong>🏆 Best Option for Your Scenario:</strong> {best_option} with total cost of ₹{costs[best_option]:,.2f}
</div>
""", unsafe_allow_html=True)

# Recommendations
col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ When to Choose Personal Loan")
    st.markdown("""
    - You need the **full amount immediately**
    - You want **fixed monthly payments** for budgeting
    - You'll use **close to 100%** of the borrowed amount
    - You prefer **longer tenure** (24-60 months)
    - You value **simplicity** and predictability
    - You don't have FD or high credit limit
    """)

with col2:
    st.subheader("✅ When to Choose Overdraft")
    st.markdown("""
    - Your need is **variable** or uncertain
    - You'll use only **30-70%** of the limit
    - You need funds for **short durations**
    - You want **flexibility** in repayments
    - You can repay quickly when you have surplus
    - You have FD for collateral (best rates)
    """)

# Usage pattern impact
st.header("📉 Impact of Usage Pattern on Overdraft Cost")

st.markdown("""
This is where overdraft marketing claims often mislead borrowers. Let's see how utilization affects actual costs:
""")

utilization_scenarios = [10, 25, 50, 75, 100]
od_costs_by_util = []

for util in utilization_scenarios:
    cost = calculate_overdraft_salary_cost(loan_amount, selected_od_salary_bank, tenure_months, util, utilization_days)
    od_costs_by_util.append(cost['total_cost'])

comparison_df = pd.DataFrame({
    'Utilization (%)': utilization_scenarios,
    'Overdraft Total Cost (₹)': od_costs_by_util,
    'Personal Loan Cost (₹)': [loan_cost['total_cost']] * len(utilization_scenarios)
})

fig_util = go.Figure()
fig_util.add_trace(go.Scatter(x=comparison_df['Utilization (%)'],
                               y=comparison_df['Overdraft Total Cost (₹)'],
                               name='Overdraft', mode='lines+markers',
                               line=dict(color='#ff7f0e', width=3)))
fig_util.add_trace(go.Scatter(x=comparison_df['Utilization (%)'],
                               y=comparison_df['Personal Loan Cost (₹)'],
                               name='Personal Loan (Fixed)', mode='lines',
                               line=dict(color='#1f77b4', width=3, dash='dash')))

fig_util.update_layout(
    title='How Utilization Affects Overdraft Cost vs Personal Loan',
    xaxis_title='Average Utilization (%)',
    yaxis_title='Total Cost (₹)',
    height=400,
    hovermode='x unified'
)

st.plotly_chart(fig_util, use_container_width=True)

st.markdown(f"""
**Critical Insight:** At your current utilization of {utilization_percentage}%, the overdraft costs ₹{od_salary_cost['total_cost']:,.2f}
compared to ₹{loan_cost['total_cost']:,.2f} for a personal loan. This represents a **{abs(od_salary_cost['total_cost'] - loan_cost['total_cost']) / loan_cost['total_cost'] * 100:.1f}%
{'saving' if od_salary_cost['total_cost'] < loan_cost['total_cost'] else 'additional cost'}**.
""")

# All banks comparison
st.header("🏦 Compare All Banks")

st.subheader("Personal Loan Comparison")
pl_comparison = []
for bank, data in BANK_DATA["Personal Loans"].items():
    cost = calculate_personal_loan_cost(loan_amount, bank, tenure_months)
    pl_comparison.append({
        "Bank": bank,
        "Interest Rate (%)": data["interest_rate"],
        "Processing Fee (%)": data["processing_fee"],
        "Prepayment Charge (%)": data["prepayment_charge"],
        "Monthly EMI (₹)": f"{cost['emi']:,.0f}",
        "Total Interest (₹)": f"{cost['total_interest']:,.0f}",
        "Total Cost (₹)": f"{cost['total_cost']:,.0f}"
    })

st.dataframe(pd.DataFrame(pl_comparison), use_container_width=True, hide_index=True)

st.subheader("Overdraft Against Salary Comparison")
od_comparison = []
for bank, data in BANK_DATA["Overdraft Against Salary"].items():
    cost = calculate_overdraft_salary_cost(loan_amount, bank, tenure_months, utilization_percentage, utilization_days)
    od_comparison.append({
        "Bank": bank,
        "Interest Rate (%)": data["interest_rate"],
        "Processing Fee (%)": data["processing_fee"],
        "Renewal Fee (₹)": data["renewal_fee"],
        "Avg Monthly Interest (₹)": f"{cost['monthly_interest']:,.0f}",
        "Total Interest (₹)": f"{cost['total_interest']:,.0f}",
        "Total Cost (₹)": f"{cost['total_cost']:,.0f}"
    })

st.dataframe(pd.DataFrame(od_comparison), use_container_width=True, hide_index=True)

st.subheader("Overdraft Against FD Comparison")
od_fd_comparison = []
for bank, data in BANK_DATA["Overdraft Against FD"].items():
    cost = calculate_overdraft_fd_cost(loan_amount, bank, tenure_months, utilization_percentage, utilization_days, required_fd)
    od_fd_comparison.append({
        "Bank": bank,
        "FD Rate (%)": data["fd_rate"],
        "Spread (%)": data["spread"],
        "OD Rate (%)": data["fd_rate"] + data["spread"],
        "Required FD (₹)": f"{required_fd:,.0f}",
        "FD Interest Earned (₹)": f"{cost['fd_interest_earned']:,.0f}",
        "Net Cost (₹)": f"{cost['total_cost']:,.0f}"
    })

st.dataframe(pd.DataFrame(od_fd_comparison), use_container_width=True, hide_index=True)

# Hidden charges section
st.header("⚠️ Hidden Charges to Watch Out For")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Personal Loan Hidden Charges")
    st.markdown("""
    1. **Processing Fee**: 1.5% - 3.5% + 18% GST
    2. **Prepayment Charges**: 0% - 6% of outstanding
       - ⚡ RBI Update: Will be 0% from Jan 2026
    3. **Late Payment Fee**: ₹500 - ₹1,000 per instance
    4. **Bounce Charges**: ₹350 - ₹750 per bounce
    5. **Conversion Charges**: If switching from fixed to floating
    6. **Documentation Charges**: ₹500 - ₹2,000
    7. **Stamp Duty**: As per state (0.1% - 0.5%)
    """)

with col2:
    st.markdown("### Overdraft Hidden Charges")
    st.markdown("""
    1. **Renewal Fee**: ₹250 - ₹500 annually
    2. **Over-limit Charges**: 2% - 3% per month
    3. **Non-utilization Charges**: Some banks charge if not used
    4. **Physical Statement Charges**: ₹50 - ₹200 per request
    5. **Cheque Bounce**: ₹350 - ₹750 per bounce
    6. **Limit Enhancement Fee**: ₹250 - ₹500
    7. **Cash Withdrawal Charges**: 1% - 2.5% at some banks
    """)

# Key differences
st.header("🔑 Key Differences Summary")

differences_df = pd.DataFrame({
    "Feature": [
        "Interest Calculation",
        "Interest Rate Range",
        "Processing Fee",
        "Disbursement Time",
        "Repayment Flexibility",
        "Prepayment Charges",
        "Credit Score Impact",
        "Documentation",
        "Best For"
    ],
    "Personal Loan": [
        "On entire amount from day 1",
        "10% - 20% p.a.",
        "1.5% - 3.5% + GST",
        "1-7 days",
        "Fixed EMI only",
        "0% - 6% (0% from Jan 2026)",
        "High if EMI bounces",
        "Extensive",
        "Full amount needed, fixed payments"
    ],
    "Overdraft": [
        "Only on utilized amount, daily",
        "13% - 15% p.a.",
        "Usually 0% - 1%",
        "Instant (if limit approved)",
        "Very flexible",
        "None",
        "High if over-limit frequently",
        "Minimal",
        "Variable needs, short-term use"
    ]
})

st.table(differences_df)

# Footer with disclaimer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
<strong>Disclaimer:</strong> This tool provides estimates based on research from bank websites and financial portals as of October 2025.
Actual rates and charges may vary based on your credit profile, relationship with the bank, and current market conditions.
Always verify with the bank before making a decision. The calculations assume regular repayment behavior and don't account for
default scenarios or credit score deterioration.

<br><br>

<strong>Data Sources:</strong> HDFC Bank, ICICI Bank, Axis Bank, SBI, Bajaj Finserv, IDFC First Bank, Tata Capital,
RBI Guidelines, and various financial comparison portals (October 2025)

<br><br>

<strong>RBI Update (July 2025):</strong> From January 1, 2026, no prepayment or foreclosure charges will be levied on
personal loans taken by individual borrowers, regardless of whether they have a co-borrower.

</div>
""", unsafe_allow_html=True)
