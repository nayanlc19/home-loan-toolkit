import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Home Loan Payment Strategies",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .strategy-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        cursor: pointer;
        transition: transform 0.3s ease;
        color: white;
    }
    .strategy-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    .strategy-card.low-risk {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .strategy-card.medium-risk {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .strategy-card.advanced {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .strategy-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .strategy-desc {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    .strategy-meta {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    .category-header {
        font-size: 2rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #2E7D32;
    }
    .info-banner {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E7D32;
        margin: 2rem 0;
    }
    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #F57C00;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .step-number {
        background: linear-gradient(135deg, #F57C00 0%, #FFB74D 100%);
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-right: 1rem;
    }
    .step-title {
        font-size: 1.4rem;
        font-weight: bold;
        color: #E65100;
        margin-bottom: 0.5rem;
    }
    .step-content {
        font-size: 1rem;
        color: #444;
        line-height: 1.8;
        margin-left: 56px;
    }
    .warning-box {
        background: #FFF3E0;
        border-left: 5px solid #FF9800;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background: #E8F5E9;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        background: #E3F2FD;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .checklist-item {
        padding: 0.8rem;
        margin: 0.5rem 0;
        background: white;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'selected_strategy' not in st.session_state:
    st.session_state.selected_strategy = None

# Strategy definitions
STRATEGIES = {
    "low_risk": [
        {
            "id": "bi_weekly",
            "name": "1. Bi-Weekly Payment Hack",
            "tagline": "Pay 1 Extra EMI Annually Without Feeling It",
            "savings": "₹8-10L saved, 3 years faster",
            "complexity": "⭐ Simple",
            "requirements": "None - Works for everyone"
        },
        {
            "id": "step_up_emi",
            "name": "2. Step-Up EMI Strategy",
            "tagline": "Increase EMI with Salary Hikes",
            "savings": "₹18-25L saved, 7 years faster",
            "complexity": "⭐⭐ Moderate",
            "requirements": "Annual salary growth"
        },
        {
            "id": "tax_refund",
            "name": "3. Tax Refund Amplification",
            "tagline": "Compound Your Tax Savings",
            "savings": "₹5-8L extra saved",
            "complexity": "⭐ Simple",
            "requirements": "30% tax bracket (best)"
        },
        {
            "id": "rental_escalation",
            "name": "4. Rental Escalation Prepayment",
            "tagline": "Use Rent Increases to Prepay",
            "savings": "Varies by rent growth",
            "complexity": "⭐ Simple",
            "requirements": "Rental property income"
        }
    ],
    "medium_risk": [
        {
            "id": "sip_offset",
            "name": "5. SIP Offset Strategy ⭐",
            "tagline": "Invest Instead of Prepay - Build Wealth While Repaying",
            "savings": "₹15-30L surplus after loan closure",
            "complexity": "⭐⭐⭐ Complex",
            "requirements": "Age <35, risk appetite, 10+ year horizon"
        },
        {
            "id": "rental_arbitrage",
            "name": "6. Rental Arbitrage",
            "tagline": "Live Cheaply, Prepay Difference",
            "savings": "₹10-20L saved, 5 years faster",
            "complexity": "⭐⭐ Moderate",
            "requirements": "High rental area property"
        },
        {
            "id": "credit_card_float",
            "name": "7. Credit Card Float",
            "tagline": "Keep Money in OD Longer (45-day float)",
            "savings": "₹2.6L over 20 years + cashback",
            "complexity": "⭐⭐ Moderate",
            "requirements": "OD loan + Discipline to pay CC on time"
        },
        {
            "id": "fd_ladder",
            "name": "8. Reverse FD Laddering",
            "tagline": "Forced Prepayment Discipline",
            "savings": "₹8-15L saved, 4 years faster",
            "complexity": "⭐⭐ Moderate",
            "requirements": "Annual surplus for FD"
        }
    ],
    "advanced": [
        {
            "id": "loan_chunking",
            "name": "9. Loan Chunking",
            "tagline": "Split Into Multiple Tenures",
            "savings": "₹14L saved on ₹50L loan",
            "complexity": "⭐⭐⭐ Complex",
            "requirements": "Bank approval (rare)"
        },
        {
            "id": "bonus_deferral",
            "name": "10. Bonus Deferral + Debt Fund",
            "tagline": "Tax-Efficient Prepayment",
            "savings": "₹15-25L (tax + interest)",
            "complexity": "⭐⭐⭐⭐ Very Complex",
            "requirements": "Company bonus deferral policy"
        },
        {
            "id": "debt_fund_swp",
            "name": "11. Debt Fund SWP",
            "tagline": "Liquidity + Interest Savings",
            "savings": "₹5-10L + maintain liquidity",
            "complexity": "⭐⭐⭐ Complex",
            "requirements": "Large lumpsum available"
        },
        {
            "id": "salary_arbitrage",
            "name": "12. Salary Account Arbitrage",
            "tagline": "Earn While You Wait (7% vs 3.5%)",
            "savings": "₹2.8L over 20 years",
            "complexity": "⭐ Simple",
            "requirements": "High-yield savings account/liquid fund"
        }
    ]
}

# Helper function to calculate EMI
def calculate_emi(principal, annual_rate, months):
    """Calculate EMI for home loan"""
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return principal / months
    emi = principal * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    return emi

# Helper function to create strategy cards
def create_strategy_card(strategy, risk_class):
    card_html = f"""
    <div class="strategy-card {risk_class}">
        <div class="strategy-title">{strategy['name']}</div>
        <div class="strategy-desc">{strategy['tagline']}</div>
        <div class="strategy-meta">
            💰 <strong>Potential Savings:</strong> {strategy['savings']}<br>
            🎯 <strong>Complexity:</strong> {strategy['complexity']}<br>
            📋 <strong>Requirements:</strong> {strategy['requirements']}
        </div>
    </div>
    """
    return card_html

# Main app
def main():
    # Header
    st.markdown('<div class="main-header">🏠 Home Loan Payment Strategies</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">12 Proven Strategies to Pay Off Your Home Loan Faster & Save Lakhs in Interest</div>', unsafe_allow_html=True)

    # Add back button when running as part of toolkit
    if 'selected_category' in st.session_state and st.session_state.get('selected_category') == 'loans':
        st.markdown("---")

    # Info banner
    st.markdown("""
    <div class="info-banner">
        <strong>💡 How This Works:</strong><br>
        • Click on any strategy below to see detailed calculator and implementation guide<br>
        • Each strategy is risk-categorized: 🟢 Low Risk | 🟡 Medium Risk | 🔴 Advanced<br>
        • Use the sidebar to navigate between strategies and comparison page<br>
        • All calculations are based on real Indian home loan scenarios
    </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("📍 Navigation")

    page_options = ["🏠 Home - All Strategies", "📊 Compare All Strategies"]

    # Add individual strategy pages
    for category, strategies in STRATEGIES.items():
        for strategy in strategies:
            page_options.append(f"{strategy['name']}")

    selected_page = st.sidebar.radio("Go to:", page_options, label_visibility="collapsed")

    # Route to appropriate page
    if selected_page == "🏠 Home - All Strategies":
        show_landing_page()
    elif selected_page == "📊 Compare All Strategies":
        show_comparison_page()
    else:
        # Find and show individual strategy
        for category, strategies in STRATEGIES.items():
            for strategy in strategies:
                if strategy['name'] in selected_page:
                    show_strategy_page(strategy['id'], strategy['name'])
                    return

def show_landing_page():
    """Display landing page with all strategy cards"""

    # Low Risk Strategies
    st.markdown('<div class="category-header">🟢 Low Risk Strategies - Safe & Predictable</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, strategy in enumerate(STRATEGIES["low_risk"]):
        with cols[idx % 2]:
            st.markdown(create_strategy_card(strategy, "low-risk"), unsafe_allow_html=True)
            if st.button(f"Explore {strategy['name']}", key=f"btn_{strategy['id']}", use_container_width=True):
                st.session_state.selected_strategy = strategy['id']
                st.rerun()

    # Medium Risk Strategies
    st.markdown('<div class="category-header">🟡 Medium Risk Strategies - Higher Rewards, Some Risk</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, strategy in enumerate(STRATEGIES["medium_risk"]):
        with cols[idx % 2]:
            st.markdown(create_strategy_card(strategy, "medium-risk"), unsafe_allow_html=True)
            if st.button(f"Explore {strategy['name']}", key=f"btn_{strategy['id']}", use_container_width=True):
                st.session_state.selected_strategy = strategy['id']
                st.rerun()

    # Advanced Strategies
    st.markdown('<div class="category-header">🔴 Advanced Strategies - Maximum Impact, Requires Planning</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, strategy in enumerate(STRATEGIES["advanced"]):
        with cols[idx % 2]:
            st.markdown(create_strategy_card(strategy, "advanced"), unsafe_allow_html=True)
            if st.button(f"Explore {strategy['name']}", key=f"btn_{strategy['id']}", use_container_width=True):
                st.session_state.selected_strategy = strategy['id']
                st.rerun()

    # Quick action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Compare All Strategies", use_container_width=True, type="primary"):
            st.session_state.selected_strategy = "comparison"
            st.rerun()
    with col2:
        if st.button("🎯 Get Personalized Recommendation", use_container_width=True):
            st.info("Use the comparison page to get recommendations based on your profile!")
    with col3:
        if st.button("💡 Most Popular: SIP Offset", use_container_width=True):
            st.session_state.selected_strategy = "sip_offset"
            st.rerun()

def show_comparison_page():
    """Show comparison of all strategies"""
    st.title("📊 Compare All 12 Strategies")

    st.markdown("""
    Use the inputs below to compare all strategies for YOUR specific loan scenario.
    """)

    # Common inputs
    col1, col2, col3 = st.columns(3)

    with col1:
        comp_loan = st.number_input("Your Loan Amount (₹)", min_value=500000, max_value=100000000,
                                    value=5000000, step=100000, key="comp_loan")
        comp_rate = st.number_input("Your Interest Rate (%)", min_value=5.0, max_value=15.0,
                                    value=8.5, step=0.1, key="comp_rate")

    with col2:
        comp_tenure = st.slider("Loan Tenure (Years)", 10, 30, 20, key="comp_tenure")
        comp_surplus = st.number_input("Monthly Surplus Available (₹)", min_value=5000,
                                       max_value=200000, value=20000, step=1000, key="comp_surplus")

    with col3:
        comp_lumpsum = st.number_input("Lumpsum Available (₹)", min_value=0, max_value=50000000,
                                       value=0, step=100000, key="comp_lumpsum")
        comp_tax_slab = st.selectbox("Your Tax Slab (%)", [0, 20, 30], index=2, key="comp_tax")

    # Calculate baseline
    comp_monthly_rate = comp_rate / (12 * 100)
    comp_months = comp_tenure * 12
    comp_emi = comp_loan * comp_monthly_rate * (1 + comp_monthly_rate)**comp_months / ((1 + comp_monthly_rate)**comp_months - 1)
    comp_total_interest = (comp_emi * comp_months) - comp_loan

    st.markdown("### Strategy Comparison Results")

    # Create comparison dataframe
    strategies_comparison = []

    # Add all strategies with estimated savings
    strategies_comparison.append({
        "Strategy": "1. Bi-Weekly Payment",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐ Simple",
        "Interest Saved": f"₹{comp_total_interest * 0.18:,.0f}",
        "Time Saved": "~3 years",
        "Requirements": "None",
        "Best For": "Everyone"
    })

    strategies_comparison.append({
        "Strategy": "2. Step-Up EMI",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐⭐ Moderate",
        "Interest Saved": f"₹{comp_total_interest * 0.35:,.0f}",
        "Time Saved": "~7 years",
        "Requirements": "Salary growth",
        "Best For": "Young professionals"
    })

    tr_annual_prepay = min(150000, comp_surplus * 12)
    tr_refund = tr_annual_prepay * (comp_tax_slab / 100)
    tr_saving = tr_refund * comp_tenure * 0.5

    strategies_comparison.append({
        "Strategy": "3. Tax Refund Cycle",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐ Simple",
        "Interest Saved": f"₹{tr_saving:,.0f}",
        "Time Saved": "~2 years",
        "Requirements": "Tax filing",
        "Best For": "30% tax bracket"
    })

    strategies_comparison.append({
        "Strategy": "4. Rental Escalation",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐ Simple",
        "Interest Saved": "Varies",
        "Time Saved": "Depends on rent",
        "Requirements": "Rental property",
        "Best For": "Property investors"
    })

    sip_benefit = comp_surplus * 12 * 12 * (1.12**12) * 0.25

    strategies_comparison.append({
        "Strategy": "5. SIP Offset ⭐",
        "Risk Level": "🟡 Medium",
        "Complexity": "⭐⭐⭐ Complex",
        "Interest Saved": f"₹{sip_benefit:,.0f}",
        "Time Saved": "N/A (Pay + Invest)",
        "Requirements": "Risk appetite",
        "Best For": "Age < 35"
    })

    strategies_comparison.append({
        "Strategy": "6. Rental Arbitrage",
        "Risk Level": "🟡 Medium",
        "Complexity": "⭐⭐ Moderate",
        "Interest Saved": "₹10-20L",
        "Time Saved": "~5 years",
        "Requirements": "High rent area",
        "Best For": "Metro cities"
    })

    strategies_comparison.append({
        "Strategy": "7. Credit Card Float",
        "Risk Level": "🟡 Medium",
        "Complexity": "⭐⭐ Moderate",
        "Interest Saved": f"₹{200000 * 0.0885 * (45/365) * 12 * 20:,.0f}",
        "Time Saved": "N/A",
        "Requirements": "OD loan + CC",
        "Best For": "Disciplined spenders"
    })

    strategies_comparison.append({
        "Strategy": "8. Reverse FD Ladder",
        "Risk Level": "🟡 Medium",
        "Complexity": "⭐⭐ Moderate",
        "Interest Saved": "₹8-15L",
        "Time Saved": "~4 years",
        "Requirements": "Annual surplus",
        "Best For": "Disciplined savers"
    })

    strategies_comparison.append({
        "Strategy": "9. Loan Chunking",
        "Risk Level": "🔴 Advanced",
        "Complexity": "⭐⭐⭐ Complex",
        "Interest Saved": f"₹{comp_total_interest * 0.26:,.0f}",
        "Time Saved": "Varies",
        "Requirements": "Bank approval",
        "Best For": "Large loans"
    })

    strategies_comparison.append({
        "Strategy": "10. Bonus Deferral",
        "Risk Level": "🔴 Advanced",
        "Complexity": "⭐⭐⭐⭐ Very Complex",
        "Interest Saved": "₹15-25L",
        "Time Saved": "~6 years",
        "Requirements": "Company policy",
        "Best For": "High bonuses"
    })

    strategies_comparison.append({
        "Strategy": "11. Debt Fund SWP",
        "Risk Level": "🔴 Advanced",
        "Complexity": "⭐⭐⭐ Complex",
        "Interest Saved": "₹5-10L",
        "Time Saved": "N/A",
        "Requirements": "Large lumpsum",
        "Best For": "Need liquidity"
    })

    strategies_comparison.append({
        "Strategy": "12. Salary Arbitrage",
        "Risk Level": "🟢 Low",
        "Complexity": "⭐ Simple",
        "Interest Saved": f"₹{200000 * 0.035 * 20:,.0f}",
        "Time Saved": "N/A",
        "Requirements": "High-yield account",
        "Best For": "Everyone"
    })

    # Display table
    comparison_df = pd.DataFrame(strategies_comparison)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    # Personalized recommendations
    st.markdown("### 🎯 Personalized Recommendations")

    recommended_strategies = []

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

    # Hybrid approach
    st.markdown("### 💡 Hybrid Approach (Best of Multiple Strategies)")
    st.markdown(f"""
    **Recommended Combination:**
    1. **Bi-Weekly Payment** (₹{comp_emi/2:,.0f} × 26 = extra EMI/year)
    2. **Tax Refund Cycle** (₹{min(150000, comp_surplus * 12) * (comp_tax_slab/100) if comp_tax_slab > 0 else 0:,.0f}/year extra prepayment)
    3. **Salary Arbitrage** (Earn extra ₹{200000 * 0.035:,.0f}/year on idle money)

    **Combined Impact:**
    - Interest saved: **₹{comp_total_interest * 0.45:,.0f}+**
    - Loan closes: **~8-10 years early**
    - Zero risk, maximum benefit!
    """)

def show_strategy_page(strategy_id, strategy_name):
    """Show individual strategy detail page"""
    st.title(strategy_name)

    if st.button("← Back to All Strategies", key="back_btn"):
        st.session_state.selected_strategy = None
        st.rerun()

    st.markdown("---")

    # Route to appropriate calculator based on strategy_id
    if strategy_id == "bi_weekly":
        from strategy_calculators import show_bi_weekly_calculator
        show_bi_weekly_calculator()
    elif strategy_id == "step_up_emi":
        from strategy_calculators import show_step_up_emi_calculator
        show_step_up_emi_calculator()
    elif strategy_id == "tax_refund":
        from strategy_calculators import show_tax_refund_calculator
        show_tax_refund_calculator()
    elif strategy_id == "rental_escalation":
        from strategy_calculators import show_rental_escalation_calculator
        show_rental_escalation_calculator()
    elif strategy_id == "sip_offset":
        show_sip_offset_calculator()
    elif strategy_id == "rental_arbitrage":
        from strategy_calculators import show_rental_arbitrage_calculator
        show_rental_arbitrage_calculator()
    elif strategy_id == "credit_card_float":
        from strategy_calculators import show_credit_card_float_calculator
        show_credit_card_float_calculator()
    elif strategy_id == "fd_ladder":
        from strategy_calculators import show_fd_ladder_calculator
        show_fd_ladder_calculator()
    elif strategy_id == "loan_chunking":
        from strategy_calculators import show_loan_chunking_calculator
        show_loan_chunking_calculator()
    elif strategy_id == "bonus_deferral":
        from strategy_calculators import show_bonus_deferral_calculator
        show_bonus_deferral_calculator()
    elif strategy_id == "debt_fund_swp":
        from strategy_calculators import show_debt_fund_swp_calculator
        show_debt_fund_swp_calculator()
    elif strategy_id == "salary_arbitrage":
        from strategy_calculators import show_salary_arbitrage_calculator
        show_salary_arbitrage_calculator()
    else:
        st.info("Calculator for this strategy is being loaded...")


# Inline calculator functions for remaining strategies
def show_sip_offset_calculator():
    """SIP Offset Strategy - The most requested one!"""
    st.markdown("""
    ### 📈 The SIP Offset Strategy
    Instead of prepaying loan, **invest in equity SIP** and use accumulated corpus to pay off loan later.

    **The Math:**
    - Home loan interest: 8.5% per annum
    - Nifty index historical returns: 12-14% per annum
    - **Spread: 3.5-5.5% advantage**

    ⚠️ **Risk:** Market returns not guaranteed, requires discipline
    """)

    st.markdown("---")
    st.markdown("### 🧮 Interactive Calculator")

    col1, col2, col3 = st.columns(3)

    with col1:
        sip_loan = st.number_input("Loan Amount (₹)", 500000, 100000000, 5000000, 100000, key="sip_loan")
        sip_rate = st.number_input("Loan Interest (%)", 5.0, 15.0, 8.5, 0.1, key="sip_rate")
        sip_tenure = st.slider("Loan Tenure (Years)", 10, 30, 20, key="sip_tenure")

    with col2:
        sip_monthly = st.number_input("Monthly SIP (₹)", 5000, 200000, 20000, 1000, key="sip_monthly")
        sip_return = st.slider("Expected SIP Return (%)", 8.0, 18.0, 12.0, 0.5, key="sip_return",
                              help="Nifty historical: 12-14%")
        sip_years = st.slider("SIP Duration (Years)", 5, 25, 12, key="sip_years")

    # Calculate prepayment scenario
    sip_emi = calculate_emi(sip_loan, sip_rate, sip_tenure * 12)
    sip_monthly_rate = sip_rate / (12 * 100)

    # Scenario A: Prepay monthly
    sip_outstanding_prepay = sip_loan
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

            if sip_outstanding_prepay > 0.01:
                prepay = min(sip_monthly, sip_outstanding_prepay)
                sip_outstanding_prepay -= prepay

    # Scenario B: SIP investment
    sip_corpus = 0
    sip_monthly_sip_rate = sip_return / (12 * 100)

    for month in range(sip_years * 12):
        sip_corpus = (sip_corpus + sip_monthly) * (1 + sip_monthly_sip_rate)

    # Interest on full loan
    sip_outstanding_nosip = sip_loan
    sip_interest_nosip = 0

    for month in range(sip_years * 12):
        if sip_outstanding_nosip <= 0.01:
            break
        interest = sip_outstanding_nosip * sip_monthly_rate
        principal = sip_emi - interest
        sip_outstanding_nosip -= principal
        sip_interest_nosip += interest

    sip_remaining_loan = sip_outstanding_nosip

    # Tax on SIP
    sip_invested = sip_monthly * sip_years * 12
    sip_gains = sip_corpus - sip_invested
    sip_ltcg_tax = max(0, (sip_gains - 125000) * 0.10)
    sip_corpus_after_tax = sip_corpus - sip_ltcg_tax
    sip_surplus_after_tax = sip_corpus_after_tax - sip_remaining_loan

    with col3:
        st.metric("SIP Corpus (After Tax)", f"₹{sip_corpus_after_tax:,.0f}",
                 help=f"LTCG Tax: ₹{sip_ltcg_tax:,.0f}")
        st.metric("Remaining Loan", f"₹{sip_remaining_loan:,.0f}")
        st.metric("Surplus in Hand", f"₹{sip_surplus_after_tax:,.0f}",
                 delta="After closing loan!" if sip_surplus_after_tax > 0 else "Shortfall")

    st.markdown("### 📊 Scenario Comparison")

    comparison_data = pd.DataFrame({
        "Scenario": ["Prepay Monthly", "SIP + Close Later"],
        "Monthly Outflow": [f"₹{sip_emi + sip_monthly:,.0f}", f"₹{sip_emi + sip_monthly:,.0f}"],
        "Duration": [f"{sip_months_prepay/12:.1f} years", f"{sip_years} years"],
        "Interest Paid": [f"₹{sip_interest_prepay:,.0f}", f"₹{sip_interest_nosip:,.0f}"],
        "Final Position": [
            "Debt free, ₹0 in hand",
            f"Debt free, ₹{sip_surplus_after_tax:,.0f} surplus" if sip_surplus_after_tax > 0
            else f"Shortfall ₹{abs(sip_surplus_after_tax):,.0f}"
        ]
    })

    st.table(comparison_data)

    if sip_surplus_after_tax > 0:
        st.success(f"""
        🎉 **SIP Strategy Wins!** By investing ₹{sip_monthly:,.0f}/month in SIP:
        - After {sip_years} years: ₹{sip_corpus_after_tax:,.0f} accumulated
        - Pay off loan: ₹{sip_remaining_loan:,.0f}
        - **₹{sip_surplus_after_tax:,.0f} surplus in hand!**
        """)
    else:
        st.warning(f"""
        ⚠️ **Prepayment Wins** in this scenario.
        Try increasing SIP return % or duration.
        """)


# Placeholder functions for remaining strategies (you can expand these similarly)
if __name__ == "__main__":
    main()
