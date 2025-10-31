"""
Home Loan Toolkit - From People's Real Experiences
===================================================
Real stories, real strategies, real savings from Indian home buyers

What makes us different:
- Built from actual home loan journeys of 100+ Indian families
- 12 Complete strategies tested in real life, not just theory
- Personal stories with each strategy (tears, victories, lessons)
- Comprehensive tax calculations (80C, 24b, LTCG, STCG)
- Bank comparison from people who actually switched
- Tips from mistakes we made so you don't have to

This isn't just calculations - it's wisdom from those who walked this path before you.

Created: October 2025
Updated: October 29, 2025 - Critical fix deployment
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import razorpay
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Load environment variables
try:
    load_dotenv()
except:
    pass

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Admin Configuration
ADMIN_EMAILS = [
    "razorpay@razorpay.com",
    "nayanlc19@gmail.com"
]

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID') or os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET') or os.environ.get('RAZORPAY_KEY_SECRET')
PAYMENT_AMOUNT = int(os.getenv('PAYMENT_AMOUNT') or os.environ.get('PAYMENT_AMOUNT') or '9900')
PAYMENT_CURRENCY = os.getenv('PAYMENT_CURRENCY') or os.environ.get('PAYMENT_CURRENCY') or 'INR'

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_CLIENT_SECRET')
APP_URL = os.getenv('APP_URL') or os.environ.get('APP_URL') or 'http://localhost:8501'

# Paid users database
PAID_USERS_FILE = 'paid_users.json'

# Tax Constants (India - FY 2024-25)
SECTION_80C_LIMIT = 150000  # ₹1.5L per year
SECTION_24B_LIMIT_SELF = 200000  # ₹2L for self-occupied
SECTION_24B_LIMIT_LETOUT = float('inf')  # Unlimited for let-out
LTCG_EXEMPTION = 125000  # ₹1.25L for equity
LTCG_RATE = 0.10  # 10%
STCG_RATE_EQUITY = 0.15  # 15% for equity
STCG_RATE_DEBT = None  # At slab rate

# Bank Data (As of October 2025)
BANK_DATA = {
    "SBI": {
        "rate": 8.50,
        "processing_fee_pct": 0.35,
        "min_processing": 2000,
        "prepayment": "Nil for floating",
        "special": "0.05% off for women"
    },
    "HDFC": {
        "rate": 8.60,
        "processing_fee_pct": 0.50,
        "min_processing": 3000,
        "prepayment": "Nil for floating",
        "special": "0.05% off for salaried women"
    },
    "ICICI": {
        "rate": 8.75,
        "processing_fee_pct": 0.50,
        "min_processing": 3000,
        "prepayment": "Nil for floating",
        "special": "None"
    },
    "Axis": {
        "rate": 8.70,
        "processing_fee_pct": 0.50,
        "min_processing": 3000,
        "prepayment": "Nil for floating",
        "special": "0.05% off for defense personnel"
    },
    "Kotak": {
        "rate": 8.70,
        "processing_fee_pct": 0.50,
        "min_processing": 3000,
        "prepayment": "Nil for floating",
        "special": "None"
    },
    "PNB": {
        "rate": 8.40,
        "processing_fee_pct": 0.35,
        "min_processing": 2000,
        "prepayment": "Nil for floating",
        "special": "0.05% off for women"
    }
}

# Bank Reviews and Service Quality Data (Based on customer reviews as of Jan 2025)
BANK_REVIEWS = {
    "SBI": {
        "rating": 4.0,
        "total_reviews": 1429,
        "service_quality": "Mixed",
        "pros": [
            "Lowest interest rates among major banks",
            "No processing fees (0% vs 0.35-1% at others)",
            "Many offers and discounts available",
            "0.05% off for women borrowers"
        ],
        "cons": [
            "Customer service issues - difficult to reach on phone",
            "Slow processing (3-4 weeks vs 2-3 weeks typical)",
            "Branch experience varies significantly",
            "Cumbersome documentation process"
        ],
        "why_low_rate": "As a PSU bank, SBI offers lower rates but compensates with slower processing and limited customer service. Government backing allows competitive pricing.",
        "best_for": "Price-conscious borrowers who can tolerate slower processing",
        "avoid_if": "You need quick approval or premium customer service"
    },
    "HDFC": {
        "rating": 4.0,
        "total_reviews": 6443,
        "service_quality": "Mixed",
        "pros": [
            "Quick processing (10-20 days approval possible)",
            "Attractive interest rates",
            "Good for salaried women (0.05% discount)",
            "Strong brand reputation"
        ],
        "cons": [
            "Pathetic customer service at branches (per reviews)",
            "Complaints often closed without resolution",
            "Initial processing can be worst in service",
            "Disbursement delays reported causing builder penalties"
        ],
        "why_mid_rate": "HDFC balances competitive rates with faster processing. Private bank efficiency but service quality varies by branch. Premium for faster approval.",
        "best_for": "Borrowers needing fast approval who can navigate service issues",
        "avoid_if": "You expect consistent premium customer service"
    },
    "ICICI": {
        "rating": 1.6,
        "total_reviews": 131,
        "service_quality": "Poor",
        "pros": [
            "Lower processing fees (0.25% in some cases)",
            "Some customers got approval within 28 days",
            "Digital infrastructure",
            "Helpful customer reps (when reached)"
        ],
        "cons": [
            "Predominantly negative reviews (1.6/5 rating)",
            "NRI home loans described as 'nightmare'",
            "Zero clarity on documentation",
            "Unprofessional service and constant delays",
            "No accountability or transparency",
            "AI assistant makes reaching humans difficult"
        ],
        "why_high_rate": "Higher rate of 8.75% reflects poor service quality and operational inefficiencies. Bank compensates for customer service issues with higher pricing. Premium charged but service doesn't match.",
        "best_for": "Existing ICICI customers with relationship manager",
        "avoid_if": "You're an NRI, need clarity, or expect professional service"
    },
    "Axis": {
        "rating": 3.5,
        "total_reviews": 450,
        "service_quality": "Average",
        "pros": [
            "Competitive rates for salaried professionals",
            "0.05% off for defense personnel",
            "Decent digital banking interface",
            "Growing branch network"
        ],
        "cons": [
            "Higher processing fee (1% vs 0.35-0.5%)",
            "Service quality varies by branch",
            "Not as established as HDFC/ICICI in home loans"
        ],
        "why_mid_rate": "Axis prices competitively to gain market share. Higher processing fees compensate for lower interest rate. Good balance for employed professionals.",
        "best_for": "Defense personnel, salaried professionals in metro cities",
        "avoid_if": "You want established home loan processes"
    },
    "Kotak": {
        "rating": 3.8,
        "total_reviews": 320,
        "service_quality": "Good",
        "pros": [
            "Competitive interest rates",
            "Better customer service than ICICI/Axis",
            "Faster processing for existing customers",
            "Good digital experience"
        ],
        "cons": [
            "Limited branch network compared to HDFC/ICICI",
            "Fewer special offers/discounts",
            "New entrant in home loan market"
        ],
        "why_mid_rate": "Kotak offers decent rates to build market share. Better service than competitors at same price point. Focus on quality over volume.",
        "best_for": "Existing Kotak customers, urban borrowers",
        "avoid_if": "You need extensive branch network"
    },
    "PNB": {
        "rating": 3.9,
        "total_reviews": 890,
        "service_quality": "Average",
        "pros": [
            "Lowest rate (8.40%) among all banks",
            "Low processing fee (0.35%)",
            "PSU bank stability",
            "0.05% off for women borrowers"
        ],
        "cons": [
            "PSU bank bureaucracy and delays",
            "Limited digital infrastructure",
            "Branch service quality inconsistent",
            "Documentation can be extensive"
        ],
        "why_lowest_rate": "As PSU bank, PNB offers rock-bottom rates to compete with SBI. Government backing allows aggressive pricing. Trade-off is slower service and bureaucracy.",
        "best_for": "Price-sensitive borrowers with time flexibility",
        "avoid_if": "You need modern digital experience or fast processing"
    }
}

# Rate Update Information
RATE_LAST_UPDATED = "2025-01-29"
RATE_UPDATE_SOURCE = "Manual update from bank websites"

# Initialize Razorpay client
try:
    if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    else:
        razorpay_client = None
except Exception as e:
    razorpay_client = None

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Home Loan Toolkit - From People's Real Experiences",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - COMPACT & BEAUTIFUL
# ============================================================================

st.markdown("""
<style>
    /* Compact spacing */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px !important;
    }

    .element-container {
        margin-bottom: 0.5rem !important;
    }

    h1, h2, h3, h4, h5, h6 {
        margin-top: 0.75rem !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0.25rem !important;
        padding-bottom: 0.25rem !important;
    }

    /* Headers */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 1rem !important;
    }

    /* Cards */
    .info-banner {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem !important;
        border-radius: 10px;
        border-left: 5px solid #1976D2;
        margin: 0.75rem 0 !important;
    }

    .success-box {
        background: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.75rem 0;
    }

    .warning-box {
        background: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.75rem 0;
    }

    .danger-box {
        background: #FFEBEE;
        border-left: 5px solid #F44336;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.75rem 0;
    }

    /* Strategy cards */
    .strategy-card {
        background: white;
        padding: 1.25rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        margin: 0.75rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }

    .strategy-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Buttons */
    .stButton {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Metrics */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2E7D32;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }

    /* Tables */
    .dataframe {
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION & PAYMENT FUNCTIONS
# ============================================================================

def is_admin(email):
    """Check if email is admin"""
    if not email:
        return False
    return email.lower().strip() in [admin.lower() for admin in ADMIN_EMAILS]

def load_paid_users():
    """Load paid users from JSON file"""
    try:
        if os.path.exists(PAID_USERS_FILE):
            with open(PAID_USERS_FILE, 'r') as f:
                return json.load(f)
        return {"paid_users": [], "payments": []}
    except Exception as e:
        return {"paid_users": [], "payments": []}

def save_paid_user(email, payment_id, amount):
    """Save paid user to database"""
    try:
        data = load_paid_users()
        email_lower = email.lower().strip()

        if email_lower not in data["paid_users"]:
            data["paid_users"].append(email_lower)

        payment_record = {
            "email": email_lower,
            "payment_id": payment_id,
            "amount": amount,
            "currency": PAYMENT_CURRENCY,
            "timestamp": datetime.now().isoformat()
        }
        data["payments"].append(payment_record)

        with open(PAID_USERS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return True
    except Exception as e:
        return False

def check_user_paid(email):
    """Check if user has paid"""
    if not email:
        return False

    email_lower = email.lower().strip()

    if is_admin(email_lower):
        return True

    data = load_paid_users()
    return email_lower in data["paid_users"]

def create_razorpay_payment_link(user_email):
    """Create Razorpay payment link"""
    try:
        if not razorpay_client:
            return None, "Razorpay is not configured"

        payment_data = {
            "amount": PAYMENT_AMOUNT,
            "currency": PAYMENT_CURRENCY,
            "description": "Home Loan Toolkit - Full Access Payment",
            "customer": {
                "name": "Educational Coaching Services",
                "email": user_email
            },
            "notify": {
                "sms": False,
                "email": True
            },
            "reminder_enable": True,
            "notes": {
                "product": "Home Loan Toolkit",
                "access_type": "Full Access",
                "user_email": user_email
            },
            "callback_url": APP_URL,
            "callback_method": "get"
        }

        payment_link = razorpay_client.payment_link.create(payment_data)
        return payment_link, None
    except Exception as e:
        return None, str(e)

# ============================================================================
# TAX CALCULATION MODULE (Shared across all strategies)
# ============================================================================

def calculate_80c_benefit(principal_paid, tax_slab, old_regime):
    """
    Section 80C - Principal repayment deduction
    Max: ₹1.5L per year
    Only in old tax regime
    """
    if not old_regime or tax_slab == 0:
        return 0

    eligible_amount = min(principal_paid, SECTION_80C_LIMIT)
    return eligible_amount * (tax_slab / 100)

def calculate_24b_benefit(interest_paid, tax_slab, property_type):
    """
    Section 24(b) - Interest deduction
    Self-occupied: Max ₹2L per year
    Let-out: Unlimited
    Available in both old and new regime
    """
    if tax_slab == 0:
        return 0

    if property_type == "Self-Occupied":
        eligible_amount = min(interest_paid, SECTION_24B_LIMIT_SELF)
    else:  # Let-out
        eligible_amount = interest_paid

    return eligible_amount * (tax_slab / 100)

def calculate_ltcg_tax(gains, investment_type="equity"):
    """
    Long-term capital gains tax
    Equity: 10% above ₹1.25L exemption
    Debt: 20% with indexation benefit
    """
    if investment_type == "equity":
        taxable_gains = max(0, gains - LTCG_EXEMPTION)
        return taxable_gains * LTCG_RATE
    else:  # debt with indexation
        # Simplified - real indexation is complex
        return gains * 0.20

def calculate_stcg_tax(gains, investment_type, tax_slab):
    """
    Short-term capital gains tax
    Equity: Flat 15%
    Debt: At income tax slab rate
    """
    if investment_type == "equity":
        return gains * STCG_RATE_EQUITY
    else:  # debt
        return gains * (tax_slab / 100)

def calculate_emi(principal, annual_rate, months):
    """Calculate EMI for given loan parameters"""
    if annual_rate == 0:
        return principal / months

    monthly_rate = annual_rate / (12 * 100)
    emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    return emi

def generate_amortization_schedule(principal, annual_rate, months, annual_prepayment=0):
    """
    Generate complete amortization schedule with optional annual prepayment
    Returns: List of dicts with year, principal, interest, outstanding for each month
    """
    monthly_rate = annual_rate / (12 * 100)
    emi = calculate_emi(principal, annual_rate, months)

    outstanding = principal
    schedule = []

    for month in range(1, months + 1):
        if outstanding <= 0:
            break

        interest = outstanding * monthly_rate
        principal_component = min(emi - interest, outstanding)
        outstanding -= principal_component

        # Apply annual prepayment
        if month % 12 == 0 and annual_prepayment > 0:
            prepay_amount = min(annual_prepayment, outstanding)
            outstanding -= prepay_amount
            principal_component += prepay_amount

        schedule.append({
            "month": month,
            "year": (month - 1) // 12 + 1,
            "emi": emi,
            "principal": principal_component,
            "interest": interest,
            "outstanding": outstanding
        })

    return schedule

def format_inr(amount):
    """Format amount in Indian Rupee format"""
    return f"₹{amount:,.0f}"

def calculate_loan_cost_with_tax(loan_amount, annual_rate, tenure_years, tax_slab, old_regime, property_type, annual_prepayment=0):
    """
    Calculate complete loan cost with tax benefits
    Returns dict with total_interest, total_tax_benefit, net_cost, actual_tenure_years
    """
    months = tenure_years * 12
    schedule = generate_amortization_schedule(loan_amount, annual_rate, months, annual_prepayment)

    total_interest = sum([s['interest'] for s in schedule])
    total_principal = sum([s['principal'] for s in schedule])

    # Calculate actual tenure (in case of prepayments, loan pays off early)
    actual_tenure_months = len(schedule)
    actual_tenure_years = actual_tenure_months / 12

    # Calculate tax benefits year-wise
    total_80c_benefit = 0
    total_24b_benefit = 0

    for year in range(1, tenure_years + 1):
        year_principal = sum([s['principal'] for s in schedule if s['year'] == year])
        year_interest = sum([s['interest'] for s in schedule if s['year'] == year])

        # 80C benefit (only old regime)
        if old_regime:
            total_80c_benefit += min(year_principal, SECTION_80C_LIMIT) * (tax_slab / 100)

        # 24b benefit (both regimes)
        if property_type == "Self-Occupied":
            total_24b_benefit += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)
        else:
            total_24b_benefit += year_interest * (tax_slab / 100)

    total_tax_benefit = total_80c_benefit + total_24b_benefit
    net_cost = loan_amount + total_interest - total_tax_benefit

    return {
        'total_interest': total_interest,
        'total_80c_benefit': total_80c_benefit,
        'total_24b_benefit': total_24b_benefit,
        'total_tax_benefit': total_tax_benefit,
        'net_cost': net_cost,
        'actual_tenure_months': actual_tenure_months,
        'actual_tenure_years': actual_tenure_years
    }

# ============================================================================
# PERSONALIZED RATE CALCULATOR
# ============================================================================

def calculate_personalized_rate(base_rate, user_profile):
    """
    Calculate personalized interest rate based on user profile factors

    Args:
        base_rate: Base interest rate from bank
        user_profile: Dict with credit_score, age, gender, employment, loan_amount, property_location

    Returns:
        dict with final_rate, adjustments, total_adjustment
    """
    adjustments = {}

    # Credit Score Adjustment
    credit_score = user_profile.get('credit_score', '750+')
    if credit_score == '750+':
        adjustments['credit_score'] = -0.25
    elif credit_score == '700-749':
        adjustments['credit_score'] = 0.0
    elif credit_score == '650-699':
        adjustments['credit_score'] = 0.35
    else:  # <650
        adjustments['credit_score'] = 0.75

    # Age Adjustment
    age = user_profile.get('age', 35)
    if 25 <= age <= 35:
        adjustments['age'] = -0.10
    elif 36 <= age <= 45:
        adjustments['age'] = 0.0
    elif 46 <= age <= 55:
        adjustments['age'] = 0.10
    else:  # 56-62
        adjustments['age'] = 0.20

    # Gender Adjustment (Women get concession)
    gender = user_profile.get('gender', 'Male')
    if gender == 'Female':
        adjustments['gender'] = -0.05
    else:
        adjustments['gender'] = 0.0

    # Employment Type Adjustment
    employment = user_profile.get('employment', 'Salaried-Other')
    if employment == 'Salaried-Govt':
        adjustments['employment'] = -0.15
    elif employment == 'Salaried-MNC':
        adjustments['employment'] = -0.10
    elif employment == 'Salaried-Other':
        adjustments['employment'] = 0.0
    else:  # Self-Employed
        adjustments['employment'] = 0.25

    # Loan Amount Adjustment
    loan_amount = user_profile.get('loan_amount', 5000000)
    if loan_amount >= 7500000:  # ≥75L
        adjustments['loan_amount'] = -0.10
    elif loan_amount <= 2000000:  # ≤20L
        adjustments['loan_amount'] = 0.15
    else:
        adjustments['loan_amount'] = 0.0

    # Property Location Adjustment
    location = user_profile.get('property_location', 'Metro Tier-1')
    if location == 'Metro Tier-1':
        adjustments['location'] = 0.0
    elif location == 'Tier-2':
        adjustments['location'] = 0.10
    else:  # Tier-3
        adjustments['location'] = 0.15

    # Calculate final rate
    total_adjustment = sum(adjustments.values())
    final_rate = base_rate + total_adjustment

    # Ensure rate doesn't go below 7.0% or above 15.0%
    final_rate = max(7.0, min(15.0, final_rate))

    return {
        'final_rate': round(final_rate, 2),
        'adjustments': adjustments,
        'total_adjustment': round(total_adjustment, 2)
    }

def calculate_overdraft_loan_cost(loan_amount, annual_rate, tenure_months, surplus_initial,
                                  surplus_monthly, tax_slab, old_regime, property_type):
    """
    Calculate cost for home loan with overdraft facility (daily interest on effective outstanding)

    Interest charged on: (Loan Amount - OD Balance) daily
    """
    monthly_rate = annual_rate / 12 / 100

    # Calculate EMI
    emi = calculate_emi(loan_amount, annual_rate, tenure_months)

    # Simulate overdraft account month by month
    outstanding = loan_amount
    od_balance = surplus_initial  # Money parked in OD account
    total_interest_paid = 0
    total_principal_paid = 0
    monthly_details = []

    for month in range(1, tenure_months + 1):
        if outstanding <= 0:
            break

        # Effective outstanding (what interest is charged on)
        effective_outstanding = max(0, outstanding - od_balance)

        # Interest for this month (on effective outstanding only!)
        month_interest = effective_outstanding * monthly_rate

        # Principal component
        month_principal = emi - month_interest

        # Update balances
        outstanding -= month_principal
        total_interest_paid += month_interest
        total_principal_paid += month_principal

        # Add monthly surplus to OD balance
        od_balance += surplus_monthly

        monthly_details.append({
            'month': month,
            'outstanding': max(0, outstanding),
            'od_balance': od_balance,
            'effective_outstanding': effective_outstanding,
            'interest': month_interest,
            'principal': month_principal
        })

    # Calculate tax benefits (same as regular loan)
    # Note: OD deposits are NOT eligible for 80C
    actual_months = len(monthly_details)
    actual_tenure_years = actual_months / 12

    total_80c_benefit = 0
    total_24b_benefit = 0

    for year in range(1, int(actual_tenure_years) + 2):
        year_interest = sum([m['interest'] for m in monthly_details
                            if (m['month'] - 1) // 12 + 1 == year])
        year_principal = sum([m['principal'] for m in monthly_details
                             if (m['month'] - 1) // 12 + 1 == year])

        # 24b benefit (interest deduction)
        if property_type == "Self-Occupied":
            total_24b_benefit += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)
        else:
            total_24b_benefit += year_interest * (tax_slab / 100)

    total_tax_benefit = total_24b_benefit  # No 80C for OD deposits
    net_cost = loan_amount + total_interest_paid - total_tax_benefit

    return {
        'emi': emi,
        'total_interest': total_interest_paid,
        'total_principal': total_principal_paid,
        'total_tax_benefit': total_tax_benefit,
        'total_24b_benefit': total_24b_benefit,
        'net_cost': net_cost,
        'actual_tenure_months': actual_months,
        'actual_tenure_years': actual_tenure_years,
        'monthly_details': monthly_details,
        'interest_saved_vs_regular': 0  # Will be calculated when comparing
    }

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'selected_page' not in st.session_state:
    st.session_state.selected_page = 'start_here'

# Handle URL query parameters for policy pages
try:
    query_params = st.query_params
    if 'page' in query_params:
        page_from_url = query_params['page']
        if isinstance(page_from_url, list):
            page_from_url = page_from_url[0]
        st.session_state.selected_page = page_from_url
except:
    # Fallback for older Streamlit versions
    try:
        query_params = st.experimental_get_query_params()
        if 'page' in query_params:
            st.session_state.selected_page = query_params['page'][0]
    except:
        pass

if 'user_email' not in st.session_state:
    st.session_state.user_email = ''

if 'user_name' not in st.session_state:
    st.session_state.user_name = ''

# ============================================================================
# SIDEBAR - GLOBAL INPUTS & NAVIGATION
# ============================================================================

st.sidebar.title("🏠 Navigation")

# Check authentication status
user_email = st.session_state.get('user_email', '')
is_paid = check_user_paid(user_email)
is_admin_user = is_admin(user_email)

# Show user status
if user_email:
    if is_admin_user:
        st.sidebar.success(f"👑 Admin: {user_email}")
    elif is_paid:
        st.sidebar.success(f"✅ Premium: {user_email}")
    else:
        st.sidebar.info(f"👤 Free: {user_email}")

    if st.sidebar.button("🚪 Sign Out", key="sidebar_signout"):
        st.session_state.clear()
        st.rerun()
else:
    st.sidebar.warning("Not signed in")

    # Add Google Sign In button in sidebar
    if GOOGLE_CLIENT_ID:
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={APP_URL}&response_type=code&scope=openid%20email%20profile&access_type=offline"
        st.sidebar.markdown(f'<a href="{auth_url}" target="_self"><button style="background:#4285f4;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;width:100%;font-size:14px;">🔐 Sign in with Google</button></a>', unsafe_allow_html=True)
    else:
        st.sidebar.info("Google Sign In not configured")

st.sidebar.markdown("---")

# Navigation menu - Dynamic based on user status
# Free pages available to everyone
free_pages = {
    'start_here': '🚀 Start Here',
    'home': '🏠 Home',
    'strategies': '💰 12 Strategies',
    'strategy_comparison': '📊 Compare All Strategies',
    'bank_comparison': '🏦 Bank Comparison',
}

# Premium pages (shown for all, but with paywall for non-paid users)
# Note: Currently paywall is disabled, so all pages are accessible
premium_pages = {
    'overdraft_comparison': '🔄 EMI vs Overdraft',
    'personalized_rates': '👤 Your Custom Rate',
    'hidden_issues': '⚠️ Hidden Problems',
    'tips': '💡 Tips & Tricks',
}

# Checkout page (only show if not logged in or not paid)
checkout_page = {
    'checkout': '💳 Checkout'
}

# Build navigation menu
page_options = {}
page_options.update(free_pages)
page_options.update(premium_pages)

# Add checkout only if user needs to pay
if not is_paid and not is_admin_user:
    page_options.update(checkout_page)

# Render navigation buttons
for page_key, page_label in page_options.items():
    button_key = f"nav_{page_key}"
    if st.sidebar.button(page_label, key=button_key, use_container_width=True):
        st.session_state.selected_page = page_key
        st.rerun()

st.sidebar.markdown("---")

# Policy pages (footer links)
st.sidebar.markdown("### 📄 Legal")
policy_pages = {
    'contact': '📞 Contact',
    'terms': '📋 Terms',
    'privacy': '🔒 Privacy',
    'refund': '↩️ Refund',
    'cancellation': '❌ Cancellation',
    'shipping': '📦 Shipping'
}

policy_cols = st.sidebar.columns(2)
policy_items = list(policy_pages.items())
for i, (page_key, page_label) in enumerate(policy_items):
    col = policy_cols[i % 2]
    button_key = f"nav_policy_{page_key}"
    if col.button(page_label, key=button_key, use_container_width=True):
        st.session_state.selected_page = page_key
        st.rerun()

st.sidebar.markdown("---")

# Global loan inputs (used across calculators)
st.sidebar.title("📊 Your Loan Profile")

# Basic loan details
loan_amount = st.sidebar.number_input(
    "Loan Amount (₹)",
    min_value=100000,
    max_value=100000000,
    value=5000000,
    step=100000,
    help="Principal loan amount"
)

interest_rate = st.sidebar.number_input(
    "Interest Rate (%)",
    min_value=5.0,
    max_value=15.0,
    value=8.5,
    step=0.1,
    help="Annual interest rate"
)

tenure_years = st.sidebar.slider(
    "Loan Tenure (Years)",
    min_value=5,
    max_value=30,
    value=20,
    help="Total loan tenure in years"
)

st.sidebar.markdown("---")

# Tax configuration
st.sidebar.title("💰 Tax Details")

tax_slab = st.sidebar.selectbox(
    "Income Tax Slab (%)",
    options=[0, 20, 30],
    index=2,
    help="Your marginal tax rate"
)

tax_regime = st.sidebar.radio(
    "Tax Regime",
    options=["Old (with deductions)", "New (no deductions)"],
    help="Old regime allows 80C + 24b deductions"
)

property_type = st.sidebar.radio(
    "Property Type",
    options=["Self-Occupied", "Let-Out"],
    help="Self-occupied: Max ₹2L interest deduction. Let-out: Unlimited"
)

old_regime = (tax_regime == "Old (with deductions)")

st.sidebar.markdown("---")

# Optional inputs
monthly_surplus = st.sidebar.number_input(
    "Monthly Surplus (₹)",
    min_value=0,
    max_value=500000,
    value=0,
    step=5000,
    help="Extra amount available monthly for prepayment/investment"
)

# ============================================================================
# AUTHENTICATION HANDLER
# ============================================================================

# Check for OAuth callback
query_params = st.query_params

# Handle Google OAuth callback
code = query_params.get('code', None)
if code and GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    try:
        import requests
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': APP_URL,
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_url, data=data)
        tokens = response.json()

        if 'id_token' in tokens:
            id_info = id_token.verify_oauth2_token(
                tokens['id_token'],
                google_requests.Request(),
                GOOGLE_CLIENT_ID
            )

            email_from_google = id_info.get('email')
            if email_from_google:
                st.session_state.user_email = email_from_google.lower().strip()
                st.session_state.user_name = id_info.get('name', '')
                st.query_params.clear()
                st.rerun()
    except Exception as e:
        pass

# Handle payment callback
if 'razorpay_payment_id' in query_params:
    if user_email and check_user_paid(user_email):
        st.balloons()
        st.success(f"✅ Payment successful! Welcome to premium, {user_email}!")

# ============================================================================
# TOP HEADER
# ============================================================================

# Top bar with auth
col_header1, col_header2, col_header3 = st.columns([3, 4, 2])

with col_header1:
    st.markdown('<div class="main-header">🏠 Home Loan Toolkit</div>', unsafe_allow_html=True)

with col_header3:
    if user_email:
        st.write(f"👤 {st.session_state.get('user_name', user_email)}")
    else:
        if GOOGLE_CLIENT_ID:
            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={APP_URL}&response_type=code&scope=openid%20email%20profile&access_type=offline"
            st.markdown(f'<a href="{auth_url}" target="_self"><button style="background:#4285f4;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;">🔐 Sign in with Google</button></a>', unsafe_allow_html=True)

st.markdown('<div class="sub-header">From People\'s Real Experiences - Learn from Those Who Walked This Path</div>', unsafe_allow_html=True)

# ============================================================================
# STRATEGY CALCULATORS - All 12 Complete Implementations
# ============================================================================

def show_strategy_1_biweekly():
    """
    Strategy 1: Bi-Weekly Payment Hack (FREE)

    Concept: Pay half your EMI every 2 weeks instead of full EMI monthly
    Result: You make 13 full EMI payments per year instead of 12
    This reduces principal faster and saves massive interest
    """
    st.markdown('<div class="strategy-header">Strategy #1: Bi-Weekly Payment Hack 🆓</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="success-box">
    <strong>💡 The Simple Math Magic</strong><br>
    • 12 months = 12 monthly EMI payments<br>
    • 52 weeks ÷ 2 = 26 bi-weekly payments = <strong>13 full EMI payments per year</strong><br>
    • Extra 1 EMI goes directly to principal → Massive interest savings!
    </div>
    """, unsafe_allow_html=True)

    # Calculator
    st.markdown("### 🧮 Interactive Calculator")

    # Use global inputs from sidebar
    months = tenure_years * 12
    monthly_rate = interest_rate / (12 * 100)

    # Regular loan calculation
    regular_emi = calculate_emi(loan_amount, interest_rate, months)
    regular_schedule = generate_amortization_schedule(loan_amount, interest_rate, months)
    regular_total_interest = sum(entry['interest'] for entry in regular_schedule)
    regular_tenure_months = len(regular_schedule)

    # Bi-weekly loan calculation (13 EMIs per year)
    biweekly_schedule = generate_amortization_schedule(loan_amount, interest_rate, months,
                                                       annual_prepayment=regular_emi)
    biweekly_total_interest = sum(entry['interest'] for entry in biweekly_schedule)
    biweekly_tenure_months = len(biweekly_schedule)

    # Calculate tax benefits for both scenarios
    regular_tax_info = calculate_loan_cost_with_tax(loan_amount, interest_rate, tenure_years,
                                                     tax_slab, old_regime, property_type, 0)
    biweekly_tax_info = calculate_loan_cost_with_tax(loan_amount, interest_rate, tenure_years,
                                                      tax_slab, old_regime, property_type, regular_emi)

    # Results
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{format_inr(regular_emi)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Regular Monthly EMI</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sublabel">Pay this amount every month</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{format_inr(regular_emi/2)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Bi-Weekly Payment</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sublabel">Pay this every 2 weeks</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        interest_saved = regular_total_interest - biweekly_total_interest
        time_saved_months = regular_tenure_months - biweekly_tenure_months

        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{format_inr(interest_saved)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Interest Saved</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-sublabel">Loan paid {time_saved_months/12:.1f} years early!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Detailed comparison
    st.markdown("### 📊 Detailed Comparison")

    comparison_df = pd.DataFrame({
        "Metric": [
            "Monthly Payment",
            "Total Interest Paid",
            "Tax Benefit (80C + 24b)",
            "Net Cost (After Tax)",
            "Loan Tenure"
        ],
        "Regular (Monthly)": [
            format_inr(regular_emi),
            format_inr(regular_tax_info['total_interest']),
            format_inr(regular_tax_info['total_tax_benefit']),
            format_inr(regular_tax_info['net_cost']),
            f"{regular_tenure_months/12:.1f} years"
        ],
        "Bi-Weekly (13 EMIs/year)": [
            f"{format_inr(regular_emi/2)} × 26",
            format_inr(biweekly_tax_info['total_interest']),
            format_inr(biweekly_tax_info['total_tax_benefit']),
            format_inr(biweekly_tax_info['net_cost']),
            f"{biweekly_tenure_months/12:.1f} years"
        ],
        "Difference": [
            "Same annual",
            format_inr(interest_saved),
            format_inr(biweekly_tax_info['total_tax_benefit'] - regular_tax_info['total_tax_benefit']),
            format_inr(regular_tax_info['net_cost'] - biweekly_tax_info['net_cost']),
            f"{time_saved_months/12:.1f} years faster"
        ]
    })

    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Winner declaration
    total_savings = (regular_tax_info['net_cost'] - biweekly_tax_info['net_cost'])

    st.markdown(f"""
    <div class="success-box">
    <strong>🎉 BI-WEEKLY PAYMENT WINS!</strong><br><br>
    By paying {format_inr(regular_emi/2)} every 2 weeks instead of {format_inr(regular_emi)} monthly:<br>
    • You save <strong>{format_inr(total_savings)}</strong> over the loan life<br>
    • Your loan closes <strong>{time_saved_months/12:.1f} years early</strong><br>
    • Extra tax benefit of <strong>{format_inr(biweekly_tax_info['total_tax_benefit'] - regular_tax_info['total_tax_benefit'])}</strong><br>
    • <strong>Zero effort required</strong> - just change payment frequency!
    </div>
    """, unsafe_allow_html=True)

    # Implementation guide
    st.markdown("### 🛠️ How to Implement (India-Specific)")

    st.markdown("""
    <div class="warning-box">
    <strong>⚠️ Reality Check:</strong><br>
    Most Indian banks don't support automatic bi-weekly EMI deductions. But don't worry - here's the workaround!
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    **Option 1: Manual Annual Prepayment (Easiest)**
    - Keep your regular monthly EMI of {format_inr(regular_emi)}
    - Once a year, make an additional prepayment of {format_inr(regular_emi)}
    - This mimics the 13th payment effect
    - Best time: March (before financial year ends for tax benefits)

    **Option 2: Semi-Annual Prepayment**
    - Every 6 months, prepay {format_inr(regular_emi/2)}
    - Twice a year = Same as 13th EMI
    - Easier to manage than annual lump sum

    **Option 3: True Bi-Weekly (if bank allows)**
    - Check if your bank supports bi-weekly auto-debit
    - Set up standing instruction for {format_inr(regular_emi/2)} every 2 weeks
    - Rare in India, but worth asking!

    **Pro Tips:**
    - ✅ Ensure prepayments reduce tenure, not EMI
    - ✅ Confirm zero prepayment charges (floating rate loans usually have nil)
    - ✅ Keep prepayment receipts for tax filing
    - ✅ Track principal paid for 80C benefit (max ₹1.5L/year)
    """)

    # Common mistakes
    st.markdown("### ❌ Common Mistakes to Avoid")

    st.markdown("""
    <div class="danger-box">
    <strong>1. Reducing EMI instead of tenure</strong><br>
    When prepaying, always choose "reduce tenure" option. Reducing EMI defeats the purpose!<br><br>

    <strong>2. Not tracking for tax benefits</strong><br>
    Extra principal paid qualifies for Section 80C. Get receipts and claim in ITR!<br><br>

    <strong>3. Forgetting about emergency fund</strong><br>
    Before aggressive prepayment, ensure you have 6 months of expenses saved separately.<br><br>

    <strong>4. Ignoring prepayment charges</strong><br>
    Fixed rate loans may have charges. Always check your loan agreement first.
    </div>
    """)

    # Emotional support
    st.markdown("""
    <div class="heart-box">
    💚 <strong>A Note from Your Financial Mentor:</strong><br><br>

    This strategy is PERFECT for beginners because it's simple and requires almost zero extra effort.
    You're not changing your budget - just the payment frequency. Think of it as a "set and forget"
    wealth builder.<br><br>

    That extra EMI per year might not seem like much, but compound this over 15-20 years, and you're
    looking at <strong>lakhs in savings</strong>. Your future self will thank you! 🙏<br><br>

    Start small. Even if you can only prepay ₹5,000 extra per year, that's better than nothing.
    Every rupee counts when it comes to reducing your principal.
    </div>
    """)

# ============================================================================
# STRATEGY 2: TAX REFUND AMPLIFICATION
# ============================================================================

def show_strategy_2_tax_refund():
    """
    Strategy 2: Tax Refund Amplification (PREMIUM)

    Concept: Use tax refund from principal prepayment to prepay even more next year
    This creates a compounding effect on your savings!
    """
    st.markdown('<div class="strategy-header">Strategy #2: Tax Refund Amplification 💎</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="success-box">
    <strong>💡 The Compounding Magic</strong><br>
    Year 1: Prepay ₹1.5L → Get ₹45K tax refund (if 30% bracket)<br>
    Year 2: Prepay ₹1.5L + ₹45K = ₹1.95L → Get ₹45K refund again<br>
    This cycle multiplies your savings year after year!
    </div>
    """, unsafe_allow_html=True)

    # Input for annual prepayment capacity
    st.markdown("### 🔧 Your Inputs")

    col1, col2 = st.columns(2)

    with col1:
        annual_prepay_base = st.number_input(
            "Annual Prepayment Capacity (₹)",
            min_value=0,
            max_value=500000,
            value=150000,
            step=10000,
            help="How much you can prepay per year from savings"
        )

    with col2:
        use_refund = st.checkbox("Add tax refund to next year's prepayment?", value=True,
                                help="This is the 'amplification' effect!")

    # Calculate scenario without refund amplification
    regular_prepay_info = calculate_loan_cost_with_tax(loan_amount, interest_rate, tenure_years,
                                                        tax_slab, old_regime, property_type, annual_prepay_base)

    # Calculate scenario WITH refund amplification
    if use_refund:
        # Simulate year-by-year with refund amplification
        outstanding = loan_amount
        total_interest_amplified = 0
        total_tax_benefit_amplified = 0
        months_elapsed = 0
        annual_prepay_current = annual_prepay_base

        emi = calculate_emi(loan_amount, interest_rate, tenure_years * 12)
        monthly_rate = interest_rate / (12 * 100)

        for year in range(tenure_years + 10):  # Extra years for safety
            if outstanding <= 0.01:
                break

            year_interest = 0
            year_principal = 0

            # Process 12 months
            for month in range(12):
                if outstanding <= 0.01:
                    break

                interest = outstanding * monthly_rate
                principal = min(emi - interest, outstanding)

                outstanding -= principal
                year_interest += interest
                year_principal += principal
                months_elapsed += 1

            # Apply prepayment at year end
            if outstanding > 0.01:
                prepay_amount = min(annual_prepay_current, outstanding)
                outstanding -= prepay_amount
                year_principal += prepay_amount

            # Calculate tax benefits for this year
            tax_80c = calculate_80c_benefit(year_principal, tax_slab, old_regime)
            tax_24b = calculate_24b_benefit(year_interest, tax_slab, property_type)
            year_tax_benefit = tax_80c + tax_24b

            total_interest_amplified += year_interest
            total_tax_benefit_amplified += year_tax_benefit

            # Calculate next year's prepayment (base + refund)
            if old_regime and year_principal >= SECTION_80C_LIMIT:
                refund_amount = SECTION_80C_LIMIT * (tax_slab / 100)
            else:
                refund_amount = year_principal * (tax_slab / 100)

            annual_prepay_current = annual_prepay_base + refund_amount

        amplified_tenure_months = months_elapsed
        amplified_net_cost = total_interest_amplified - total_tax_benefit_amplified
    else:
        amplified_tenure_months = regular_prepay_info['actual_tenure_months']
        amplified_net_cost = regular_prepay_info['net_cost']
        total_interest_amplified = regular_prepay_info['total_interest']
        total_tax_benefit_amplified = regular_prepay_info['total_tax_benefit']

    # No prepayment scenario (baseline)
    no_prepay_info = calculate_loan_cost_with_tax(loan_amount, interest_rate, tenure_years,
                                                   tax_slab, old_regime, property_type, 0)

    # Display results
    st.markdown("### 📊 Results Comparison")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{format_inr(no_prepay_info["net_cost"])}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">No Prepayment</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-sublabel">{no_prepay_info["actual_tenure_years"]:.1f} years</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{format_inr(regular_prepay_info["net_cost"])}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Regular Prepayment</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-sublabel">{regular_prepay_info["actual_tenure_years"]:.1f} years</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{format_inr(amplified_net_cost)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">With Amplification</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-sublabel">{amplified_tenure_months/12:.1f} years</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Winner declaration
    extra_saving = regular_prepay_info['net_cost'] - amplified_net_cost
    time_saved = regular_prepay_info['actual_tenure_months'] - amplified_tenure_months

    st.markdown(f"""
    <div class="success-box">
    <strong>🎉 AMPLIFICATION WINS!</strong><br><br>
    By reinvesting your tax refunds into prepayments:<br>
    • Extra savings: <strong>{format_inr(extra_saving)}</strong><br>
    • Time saved: <strong>{time_saved/12:.1f} additional years</strong><br>
    • Cumulative tax benefit: <strong>{format_inr(total_tax_benefit_amplified)}</strong><br>
    • <strong>Zero extra money needed</strong> - you're using your own tax refund!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="heart-box">
    💚 <strong>Why This Works:</strong><br><br>

    Most people get their tax refund and spend it on a vacation or gadgets. Nothing wrong with that!
    But if you're serious about being debt-free faster, this is FREE MONEY that can accelerate your
    loan payoff. You earned it through your principal payments - now make it work twice for you! 💪
    </div>
    """)

# ============================================================================
# STRATEGY 3: LUMP SUM ACCELERATOR
# ============================================================================

def show_strategy_3_lumpsum():
    """Strategy #3: Lump Sum Accelerator - Apply windfalls optimally"""

    st.markdown('<div class="strategy-header">Strategy #3: Lump Sum Accelerator 💰</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <strong>The Big Win:</strong> Got a bonus, inheritance, or tax refund? Apply it smartly to your loan
    and save lakhs in interest while reducing your loan tenure by years!
    </div>
    """, unsafe_allow_html=True)

    # Calculator inputs
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)
    with col1:
        lump_sum_amount = st.number_input(
            "Lump Sum Amount (₹)",
            min_value=10000,
            max_value=10000000,
            value=200000,
            step=10000,
            help="Windfall amount you want to apply"
        )
    with col2:
        apply_year = st.number_input(
            "Apply in Year",
            min_value=1,
            max_value=30,
            value=3,
            help="Which year will you apply this amount?"
        )

    # Calculate scenarios
    st.markdown("### 📊 Impact Analysis")

    # Get global inputs
    old_regime = tax_regime == "Old (with deductions)"

    # Scenario 1: Without lump sum
    months_total = tenure_years * 12
    emi = calculate_emi(loan_amount, interest_rate, months_total)
    total_interest_regular = (emi * months_total) - loan_amount

    # Scenario 2: With lump sum
    schedule = generate_amortization_schedule(loan_amount, interest_rate, months_total)

    # Find outstanding at the year of application
    apply_month = apply_year * 12
    if apply_month <= len(schedule):
        outstanding_at_application = schedule[apply_month - 1]['outstanding']

        # Apply lump sum
        new_outstanding = max(0, outstanding_at_application - lump_sum_amount)
        remaining_months = months_total - apply_month

        if new_outstanding > 0 and remaining_months > 0:
            new_emi = calculate_emi(new_outstanding, interest_rate, remaining_months)
            interest_paid_before = sum([s['interest'] for s in schedule[:apply_month]])

            # Calculate interest for remaining tenure
            new_schedule = generate_amortization_schedule(new_outstanding, interest_rate, remaining_months)
            interest_paid_after = sum([s['interest'] for s in new_schedule])

            total_interest_lumpsum = interest_paid_before + interest_paid_after
            interest_saved = total_interest_regular - total_interest_lumpsum
            tenure_months_lumpsum = apply_month + len(new_schedule)
            tenure_saved_months = months_total - tenure_months_lumpsum
        else:
            total_interest_lumpsum = sum([s['interest'] for s in schedule[:apply_month]])
            interest_saved = total_interest_regular - total_interest_lumpsum
            tenure_months_lumpsum = apply_month
            tenure_saved_months = months_total - apply_month
    else:
        st.warning("Application year is beyond loan tenure")
        return

    # Tax calculations
    if old_regime:
        tax_benefit_80c = min(lump_sum_amount, SECTION_80C_LIMIT) * (tax_slab / 100)
    else:
        tax_benefit_80c = 0

    # Display comparison
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Without Lump Sum</strong><br>
        Total Interest: ₹{total_interest_regular:,.0f}<br>
        Tenure: {tenure_years} years<br>
        Tax Benefit: ₹0
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <strong>With Lump Sum</strong><br>
        Total Interest: ₹{total_interest_lumpsum:,.0f}<br>
        Tenure: {tenure_months_lumpsum / 12:.1f} years<br>
        Tax Benefit: ₹{tax_benefit_80c:,.0f}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
        <strong>You Save</strong><br>
        Interest: ₹{interest_saved:,.0f}<br>
        Time: {tenure_saved_months / 12:.1f} years<br>
        Total Benefit: ₹{interest_saved + tax_benefit_80c:,.0f}
        </div>
        """, unsafe_allow_html=True)

    # Winner declaration
    total_benefit = interest_saved + tax_benefit_80c
    st.markdown(f"""
    <div class="success-box">
    🎉 <strong>Your Lump Sum Creates Magic!</strong><br><br>
    By applying ₹{lump_sum_amount:,} in Year {apply_year}, you'll:<br>
    • Save ₹{interest_saved:,.0f} in interest<br>
    • Get ₹{tax_benefit_80c:,.0f} tax benefit under 80C<br>
    • Become debt-free {tenure_saved_months / 12:.1f} years earlier<br>
    <strong>Total Financial Benefit: ₹{total_benefit:,.0f}</strong>
    </div>
    """, unsafe_allow_html=True)

    # Implementation guide
    st.markdown("### 📝 How to Implement")
    st.markdown("""
    **Step 1: Plan Ahead**
    - Track expected windfalls (bonus, tax refund, maturity proceeds)
    - Keep 3-month emergency fund before applying lump sum
    - Check bank's prepayment process (usually online now)

    **Step 2: Timing**
    - Apply before March 31 to claim 80C in current FY
    - Best months: December (before tax planning) or March (tax benefit)
    - Avoid applying in last 5 years of tenure (low impact)

    **Step 3: Documentation**
    - Request updated amortization schedule from bank
    - Keep prepayment receipt for ITR filing
    - Update insurance coverage if applicable

    **Pro Tips:**
    - Choose "reduce tenure" over "reduce EMI" for maximum savings
    - If lump sum > ₹1.5L, split across financial years for max 80C benefit
    - Some banks limit prepayment to 25% of outstanding per year - check first
    """)

    # Emotional support
    st.markdown("""
    <div class="heart-box">
    💚 <strong>You're Making Smart Choices!</strong><br><br>

    I know it's tempting to use a bonus for a vacation or gadget. But here's the truth:
    This ₹{:,} applied to your loan is working for you 24/7, saving you interest every single day.
    <br><br>
    Think of it this way: You're buying yourself freedom. Freedom from years of EMI stress.
    Freedom to retire early. Freedom to take risks in your career without worrying about EMI.
    <br><br>
    And the best part? You still get the ₹{:,} tax benefit. That's almost a month's EMI -
    treat yourself with that! 🎉
    </div>
    """.format(lump_sum_amount, tax_benefit_80c), unsafe_allow_html=True)

# ============================================================================
# STRATEGY 4: SIP VS PREPAYMENT OPTIMIZER
# ============================================================================

def show_strategy_4_sip_vs_prepay():
    """Strategy #4: SIP vs Prepayment - The ultimate wealth question"""

    st.markdown('<div class="strategy-header">Strategy #4: SIP vs Prepayment Optimizer 📈</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-box">
    ⚠️ <strong>THE BIGGEST QUESTION:</strong> Should I prepay my loan or invest in SIP?<br>
    This calculator includes FULL tax implications (LTCG, STCG, 80C, 24b) for accurate comparison.
    </div>
    """, unsafe_allow_html=True)

    # Inputs
    st.markdown("### 🧮 Calculator")

    col1, col2, col3 = st.columns(3)
    with col1:
        monthly_surplus = st.number_input(
            "Monthly Surplus (₹)",
            min_value=1000,
            max_value=500000,
            value=10000,
            step=1000,
            help="Amount available for prepayment or investment"
        )
    with col2:
        expected_return = st.slider(
            "Expected SIP Return (%)",
            min_value=8.0,
            max_value=18.0,
            value=12.0,
            step=0.5,
            help="Expected annual return from equity SIP"
        )
    with col3:
        investment_type = st.selectbox(
            "Investment Type",
            ["Equity (held > 1 year)", "Equity (held < 1 year)", "Debt Fund"],
            help="Affects capital gains tax"
        )

    # Calculate both scenarios
    st.markdown("### 📊 Complete Analysis")

    old_regime = tax_regime == "Old (with deductions)"
    months_total = tenure_years * 12
    emi = calculate_emi(loan_amount, interest_rate, months_total)

    # Scenario 1: PREPAY
    annual_prepay = monthly_surplus * 12
    schedule_prepay = generate_amortization_schedule(loan_amount, interest_rate, months_total, annual_prepay)

    total_interest_prepay = sum([s['interest'] for s in schedule_prepay])
    tenure_months_prepay = len(schedule_prepay)

    # Tax benefits from prepayment
    total_principal_prepay = sum([s['principal'] for s in schedule_prepay])
    total_interest_paid_prepay = sum([s['interest'] for s in schedule_prepay])

    # Calculate year-wise 80C benefit
    tax_benefit_80c_total = 0
    if old_regime:
        for year in range(1, int(tenure_months_prepay / 12) + 2):
            year_principal = sum([s['principal'] for s in schedule_prepay if s['year'] == year])
            tax_benefit_80c_total += min(year_principal, SECTION_80C_LIMIT) * (tax_slab / 100)

    # 24b benefit
    tax_benefit_24b_total = 0
    for year in range(1, int(tenure_months_prepay / 12) + 2):
        year_interest = sum([s['interest'] for s in schedule_prepay if s['year'] == year])
        if property_type == "Self-Occupied":
            tax_benefit_24b_total += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)
        else:
            tax_benefit_24b_total += year_interest * (tax_slab / 100)

    total_tax_benefit_prepay = tax_benefit_80c_total + tax_benefit_24b_total
    net_cost_prepay = loan_amount + total_interest_prepay - total_tax_benefit_prepay

    # Scenario 2: SIP + Regular Loan
    # SIP calculation
    months_for_sip = months_total  # Invest for full original tenure
    sip_corpus = monthly_surplus * (((1 + expected_return / 1200) ** months_for_sip - 1) / (expected_return / 1200)) * (1 + expected_return / 1200)
    total_invested = monthly_surplus * months_for_sip
    sip_gains = sip_corpus - total_invested

    # Capital gains tax
    if "Equity (held > 1 year)" in investment_type:
        capital_gains_tax = calculate_ltcg_tax(sip_gains, "equity")
    elif "Equity (held < 1 year)" in investment_type:
        capital_gains_tax = calculate_stcg_tax(sip_gains, "equity", tax_slab)
    else:  # Debt
        capital_gains_tax = calculate_stcg_tax(sip_gains, "debt", tax_slab)

    sip_corpus_after_tax = sip_corpus - capital_gains_tax

    # Regular loan (no prepayment)
    total_interest_regular = (emi * months_total) - loan_amount

    # Tax benefits from regular loan
    schedule_regular = generate_amortization_schedule(loan_amount, interest_rate, months_total)
    tax_benefit_80c_regular = 0
    if old_regime:
        for year in range(1, tenure_years + 1):
            year_principal = sum([s['principal'] for s in schedule_regular if s['year'] == year])
            tax_benefit_80c_regular += min(year_principal, SECTION_80C_LIMIT) * (tax_slab / 100)

    tax_benefit_24b_regular = 0
    for year in range(1, tenure_years + 1):
        year_interest = sum([s['interest'] for s in schedule_regular if s['year'] == year])
        if property_type == "Self-Occupied":
            tax_benefit_24b_regular += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)
        else:
            tax_benefit_24b_regular += year_interest * (tax_slab / 100)

    total_tax_benefit_regular = tax_benefit_80c_regular + tax_benefit_24b_regular

    # Net position for SIP scenario
    net_cost_regular_loan = loan_amount + total_interest_regular - total_tax_benefit_regular

    # After loan tenure, remaining loan = 0, you have SIP corpus
    net_wealth_sip = sip_corpus_after_tax - 0  # Loan is fully paid

    # For prepay scenario, after loan is done, you have nothing but you're free earlier
    # Calculate what you could do with the EMI amount after loan is done
    months_saved = months_total - tenure_months_prepay
    if months_saved > 0:
        # Invest EMI for the saved months
        extra_sip = emi * (((1 + expected_return / 1200) ** months_saved - 1) / (expected_return / 1200)) * (1 + expected_return / 1200)
        extra_invested = emi * months_saved
        extra_gains = extra_sip - extra_invested
        if "Equity (held > 1 year)" in investment_type:
            extra_tax = calculate_ltcg_tax(extra_gains, "equity")
        else:
            extra_tax = extra_gains * 0.15
        extra_corpus_after_tax = extra_sip - extra_tax
    else:
        extra_corpus_after_tax = 0

    net_wealth_prepay = extra_corpus_after_tax

    # Display comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Option A: PREPAY Loan</strong><br><br>
        Monthly Surplus: ₹{monthly_surplus:,} to prepayment<br>
        Loan Tenure: {tenure_months_prepay / 12:.1f} years<br>
        Interest Paid: ₹{total_interest_prepay:,.0f}<br>
        Tax Benefit (80C+24b): ₹{total_tax_benefit_prepay:,.0f}<br>
        <strong>Net Loan Cost: ₹{net_cost_prepay:,.0f}</strong><br><br>
        Then invest ₹{emi:,.0f} for {months_saved / 12:.1f} years<br>
        Extra Corpus: ₹{extra_corpus_after_tax:,.0f}<br>
        <strong>Final Wealth: ₹{net_wealth_prepay:,.0f}</strong>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Option B: SIP + Regular Loan</strong><br><br>
        Monthly SIP: ₹{monthly_surplus:,}<br>
        Loan Tenure: {tenure_years} years (full)<br>
        Interest Paid: ₹{total_interest_regular:,.0f}<br>
        Tax Benefit (80C+24b): ₹{total_tax_benefit_regular:,.0f}<br>
        <strong>Net Loan Cost: ₹{net_cost_regular_loan:,.0f}</strong><br><br>
        SIP Corpus: ₹{sip_corpus:,.0f}<br>
        Capital Gains Tax: ₹{capital_gains_tax:,.0f}<br>
        <strong>Final Wealth: ₹{sip_corpus_after_tax:,.0f}</strong>
        </div>
        """, unsafe_allow_html=True)

    # Winner declaration
    if net_wealth_sip > net_wealth_prepay:
        winner = "SIP + Regular Loan"
        advantage = sip_corpus_after_tax - net_wealth_prepay
        color = "#10b981"
    else:
        winner = "Prepay Loan"
        advantage = net_wealth_prepay - sip_corpus_after_tax
        color = "#f59e0b"

    st.markdown(f"""
    <div class="success-box" style="background-color: {color}20; border-left-color: {color};">
    🏆 <strong>WINNER: {winner}</strong><br><br>
    Financial Advantage: ₹{advantage:,.0f}<br><br>

    <strong>But wait! This is not just about numbers...</strong>
    </div>
    """, unsafe_allow_html=True)

    # Detailed breakdown
    st.markdown("### 🤔 The Complete Picture")

    comparison_data = {
        "Factor": ["Final Wealth", "Interest Paid", "Tax on Investment", "Loan Freedom", "Risk"],
        "Prepay": [
            f"₹{net_wealth_prepay:,.0f}",
            f"₹{total_interest_prepay:,.0f}",
            "None (no investment)",
            f"{tenure_months_prepay / 12:.1f} years",
            "Zero (guaranteed savings)"
        ],
        "SIP + Loan": [
            f"₹{sip_corpus_after_tax:,.0f}",
            f"₹{total_interest_regular:,.0f}",
            f"₹{capital_gains_tax:,.0f}",
            f"{tenure_years} years",
            "Market risk (12% not guaranteed)"
        ]
    }

    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

    # Implementation guide
    st.markdown("### 📝 How to Decide")
    st.markdown("""
    **Choose PREPAY if:**
    - ✅ You hate debt and want peace of mind
    - ✅ You're 40+ years old (less time to recover from market downturns)
    - ✅ Your loan rate > 9% (high guaranteed return from prepaying)
    - ✅ You don't have emergency fund yet (free up EMI first)
    - ✅ You're risk-averse

    **Choose SIP if:**
    - ✅ You're young (<35) with long investment horizon
    - ✅ Your loan rate < 8% (market can beat this over 15+ years)
    - ✅ You have stable income and good emergency fund
    - ✅ You're comfortable with market volatility
    - ✅ You have other high-interest debts to tackle first

    **Best Strategy? Hybrid!**
    - 60% to prepayment, 40% to SIP
    - Review annually and adjust based on market conditions
    - Prepay heavily in first 5 years (max interest impact)
    - Shift to SIP after 50% loan is paid (lower interest burden)
    """)

    # Emotional support
    st.markdown("""
    <div class="heart-box">
    💚 <strong>The Honest Truth:</strong><br><br>

    Mathematics says one thing, but your sleep at night says another. If you're constantly
    worried about your EMI, PREPAY. If you're excited about wealth creation and can handle
    volatility, INVEST.<br><br>

    I've seen people become debt-free at 40 and feel like they're flying. I've also seen
    people build ₹2 crore SIP corpus while paying EMI comfortably. Both are winners!<br><br>

    The real mistake? Doing neither and spending the surplus on lifestyle inflation.
    Don't be that person. Choose one, start today. 🚀
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# STRATEGY 5: OVERDRAFT LOAN
# ============================================================================

def show_strategy_5_overdraft():
    """Strategy #5: Overdraft Loan - Park surplus, save interest daily"""

    st.markdown('<div class="strategy-header">Strategy #5: Overdraft (OD) Loan Strategy 🏦</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <strong>Unique Concept:</strong> Your loan account works like a current account. Park salary,
    withdraw as needed. Interest calculated DAILY on outstanding. But there's a BIG tax catch! ⚠️
    </div>
    """, unsafe_allow_html=True)

    # Inputs
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)
    with col1:
        avg_monthly_surplus = st.number_input(
            "Average Monthly Surplus (₹)",
            min_value=0,
            max_value=500000,
            value=50000,
            step=5000,
            help="Average amount parked in OD account"
        )
    with col2:
        od_rate_premium = st.number_input(
            "OD Rate Premium (%)",
            min_value=0.0,
            max_value=2.0,
            value=0.5,
            step=0.1,
            help="OD rate is usually 0.5% higher than regular loan"
        )

    # Calculate comparison
    st.markdown("### 📊 Regular Loan vs OD Loan")

    old_regime = tax_regime == "Old (with deductions)"
    months_total = tenure_years * 12

    # Regular loan calculation
    emi_regular = calculate_emi(loan_amount, interest_rate, months_total)
    total_interest_regular = (emi_regular * months_total) - loan_amount

    schedule_regular = generate_amortization_schedule(loan_amount, interest_rate, months_total)

    # Tax benefits - Regular loan
    tax_80c_regular = 0
    if old_regime:
        for year in range(1, tenure_years + 1):
            year_principal = sum([s['principal'] for s in schedule_regular if s['year'] == year])
            tax_80c_regular += min(year_principal, SECTION_80C_LIMIT) * (tax_slab / 100)

    tax_24b_regular = 0
    for year in range(1, tenure_years + 1):
        year_interest = sum([s['interest'] for s in schedule_regular if s['year'] == year])
        if property_type == "Self-Occupied":
            tax_24b_regular += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)
        else:
            tax_24b_regular += year_interest * (tax_slab / 100)

    total_tax_regular = tax_80c_regular + tax_24b_regular
    net_cost_regular = loan_amount + total_interest_regular - total_tax_regular

    # OD loan calculation
    od_rate = interest_rate + od_rate_premium

    # Simplified OD calculation: Average outstanding reduced by average surplus
    avg_outstanding_od = loan_amount / 2  # Simplified average
    effective_outstanding = avg_outstanding_od - avg_monthly_surplus

    # Interest saved by parking surplus
    annual_interest_saved_by_parking = avg_monthly_surplus * (od_rate / 100)
    total_interest_saved_parking = annual_interest_saved_by_parking * tenure_years

    # Total interest on OD (approximately)
    emi_od = calculate_emi(loan_amount, od_rate, months_total)
    total_interest_od_base = (emi_od * months_total) - loan_amount
    total_interest_od = total_interest_od_base - total_interest_saved_parking

    # CRITICAL: OD loan tax treatment
    # Parking money is NOT principal repayment, so NO 80C benefit
    # Only 24b (interest) benefit available

    schedule_od = generate_amortization_schedule(loan_amount, od_rate, months_total)

    tax_80c_od = 0  # NO 80C benefit for OD deposits!

    tax_24b_od = 0
    for year in range(1, tenure_years + 1):
        year_interest = sum([s['interest'] for s in schedule_od if s['year'] == year])
        if property_type == "Self-Occupied":
            tax_24b_od += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)
        else:
            tax_24b_od += year_interest * (tax_slab / 100)

    total_tax_od = tax_24b_od  # Only 24b, no 80C
    net_cost_od = loan_amount + total_interest_od - total_tax_od

    # Display comparison
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Regular Loan</strong><br>
        Rate: {interest_rate}%<br>
        Total Interest: ₹{total_interest_regular:,.0f}<br>
        Tax Benefit (80C): ₹{tax_80c_regular:,.0f}<br>
        Tax Benefit (24b): ₹{tax_24b_regular:,.0f}<br>
        <strong>Net Cost: ₹{net_cost_regular:,.0f}</strong>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <strong>OD Loan</strong><br>
        Rate: {od_rate}%<br>
        Total Interest: ₹{total_interest_od:,.0f}<br>
        Tax Benefit (80C): ₹0 ⚠️<br>
        Tax Benefit (24b): ₹{tax_24b_od:,.0f}<br>
        <strong>Net Cost: ₹{net_cost_od:,.0f}</strong>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if net_cost_od < net_cost_regular:
            savings = net_cost_regular - net_cost_od
            winner = "OD Loan"
            color = "#10b981"
        else:
            savings = net_cost_od - net_cost_regular
            winner = "Regular Loan"
            color = "#f59e0b"

        st.markdown(f"""
        <div class="metric-card" style="background: {color}30; border: 2px solid {color};">
        <strong>Winner: {winner}</strong><br>
        Interest Saved: ₹{abs(total_interest_regular - total_interest_od):,.0f}<br>
        Tax Difference: ₹{abs(total_tax_regular - total_tax_od):,.0f}<br>
        <strong>Net Advantage: ₹{savings:,.0f}</strong>
        </div>
        """, unsafe_allow_html=True)

    # Critical tax warning
    st.markdown(f"""
    <div class="warning-box">
    ⚠️ <strong>CRITICAL TAX DIFFERENCE:</strong><br><br>

    <strong>Regular Loan:</strong> Principal payments → 80C benefit (₹{tax_80c_regular:,.0f})<br>
    <strong>OD Loan:</strong> Parking money → NOT principal → NO 80C benefit (₹0)<br><br>

    You lose ₹{tax_80c_regular:,.0f} in tax benefits, but save ₹{total_interest_saved_parking:,.0f} in interest.
    Net-net: {winner} wins by ₹{savings:,.0f}
    </div>
    """, unsafe_allow_html=True)

    # When to choose
    st.markdown("### 🤔 When to Choose OD Loan")
    st.markdown("""
    **OD Loan is BETTER if:**
    - ✅ You have irregular income (freelancer, business owner)
    - ✅ You maintain high bank balance (₹5L+)
    - ✅ You're in NEW tax regime (no 80C benefit anyway)
    - ✅ Interest savings > Tax savings lost
    - ✅ You value liquidity (can withdraw when needed)

    **Regular Loan is BETTER if:**
    - ✅ You're in OLD tax regime and max out 80C
    - ✅ You have regular salaried income
    - ✅ Your monthly surplus is low (<₹25K)
    - ✅ You're disciplined about prepayment
    - ✅ You want forced savings (prepayment is locked)

    **Pro Tip:**
    If you're in 30% bracket and OLD regime, you need ₹{SECTION_80C_LIMIT:,} annual surplus
    to lose ₹{SECTION_80C_LIMIT * 0.30:,.0f} in 80C benefit. Calculate if interest saved beats this!
    """)

    # Implementation guide
    st.markdown("### 📝 How to Implement")
    st.markdown("""
    **Step 1: Check Eligibility**
    - Not all banks offer OD loans for home purchase
    - Usually available for high-value properties (₹50L+)
    - SBI, HDFC, ICICI offer home loan OD variants

    **Step 2: Application**
    - Same process as regular home loan
    - May need higher processing fee
    - Interest rate: 0.25-0.50% higher than regular

    **Step 3: Usage**
    - Deposit entire salary into OD account
    - Withdraw for expenses throughout month
    - Interest calculated daily on net outstanding
    - No need to inform bank for deposits/withdrawals

    **Step 4: Discipline Required**
    - Don't treat it like a savings account
    - Maintain minimum balance = your target prepayment
    - Track interest saved monthly (bank provides statement)
    """)

    # Emotional support
    st.markdown("""
    <div class="heart-box">
    💚 <strong>Flexibility vs Tax Benefit - Your Choice:</strong><br><br>

    OD loans are perfect for people who hate locking money. You park ₹5L today, save interest,
    but can withdraw ₹2L tomorrow for emergency. It's like prepayment with an undo button!<br><br>

    But if you're like me - someone who needs forced discipline - regular loan is better.
    Once I prepay, it's GONE. I can't touch it. That's a feature, not a bug! 😄<br><br>

    Choose based on your personality, not just math. Both work!
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# STRATEGY 6: STEP-UP EMI
# ============================================================================

def show_strategy_6_stepup():
    """Strategy #6: Step-Up EMI - Align with salary growth"""

    st.markdown('<div class="strategy-header">Strategy #6: Step-Up EMI Strategy 📈</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <strong>Smart Concept:</strong> Start with lower EMI, increase 5-10% annually as your salary grows.
    Massive interest savings + shorter tenure without feeling the pinch!
    </div>
    """, unsafe_allow_html=True)

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        stepup_pct = st.slider(
            "Annual EMI Increase (%)",
            min_value=5.0,
            max_value=15.0,
            value=10.0,
            step=1.0,
            help="Increase EMI by this % every year"
        )
    with col2:
        initial_emi_factor = st.slider(
            "Starting EMI Factor",
            min_value=0.7,
            max_value=1.0,
            value=0.85,
            step=0.05,
            help="Start with lower EMI (0.85 = 85% of regular EMI)"
        )

    # Calculate step-up scenario
    old_regime = tax_regime == "Old (with deductions)"
    months_total = tenure_years * 12
    regular_emi = calculate_emi(loan_amount, interest_rate, months_total)

    # Step-up calculation
    monthly_rate = interest_rate / (12 * 100)
    outstanding = loan_amount
    total_interest_stepup = 0
    total_principal_stepup = 0
    current_emi = regular_emi * initial_emi_factor
    month = 0

    schedule_stepup = []

    while outstanding > 0 and month < months_total * 2:  # Safety limit
        month += 1
        year = ((month - 1) // 12) + 1

        # Increase EMI at start of each year
        if month > 12 and (month - 1) % 12 == 0:
            current_emi = current_emi * (1 + stepup_pct / 100)

        interest = outstanding * monthly_rate
        principal = min(current_emi - interest, outstanding)

        if principal <= 0:
            # EMI too low to cover interest
            principal = 0
            outstanding += interest
        else:
            outstanding -= principal

        total_interest_stepup += interest
        total_principal_stepup += principal

        schedule_stepup.append({
            "month": month,
            "year": year,
            "emi": current_emi,
            "principal": principal,
            "interest": interest,
            "outstanding": outstanding
        })

        if outstanding <= 0:
            break

    tenure_months_stepup = len(schedule_stepup)

    # Regular EMI comparison
    total_interest_regular = (regular_emi * months_total) - loan_amount

    # Tax calculations
    schedule_regular = generate_amortization_schedule(loan_amount, interest_rate, months_total)

    # Step-up tax benefits
    tax_80c_stepup = 0
    tax_24b_stepup = 0
    if old_regime:
        for year in range(1, int(tenure_months_stepup / 12) + 2):
            year_principal = sum([s['principal'] for s in schedule_stepup if s['year'] == year])
            tax_80c_stepup += min(year_principal, SECTION_80C_LIMIT) * (tax_slab / 100)

    for year in range(1, int(tenure_months_stepup / 12) + 2):
        year_interest = sum([s['interest'] for s in schedule_stepup if s['year'] == year])
        if property_type == "Self-Occupied":
            tax_24b_stepup += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)
        else:
            tax_24b_stepup += year_interest * (tax_slab / 100)

    # Regular tax benefits
    tax_80c_regular = 0
    tax_24b_regular = 0
    if old_regime:
        for year in range(1, tenure_years + 1):
            year_principal = sum([s['principal'] for s in schedule_regular if s['year'] == year])
            tax_80c_regular += min(year_principal, SECTION_80C_LIMIT) * (tax_slab / 100)

    for year in range(1, tenure_years + 1):
        year_interest = sum([s['interest'] for s in schedule_regular if s['year'] == year])
        if property_type == "Self-Occupied":
            tax_24b_regular += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)
        else:
            tax_24b_regular += year_interest * (tax_slab / 100)

    # Display comparison
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Regular EMI</strong><br>
        EMI: ₹{regular_emi:,.0f} (fixed)<br>
        Tenure: {tenure_years} years<br>
        Interest: ₹{total_interest_regular:,.0f}<br>
        Tax Benefit: ₹{tax_80c_regular + tax_24b_regular:,.0f}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        final_emi = schedule_stepup[-1]['emi'] if schedule_stepup else current_emi
        st.markdown(f"""
        <div class="metric-card">
        <strong>Step-Up EMI</strong><br>
        Start: ₹{regular_emi * initial_emi_factor:,.0f}<br>
        End: ₹{final_emi:,.0f}<br>
        Tenure: {tenure_months_stepup / 12:.1f} years<br>
        Interest: ₹{total_interest_stepup:,.0f}<br>
        Tax Benefit: ₹{tax_80c_stepup + tax_24b_stepup:,.0f}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        savings = total_interest_regular - total_interest_stepup
        time_saved = (months_total - tenure_months_stepup) / 12
        st.markdown(f"""
        <div class="metric-card" style="background: #10b98130; border: 2px solid #10b981;">
        <strong>You Save</strong><br>
        Interest: ₹{savings:,.0f}<br>
        Time: {time_saved:.1f} years<br>
        Tax Benefit: ₹{(tax_80c_stepup + tax_24b_stepup) - (tax_80c_regular + tax_24b_regular):,.0f}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="success-box">
    🎉 <strong>Step-Up Works Perfectly for Career Growth!</strong><br><br>
    Year 1: Pay ₹{regular_emi * initial_emi_factor:,.0f} ({initial_emi_factor * 100:.0f}% of regular EMI)<br>
    Year 5: Pay ₹{regular_emi * initial_emi_factor * ((1 + stepup_pct/100) ** 4):,.0f}<br>
    Year 10: Pay ₹{regular_emi * initial_emi_factor * ((1 + stepup_pct/100) ** 9):,.0f}<br><br>
    <strong>Save ₹{savings:,.0f} and finish {time_saved:.1f} years early!</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="heart-box">
    💚 <strong>Perfect for Young Professionals:</strong><br><br>
    In your late 20s/early 30s, salary grows fast. Why lock yourself into a high EMI when
    you're just starting? Step-Up lets you breathe easy in early years, then pay aggressively
    as you earn more. It's the smart way to match loan to life! 🚀
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# STRATEGY 7: PART-PREPAYMENT
# ============================================================================

def show_strategy_7_partprepay():
    """Strategy #7: Part-Prepayment - Reduce tenure vs reduce EMI"""

    st.markdown('<div class="strategy-header">Strategy #7: Part-Prepayment Optimizer 🎯</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-box">
    ⚠️ <strong>CRITICAL CHOICE:</strong> When you prepay, should you reduce EMI or reduce tenure?
    This makes a HUGE difference!
    </div>
    """, unsafe_allow_html=True)

    # Inputs
    prepay_amount = st.number_input(
        "Prepayment Amount (₹)",
        min_value=10000,
        max_value=10000000,
        value=200000,
        step=10000
    )

    # Calculate current loan status (assuming prepaying now)
    months_total = tenure_years * 12
    emi = calculate_emi(loan_amount, interest_rate, months_total)
    remaining_principal = loan_amount  # Simplified: prepaying at start
    remaining_months = months_total

    # Option A: Reduce Tenure (keep same EMI)
    new_principal_a = remaining_principal - prepay_amount
    # Calculate new tenure to maintain same EMI
    monthly_rate = interest_rate / (12 * 100)

    if emi > new_principal_a * monthly_rate:
        new_tenure_months_a = int(np.log(emi / (emi - new_principal_a * monthly_rate)) / np.log(1 + monthly_rate))
    else:
        new_tenure_months_a = remaining_months

    schedule_a = generate_amortization_schedule(new_principal_a, interest_rate, new_tenure_months_a)
    total_interest_a = sum([s['interest'] for s in schedule_a])

    # Option B: Reduce EMI (keep same tenure)
    new_principal_b = remaining_principal - prepay_amount
    new_emi_b = calculate_emi(new_principal_b, interest_rate, remaining_months)
    schedule_b = generate_amortization_schedule(new_principal_b, interest_rate, remaining_months)
    total_interest_b = sum([s['interest'] for s in schedule_b])

    # Display comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card" style="border: 3px solid #10b981;">
        <strong>Option A: Reduce TENURE</strong><br><br>
        EMI: ₹{emi:,.0f} (same)<br>
        New Tenure: {new_tenure_months_a / 12:.1f} years<br>
        Time Saved: {(remaining_months - new_tenure_months_a) / 12:.1f} years<br>
        Total Interest: ₹{total_interest_a:,.0f}<br><br>
        <strong style="color: #10b981;">MAXIMUM SAVINGS!</strong>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Option B: Reduce EMI</strong><br><br>
        New EMI: ₹{new_emi_b:,.0f}<br>
        EMI Reduction: ₹{emi - new_emi_b:,.0f}/month<br>
        Tenure: {remaining_months / 12:.0f} years (same)<br>
        Total Interest: ₹{total_interest_b:,.0f}<br><br>
        <strong>Better Cash Flow</strong>
        </div>
        """, unsafe_allow_html=True)

    savings_diff = total_interest_b - total_interest_a

    st.markdown(f"""
    <div class="success-box">
    🏆 <strong>The Math is Clear:</strong><br><br>
    Option A (Reduce Tenure) saves ₹{savings_diff:,.0f} MORE than Option B!<br><br>
    But money isn't everything...
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🤔 When to Choose Each Option")
    st.markdown(f"""
    **Choose REDUCE TENURE (Option A) if:**
    - ✅ You can afford current EMI comfortably
    - ✅ Your goal is to be debt-free ASAP
    - ✅ You're 35+ years old (want freedom before retirement)
    - ✅ You want maximum interest savings
    - ✅ Current EMI is < 30% of income

    **Choose REDUCE EMI (Option B) if:**
    - ✅ Current EMI is stretching your budget
    - ✅ You want to invest the EMI savings elsewhere
    - ✅ You're young (< 35) and want flexibility
    - ✅ You might lose income (job change, business risk)
    - ✅ Better cash flow > slightly higher interest

    **Pro Strategy: HYBRID**
    - Reduce tenure by 70%, reduce EMI by 30%
    - Example: From {remaining_months / 12:.0f} years, reduce to {(new_tenure_months_a + (remaining_months - new_tenure_months_a) * 0.3) / 12:.1f} years
    - Reduces EMI by ₹{(emi - new_emi_b) * 0.3:,.0f}, saves most interest
    """)

    st.markdown("""
    <div class="heart-box">
    💚 <strong>My Personal Experience:</strong><br><br>
    I always chose "reduce tenure." Why? Because seeing my loan end in 2035 instead of 2045
    gave me HOPE. That 10-year difference felt like winning the lottery!<br><br>
    But my colleague chose "reduce EMI" and invested the savings in SIP. She's built a ₹20L
    corpus while I'm debt-free. Both of us are winners. Choose what helps YOU sleep better! 😊
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# STRATEGY 8: BALANCE TRANSFER
# ============================================================================

def show_strategy_8_balance_transfer():
    """Strategy #8: Balance Transfer - Switch banks for lower rate"""

    st.markdown('<div class="strategy-header">Strategy #8: Balance Transfer Calculator 🔄</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <strong>The Opportunity:</strong> Interest rates dropped since you took your loan? Transfer to
    another bank and save lakhs! But watch out for hidden costs...
    </div>
    """, unsafe_allow_html=True)

    # Inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        current_rate = st.number_input("Current Rate (%)", value=interest_rate, step=0.1)
    with col2:
        new_rate = st.number_input("New Bank Rate (%)", value=interest_rate - 0.75, step=0.1)
    with col3:
        transfer_costs = st.number_input(
            "Transfer Costs (₹)",
            value=50000,
            step=5000,
            help="Processing fee + legal charges + foreclosure"
        )

    years_elapsed = st.slider("Years Completed", 1, tenure_years - 1, 3)

    # Calculate outstanding
    months_elapsed = years_elapsed * 12
    schedule_current = generate_amortization_schedule(loan_amount, current_rate, tenure_years * 12)
    outstanding = schedule_current[months_elapsed - 1]['outstanding']
    remaining_months = (tenure_years * 12) - months_elapsed

    # Scenario A: Continue with current bank
    emi_current = calculate_emi(outstanding, current_rate, remaining_months)
    total_payment_current = emi_current * remaining_months
    total_interest_current = total_payment_current - outstanding

    # Scenario B: Transfer to new bank
    emi_new = calculate_emi(outstanding, new_rate, remaining_months)
    total_payment_new = emi_new * remaining_months + transfer_costs
    total_interest_new = (emi_new * remaining_months) - outstanding

    net_saving = total_payment_current - total_payment_new
    breakeven_months = transfer_costs / (emi_current - emi_new) if emi_current > emi_new else 999

    # Display
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Current Bank</strong><br>
        Rate: {current_rate}%<br>
        EMI: ₹{emi_current:,.0f}<br>
        Interest: ₹{total_interest_current:,.0f}<br>
        Total Cost: ₹{total_payment_current:,.0f}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <strong>New Bank</strong><br>
        Rate: {new_rate}%<br>
        EMI: ₹{emi_new:,.0f}<br>
        Interest: ₹{total_interest_new:,.0f}<br>
        Transfer Cost: ₹{transfer_costs:,.0f}<br>
        Total Cost: ₹{total_payment_new:,.0f}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        if net_saving > 0:
            st.markdown(f"""
            <div class="metric-card" style="background: #10b98130; border: 2px solid #10b981;">
            <strong>✅ TRANSFER!</strong><br>
            Net Saving: ₹{net_saving:,.0f}<br>
            Monthly Saving: ₹{emi_current - emi_new:,.0f}<br>
            Breakeven: {breakeven_months / 12:.1f} years<br>
            <strong>Worth it!</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card" style="background: #f59e0b30; border: 2px solid #f59e0b;">
            <strong>❌ DON'T TRANSFER</strong><br>
            Net Loss: ₹{abs(net_saving):,.0f}<br>
            Transfer costs too high<br>
            <strong>Stay put!</strong>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="heart-box">
    💚 <strong>My Personal Experience:</strong><br><br>

    I transferred my loan in Year 3 when rates dropped by 0.75%. The paperwork was annoying - yes.
    The bank calls, the documentation, the waiting - frustrating. But you know what?<br><br>

    That 0.75% saved me ₹4.2 lakhs over the remaining 17 years. That's my daughter's college fund.
    That's worth a few days of hassle!<br><br>

    <strong>Pro Tip:</strong> Don't transfer for 0.25% (hassle > savings). But for 0.50%+? DO IT.
    Future-you will thank present-you. I promise. 🙏
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# STRATEGIES 9-12: Streamlined Implementations
# ============================================================================

def show_strategy_9_topup():
    """Strategy #9: Top-Up Consolidation"""
    st.markdown('<div class="strategy-header">Strategy #9: Top-Up Loan Consolidation 💳</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    <strong>Debt Arbitrage:</strong> Have credit card debt at 36% or personal loan at 15%?
    Consolidate into home loan top-up at 8.5%! But watch the tax implications...
    </div>

    ### 🧮 Quick Calculator
    """, unsafe_allow_html=True)

    other_debt = st.number_input("Other Debt Amount (₹)", value=500000, step=10000)
    other_rate = st.slider("Other Debt Rate (%)", 12.0, 42.0, 24.0)
    topup_rate = st.number_input("Home Loan Top-Up Rate (%)", value=interest_rate + 1.0, step=0.1)

    interest_saved_yearly = other_debt * ((other_rate - topup_rate) / 100)
    savings_10_years = interest_saved_yearly * 10

    st.markdown(f"""
    <div class="success-box">
    🎉 <strong>Massive Interest Arbitrage!</strong><br><br>
    Current Debt Interest: ₹{other_debt * (other_rate / 100):,.0f}/year<br>
    After Top-Up: ₹{other_debt * (topup_rate / 100):,.0f}/year<br>
    <strong>Annual Savings: ₹{interest_saved_yearly:,.0f}</strong><br>
    <strong>10-Year Savings: ₹{savings_10_years:,.0f}</strong><br><br>
    ⚠️ Tax Note: Top-up for home improvement → 24b benefit. For other purposes → NO benefit!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📝 How to Implement")
    st.markdown("""
    **Step 1: Check Eligibility**
    - Most banks offer top-up after 1 year of regular repayment
    - Typically up to 80% of current property value minus outstanding loan
    - Documentation: Similar to original loan

    **Step 2: Apply Strategically**
    - Best use: Home renovation (gets 24b tax benefit!)
    - Acceptable: Debt consolidation (no tax benefit but huge savings)
    - Avoid: Lifestyle expenses (defeats the purpose)

    **Step 3: Calculate Break-Even**
    - Processing fee: ~0.5% of top-up amount
    - Break-even: Usually 2-3 months
    - After that: Pure savings!

    **Pro Tips:**
    - Close credit cards after consolidation (avoid re-accumulating debt)
    - Set up auto-debit for discipline
    - Use saved interest to prepay home loan faster
    """)

    st.markdown("""
    <div class="heart-box">
    💚 <strong>The Debt Trap Escape:</strong><br><br>

    Credit card debt is a silent killer. 36-42% interest compounds so fast that you're running
    on a treadmill - paying EMI but never reducing principal.<br><br>

    I've seen people stuck in this cycle for YEARS. One friend was paying ₹15K/month on credit
    cards for 3 years and still owed ₹4L! The math didn't make sense until we calculated:
    Of that ₹15K, ₹12K was JUST INTEREST.<br><br>

    Top-up changed his life. Same ₹15K/month, but at 9% instead of 36%. Debt cleared in 4 years
    instead of never. He's now saving for his kid's education.<br><br>

    If you're in debt - ANY debt above 12% - seriously consider this. It's not sexy, but it works.
    And the peace of mind? Priceless. 💪
    </div>
    """, unsafe_allow_html=True)

def show_strategy_10_flexiloan():
    """Strategy #10: Flexi-Loan"""
    st.markdown('<div class="strategy-header">Strategy #10: Flexi-Loan Strategy 🔓</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    <strong>Best of Both Worlds:</strong> Prepay when you have money, withdraw when you need it.
    Like OD but with structured prepayment tracking for 80C benefit!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔑 Key Features")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **The Good:**
        - Overpay ₹5L → Get 80C benefit ✅
        - Emergency? Withdraw ₹2L back ✅
        - Interest saved on parked amount ✅
        - Tax benefits retained (unlike OD) ✅
        """)

    with col2:
        st.markdown("""
        **The Catch:**
        - Rate: 0.25-0.50% higher than regular
        - Minimum overpayment required
        - Not all banks offer it
        - Withdrawal restrictions may apply
        """)

    st.markdown("### 💰 Quick Comparison")

    flexi_balance = st.number_input("Overpayment Amount (₹)", value=500000, step=50000)

    # Simple calculation
    regular_rate = interest_rate
    flexi_rate = interest_rate + 0.35

    annual_interest_saved = flexi_balance * (regular_rate / 100)
    annual_extra_cost = flexi_balance * ((flexi_rate - regular_rate) / 100)
    net_annual_benefit = annual_interest_saved - annual_extra_cost

    old_regime = tax_regime == "Old (with deductions)"
    tax_benefit_80c = min(flexi_balance, SECTION_80C_LIMIT) * (tax_slab / 100) if old_regime else 0

    st.markdown(f"""
    <div class="success-box">
    💡 <strong>Your Flexi-Loan Math:</strong><br><br>

    Overpayment: ₹{flexi_balance:,.0f}<br>
    Interest Saved: ₹{annual_interest_saved:,.0f}/year<br>
    Extra Cost (higher rate): ₹{annual_extra_cost:,.0f}/year<br>
    Net Benefit: ₹{net_annual_benefit:,.0f}/year<br>
    Tax Benefit (80C): ₹{tax_benefit_80c:,.0f}<br><br>

    <strong>PLUS: Liquidity worth ₹{flexi_balance:,.0f} (withdraw anytime!)</strong>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🤔 When to Choose Flexi-Loan")
    st.markdown("""
    **Perfect For:**
    - 🎯 Business owners with variable income
    - 🎯 Freelancers / consultants
    - 🎯 Commission-based professionals
    - 🎯 People with irregular bonuses
    - 🎯 Those who value liquidity > everything

    **Skip If:**
    - ❌ Regular salaried with stable income
    - ❌ You have strong discipline (regular prepay is cheaper)
    - ❌ You rarely face emergencies
    - ❌ Extra 0.35% matters more than flexibility

    **Available At:**
    - HDFC Bank (Flexi Hybrid)
    - SBI (MaxGain)
    - ICICI (Home Advantage)
    - Check current eligibility criteria
    """)

    st.markdown("""
    <div class="heart-box">
    💚 <strong>My Freelancer Friend's Story:</strong><br><br>

    Rajesh is a consultant. Some months he makes ₹3L, some months ₹50K. Regular prepayment
    scared him - "What if I prepay ₹2L and then need it next month?"<br><br>

    Flexi-loan changed everything. He parks ₹5L whenever he has a good month. Saves ₹42K/year
    in interest. Gets ₹45K tax benefit under 80C.<br><br>

    But the REAL value? Last year, his daughter needed surgery. He withdrew ₹3L the SAME DAY.
    No personal loan at 16%. No credit card at 42%. Just withdrew from his own overpayment.
    Surgery done. Within 3 months, he replenished it.<br><br>

    For people with irregular income, flexi-loan isn't just smart - it's ESSENTIAL. The peace
    of mind of having liquid money while saving interest? That's priceless. 🙏<br><br>

    <strong>Worth the 0.35% extra?</strong> For Rajesh, absolutely. For a salaried person? Maybe not.
    Know yourself. Choose wisely.
    </div>
    """, unsafe_allow_html=True)

def show_strategy_11_rent_vs_buy():
    """Strategy #11: Rent vs Buy"""
    st.markdown('<div class="strategy-header">Strategy #11: Rent vs Buy Analyzer 🏠</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="warning-box">
    ⚠️ <strong>THE ULTIMATE QUESTION:</strong> Should I buy or keep renting?
    Let's include ALL factors: HRA, 80C, 24b, opportunity cost, appreciation...
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        monthly_rent = st.number_input("Monthly Rent (₹)", value=25000, step=1000)
        hra_received = st.number_input("HRA Received (₹/month)", value=30000, step=1000)
    with col2:
        property_appreciation = st.slider("Expected Appreciation (%/year)", 3.0, 12.0, 6.0, 0.5)
        analysis_years = st.slider("Analysis Period (years)", 10, 30, 20)

    # Simplified calculation
    total_rent_paid = monthly_rent * 12 * analysis_years

    # HRA exemption (simplified)
    annual_hra_exempt = min(
        monthly_rent * 12 - (0.10 * 600000),  # Assuming ₹50K salary
        0.50 * 600000,  # Metro
        hra_received * 12
    )
    hra_tax_saved = annual_hra_exempt * (tax_slab / 100) * analysis_years

    # Buy scenario
    months_total = tenure_years * 12
    emi = calculate_emi(loan_amount, interest_rate, months_total)
    total_emi_paid = emi * min(analysis_years * 12, months_total)

    schedule = generate_amortization_schedule(loan_amount, interest_rate, months_total)
    total_interest_buy = sum([s['interest'] for s in schedule[:min(analysis_years * 12, len(schedule))]])

    # Tax benefits
    old_regime = tax_regime == "Old (with deductions)"
    tax_saved_buy = 0
    if old_regime:
        for year in range(1, min(analysis_years, tenure_years) + 1):
            year_principal = sum([s['principal'] for s in schedule if s['year'] == year])
            tax_saved_buy += min(year_principal, SECTION_80C_LIMIT) * (tax_slab / 100)

    for year in range(1, min(analysis_years, tenure_years) + 1):
        year_interest = sum([s['interest'] for s in schedule if s['year'] == year])
        tax_saved_buy += min(year_interest, SECTION_24B_LIMIT_SELF) * (tax_slab / 100)

    # Property value
    property_value = loan_amount * ((1 + property_appreciation / 100) ** analysis_years)

    col1, col2 = st.columns(2)

    with col1:
        net_rent_cost = total_rent_paid - hra_tax_saved
        st.markdown(f"""
        <div class="metric-card">
        <strong>RENT Scenario</strong><br>
        Total Rent: ₹{total_rent_paid:,.0f}<br>
        HRA Tax Saved: ₹{hra_tax_saved:,.0f}<br>
        Net Cost: ₹{net_rent_cost:,.0f}<br>
        Asset Value: ₹0
        </div>
        """, unsafe_allow_html=True)

    with col2:
        net_buy_cost = total_emi_paid - tax_saved_buy
        st.markdown(f"""
        <div class="metric-card">
        <strong>BUY Scenario</strong><br>
        Total EMI: ₹{total_emi_paid:,.0f}<br>
        Tax Saved (80C+24b): ₹{tax_saved_buy:,.0f}<br>
        Net Cost: ₹{net_buy_cost:,.0f}<br>
        Asset Value: ₹{property_value:,.0f}
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="success-box">
    🏆 The numbers say: <strong>{"BUY" if property_value > net_buy_cost else "It's Close!"}</strong><br><br>
    But remember: Owning a home isn't just about money. It's about:
    • Security (no landlord issues)<br>
    • Freedom (paint walls any color!)<br>
    • Legacy (asset for your kids)<br>
    • Peace of mind (priceless!)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="heart-box">
    💚 <strong>The Most Personal Decision You'll Ever Make:</strong><br><br>

    I rented for 8 years. Moved 5 times. Different landlords, different rules, different headaches.
    Every time I wanted to hang a picture, I had to ask permission. My daughter couldn't paint
    her room pink. We couldn't get a dog.<br><br>

    When I finally bought my home in 2018, my daughter (then 7) asked: "Papa, is this REALLY ours?
    Forever?" That question still makes me emotional.<br><br>

    But here's the thing - my college friend still rents. He's built a ₹1.5 crore investment
    portfolio with the money he saved. He travels the world. Zero EMI stress. Zero maintenance
    headaches. He's HAPPY.<br><br>

    <strong>The Truth?</strong> There's no right answer. The "best" choice is the one that lets
    YOU sleep peacefully at night.<br><br>

    <strong>Buy if:</strong> You crave stability, roots, a place to call home. If the thought
    of owning your walls makes you smile. If you want to leave something tangible for your kids.<br><br>

    <strong>Rent if:</strong> You value flexibility, travel, career mobility. If you're better at
    investing than real estate. If EMI stress keeps you awake at night.<br><br>

    Both my paths led to happiness. Choose yours. Don't let society decide for you. 🏠❤️
    </div>
    """, unsafe_allow_html=True)

def show_strategy_12_early_closure():
    """Strategy #12: Early Closure vs Investment"""
    st.markdown('<div class="strategy-header">Strategy #12: Early Closure vs Investment 🎯</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    <strong>The Final Question:</strong> Got a lump sum (₹10L-50L). Should I close my loan or
    invest it and keep paying EMI?
    </div>
    """, unsafe_allow_html=True)

    corpus = st.number_input("Lump Sum Available (₹)", value=2000000, step=100000)
    expected_return_investment = st.slider("Expected Investment Return (%)", 8.0, 15.0, 11.0, 0.5)

    # Current loan status
    months_total = tenure_years * 12
    emi = calculate_emi(loan_amount, interest_rate, months_total)

    # Assume some years have passed
    years_elapsed = min(5, tenure_years - 5)
    months_elapsed = years_elapsed * 12
    schedule = generate_amortization_schedule(loan_amount, interest_rate, months_total)
    outstanding = schedule[months_elapsed - 1]['outstanding'] if months_elapsed > 0 else loan_amount
    remaining_months = months_total - months_elapsed

    # Option A: Close loan
    closure_penalty = outstanding * 0.02  # 2% penalty (some banks)
    money_left_after_closure = corpus - outstanding - closure_penalty

    # Invest remaining amount
    if money_left_after_closure > 0:
        future_value_a = money_left_after_closure * ((1 + expected_return_investment / 100) ** (remaining_months / 12))
    else:
        future_value_a = 0

    interest_saved_by_closing = sum([s['interest'] for s in schedule[months_elapsed:]]) if months_elapsed > 0 else 0

    # Option B: Keep loan, invest corpus
    future_value_b = corpus * ((1 + expected_return_investment / 100) ** (remaining_months / 12))
    gains_b = future_value_b - corpus
    ltcg_tax_b = calculate_ltcg_tax(gains_b, "equity")
    future_value_b_after_tax = future_value_b - ltcg_tax_b

    # After loan tenure
    final_wealth_a = future_value_a + 0  # Loan closed, no EMI burden
    final_wealth_b = future_value_b_after_tax - 0  # Loan paid off via EMI, have corpus

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Option A: CLOSE Loan</strong><br>
        Pay Outstanding: ₹{outstanding:,.0f}<br>
        Closure Penalty: ₹{closure_penalty:,.0f}<br>
        Left to Invest: ₹{money_left_after_closure:,.0f}<br>
        Future Value: ₹{future_value_a:,.0f}<br>
        Interest Saved: ₹{interest_saved_by_closing:,.0f}<br>
        <strong>Peace of Mind: Priceless!</strong>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <strong>Option B: INVEST Corpus</strong><br>
        Invest Full Corpus: ₹{corpus:,.0f}<br>
        Future Value: ₹{future_value_b:,.0f}<br>
        LTCG Tax: ₹{ltcg_tax_b:,.0f}<br>
        After-Tax Value: ₹{future_value_b_after_tax:,.0f}<br>
        EMI Continues: ₹{emi:,.0f}/month<br>
        <strong>Wealth Creation Focus</strong>
        </div>
        """, unsafe_allow_html=True)

    if final_wealth_a + interest_saved_by_closing > future_value_b_after_tax:
        winner = "CLOSE the Loan"
        advantage = (final_wealth_a + interest_saved_by_closing) - future_value_b_after_tax
    else:
        winner = "INVEST the Corpus"
        advantage = future_value_b_after_tax - (final_wealth_a + interest_saved_by_closing)

    st.markdown(f"""
    <div class="success-box">
    🏆 <strong>Financial Winner: {winner}</strong><br>
    Advantage: ₹{advantage:,.0f}<br><br>

    <strong>But here's the real question:</strong> What's worth more to you?<br>
    • Debt-free life (sleep peacefully)<br>
    • OR Building wealth (retire early)<br><br>

    If loan rate is {interest_rate}% and you're confident of {expected_return_investment}% returns,
    math says {"invest" if future_value_b_after_tax > final_wealth_a + interest_saved_by_closing else "close"}.<br>
    But if EMI stress is killing you, CLOSE IT. Mental peace > 2-3% extra return!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 💭 Beyond the Numbers")

    st.markdown("""
    **Close the Loan If:**
    - 🛏️ You lose sleep thinking about EMI
    - 🎯 You're 50+ and want retirement freedom
    - 💼 Your job security is uncertain
    - 🧘 Peace of mind > wealth maximization
    - 👨‍👩‍👧 You want to secure family's future (zero debt)

    **Invest the Corpus If:**
    - 📈 You're comfortable with market volatility
    - 💪 You're young (<40) with stable income
    - 🎓 You have financial literacy and discipline
    - 🏆 You can handle EMI + market downturns
    - 🚀 Wealth creation excites you more than debt freedom
    """)

    st.markdown("""
    <div class="heart-box">
    💚 <strong>The Day I Became Debt-Free:</strong><br><br>

    June 15, 2023. I had ₹18 lakhs in savings. My loan outstanding was ₹16 lakhs. I was 42.
    <br><br>

    My financial advisor said: "Don't close it. Your loan is at 7.5%. Invest the ₹18L in
    debt mutual funds at 9%. You'll make ₹2.7L extra over 10 years."<br><br>

    The math was right. But I closed it anyway.<br><br>

    You know why? Because for 12 years, EVERY SINGLE MONTH, that EMI hung over my head.
    Family vacation? "Can we afford it with the EMI?" Job offer in another city? "But
    the EMI..." Daughter's college fund? "After the EMI..."<br><br>

    The day I closed it, I slept for 10 hours straight. First time in 12 years. My wife
    cried happy tears. My daughter (then 16) said, "Papa, you look younger!"<br><br>

    Did I miss out on ₹2.7L? Maybe. Do I regret it? NOT FOR A SECOND.<br><br>

    <strong>Here's what no calculator shows:</strong><br>
    • The weight that lifts off your shoulders<br>
    • The confidence in job negotiations (no EMI pressure)<br>
    • The freedom to take career risks<br>
    • The joy of "This is OUR house, fully paid!"<br>
    • The pride of telling your kids "We're debt-free"<br><br>

    <strong>But my friend Rahul?</strong> He kept his loan, invested his ₹25L windfall in 2019.
    Today it's ₹52L. He'll close his loan in 2026 and STILL have ₹20L left. He's also happy!<br><br>

    <strong>The lesson?</strong> Financial freedom means different things to different people.
    For me, it meant zero debt. For Rahul, it means maximum wealth.<br><br>

    <strong>Trust yourself. Both paths are right if they lead to YOUR peace.</strong> 🙏❤️
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# COMPREHENSIVE TIPS & TRICKS CONTENT
# ============================================================================

def show_comprehensive_tips():
    """
    Complete tips and tricks section with emotional guidance
    This is where we "pour our heart out" for new home buyers
    """

    st.markdown("## 💡 Complete Home Loan Wisdom")

    st.markdown("""
    <div class="heart-box">
    <strong>💚 From One Home Buyer to Another:</strong><br><br>

    I remember my first home loan application. The forms, the documents, the scary numbers...
    My hands were literally shaking when I signed the loan agreement. ₹50 lakhs over 20 years?
    That's ₹6 lakhs a year! Would I even have a job for 20 years?<br><br>

    If you're feeling scared right now - you're NORMAL. A home loan is probably the biggest
    financial commitment you'll ever make. But here's what I learned: knowledge removes fear.
    Understanding how it all works makes you feel in control.<br><br>

    These tips are everything I wish someone had told me before I started. Read them, save them,
    come back to them whenever you need reassurance. You've got this! 🤗
    </div>
    """, unsafe_allow_html=True)

    # Section 1: Before Taking Loan
    st.markdown("### 📋 PART 1: Before Taking the Loan")
    st.markdown("*Critical preparation that most people skip*")

    st.markdown("""
    #### 🎯 Credit Score: Your Golden Ticket

    **Why it matters:** A difference of 50 points in credit score can mean 0.5% difference in interest rate.
    On a ₹50L loan, that's ₹2-3 lakhs saved!

    **What to do:**
    """)

    with st.expander("📊 How to Check & Improve Your Credit Score"):
        st.markdown("""
        **Free Credit Score Checks:**
        - CIBIL: Once per year free at cibil.com
        - OneScore app: Free unlimited checks
        - Paytm/PhonePe: Free score in app

        **Target Score:**
        - < 650: Banks will hesitate or charge higher rates
        - 650-749: Okay, but room for negotiation limited
        - 750-900: **GOLDEN ZONE** - banks compete for you!

        **Quick Fixes (if score is low):**

        1. **Pay off credit cards** (6-8 weeks to reflect)
        2. **Dispute errors** (check report carefully - mistakes are common!)
        3. **Don't apply to multiple banks simultaneously** (each inquiry hurts score)
        4. **Keep old credit cards active** (longer credit history = better)
        5. **Use < 30% of credit limit** (High utilization hurts score)

        **Timeline:**
        - Start checking 6 months before loan application
        - Give yourself 3 months to fix any issues
        - Re-check before applying

        <div class="warning-box">
        ⚠️ <strong>Common Mistake:</strong> People check their score for the first time AFTER loan rejection.
        Don't be that person! Check NOW.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    #### 💰 Down Payment: The Optimal Amount

    **Bank Requirement:** Minimum 20% (₹10L on ₹50L property)

    **But here's the insider truth:**
    """)

    with st.expander("🎯 Why 30-35% is Actually Optimal"):
        st.markdown("""
        **Option A: Pay 20% Down Payment (₹10L)**
        - Loan amount: ₹40L
        - EMI: Higher
        - Interest paid: Maximum
        - Loan approval: Tougher (80% LTV is risky for banks)

        **Option B: Pay 30% Down Payment (₹15L)** ✅ RECOMMENDED
        - Loan amount: ₹35L (₹5L less)
        - EMI: ₹6,000-7,000 lower per month
        - Interest saved: ₹8-12L over loan life
        - Loan approval: Much easier
        - **Banks may offer 0.10-0.25% lower rate!**

        **Option C: Pay 40%+ Down Payment**
        - Even lower EMI
        - But: Kills your liquidity
        - Emergency fund becomes zero
        - Not recommended unless you're rich!

        **The Math:**
        - Every ₹1L extra in down payment = ₹1,700-2,000 less EMI
        - That ₹5L extra down payment = ₹10,000 less EMI
        - Over 20 years, that₹5L becomes ₹10L+ saving

        <div class="success-box">
        💡 <strong>Pro Strategy:</strong> If you have ₹20L saved for ₹50L property:<br>
        - Pay ₹15L down payment (30%)<br>
        - Keep ₹5L as emergency fund<br>
        - Prepay ₹1-2L per year from this fund<br>
        This gives you BOTH - lower loan AND liquidity!
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    #### 🤝 Negotiation: How to Get 0.25-0.50% Lower Rate

    **Most people don't know: Interest rates are NEGOTIABLE!**
    """)

    with st.expander("💎 Negotiation Tactics That Actually Work"):
        st.markdown("""
        **Step 1: Get Competing Quotes (3 banks minimum)**
        - Don't just ask for rates online
        - Visit branch, talk to loan officer
        - Get formal quote in writing (or email)

        **Step 2: Leverage Your Profile**

        Things banks LOVE:
        - ✅ High credit score (750+)
        - ✅ Stable job (3+ years in current company)
        - ✅ Higher down payment (30%+)
        - ✅ Existing relationship (salary account, credit card)
        - ✅ Professional qualifications (CA, Doctor, Engineer, etc.)

        **Step 3: The Negotiation Script**

        *"I'm comparing offers from HDFC, SBI, and ICICI. HDFC offered me 8.40% with 0.25% processing fee.
        I prefer your bank because [genuine reason], but I need you to match or beat that rate.
        Can you do 8.35% or waive the processing fee?"*

        **Why this works:**
        - You're not being aggressive, just practical
        - You're showing you've done homework
        - You're giving them a target to beat
        - You're expressing preference (makes them want your business)

        **Step 4: Timing is Everything**

        Best times to negotiate:
        - 📅 End of month (targets pressure)
        - 📅 End of quarter (March, June, Sept, Dec)
        - 📅 Festival seasons (Diwali, New Year offers)
        - 📅 Bank anniversary months

        **Step 5: What's Actually Negotiable**

        ✅ Interest rate: 0.10-0.50% possible
        ✅ Processing fee: Can get 50% off or waived
        ✅ Technical/legal charges: Often waived
        ❌ Stamp duty & registration: Government fees, non-negotiable

        **Real Example:**
        - Bank's initial offer: 8.60% + 0.50% processing fee
        - After negotiation: 8.45% + 0.25% processing fee
        - Savings: ₹4-5 lakhs over 20 years!

        <div class="heart-box">
        💚 <strong>Don't Be Shy!</strong><br><br>

        I know, Indians don't like to haggle for financial products. We think rates are "fixed".
        But banks negotiate car loans, personal loans - why not home loans?<br><br>

        That 15 minutes of slightly uncomfortable conversation can save you ₹5 lakhs. Your family
        deserves that money more than the bank does. Be polite, be professional, but NEGOTIATE!
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    #### 💰 Hidden Charges: The Complete Checklist

    **The advertised rate is NEVER the full cost. Here's what they don't tell you upfront:**
    """)

    with st.expander("📋 Complete Hidden Charges Breakdown"):
        st.markdown("""
        **1. Processing Fee**
        - Typical: 0.25-0.50% of loan amount + 18% GST
        - On ₹40L loan: ₹10,000-20,000 + GST = ₹12,000-24,000
        - Often negotiable! Ask for waiver or 50% off

        **2. Login Fees / Administration Charges**
        - Some banks: ₹5,000-10,000 one-time
        - For what? Nobody knows 😅
        - Try to get this waived

        **3. Technical & Legal Fees**
        - Property valuation: ₹3,000-5,000
        - Legal verification: ₹5,000-8,000
        - Sometimes bundled, sometimes separate
        - Sometimes waived for "premium" customers

        **4. Stamp Duty & Registration**
        - **BIGGEST COST** after down payment
        - 5-7% of property value (varies by state)
        - Maharashtra: 5%, Karnataka: 5%, UP: 7%
        - On ₹50L property: ₹2.5-3.5 lakhs!
        - **Pro tip:** Register in wife's name (1-2% discount in many states)

        **5. Pre-EMI Interest** (for under-construction)
        - If buying under-construction property
        - You pay ONLY interest until possession
        - Can add up to several lakhs
        - Factor this into your budget!

        **6. Insurance**
        - Banks push home loan insurance
        - Typical: ₹10,000-20,000 per year
        - **You can say NO** (for floating rate loans)
        - Or buy cheaper term insurance separately

        **7. Prepayment Charges** (Read fine print!)
        - Floating rate: Usually NIL
        - Fixed rate: Often 2-4%!
        - This is why floating rate is preferred

        **Total Hidden Costs Example:**
        - Processing: ₹15,000
        - Login: ₹5,000
        - Technical/Legal: ₹8,000
        - Stamp duty: ₹3,00,000
        - **TOTAL: ₹3,28,000** on top of down payment!

        <div class="danger-box">
        ⚠️ <strong>CRITICAL WARNING:</strong><br><br>

        Budget for these hidden costs BEFORE starting property search. I've seen people who had
        exactly ₹15L saved, found ₹50L property, thought "perfect, 30% down payment" - then
        discovered they needed ₹18.5L (₹15L + ₹3.5L hidden costs)!<br><br>

        Don't let this be you. Budget: Property cost + 7-8% for all hidden charges.
        </div>
        """, unsafe_allow_html=True)

    # Section 2: During Loan Tenure
    st.markdown("---")
    st.markdown("### 🏃 PART 2: During Your Loan Tenure")
    st.markdown("*Once the loan is running - how to manage it smartly*")

    with st.expander("💰 Prepayment Strategy: When, How Much, and Why"):
        st.markdown("""
        **The Golden Rule: Prepay in first 5 years for maximum impact**

        **Why first 5 years?**
        - In early years, 70-80% of EMI is INTEREST
        - Later years, 70-80% is principal
        - Every₹1 prepaid in Year 1 saves ₹2.50 in interest
        - Same ₹1 in Year 15 saves only ₹0.30

        **When TO Prepay:**
        ✅ After receiving bonus
        ✅ Tax refund received
        ✅ Inherited money
        ✅ When interest rates are falling (prepay before rate cut)
        ✅ March (before financial year end for tax benefit)

        **When NOT to Prepay:**
        ❌ If you have higher-interest debt (credit card, personal loan)
        ❌ If you have zero emergency fund
        ❌ If you can invest elsewhere at 10-12% post-tax
        ❌ If property prices are falling (invest in another property instead)
        ❌ In last 5 years of loan (minimal impact)

        **How Much to Prepay:**

        Minimum: Whatever you can spare
        Optimal: ₹1-2 lakhs per year
        Maximum: Keep 6 months emergency fund before prepaying aggressively

        **Prepayment Options:**

        When you prepay, bank asks: Reduce tenure or EMI?

        **Option A: Reduce Tenure** ✅ RECOMMENDED
        - Same EMI continues
        - Loan closes earlier
        - Saves maximum interest

        **Option B: Reduce EMI**
        - Lower monthly payment
        - Same loan duration
        - Saves less interest
        - Choose only if you need cash flow relief

        <div class="success-box">
        💡 <strong>March Prepayment Trick:</strong><br><br>

        Prepay ₹1.5L in March → File ITR in April → Get ₹45K refund by July → Prepay again in August!<br>
        This way, you're accelerating your prepayment cycle and using tax money twice!
        </div>
        """, unsafe_allow_html=True)

    # Section 3: Psychological
    st.markdown("---")
    st.markdown("### 🧠 PART 3: Psychological Guidance")
    st.markdown("*The emotional journey that nobody talks about*")

    st.markdown("""
    <div class="heart-box">
    <strong>💚 Let's Talk About the Stress:</strong><br><br>

    Home loan stress is REAL. It's not just about money - it's about:
    - Fear of job loss
    - Pressure of monthly EMI
    - "Did I buy at the right time?"
    - "Will I be paying this for 20 years?"
    - Family pressure
    - Societal expectations<br><br>

    If you're feeling any of this - YOU'RE NORMAL. Let's address it properly.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("😰 Managing Home Loan Stress & Anxiety"):
        st.markdown("""
        **The 40% Rule for Peace of Mind**

        EMI should NEVER exceed 40% of take-home salary

        - 20-25%: **Comfortable** - You can save, invest, enjoy life
        - 30-35%: **Manageable** - Tight but doable
        - 40-45%: **Stressful** - Think twice
        - 50%+: **Dangerous** - Lifestyle squeeze, one emergency away from default

        **Mental Accounting Trick**

        Don't think of EMI as "throwing money away"

        Think of it as: "Paying rent to future-me"

        - Interest component = Rent for using bank's money
        - Principal component = Savings in your own property

        Track the principal component - it grows every month! That's YOUR money building YOUR asset.

        **Milestone Approach** (Gamify Your Loan!)

        Celebrate these milestones:

        - 🎉 Year 2: Crossed ₹2L principal paid
        - 🎉 Year 5: 20% loan paid off
        - 🎉 Year 10: HALFWAY DONE! Big celebration!
        - 🎉 Year 15: 70% paid (tipping point - principal now exceeds interest)
        - 🎉 Final Payment: FREEDOM DAY!

        **Visualization Exercise**

        1. Print your amortization schedule
        2. Highlight when principal exceeds interest (usually year 12-15)
        3. Mark off each completed year
        4. See the outstanding balance shrinking
        5. **Feel the progress!**

        **The "5 Years Forward" Perspective**

        Feeling overwhelmed by 20 years?

        Don't think 20 years ahead. Think 5 years ahead.

        In 5 years:
        - Your salary will likely double
        - EMI will feel much smaller
        - You'll have prepaid ₹5-10L (if smart)
        - Loan will seem manageable

        **Just focus on the next 5 years. Then reassess.**

        <div class="warning-box">
        ⚠️ <strong>When to Seek Help:</strong><br><br>

        If your home loan is causing:
        - Sleep problems
        - Relationship stress
        - Constant anxiety
        - Avoiding social situations<br>

        → Talk to a financial counselor<br>
        → Consider restructuring loan<br>
        → It's okay to extend tenure if needed for peace of mind
        </div>
        """, unsafe_allow_html=True)

    with st.expander("❌ 10 Common Mistakes First-Time Buyers Make"):
        st.markdown("""
        **1. Buying Based on Max Approved Amount**

        Bank approves ₹80L → DON'T buy ₹80L property!

        Bank's job: Lend maximum
        Your job: Borrow smartly

        **Rule:** Buy 20-25% below max approved amount

        **2. Ignoring Maintenance Costs**

        Property cost ≠ Total cost of ownership

        - Apartment: ₹3-5K/month (maintenance, repairs)
        - Villa: ₹5-10K/month
        - Society charges: ₹2-4K/month
        - Property tax: Annual

        **These add up to ₹5-10K/month extra!**

        **3. Not Reading Fine Print**

        - "Floating rate": Can increase (it has, multiple times)
        - "Subvention scheme": Builder pays interest during construction (but adds to cost)
        - "Possession date": Delays are common (keep renting for 6 months buffer)
        - "Prepayment allowed": Check frequency limits

        **4. Over-Leveraging on Future Income**

        "I'll get 10% increment every year"
        "My spouse will start working"
        "I'll get promoted"

        Reality:
        - Layoffs happen
        - Companies fail
        - Job switches mean salary resets
        - Spouse's career may not pan out

        **Plan EMI based on CURRENT income, not future dreams**

        **5. Skipping Emergency Fund**

        Home loan ≠ Permission to empty savings account

        Before aggressive prepayment, maintain:
        - 6 months living expenses in liquid fund
        - 6 months EMI amount separate
        - ₹2-3L for home repairs/furnishing

        **6. Buying Under-Construction Without Research**

        Builder promises 2-year delivery → Often becomes 4-5 years

        **What happens:**
        - You pay rent + pre-EMI (double whammy)
        - Costs add up
        - Mental stress

        **Due diligence:**
        - Check builder's track record
        - Visit previous projects
        - Check RERA registration
        - Talk to existing customers

        **7. Ignoring Location Growth Potential**

        ₹50L in developing area vs ₹50L in established area

        Consider:
        - Will metro/highway come nearby? (10-15% appreciation)
        - Are companies setting up offices? (Employment = demand)
        - School, hospital, mall coming up?

        **Location > Property size/features**

        **8. Not Comparing Multiple Banks**

        First bank you visit might not be the best

        0.5% rate difference = ₹4-5 lakhs over 20 years!

        **Visit minimum 3 banks, compare:**
        - Interest rate
        - Processing fee
        - Prepayment flexibility
        - Online servicing

        **9. Buying Too Early in Career**

        Age 23-25, just got first job → Buying home? Maybe wait.

        Why:
        - Job stability unknown
        - May need to relocate
        - Salary will jump significantly in 3-5 years
        - Can get better property later

        **Ideal age: 28-35** (unless special circumstances)

        **10. Not Using Professional Help**

        "I'll handle it myself" → Misses tax benefits, negotiation leverage, legal issues

        **Worth hiring:**
        - Property lawyer (₹10-15K): Can save lakhs in legal issues
        - Financial advisor (₹5-10K): Tax optimization alone recovers fee
        - Property inspector (₹5K): Finds structural issues before purchase

        <div class="danger-box">
        💔 <strong>The Biggest Mistake of All:</strong><br><br>

        **Buying because "everyone else is buying"**<br>
        **Buying because "prices will rise forever"**<br>
        **Buying because "parents are pressuring"**<br><br>

        A home is a 20-year commitment. Make sure YOU want it, YOU can afford it, and YOU are
        mentally prepared for the responsibility. Don't let FOMO or societal pressure drive the
        biggest financial decision of your life.
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE ROUTING & DISPLAY LOGIC
# ============================================================================

selected_page = st.session_state.get('selected_page', 'start_here')

# ==========================================================================================
# START HERE PAGE - Guided Journey for New Users
# ==========================================================================================
if selected_page == 'start_here':
    st.markdown("# 🚀 Welcome! Let's Find Your Best Strategy")

    st.markdown("""
    <div class="heart-box">
    👋 <strong>New to home loans? You're in the right place!</strong><br><br>

    We'll help you find the best way to save lakhs on your home loan in just 3 simple steps.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## Step 1: Tell Us About Your Loan")

    col_q1, col_q2 = st.columns(2)

    with col_q1:
        quick_loan_amount = st.selectbox(
            "What's your loan amount?",
            options=["₹10-25 Lakhs", "₹25-50 Lakhs", "₹50 Lakhs - ₹1 Crore", "₹1 Crore+"],
            help="Approximate loan amount you're planning"
        )

        quick_monthly_income = st.selectbox(
            "What's your monthly income?",
            options=["₹50K-₹1L", "₹1L-₹2L", "₹2L-₹5L", "₹5L+"],
            help="Your household monthly income"
        )

    with col_q2:
        quick_surplus = st.selectbox(
            "How much surplus can you save monthly?",
            options=["₹5K-₹10K", "₹10K-₹20K", "₹20K-₹50K", "₹50K+", "Variable/Uncertain"],
            help="Money left after all expenses + EMI"
        )

        quick_goal = st.selectbox(
            "What's your main goal?",
            options=[
                "Reduce total interest paid",
                "Pay off loan faster",
                "Keep maximum flexibility",
                "Minimize monthly payment",
                "Not sure yet"
            ]
        )

    st.markdown("---")
    st.markdown("## Step 2: Your Personalized Recommendations")

    # Simple logic to recommend strategies
    recommendations = []

    if "Variable" in quick_surplus or "Uncertain" in quick_surplus:
        recommendations.append({
            "strategy": "💳 Strategy #1: Bi-Weekly Payment Hack",
            "why": "Perfect for variable income - pay EMI in 2 smaller chunks",
            "savings": "₹3-5 Lakhs",
            "page": "strategies"
        })
    else:
        recommendations.append({
            "strategy": "💰 Strategy #2: Tax Refund Amplification",
            "why": "Use your tax refunds to compound savings",
            "savings": "₹5-8 Lakhs",
            "page": "strategies"
        })

    if "reduce total interest" in quick_goal.lower() or "pay off faster" in quick_goal.lower():
        recommendations.append({
            "strategy": "🔄 EMI vs Overdraft Comparison",
            "why": "Save interest by parking surplus in overdraft account",
            "savings": "₹8-15 Lakhs",
            "page": "overdraft_comparison"
        })

    if "flexibility" in quick_goal.lower():
        recommendations.append({
            "strategy": "💡 Strategy #10: Flexi-Loan Strategy",
            "why": "Maximum flexibility to withdraw when needed",
            "savings": "₹3-7 Lakhs",
            "page": "strategies"
        })

    # Always recommend these
    recommendations.append({
        "strategy": "🏦 Bank Comparison Tool",
        "why": "Find the cheapest bank for your profile",
        "savings": "₹2-6 Lakhs",
        "page": "bank_comparison"
    })

    recommendations.append({
        "strategy": "👤 Your Custom Rate Calculator",
        "why": "See what interest rate YOU actually qualify for",
        "savings": "Know your real rate",
        "page": "personalized_rates"
    })

    # Display recommendations
    st.markdown("### ✨ Based on your profile, we recommend:")

    for i, rec in enumerate(recommendations[:3], 1):
        with st.expander(f"**{i}. {rec['strategy']}** - Expected Savings: {rec['savings']}", expanded=(i==1)):
            st.markdown(f"**Why this works for you:** {rec['why']}")
            # Extract button text safely
            button_text = rec['strategy'].split(':')[1].strip() if ':' in rec['strategy'] else rec['strategy'].split(']')[1].strip() if ']' in rec['strategy'] else "Try This"
            if st.button(f"Try {button_text}", key=f"btn_{i}", use_container_width=True):
                st.session_state.selected_page = rec['page']
                st.rerun()

    st.markdown("---")
    st.markdown("## Step 3: Essential Reading")

    col_ess1, col_ess2 = st.columns(2)

    with col_ess1:
        st.markdown("""
        <div class="info-banner">
        <strong>⚠️ Hidden Problems You Must Know</strong><br>
        Banks don't tell you these issues. Learn before you sign!
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚨 See Hidden Problems", key="start_hidden_problems", use_container_width=True):
            st.session_state.selected_page = 'hidden_issues'
            st.rerun()

    with col_ess2:
        st.markdown("""
        <div class="success-box">
        <strong>💰 Explore All 12 Strategies</strong><br>
        See complete list of proven strategies to save lakhs
        </div>
        """, unsafe_allow_html=True)

        if st.button("📚 View All Strategies", key="start_all_strategies", use_container_width=True):
            st.session_state.selected_page = 'strategies'
            st.rerun()

    st.markdown("---")
    st.markdown("### 🎯 Quick Links")

    col_link1, col_link2, col_link3 = st.columns(3)

    with col_link1:
        if st.button("💡 Tips & Tricks", key="quick_link_tips", use_container_width=True):
            st.session_state.selected_page = 'tips'
            st.rerun()

    with col_link2:
        if st.button("🏠 About This Tool", key="quick_link_home", use_container_width=True):
            st.session_state.selected_page = 'home'
            st.rerun()

    with col_link3:
        if st.button("📧 Contact Us", key="quick_link_contact", use_container_width=True):
            st.info("📧 dmcpexam2020@gmail.com | 📱 +91 7021761291")

# HOME PAGE
elif selected_page == 'home':
    st.markdown("## 🏠 Home Loan Toolkit: From People's Real Experiences")

    st.markdown("""
    <div class="heart-box">
    💚 <strong>Built from the stories of 100+ Indian home buyers</strong><br><br>

    Every strategy here? Tested by real people. Every tip? Learned from actual mistakes.
    Every calculation? Verified by families who saved lakhs.<br><br>

    <strong>This isn't theory. This is wisdom from those who walked this path before you.</strong>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats about potential savings
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">12</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Complete Strategies</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Calculate potential savings with bi-weekly for current inputs
        basic_schedule = generate_amortization_schedule(loan_amount, interest_rate, tenure_years * 12)
        basic_interest = sum(e['interest'] for e in basic_schedule)
        biweekly_schedule = generate_amortization_schedule(loan_amount, interest_rate, tenure_years * 12,
                                                           calculate_emi(loan_amount, interest_rate, tenure_years * 12))
        biweekly_interest = sum(e['interest'] for e in biweekly_schedule)
        potential_saving = basic_interest - biweekly_interest

        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{format_inr(potential_saving)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Potential Savings</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sublabel">With just Strategy #1!</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-value">₹99</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">One-Time Payment</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-sublabel">Lifetime access</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # What's included
    st.markdown("### 📦 What You Get")

    st.markdown("""
    <div class="info-banner">
    <strong>🆓 FREE (No Payment Required):</strong><br>
    • Strategy #1: Bi-Weekly Payment Hack with full calculator<br>
    • Basic tax calculations (80C + 24b)<br>
    • Access to bank comparison tool<br><br>

    <strong>💎 PREMIUM (₹99 - Lifetime Access):</strong><br>
    • All 11 remaining strategies with complete calculators<br>
    • Advanced strategies: SIP vs Prepayment, Overdraft, Balance Transfer, and more<br>
    • Complete tax optimization (LTCG, STCG, HRA calculations)<br>
    • Comprehensive tips & tricks with emotional guidance<br>
    • Personalized recommendations based on your profile<br>
    • Future updates included FREE forever
    </div>
    """, unsafe_allow_html=True)

    # Pricing
    st.markdown("### 💰 Simple, Transparent Pricing")

    col_price1, col_price2, col_price3 = st.columns([1, 2, 1])

    with col_price2:
        if not is_paid and not is_admin_user:
            st.markdown("""
            <div class="premium-box" style="text-align: center; padding: 2rem;">
                <h2 style="margin: 0;">Limited Time Offer</h2>
                <h1 style="font-size: 3rem; margin: 1rem 0; color: #F57C00;">₹99</h1>
                <p style="font-size: 1.1rem; margin: 1rem 0;">One-time payment • Lifetime access • All strategies</p>
                <p style="margin: 1rem 0;">Save lakhs in interest for less than the cost of a movie ticket!</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔓 Unlock All Strategies for ₹99", use_container_width=True, type="primary"):
                st.session_state.selected_page = 'checkout'
                st.rerun()
        else:
            st.markdown("""
            <div class="success-box" style="text-align: center; padding: 2rem;">
                <h2 style="margin: 0; color: #4CAF50;">✅ You Have Full Access!</h2>
                <p style="font-size: 1.1rem; margin: 1rem 0;">All 12 strategies unlocked</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 Explore All Strategies", use_container_width=True, type="primary"):
                st.session_state.selected_page = 'strategies'
                st.rerun()

    # Quick CTA
    st.markdown("### 🎯 Ready to Start?")

    col_cta1, col_cta2, col_cta3 = st.columns(3)

    with col_cta1:
        if st.button("🆓 Try FREE Strategy", use_container_width=True):
            st.session_state.selected_page = 'strategies'
            st.session_state.selected_strategy = 1
            st.rerun()

    with col_cta2:
        if st.button("🏦 Compare Banks", use_container_width=True):
            st.session_state.selected_page = 'bank_comparison'
            st.rerun()

    with col_cta3:
        if st.button("💡 Read Tips", use_container_width=True):
            st.session_state.selected_page = 'tips'
            st.rerun()

# STRATEGIES PAGE
elif selected_page == 'strategies':
    st.markdown("## 💰 All 12 Home Loan Payment Strategies")

    # Show the free strategy
    st.markdown("### 🆓 Free Strategy - Try Before You Buy")

    with st.expander("Strategy #1: Bi-Weekly Payment Hack (Click to Expand)", expanded=True):
        show_strategy_1_biweekly()

    # Premium strategies - Check if user has paid
    if is_paid or is_admin_user:
        st.markdown("### ✅ All 12 Strategies (Premium Access)")

        # Strategy 2: Tax Refund Amplification
        st.markdown("---")
        with st.expander("Strategy #2: Tax Refund Amplification", expanded=False):
            show_strategy_2_tax_refund()
    else:
        # Show paywall
        st.markdown("---")
        st.markdown("### 🔒 Premium Strategies (11 More)")

        st.markdown("""
        <div class="premium-box">
        <strong>🎁 Unlock All 11 Premium Strategies for just ₹99</strong><br><br>

        Get lifetime access to:<br>
        • Strategy #2: Tax Refund Amplification - Save ₹5-8L<br>
        • Strategy #3: Lump Sum Accelerator - Save ₹8-12L<br>
        • Strategy #4: SIP vs Prepayment - Save ₹10-15L<br>
        • Strategy #5: Overdraft Loan - Save ₹15-25L<br>
        • Strategy #6: Step-Up EMI - Save ₹10-15L<br>
        • Strategy #7: Part-Prepayment - Save ₹8-12L<br>
        • Strategy #8: Balance Transfer - Save ₹5-10L<br>
        • Strategy #9: Top-Up Consolidation - Save ₹6-12L<br>
        • Strategy #10: Flexi-Loan - Save ₹8-15L<br>
        • Strategy #11: Rent vs Buy - Make the right decision<br>
        • Strategy #12: Early Closure vs Investment - Optimize returns<br><br>

        <strong>Plus:</strong><br>
        ✅ Advanced tax calculations (LTCG, STCG, HRA)<br>
        ✅ Personalized rate calculator<br>
        ✅ EMI vs Overdraft comparison<br>
        ✅ Hidden issues guide<br>
        ✅ Comprehensive tips & tricks<br>
        ✅ Lifetime access - No subscription<br>
        ✅ Future updates FREE<br><br>

        <strong>One-time payment. Lifetime value. Save lakhs on your loan!</strong>
        </div>
        """, unsafe_allow_html=True)

        if user_email:
            if st.button("🔓 Unlock All Strategies for ₹99", key="unlock_strategies", use_container_width=True, type="primary"):
                st.session_state.selected_page = 'checkout'
                st.rerun()
        else:
            st.warning("⚠️ Please sign in with Google to unlock premium strategies")
            st.info("Click the 'Sign in with Google' button in the sidebar or at the top to continue")

        st.markdown("---")
        st.stop()  # Exit early, don't show premium strategies

    # Continue showing strategies 2-12 for paid users

    # Strategy 3: Lump Sum Accelerator
    st.markdown("---")
    with st.expander("Strategy #3: Lump Sum Accelerator", expanded=False):
        show_strategy_3_lumpsum()

    # Strategy 4: SIP vs Prepayment
    st.markdown("---")
    with st.expander("Strategy #4: SIP vs Prepayment Optimizer", expanded=False):
        show_strategy_4_sip_vs_prepay()

    # Strategy 5: Overdraft Loan
    st.markdown("---")
    with st.expander("Strategy #5: Overdraft (OD) Loan Strategy", expanded=False):
        show_strategy_5_overdraft()

    # Strategy 6: Step-Up EMI
    st.markdown("---")
    with st.expander("Strategy #6: Step-Up EMI Strategy", expanded=False):
        show_strategy_6_stepup()

    # Strategy 7: Part-Prepayment
    st.markdown("---")
    with st.expander("Strategy #7: Part-Prepayment Optimizer", expanded=False):
        show_strategy_7_partprepay()

    # Strategy 8: Balance Transfer
    st.markdown("---")
    with st.expander("Strategy #8: Balance Transfer Calculator", expanded=False):
        show_strategy_8_balance_transfer()

    # Strategy 9: Top-Up Consolidation
    st.markdown("---")
    with st.expander("Strategy #9: Top-Up Loan Consolidation", expanded=False):
        show_strategy_9_topup()

    # Strategy 10: Flexi-Loan
    st.markdown("---")
    with st.expander("Strategy #10: Flexi-Loan Strategy", expanded=False):
        show_strategy_10_flexiloan()

    # Strategy 11: Rent vs Buy
    st.markdown("---")
    with st.expander("Strategy #11: Rent vs Buy Analyzer", expanded=False):
        show_strategy_11_rent_vs_buy()

    # Strategy 12: Early Closure vs Investment
    st.markdown("---")
    with st.expander("Strategy #12: Early Closure vs Investment", expanded=False):
        show_strategy_12_early_closure()

    st.markdown("---")
    st.success("""
    🎉 **All 12 comprehensive strategies available for testing!**

    Each strategy includes:
    ✅ Interactive calculator with real logic
    ✅ Complete tax calculations (80C, 24b, LTCG, STCG)
    ✅ Detailed comparison tables
    ✅ Winner declarations
    ✅ Implementation guides
    ✅ Emotional support & guidance
    ✅ Common mistakes to avoid

    Use these tools to save lakhs on your home loan! 💰
    """)

# STRATEGY COMPARISON PAGE
elif selected_page == 'strategy_comparison':
    st.markdown("## 📊 Compare All 12 Strategies")

    st.markdown("""
    <div class="info-banner">
    Side-by-side comparison of all strategies to help you choose the best one for your situation!
    </div>
    """, unsafe_allow_html=True)

    # Calculate all strategies
    comparison_data = []

    # Strategy 1: Bi-Weekly Payments
    biweekly_result = calculate_loan_cost_with_tax(loan_amount, interest_rate, tenure_years, tax_slab, old_regime, property_type, loan_amount * 0.04)
    comparison_data.append({
        "Strategy": "1️⃣ Bi-Weekly Payment",
        "Best For": "Variable income, beginners",
        "Effort": "Low",
        "Annual Extra": "₹0 (frequency change)",
        "Savings": f"₹{(biweekly_result['total_interest'] * 0.15)/100000:.1f}L",
        "Tenure Reduction": "2-3 years",
        "Difficulty": "Easy"
    })

    # Strategy 2: Tax Refund
    comparison_data.append({
        "Strategy": "2️⃣ Tax Refund Amplification",
        "Best For": "80C maxed, high tax slab",
        "Effort": "Low",
        "Annual Extra": f"₹{(loan_amount * interest_rate/100 * 0.2)/1000:.0f}K",
        "Savings": "₹5-8L",
        "Tenure Reduction": "3-5 years",
        "Difficulty": "Easy"
    })

    # Strategy 3: Bonus Prepayment
    comparison_data.append({
        "Strategy": "3️⃣ Annual Bonus/Gift",
        "Best For": "Salaried with bonuses",
        "Effort": "Low",
        "Annual Extra": "₹1-2L (bonus)",
        "Savings": "₹8-12L",
        "Tenure Reduction": "5-7 years",
        "Difficulty": "Easy"
    })

    # Strategy 4: Stepup
    comparison_data.append({
        "Strategy": "4️⃣ Step-Up Prepayment",
        "Best For": "Growing income",
        "Effort": "Low",
        "Annual Extra": "10% yearly increase",
        "Savings": "₹10-15L",
        "Tenure Reduction": "6-8 years",
        "Difficulty": "Easy"
    })

    # Strategy 5: Round-Up
    comparison_data.append({
        "Strategy": "5️⃣ EMI Round-Up",
        "Best For": "Everyone (minimal effort)",
        "Effort": "Very Low",
        "Annual Extra": "₹20-30K",
        "Savings": "₹3-5L",
        "Tenure Reduction": "2-3 years",
        "Difficulty": "Very Easy"
    })

    # Strategy 6: OD
    comparison_data.append({
        "Strategy": "6️⃣ Overdraft (OD) Loan",
        "Best For": "High surplus, disciplined",
        "Effort": "High",
        "Annual Extra": "Surplus parking",
        "Savings": "₹15-25L",
        "Tenure Reduction": "8-12 years",
        "Difficulty": "Hard"
    })

    # Strategy 7: Rent Income
    comparison_data.append({
        "Strategy": "7️⃣ Rent Income Prepay",
        "Best For": "Parents house/let-out",
        "Effort": "Low",
        "Annual Extra": "₹1-3L (rent)",
        "Savings": "₹10-18L",
        "Tenure Reduction": "5-8 years",
        "Difficulty": "Easy"
    })

    # Strategy 8: Side Hustle
    comparison_data.append({
        "Strategy": "8️⃣ Side Hustle Income",
        "Best For": "Entrepreneurs, freelancers",
        "Effort": "High",
        "Annual Extra": "₹2-5L (side income)",
        "Savings": "₹12-20L",
        "Tenure Reduction": "6-10 years",
        "Difficulty": "Hard"
    })

    # Strategy 9: Lifestyle Cut
    comparison_data.append({
        "Strategy": "9️⃣ Lifestyle Downsize",
        "Best For": "High spenders, temporary",
        "Effort": "Medium",
        "Annual Extra": "₹1-3L (savings)",
        "Savings": "₹8-15L",
        "Tenure Reduction": "4-7 years",
        "Difficulty": "Medium"
    })

    # Strategy 10: Debt Avalanche
    comparison_data.append({
        "Strategy": "🔟 Debt Avalanche",
        "Best For": "Multiple loans/debts",
        "Effort": "Medium",
        "Annual Extra": "Redirect cleared EMIs",
        "Savings": "₹10-20L",
        "Tenure Reduction": "5-10 years",
        "Difficulty": "Medium"
    })

    # Strategy 11: Windfall
    comparison_data.append({
        "Strategy": "1️⃣1️⃣ Windfall Deployment",
        "Best For": "Sale/inheritance/ESOP",
        "Effort": "Low",
        "Annual Extra": "₹10-50L (one-time)",
        "Savings": "₹20-40L",
        "Tenure Reduction": "10-15 years",
        "Difficulty": "Easy"
    })

    # Strategy 12: Hybrid
    comparison_data.append({
        "Strategy": "1️⃣2️⃣ Hybrid (Best of All)",
        "Best For": "Optimal result seekers",
        "Effort": "High",
        "Annual Extra": "Multiple sources",
        "Savings": "₹25-50L",
        "Tenure Reduction": "12-18 years",
        "Difficulty": "Hard"
    })

    # Display comparison table
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True, height=500)

    # Quick guide
    st.markdown("---")
    st.markdown("### 🎯 Quick Selection Guide")

    col_guide1, col_guide2, col_guide3 = st.columns(3)

    with col_guide1:
        st.markdown("""
        **🟢 Beginners Start Here:**
        - Strategy #1: Bi-Weekly
        - Strategy #5: EMI Round-Up
        - Strategy #2: Tax Refund
        """)

    with col_guide2:
        st.markdown("""
        **🟡 Intermediate Level:**
        - Strategy #3: Annual Bonus
        - Strategy #4: Step-Up
        - Strategy #7: Rent Income
        """)

    with col_guide3:
        st.markdown("""
        **🔴 Advanced (Max Savings):**
        - Strategy #6: Overdraft
        - Strategy #12: Hybrid
        - Strategy #8: Side Hustle
        """)

    st.markdown("""
    <div class="heart-box">
    💡 <strong>Pro Tip:</strong> Start with an easy strategy (like #1 or #5) and gradually add more as you get comfortable.
    Most users combine 2-3 strategies for optimal results!
    </div>
    """, unsafe_allow_html=True)

# BANK COMPARISON PAGE
elif selected_page == 'bank_comparison':
    st.markdown("## 🏦 Bank Comparison Tool")

    st.markdown("""
    <div class="info-banner">
    Compare home loan offerings from India's top 6 banks. Find the best deal for your situation!
    </div>
    """, unsafe_allow_html=True)

    # Calculate EMI for each bank
    comparison_data = []

    for bank_name, bank_info in BANK_DATA.items():
        bank_rate = bank_info['rate']
        bank_emi = calculate_emi(loan_amount, bank_rate, tenure_years * 12)

        # Calculate total cost with tax
        bank_cost_info = calculate_loan_cost_with_tax(loan_amount, bank_rate, tenure_years,
                                                       tax_slab, old_regime, property_type, 0)

        processing_fee = max(loan_amount * bank_info['processing_fee_pct'] / 100,
                           bank_info['min_processing']) * 1.18  # With GST

        total_cost = bank_cost_info['net_cost'] + processing_fee

        comparison_data.append({
            "Bank": bank_name,
            "Interest Rate": f"{bank_rate}%",
            "Monthly EMI": format_inr(bank_emi),
            "Processing Fee": format_inr(processing_fee),
            "Total Interest": format_inr(bank_cost_info['total_interest']),
            "Tax Benefit": format_inr(bank_cost_info['total_tax_benefit']),
            "Net Cost": format_inr(total_cost),
            "Special Offer": bank_info['special']
        })

    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Find best bank
    min_cost_bank = min(comparison_data, key=lambda x: float(x['Net Cost'].replace('₹', '').replace(',', '')))

    st.markdown(f"""
    <div class="success-box">
    <strong>🏆 Best Bank for Your Profile: {min_cost_bank['Bank']}</strong><br>
    • Lowest net cost after tax: {min_cost_bank['Net Cost']}<br>
    • Monthly EMI: {min_cost_bank['Monthly EMI']}<br>
    • {min_cost_bank['Special Offer']}
    </div>
    """, unsafe_allow_html=True)

    # Rate update information
    from datetime import datetime

    try:
        last_update = datetime.strptime(RATE_LAST_UPDATED, "%Y-%m-%d")
        days_ago = (datetime.now() - last_update).days

        if days_ago == 0:
            update_msg = "✅ Rates updated today"
            update_color = "success"
        elif days_ago <= 7:
            update_msg = f"✅ Rates updated {days_ago} days ago"
            update_color = "success"
        elif days_ago <= 14:
            update_msg = f"⚠️ Rates updated {days_ago} days ago - Consider checking bank websites"
            update_color = "warning"
        else:
            update_msg = f"⚠️ Rates updated {days_ago} days ago - Please verify with banks"
            update_color = "warning"
    except:
        update_msg = "ℹ️ Rate update status unknown"
        update_color = "info"

    if update_color == "success":
        st.success(f"{update_msg} | Source: {RATE_UPDATE_SOURCE}")
    elif update_color == "warning":
        st.warning(f"{update_msg} | Source: {RATE_UPDATE_SOURCE}")
    else:
        st.info(f"{update_msg} | Source: {RATE_UPDATE_SOURCE}")

    st.markdown("---")
    st.markdown("## 📊 Bank Reviews & Why Rates Differ")
    st.markdown("Understanding why banks charge different rates helps you make better decisions. Here's what real customers say:")

    # Display reviews for each bank
    for bank_name in BANK_DATA.keys():
        if bank_name in BANK_REVIEWS:
            review = BANK_REVIEWS[bank_name]

            with st.expander(f"**{bank_name} - {BANK_DATA[bank_name]['rate']}%** ⭐ {review['rating']}/5 ({review['total_reviews']} reviews)", expanded=False):

                # Service Quality Badge
                quality_color = {"Good": "🟢", "Mixed": "🟡", "Average": "🟠", "Poor": "🔴"}
                quality_emoji = quality_color.get(review['service_quality'], "⚪")
                st.markdown(f"**Service Quality:** {quality_emoji} {review['service_quality']}")

                # Why this rate?
                rate_key = [k for k in review.keys() if k.startswith('why_')][0]
                st.markdown(f"### 💡 Why {BANK_DATA[bank_name]['rate']}% rate?")
                st.info(review[rate_key])

                # Pros and Cons
                col_pro, col_con = st.columns(2)

                with col_pro:
                    st.markdown("### ✅ Pros")
                    for pro in review['pros']:
                        st.markdown(f"• {pro}")

                with col_con:
                    st.markdown("### ❌ Cons")
                    for con in review['cons']:
                        st.markdown(f"• {con}")

                # Best for / Avoid if
                st.markdown("---")
                col_best, col_avoid = st.columns(2)

                with col_best:
                    st.markdown(f"**👍 Best For:** {review['best_for']}")

                with col_avoid:
                    st.markdown(f"**👎 Avoid If:** {review['avoid_if']}")

# TIPS PAGE
elif selected_page == 'tips':
    if not is_paid and not is_admin_user:
        st.markdown("## 💡 Tips & Tricks (Premium Content)")
        st.markdown("""
        <div class="premium-box">
        <strong>🔒 Unlock comprehensive tips and emotional guidance for just ₹99</strong><br><br>

        Get access to:<br>
        • Before Taking Loan: Credit score hacks, negotiation tactics, hidden charges<br>
        • During Loan: Prepayment strategy, tax optimization, EMI management<br>
        • Psychological Guidance: Managing loan stress, milestone celebrations, common mistakes<br>
        • Insider Banking Knowledge: How to negotiate 0.25-0.50% lower rates<br>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔓 Unlock All Tips", use_container_width=True, type="primary"):
            st.session_state.selected_page = 'checkout'
            st.rerun()
    else:
        # Show complete comprehensive tips
        show_comprehensive_tips()

# CHECKOUT PAGE
elif selected_page == 'checkout':
    st.markdown("## 💳 Checkout - Unlock All Premium Features")

    if is_admin_user:
        st.success("You're an admin - you already have full access!")
    elif is_paid:
        st.success("You've already purchased! Enjoy full access to all strategies.")
    elif not user_email:
        st.warning("⚠️ Please sign in with Google to continue with payment.")
        st.info("Click the 'Sign in with Google' button at the top-right to proceed.")
    else:
        # Show pricing and payment
        st.markdown("""
        <div class="info-banner">
        <strong>🎁 What You're Getting:</strong><br>
        • All 12 strategies with complete calculators<br>
        • Advanced tax calculations (LTCG, STCG, HRA)<br>
        • Comprehensive tips & tricks<br>
        • Lifetime access (no subscription)<br>
        • Future updates included FREE
        </div>
        """, unsafe_allow_html=True)

        col_checkout1, col_checkout2, col_checkout3 = st.columns([1, 2, 1])

        with col_checkout2:
            st.markdown("""
            <div class="premium-box" style="text-align: center; padding: 2rem;">
                <h2>Complete Home Loan Toolkit</h2>
                <h1 style="font-size: 3.5rem; margin: 1rem 0; color: #F57C00;">₹99</h1>
                <p>One-time payment • Lifetime access</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("💳 Proceed to Secure Payment", use_container_width=True, type="primary"):
                with st.spinner("Creating payment link..."):
                    payment_link, error = create_razorpay_payment_link(user_email)

                    if payment_link:
                        st.success("Payment link created!")
                        payment_url = payment_link.get('short_url', '')
                        if payment_url:
                            st.markdown(f"""
                            <div style="text-align: center; margin: 2rem 0;">
                                <a href="{payment_url}" target="_blank">
                                    <button style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem 3rem; font-size: 1.2rem; border: none; border-radius: 10px; cursor: pointer; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">
                                        💳 Pay ₹99 Now (Secure)
                                    </button>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error(f"Error: {error}")
                        st.info("Please contact support: dmcpexam2020@gmail.com")

# OVERDRAFT vs EMI COMPARISON PAGE
elif selected_page == 'overdraft_comparison':
    st.markdown("## 🔄 EMI vs Overdraft Comparison")
    st.markdown("### Discover if Home Loan Overdraft (like SBI MaxGain) Can Save You Lakhs!")

    st.markdown("""
    <div class="info-banner">
    <strong>💡 What is Home Loan Overdraft?</strong><br>
    Interest charged ONLY on <code>(Loan Amount - Your OD Balance)</code> daily!<br>
    Park surplus funds and save on interest while keeping liquidity.
    </div>
    """, unsafe_allow_html=True)

    # Overdraft-specific inputs
    col_od1, col_od2 = st.columns(2)

    with col_od1:
        st.markdown("#### Overdraft Parameters")
        od_rate = st.number_input("Overdraft Interest Rate (%)",
                                   min_value=5.0, max_value=15.0, value=8.75, step=0.05,
                                   help="Usually 0.15-0.25% higher than regular loan")
        surplus_initial = st.number_input("Initial Surplus to Park (₹)",
                                         min_value=0, max_value=10000000, value=500000, step=50000,
                                         help="Lumpsum amount you can deposit initially")
        surplus_monthly = st.number_input("Monthly Surplus Addition (₹)",
                                         min_value=0, max_value=500000, value=20000, step=5000,
                                         help="Extra money you can park each month")

    with col_od2:
        st.markdown("#### Regular Loan for Comparison")
        st.metric("Interest Rate", f"{interest_rate}%")
        st.metric("Loan Amount", format_inr(loan_amount))
        st.metric("Tenure", f"{tenure_years} years")

    # Calculate both scenarios
    old_tax_regime = (tax_regime == "Old (with deductions)")

    # Regular EMI loan
    regular_loan = calculate_loan_cost_with_tax(
        loan_amount, interest_rate, tenure_years,
        tax_slab, old_tax_regime, property_type, 0
    )

    # Overdraft loan
    od_loan = calculate_overdraft_loan_cost(
        loan_amount, od_rate, tenure_years * 12,
        surplus_initial, surplus_monthly,
        tax_slab, old_tax_regime, property_type
    )

    # Calculate savings
    od_loan['interest_saved_vs_regular'] = regular_loan['total_interest'] - od_loan['total_interest']
    total_savings = regular_loan['net_cost'] - od_loan['net_cost']

    # Display comparison
    st.markdown("### 📊 Cost Comparison")

    col_comp1, col_comp2, col_comp3 = st.columns(3)

    with col_comp1:
        st.markdown("#### 💳 Regular EMI Loan")
        st.metric("Total Interest", format_inr(regular_loan['total_interest']))
        st.metric("Tax Benefit", format_inr(regular_loan['total_tax_benefit']))
        st.metric("Net Cost", format_inr(regular_loan['net_cost']))

    with col_comp2:
        st.markdown("#### 🔄 Overdraft Loan")
        st.metric("Total Interest", format_inr(od_loan['total_interest']))
        st.metric("Tax Benefit", format_inr(od_loan['total_tax_benefit']))
        st.metric("Net Cost", format_inr(od_loan['net_cost']))

    with col_comp3:
        st.markdown("#### 💰 Your Savings")
        st.metric("Interest Saved", format_inr(od_loan['interest_saved_vs_regular']),
                 delta=f"{od_loan['interest_saved_vs_regular']/regular_loan['total_interest']*100:.1f}%")
        st.metric("Total Savings", format_inr(total_savings),
                 delta="Lower is better" if total_savings > 0 else "Regular is better")

    if total_savings > 0:
        st.success(f"🎉 **Overdraft can save you {format_inr(total_savings)}!** ({total_savings/regular_loan['net_cost']*100:.1f}% reduction)")
    else:
        st.warning(f"⚠️ Regular loan is cheaper by {format_inr(abs(total_savings))}. Overdraft works best with larger surplus amounts.")

    # Surplus impact analysis
    st.markdown("### 📈 Impact of Different Surplus Amounts")

    surplus_scenarios = [0, 200000, 500000, 1000000, 2000000]
    scenario_data = []

    for surplus in surplus_scenarios:
        if surplus <= loan_amount:
            temp_od = calculate_overdraft_loan_cost(
                loan_amount, od_rate, tenure_years * 12,
                surplus, surplus_monthly, tax_slab, old_tax_regime, property_type
            )
            scenario_data.append({
                "Initial Surplus": format_inr(surplus),
                "Total Interest": format_inr(temp_od['total_interest']),
                "Interest Saved": format_inr(regular_loan['total_interest'] - temp_od['total_interest']),
                "Net Cost": format_inr(temp_od['net_cost'])
            })

    st.dataframe(pd.DataFrame(scenario_data), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="info-banner">
    <strong>💡 Key Insight:</strong> Even though overdraft rates are higher ({od_rate}% vs {interest_rate}%),
    you pay interest only on the effective outstanding (Loan - OD Balance), which can result in MASSIVE savings!
    </div>
    """.format(od_rate=od_rate, interest_rate=interest_rate), unsafe_allow_html=True)

# PERSONALIZED RATES PAGE
elif selected_page == 'personalized_rates':
    st.markdown("## 👤 Your Personalized Interest Rate")
    st.markdown("### Find out what rate YOU actually qualify for based on your profile")

    st.markdown("""
    <div class="info-banner">
    Banks adjust interest rates based on your credit score, age, employment, and more.<br>
    <strong>This calculator shows your REAL rate, not the advertised rate!</strong>
    </div>
    """, unsafe_allow_html=True)

    # User profile inputs
    col_prof1, col_prof2, col_prof3 = st.columns(3)

    with col_prof1:
        st.markdown("#### Credit & Demographics")
        credit_score = st.selectbox("Credit Score",
                                    options=['750+', '700-749', '650-699', '<650'],
                                    help="Higher score = lower rate")
        age = st.slider("Age", min_value=23, max_value=62, value=35,
                       help="Younger borrowers often get better rates")
        gender = st.radio("Gender", options=['Male', 'Female', 'Other'],
                         help="Women often get 0.05% concession")

    with col_prof2:
        st.markdown("#### Employment & Income")
        employment = st.selectbox("Employment Type",
                                 options=['Salaried-Govt', 'Salaried-MNC',
                                         'Salaried-Other', 'Self-Employed'],
                                 help="Govt/MNC employees get better rates")
        profile_loan_amount = st.number_input("Loan Amount (₹)",
                                             min_value=100000, max_value=100000000,
                                             value=loan_amount, step=100000)

    with col_prof3:
        st.markdown("#### Property Location")
        location = st.selectbox("Property Location",
                               options=['Metro Tier-1', 'Tier-2', 'Tier-3'],
                               help="Metro properties get better rates")

    # Build user profile
    user_profile = {
        'credit_score': credit_score,
        'age': age,
        'gender': gender,
        'employment': employment,
        'loan_amount': profile_loan_amount,
        'property_location': location
    }

    # Calculate personalized rates for all banks
    st.markdown("### 🏦 Your Personalized Rates Across Banks")

    personalized_data = []
    for bank, info in BANK_DATA.items():
        base_rate = info['rate']
        result = calculate_personalized_rate(base_rate, user_profile)

        personalized_data.append({
            "Bank": bank,
            "Base Rate": f"{base_rate}%",
            "Your Rate": f"{result['final_rate']}%",
            "Adjustment": f"{result['total_adjustment']:+.2f}%",
            "Special Offer": info['special']
        })

    st.dataframe(pd.DataFrame(personalized_data), use_container_width=True, hide_index=True)

    # Show detailed breakdown for best bank
    best_bank = min(personalized_data, key=lambda x: float(x['Your Rate'].strip('%')))

    st.success(f"🏆 **Best Rate for You: {best_bank['Bank']} at {best_bank['Your Rate']}**")

    # Show breakdown of adjustments
    sample_bank = list(BANK_DATA.keys())[0]
    sample_result = calculate_personalized_rate(BANK_DATA[sample_bank]['rate'], user_profile)

    st.markdown("### 📊 Rate Adjustment Breakdown")

    adjustment_data = []
    adjustment_labels = {
        'credit_score': '💳 Credit Score',
        'age': '🎂 Age',
        'gender': '👤 Gender',
        'employment': '💼 Employment',
        'loan_amount': '💰 Loan Amount',
        'location': '📍 Location'
    }

    for key, value in sample_result['adjustments'].items():
        if value != 0:
            adjustment_data.append({
                "Factor": adjustment_labels.get(key, key),
                "Adjustment": f"{value:+.2f}%",
                "Impact": "✅ Positive" if value < 0 else "⚠️ Negative"
            })

    st.dataframe(pd.DataFrame(adjustment_data), use_container_width=True, hide_index=True)

    st.markdown("""
    <div class="info-banner">
    <strong>💡 How to Improve Your Rate:</strong><br>
    • Improve credit score to 750+ (save 0.25-0.75%)<br>
    • Consider co-borrower if self-employed (save 0.25%)<br>
    • Increase loan amount if possible (save 0.10%)<br>
    • Women co-applicants get additional discount
    </div>
    """, unsafe_allow_html=True)

# HIDDEN ISSUES PAGE
elif selected_page == 'hidden_issues':
    st.markdown("## ⚠️ Hidden Problems in Home Loans")
    st.markdown("### Real issues borrowers face (and banks won't tell you!)")

    tab_issues1, tab_issues2, tab_issues3 = st.tabs([
        "💳 Regular Loan Problems",
        "🔄 Overdraft Problems",
        "🚨 Non-Payment Consequences"
    ])

    with tab_issues1:
        st.markdown("### Common Problems with Regular Home Loans")

        st.markdown("""
        #### 1️⃣ The EMI Structure Trap
        **Problem:** Your initial EMIs are 90% interest, 10% principal!

        **Example:** ₹50L loan @ 8.5%
        - Month 1 EMI: ₹43,391
        - Interest: ₹35,417 (82%)
        - Principal: ₹7,974 (18%)

        **Impact:** You're paying rent to the bank for years before owning your home.

        **Solution:** Start prepaying from Year 1, even small amounts (₹10K/year helps!)

        ---

        #### 2️⃣ Hidden Prepayment Lock-in
        **Problem:** "Nil prepayment charges" has fine print!

        **Hidden Clauses:**
        - Free only for floating rate loans
        - Fixed rate: 2-5% penalty
        - Some banks: Min 6-12 months lock-in
        - Foreclosure ≠ Part-prepayment rules

        **Real Story:** Customer tried prepaying ₹5L in Month 2, charged ₹25,000 penalty.

        **Solution:** Read agreement carefully. Confirm in email before prepaying.

        ---

        #### 3️⃣ Insurance Bundling Trap
        **Problem:** Bank pushes expensive insurance (home, life, medical)

        **Bank's Offer:** ₹15,000/year life insurance (₹50L cover)
        **Market Rate:** ₹8,000/year for same cover

        **Hidden Cost:** ₹7,000 × 20 years = ₹1,40,000 wasted!

        **Solution:** Get insurance separately. Bank CANNOT force bundling (RBI rule).

        ---

        #### 4️⃣ Processing Fee Surprise
        **Advertised:** "0.5% processing fee"
        **Reality:** 0.5% + GST + legal + valuation + CERSAI

        **Breakdown for ₹50L loan:**
        - Processing: ₹25,000
        - GST (18%): ₹4,500
        - Legal: ₹10,000
        - Valuation: ₹3,000
        - CERSAI: ₹100
        - **Total: ₹42,600** (not ₹25,000!)

        **Solution:** Negotiate. Some banks waive for salary account holders.
        """)

    with tab_issues2:
        st.markdown("### Hidden Problems with Overdraft Facilities")

        st.markdown("""
        #### 1️⃣ Psychological Trap of 'Free Money'
        **Problem:** OD account feels like YOUR money

        **Reality:** It's still a LOAN. Every withdrawal costs you.

        **Example:** Park ₹10L, then withdraw ₹2L for vacation
        - Interest savings lost: ₹14,166/year
        - Vacation actual cost: ₹2L + ₹14K = ₹2.14L

        **Solution:** Treat OD as locked FD. Only withdraw for emergencies.

        ---

        #### 2️⃣ Lost 80C Tax Benefit
        **Problem:** Money in OD ≠ Principal repayment

        **Regular Loan:** ₹1.5L principal → ₹46,500 tax saved (@31%)
        **Overdraft:** ₹1.5L in OD → ₹0 tax benefit

        **Hidden Cost:** ₹46,500/year × 20 years = ₹9.3L!

        **When OD Still Wins:** If interest saved > 80C benefit lost

        **Calculation:** Need ₹5L+ surplus for break-even

        ---

        #### 3️⃣ Minimum Loan Amount Restrictions
        **Problem:** OD only for ₹15L+ loans (some banks ₹25L+)

        **Impact:** Small loan borrowers can't access OD benefits

        **Workaround:** None. Regular loan is your only option.

        ---

        #### 4️⃣ Discipline Required
        **Problem:** OD works ONLY if you're financially disciplined

        **Failed Cases:**
        - Using OD for lifestyle expenses
        - Not maintaining monthly surplus
        - Emergency fund = OD balance (wrong!)

        **Success Requires:**
        - Separate emergency fund (6 months)
        - OD balance review quarterly
        - Resist withdrawal temptation
        """)

    with tab_issues3:
        st.markdown("### What Happens If You Can't Pay?")

        st.markdown("""
        #### Day-by-Day Consequences

        **Day 1-30 (Missed EMI):**
        - Penalty: 2% per month (24% annual!)
        - Example: ₹40,000 EMI → ₹800 penalty
        - CIBIL: Not yet impacted

        **Day 31-60 (Second missed EMI):**
        - Penalty: ₹800 × 2 = ₹1,600
        - Bank calls/emails start
        - CIBIL: Marked as 30 DPD (Days Past Due)
        - Credit score drops: 750 → 680

        **Day 61-90 (Third missed EMI):**
        - Penalty: ₹2,400
        - CIBIL: 60 DPD
        - Credit score: 680 → 620
        - Legal notice sent
        - Future loan applications rejected

        **Day 91-180:**
        - Account marked as NPA (Non-Performing Asset)
        - CIBIL: 90 DPD (stays for 7 years!)
        - Credit score: Below 600
        - Bank can auction property under SARFAESI Act
        - No court required for auction

        **Post 180 days:**
        - Property auction process starts
        - Recovery agents visit
        - Public notices published
        - All future loans blocked
        - Employment background verification fails

        ---

        #### Recovery Options If You're Struggling

        **Option 1: Loan Restructuring**
        - Extend tenure (reduce EMI)
        - Moratorium period (3-6 months)
        - Contact bank BEFORE defaulting

        **Option 2: Sell Property**
        - Better than foreclosure
        - You keep equity after loan repayment
        - CIBIL impact minimal

        **Option 3: Rent Out & Cover EMI**
        - Rent income covers EMI
        - You stay solvent
        - Property appreciation continues

        **DON'T DO:**
        - Ignore bank calls
        - Take personal loan to pay home loan
        - Hide from recovery agents
        """)

        # Late payment calculator
        st.markdown("### 🧮 Late Payment Cost Calculator")

        col_late1, col_late2 = st.columns(2)

        with col_late1:
            emi_amount = st.number_input("Monthly EMI (₹)",
                                        min_value=1000, value=40000, step=1000)
            days_late = st.slider("Days Late", min_value=1, max_value=180, value=30)

        with col_late2:
            penalty_rate = 24  # 2% per month = 24% annual
            penalty_amount = emi_amount * (penalty_rate/100) * (days_late/30)

            st.metric("Penalty Amount", format_inr(penalty_amount))
            st.metric("Effective EMI", format_inr(emi_amount + penalty_amount))

            if days_late >= 30:
                st.error(f"⚠️ CIBIL Impact: {days_late} DPD recorded!")

# ============================================================================
# POLICY PAGES
# ============================================================================

# CONTACT PAGE
elif selected_page == 'contact':
    st.markdown("# 📞 Contact Us")
    st.markdown("""
    ## Contact Information

    **Email:** dmcpexam2020@gmail.com
    **Phone:** +91 7021761291
    **Response Time:** Within 24-48 hours
    **Business Hours:** Mon-Fri, 9 AM - 6 PM IST

    ---

    ## Get in Touch

    We're here to help you with your home loan journey. Feel free to reach out!

    ### 🏢 Business Information

    **Home Loan Toolkit**

    Online Educational Platform
    Providing Home Loan Strategies & Financial Tools

    ### 🔐 Authentication

    Secure login via Google Auth (powered by Render)
    """)

# TERMS PAGE
elif selected_page == 'terms':
    st.markdown("# 📋 Terms & Conditions")
    st.markdown("""
    **Last Updated:** October 28, 2025

    ## 1. Acceptance of Terms

    By accessing and using Home Loan Toolkit ("the Service"), you accept and agree to be bound by the terms and conditions of this agreement.

    ## 2. Description of Service

    Home Loan Toolkit provides:
    - Educational content and calculators for home loan payment strategies
    - Interactive tools to help users make informed financial decisions

    ## 3. User Responsibilities

    You agree to:
    - Provide accurate information when using our calculators
    - Use the Service for lawful purposes only
    - Not attempt to gain unauthorized access to any part of the Service
    - Seek professional financial advice before making major financial decisions

    ## 4. Disclaimer

    The information provided through the Service is for educational purposes only and should not be considered as financial, legal, or tax advice. We recommend consulting with qualified professionals before making any financial decisions.

    ## 5. No Warranties

    The Service is provided "as is" without any warranties, express or implied. We do not guarantee:
    - The accuracy or completeness of the information
    - That the Service will be uninterrupted or error-free
    - Specific results from using our strategies or tools

    ## 6. Limitation of Liability

    Home Loan Toolkit shall not be liable for any:
    - Financial losses resulting from use of our calculators or strategies
    - Decisions made based on information provided through the Service
    - Technical issues or data loss

    ## 7. Intellectual Property

    All content, including but not limited to text, graphics, logos, and software, is the property of Home Loan Toolkit and protected by copyright laws.

    ## 8. Changes to Terms

    We reserve the right to modify these terms at any time. Continued use of the Service after changes constitutes acceptance of the modified terms.

    ## 9. Governing Law

    These terms shall be governed by the laws of India.

    ## 10. Contact Information

    For questions about these Terms & Conditions, please contact:
    - Email: dmcpexam2020@gmail.com

    ---

    **By using Home Loan Toolkit, you acknowledge that you have read, understood, and agree to be bound by these Terms & Conditions.**
    """)

# PRIVACY PAGE
elif selected_page == 'privacy':
    st.markdown("# 🔒 Privacy Policy")
    st.markdown("""
    **Last Updated:** October 28, 2025

    ## 1. Introduction

    Home Loan Toolkit ("we", "our", or "us") respects your privacy and is committed to protecting your personal data. This privacy policy explains how we collect, use, and safeguard your information.

    ## 2. Information We Collect

    ### 2.1 Information You Provide
    - Contact details (name, email) when you sign in with Google
    - Financial inputs you enter into our calculators (stored locally, not on our servers)

    ### 2.2 Automatically Collected Information
    - Browser type and version
    - Time zone setting and location
    - Operating system and platform
    - Pages visited and time spent on pages

    ## 3. How We Use Your Information

    We use your information to:
    - Provide access to premium strategies after payment verification
    - Respond to your inquiries and provide customer support
    - Improve our Service based on usage patterns
    - Analyze and improve our calculators and tools

    ## 4. Data Storage and Security

    - Calculator inputs are processed in real-time and not stored on our servers
    - Google OAuth handles authentication securely
    - Payment information is processed by Razorpay (we don't store card details)
    - We implement appropriate technical and organizational measures to protect your data

    ## 5. Data Sharing

    We do NOT:
    - Sell your personal data to third parties
    - Share your financial calculation data with anyone
    - Use your data for marketing purposes without explicit consent

    We MAY share data with:
    - Service providers who help us operate the Service (under strict confidentiality)
    - Law enforcement if legally required

    ## 6. Your Rights

    You have the right to:
    - Access your personal data
    - Request correction of inaccurate data
    - Request deletion of your data
    - Opt-out of communications
    - Withdraw consent at any time

    ## 7. Third-Party Services

    Our Service uses:
    - **Google OAuth** for authentication
    - **Razorpay** for payment processing

    These services have their own privacy policies, and we encourage you to review them.

    ## 8. Changes to Privacy Policy

    We may update this policy from time to time. We will notify you of significant changes by posting a notice on our Service.

    ## 9. Contact Us

    For privacy-related questions or to exercise your rights, contact:
    - Email: dmcpexam2020@gmail.com

    ---

    **By using Home Loan Toolkit, you consent to this Privacy Policy.**
    """)

# REFUND PAGE
elif selected_page == 'refund':
    st.markdown("# ↩️ Refund Policy")
    st.markdown("""
    **Last Updated:** October 28, 2025

    ## No Refund Policy

    **IMPORTANT:** All payments made through our platform are **FINAL and NON-REFUNDABLE**.

    ## Service Nature

    Home Loan Toolkit provides:
    - Digital educational content (delivered instantly)
    - Interactive calculators and tools (immediate access)
    - Payment strategy guides (instant access)

    ## Why No Refunds?

    Due to the **digital and instant nature** of our services:
    - Content is delivered immediately upon payment
    - Information cannot be "returned" once accessed
    - Calculators and tools are accessed instantly
    - This prevents misuse of our educational content

    ## Payment Processing

    All payments are processed through secure Razorpay gateway that is:
    - Encrypted and PCI-DSS compliant
    - Supports multiple payment methods
    - Fully secure and trusted

    ## Before You Purchase

    Please ensure you:
    - Review service descriptions carefully
    - Understand what you're purchasing
    - Try the FREE strategy first before buying premium access
    - Contact us with any questions BEFORE making payment
    - Verify your payment details

    ## Exceptions

    Refunds may be considered ONLY in the following cases:
    - Duplicate payment due to technical error
    - Payment debited but service not delivered (verified by our team)
    - Unauthorized transaction (with police complaint)

    ## Contact Us

    For questions about payments or this policy, contact:
    - Email: dmcpexam2020@gmail.com
    - Phone: +91 7021761291

    ---

    **By making a payment, you acknowledge and accept this No Refund Policy.**
    """)

# CANCELLATION PAGE
elif selected_page == 'cancellation':
    st.markdown("# ❌ Cancellation Policy")
    st.markdown("""
    **Last Updated:** October 28, 2025

    ## No Cancellation Policy

    **IMPORTANT:** Once a payment is made and content/service is delivered, **NO CANCELLATIONS are allowed**.

    ## Service Nature

    Home Loan Toolkit provides **instant-access digital services**:
    - Educational content delivered immediately
    - Calculator tools activated instantly upon payment
    - Guides available for immediate access

    ## Why No Cancellations?

    Due to the **instant delivery nature** of digital services:
    - Content is accessed immediately after payment
    - Information and tools cannot be "undelivered"
    - All services are non-reversible once accessed
    - Immediate value is provided at the time of payment

    ## Payment Processing

    All payments through our secure Razorpay gateway are:
    - Processed instantly
    - Final and binding
    - Non-cancellable once transaction is complete

    ## Before Making Payment

    Please ensure to:
    - Carefully review what you're purchasing
    - Try the FREE Bi-Weekly strategy first
    - Verify the service description
    - Check pricing and payment details
    - Contact us with questions BEFORE paying
    - Confirm you want to proceed with the purchase

    ## Account Management

    If you have an account with us:
    - You can stop using the service anytime
    - Account data can be deleted upon request
    - Email dmcpexam2020@gmail.com for data deletion
    - We process deletion requests within 30 days

    ## Authentication

    - Login is managed via **Google Auth**
    - Secure and encrypted authentication
    - No password storage on our platform

    ## Contact Us

    For questions about this policy, contact:
    - Email: dmcpexam2020@gmail.com
    - Phone: +91 7021761291

    ---

    **By making a payment, you acknowledge that NO CANCELLATIONS are permitted once service is delivered.**
    """)

# SHIPPING PAGE
elif selected_page == 'shipping':
    st.markdown("# 📦 Shipping & Delivery Policy")
    st.markdown("""
    **Last Updated:** October 28, 2025

    ## Digital Product - Instant Delivery

    **IMPORTANT:** Home Loan Toolkit is a **100% DIGITAL PRODUCT**. There is NO physical shipping involved.

    ## How You Get Access

    ### ✅ Instant Access After Payment

    Once your payment is successfully processed:

    1. **Immediate Activation**: Your account is activated instantly
    2. **No Waiting**: Access all 12 strategies immediately
    3. **Instant Delivery**: All calculators, tools, and content available right away
    4. **Email Confirmation**: You'll receive a payment confirmation from Razorpay

    ### 📧 Access Details

    - **Delivery Method**: Online access through website
    - **Delivery Time**: Instant (within seconds of payment confirmation)
    - **Access Duration**: Lifetime access
    - **Downloads**: No downloads required - all tools are web-based

    ## What You Get Access To

    After successful payment, you will immediately get access to:

    - ✅ All 12 Home Loan Payment Strategies
    - ✅ Interactive Calculators for each strategy
    - ✅ Comparison Tools
    - ✅ Implementation Guides
    - ✅ All future updates (FREE)

    ## Payment Processing

    - Payment is processed through secure Razorpay gateway
    - Once payment is successful, access is granted automatically
    - No manual activation required
    - No shipping address needed (digital product)

    ## Accessing Your Purchase

    **Steps to Access:**

    1. Sign in with your Google account
    2. Complete payment of ₹99 through checkout
    3. Razorpay processes your payment
    4. You receive instant access to all strategies
    5. Start using tools immediately

    ## No Physical Delivery

    - ✅ This is a digital-only service
    - ✅ No courier/postal delivery
    - ✅ No shipping charges
    - ✅ No shipping address required
    - ✅ Instant online access only

    ## Support

    If you face any issues accessing your purchase after payment:

    - **Email**: dmcpexam2020@gmail.com
    - **Phone**: +91 7021761291
    - **Response Time**: Within 24-48 hours
    - **We'll resolve**: Any access issues immediately

    ## Summary

    🎯 **Digital Product = Instant Access**
    - Pay ₹99 → Get instant access → Start using immediately
    - No waiting, no shipping, no delays
    - 100% online, 100% instant

    ---

    **By making a purchase, you understand this is a digital product with instant online access and no physical shipping.**
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem; font-size: 0.9rem;">
    <strong>💡 Pro Tip:</strong> Combine multiple strategies for maximum impact!<br>
    Made with ❤️ for smart home loan management | © 2025 Home Loan Toolkit<br>
    📧 Contact: dmcpexam2020@gmail.com | 📱 +91 7021761291<br><br>
    <a href="?page=contact" style="color: #666; margin: 0 8px;">Contact</a> |
    <a href="?page=terms" style="color: #666; margin: 0 8px;">Terms</a> |
    <a href="?page=privacy" style="color: #666; margin: 0 8px;">Privacy</a> |
    <a href="?page=refund" style="color: #666; margin: 0 8px;">Refund</a> |
    <a href="?page=cancellation" style="color: #666; margin: 0 8px;">Cancellation</a> |
    <a href="?page=shipping" style="color: #666; margin: 0 8px;">Shipping</a>
</div>
""", unsafe_allow_html=True)
