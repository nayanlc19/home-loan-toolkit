"""
Strategy Calculators - Individual calculator pages for each home loan strategy
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from home_loan_strategies import calculate_emi


def show_bi_weekly_calculator():
    """Bi-Weekly Payment Strategy Calculator"""
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

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
        bw_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                  value=5000000, step=100000, key="bw_loan")
        bw_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                  value=8.5, step=0.1, key="bw_rate")
        bw_tenure = st.slider("Tenure (Years)", 5, 30, 20, key="bw_tenure")

    # Calculate regular EMI
    bw_months = bw_tenure * 12
    bw_monthly_rate = bw_rate / (12 * 100)
    bw_emi = calculate_emi(bw_loan, bw_rate, bw_months)
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

    with col2:
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


def show_step_up_emi_calculator():
    """Step-Up EMI Strategy Calculator"""
    st.markdown("""
    ### How It Works
    Start with **manageable EMI**, increase it annually as your salary grows.

    **The Power:**
    - Most people get 8-12% salary hike annually
    - Allocate 50% of hike to EMI increase
    - Barely feel the pinch, save massively on interest
    """)

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
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

    with col2:
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


def show_tax_refund_calculator():
    """Tax Refund Amplification Calculator"""
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

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
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

    with col2:
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


def show_rental_escalation_calculator():
    """Rental Escalation Prepayment Calculator"""
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

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
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

    with col2:
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


def show_rental_arbitrage_calculator():
    """Rental Arbitrage Calculator"""
    st.markdown("""
    ### How It Works
    Rent out your house at premium, live in cheaper location, prepay the difference.

    **The Strategy:**
    - Your house rent potential: ₹50K/month
    - You rent cheaper house: ₹30K/month
    - **Difference of ₹20K → Goes to prepayment**

    **Why It Works:**
    - Location arbitrage (premium vs value areas)
    - Tax benefits on rental income
    - Accelerated loan closure
    """)

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
        ra_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                  value=5000000, step=100000, key="ra_loan")
        ra_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                  value=8.5, step=0.1, key="ra_rate")
        ra_rent_received = st.number_input("Rent Received (₹/month)", min_value=10000, max_value=500000,
                                           value=50000, step=1000, key="ra_rent_recv",
                                           help="Rent you receive for your house")
        ra_rent_paid = st.number_input("Rent Paid (₹/month)", min_value=5000, max_value=400000,
                                       value=30000, step=1000, key="ra_rent_paid",
                                       help="Rent you pay for cheaper house")

    # Calculate arbitrage prepayment
    ra_monthly_surplus = ra_rent_received - ra_rent_paid
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

            # Monthly prepayment from arbitrage
            if ra_outstanding > 0.01:
                prepay = min(ra_monthly_surplus, ra_outstanding)
                ra_outstanding -= prepay

        ra_years += 1

    ra_interest_regular = (ra_emi * 20 * 12) - ra_loan
    ra_savings = ra_interest_regular - ra_total_interest

    # Tax calculation (simplified)
    ra_annual_rental_income = ra_rent_received * 12
    ra_standard_deduction = ra_annual_rental_income * 0.30
    ra_taxable_rental = ra_annual_rental_income - ra_standard_deduction

    with col2:
        st.metric("Monthly Surplus", f"₹{ra_monthly_surplus:,.0f}",
                 delta=f"₹{ra_rent_received:,.0f} - ₹{ra_rent_paid:,.0f}")
        st.metric("Annual Prepayment", f"₹{ra_monthly_surplus * 12:,.0f}")
        st.metric("Total Interest Saved", f"₹{ra_savings:,.0f}")
        st.metric("Loan Duration", f"{ra_years:.1f} years", delta=f"vs 20 years")

    st.markdown(f"""
    **Your Rental Arbitrage Results:**
    - Rent received: ₹{ra_rent_received:,.0f}/month
    - Rent paid: ₹{ra_rent_paid:,.0f}/month
    - Monthly surplus for prepayment: ₹{ra_monthly_surplus:,.0f}
    - Annual prepayment: ₹{ra_monthly_surplus * 12:,.0f}
    - **Loan closes in {ra_years:.1f} years instead of 20!**
    - **Total savings: ₹{ra_savings:,.0f}**

    **Tax Considerations:**
    - Annual rental income: ₹{ra_annual_rental_income:,.0f}
    - Standard deduction (30%): ₹{ra_standard_deduction:,.0f}
    - Taxable rental income: ₹{ra_taxable_rental:,.0f}
    - Plus: You can claim HRA deduction on rent paid

    **Pro Tips:**
    - Keep rent agreements proper for tax compliance
    - Consider location carefully (schools, commute)
    - Factor in relocation costs
    - Rental income is taxable - plan accordingly
    """)


def show_credit_card_float_calculator():
    """Credit Card Float Calculator (OD Loan Only)"""
    st.markdown("""
    ### How It Works
    Use credit card's **45-day interest-free period**, keep money in OD account longer.

    **The Strategy:**
    - All expenses on credit card: ₹1L/month
    - Money stays in OD account for 45 days extra
    - Saves interest for those 45 days
    - Plus earn cashback/rewards!

    **Requirements:**
    - Overdraft loan (NOT regular loan)
    - Credit card with good limit
    - 100% on-time payment discipline
    """)

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
        cc_monthly_expenses = st.number_input("Monthly Expenses (₹)", min_value=10000, max_value=500000,
                                              value=100000, step=5000, key="cc_expenses",
                                              help="Amount you'll spend on credit card")
        cc_od_rate = st.number_input("OD Interest Rate (%)", min_value=5.0, max_value=20.0,
                                     value=13.5, step=0.1, key="cc_rate")
        cc_cashback = st.slider("Cashback/Rewards (%)", 0.0, 5.0, 1.5, 0.5, key="cc_cashback",
                                help="Typical premium cards give 1-2%")
        cc_tenure = st.slider("Loan Tenure (Years)", 5, 30, 20, key="cc_tenure")

    # Calculate savings from float
    cc_daily_rate = cc_od_rate / (365 * 100)
    cc_float_days = 45
    cc_monthly_interest_saved = cc_monthly_expenses * cc_daily_rate * cc_float_days
    cc_monthly_cashback = cc_monthly_expenses * (cc_cashback / 100)
    cc_monthly_benefit = cc_monthly_interest_saved + cc_monthly_cashback

    cc_annual_benefit = cc_monthly_benefit * 12
    cc_total_benefit = cc_annual_benefit * cc_tenure

    with col2:
        st.metric("Monthly Interest Saved", f"₹{cc_monthly_interest_saved:,.0f}",
                 help=f"₹{cc_monthly_expenses:,.0f} × {cc_float_days} days float")
        st.metric("Monthly Cashback", f"₹{cc_monthly_cashback:,.0f}",
                 help=f"{cc_cashback}% of ₹{cc_monthly_expenses:,.0f}")
        st.metric("Total Monthly Benefit", f"₹{cc_monthly_benefit:,.0f}")
        st.metric(f"{cc_tenure}-Year Total Benefit", f"₹{cc_total_benefit:,.0f}")

    st.markdown(f"""
    **Your Credit Card Float Results:**
    - Monthly expenses routed through CC: ₹{cc_monthly_expenses:,.0f}
    - Average float period: {cc_float_days} days
    - Interest saved per month: ₹{cc_monthly_interest_saved:,.0f}
    - Cashback earned per month: ₹{cc_monthly_cashback:,.0f}
    - **Total monthly benefit: ₹{cc_monthly_benefit:,.0f}**
    - **{cc_tenure}-year total benefit: ₹{cc_total_benefit:,.0f}**

    **The Math:**
    - ₹{cc_monthly_expenses:,.0f} stays in OD for {cc_float_days} extra days
    - Daily OD rate: {cc_daily_rate*100:.4f}%
    - Savings: ₹{cc_monthly_expenses:,.0f} × {cc_float_days} × {cc_daily_rate*100:.4f}% = ₹{cc_monthly_interest_saved:,.0f}

    **Critical Requirements:**
    - Pay CC bill 100% on-time (even 1 day late = disaster)
    - Only works with OD loan (regular loan won't benefit)
    - Never carry CC balance (18-42% interest kills the strategy)
    - Auto-pay setup is mandatory

    **Best Cards for This:**
    - HDFC Infinia/Diners Black (3.3% rewards)
    - Amex Platinum (2-5% cashback)
    - Axis Magnus/Reserve (5% accelerated)
    - SBI Cashback (5% online)
    """)


def show_fd_ladder_calculator():
    """FD Laddering Calculator"""
    st.markdown("""
    ### How It Works
    Create **FD ladder** with annual maturity, use proceeds to prepay loan.

    **The Strategy:**
    - Have ₹10L lumpsum → Split into 5 FDs of ₹2L each
    - 1-year, 2-year, 3-year, 4-year, 5-year FDs
    - Each year one FD matures → Prepay loan
    - Reinvest maturity into new 5-year FD

    **Why It Works:**
    - FD earns interest while waiting
    - Annual prepayment reduces loan principal
    - Better than keeping lumpsum idle
    - Enhanced: Use debt mutual funds for better returns
    """)

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
        fd_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                  value=5000000, step=100000, key="fd_loan")
        fd_rate = st.number_input("Loan Interest Rate (%)", min_value=5.0, max_value=15.0,
                                  value=8.5, step=0.1, key="fd_rate")
        fd_lumpsum = st.number_input("Lumpsum Available (₹)", min_value=100000, max_value=10000000,
                                     value=1000000, step=100000, key="fd_lumpsum")
        fd_fd_rate = st.number_input("FD Interest Rate (%)", min_value=4.0, max_value=9.0,
                                     value=7.0, step=0.1, key="fd_fd_rate")
        fd_ladder_years = st.slider("Ladder Period (Years)", 3, 10, 5, key="fd_ladder")

    # Scenario A: Prepay lumpsum immediately
    fd_outstanding_prepay = fd_loan - fd_lumpsum
    fd_monthly_rate = fd_rate / (12 * 100)
    fd_emi = calculate_emi(fd_loan, fd_rate, 20 * 12)
    fd_years_prepay = 0
    fd_interest_prepay = 0

    while fd_outstanding_prepay > 0.01 and fd_years_prepay < 20:
        for month in range(12):
            if fd_outstanding_prepay <= 0.01:
                break
            interest = fd_outstanding_prepay * fd_monthly_rate
            principal = fd_emi - interest
            if principal > fd_outstanding_prepay:
                principal = fd_outstanding_prepay
            fd_outstanding_prepay -= principal
            fd_interest_prepay += interest
        fd_years_prepay += 1

    # Scenario B: FD ladder
    fd_chunk = fd_lumpsum / fd_ladder_years
    fd_outstanding_ladder = fd_loan
    fd_interest_ladder = 0
    fd_years_ladder = 0
    fd_ladder_schedule = []

    while fd_outstanding_ladder > 0.01 and fd_years_ladder < 20:
        for month in range(12):
            if fd_outstanding_ladder <= 0.01:
                break
            interest = fd_outstanding_ladder * fd_monthly_rate
            principal = fd_emi - interest
            if principal > fd_outstanding_ladder:
                principal = fd_outstanding_ladder
            fd_outstanding_ladder -= principal
            fd_interest_ladder += interest

        # Annual FD maturity and prepayment
        if fd_years_ladder < fd_ladder_years and fd_outstanding_ladder > 0.01:
            years_held = fd_years_ladder + 1
            fd_maturity = fd_chunk * ((1 + fd_fd_rate/100) ** years_held)
            prepay_amount = min(fd_maturity, fd_outstanding_ladder)
            fd_outstanding_ladder -= prepay_amount
            fd_ladder_schedule.append(f"Year {fd_years_ladder+1}: FD matures ₹{fd_maturity:,.0f} → Prepay")

        fd_years_ladder += 1

    fd_difference = fd_interest_prepay - fd_interest_ladder

    with col2:
        st.metric("Immediate Prepay", f"{fd_years_prepay:.1f} years",
                 delta=f"₹{fd_interest_prepay:,.0f} interest")
        st.metric("FD Ladder Approach", f"{fd_years_ladder:.1f} years",
                 delta=f"₹{fd_interest_ladder:,.0f} interest")
        st.metric("Interest Difference", f"₹{abs(fd_difference):,.0f}",
                 delta="Ladder better" if fd_difference > 0 else "Prepay better")
        st.metric("FD Interest Earned", f"₹{(fd_lumpsum * (fd_fd_rate/100) * fd_ladder_years):,.0f}")

    st.markdown(f"""
    **FD Ladder Journey:**

    {chr(10).join(fd_ladder_schedule)}

    **Comparison:**
    - **Option A (Prepay now):** Loan closes in {fd_years_prepay:.1f} years, interest: ₹{fd_interest_prepay:,.0f}
    - **Option B (FD Ladder):** Loan closes in {fd_years_ladder:.1f} years, interest: ₹{fd_interest_ladder:,.0f}
    - FD interest earned: ₹{(fd_lumpsum * (fd_fd_rate/100) * fd_ladder_years):,.0f}

    **Enhanced Strategy - Debt Mutual Funds:**
    - Instead of FD, use debt funds (8-9% returns)
    - Tax efficient with indexation benefit
    - Better liquidity than FD
    - Recommended: Banking & PSU Debt Funds

    **When FD Ladder Wins:**
    - Need liquidity over the years
    - Want guaranteed returns
    - In lower tax bracket

    **When Immediate Prepay Wins:**
    - Loan rate > FD rate by 2%+
    - Want simplicity
    - No liquidity needs
    """)


def show_loan_chunking_calculator():
    """Loan Chunking Calculator"""
    st.markdown("""
    ### How It Works
    Split loan into **multiple chunks** with different tenures instead of single loan.

    **The Strategy:**
    - Need ₹50L → Take ₹20L for 10 years + ₹30L for 20 years
    - Instead of: ₹50L for 20 years
    - Close short-tenure chunk fast
    - Reduces weighted average interest

    **The Math:**
    - Chunk 1: Higher EMI, shorter tenure
    - Chunk 2: Normal EMI, normal tenure
    - Total interest < single loan interest

    **Limitation:** Most banks don't offer this. Workaround: Prepay aggressively first 10 years.
    """)

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
        lc_total_loan = st.number_input("Total Loan Amount (₹)", min_value=500000, max_value=100000000,
                                        value=5000000, step=100000, key="lc_loan")
        lc_rate = st.number_input("Interest Rate (%)", min_value=5.0, max_value=15.0,
                                  value=8.5, step=0.1, key="lc_rate")
        lc_chunk1_pct = st.slider("Chunk 1 Size (%)", 20, 60, 40, key="lc_chunk1",
                                  help="Percentage of loan in short-tenure chunk")
        lc_chunk1_tenure = st.slider("Chunk 1 Tenure (Years)", 5, 15, 10, key="lc_tenure1")
        lc_chunk2_tenure = st.slider("Chunk 2 Tenure (Years)", 15, 30, 20, key="lc_tenure2")

    # Calculate chunk amounts
    lc_chunk1 = lc_total_loan * (lc_chunk1_pct / 100)
    lc_chunk2 = lc_total_loan - lc_chunk1

    # Scenario A: Single loan
    lc_emi_single = calculate_emi(lc_total_loan, lc_rate, lc_chunk2_tenure * 12)
    lc_interest_single = (lc_emi_single * lc_chunk2_tenure * 12) - lc_total_loan

    # Scenario B: Chunked loans
    lc_emi_chunk1 = calculate_emi(lc_chunk1, lc_rate, lc_chunk1_tenure * 12)
    lc_emi_chunk2 = calculate_emi(lc_chunk2, lc_rate, lc_chunk2_tenure * 12)

    lc_interest_chunk1 = (lc_emi_chunk1 * lc_chunk1_tenure * 12) - lc_chunk1
    lc_interest_chunk2 = (lc_emi_chunk2 * lc_chunk2_tenure * 12) - lc_chunk2
    lc_total_interest_chunked = lc_interest_chunk1 + lc_interest_chunk2

    lc_combined_emi = lc_emi_chunk1 + lc_emi_chunk2
    lc_savings = lc_interest_single - lc_total_interest_chunked

    with col2:
        st.metric("Single Loan EMI", f"₹{lc_emi_single:,.0f}",
                 delta=f"Total interest: ₹{lc_interest_single:,.0f}")
        st.metric("Chunked Combined EMI", f"₹{lc_combined_emi:,.0f}",
                 delta=f"First {lc_chunk1_tenure} years")
        st.metric(f"EMI After {lc_chunk1_tenure} Years", f"₹{lc_emi_chunk2:,.0f}",
                 help="Chunk 1 closed, only Chunk 2 remains")
        st.metric("Total Interest Saved", f"₹{lc_savings:,.0f}",
                 delta=f"{(lc_savings/lc_interest_single)*100:.1f}% reduction")

    st.markdown(f"""
    **Loan Chunking Breakdown:**

    **Single Loan (₹{lc_total_loan:,.0f} for {lc_chunk2_tenure} years):**
    - EMI: ₹{lc_emi_single:,.0f}
    - Total interest: ₹{lc_interest_single:,.0f}

    **Chunked Loans:**
    - Chunk 1: ₹{lc_chunk1:,.0f} @ {lc_chunk1_tenure} years
      - EMI: ₹{lc_emi_chunk1:,.0f}
      - Interest: ₹{lc_interest_chunk1:,.0f}
    - Chunk 2: ₹{lc_chunk2:,.0f} @ {lc_chunk2_tenure} years
      - EMI: ₹{lc_emi_chunk2:,.0f}
      - Interest: ₹{lc_interest_chunk2:,.0f}

    **Results:**
    - First {lc_chunk1_tenure} years: Pay ₹{lc_combined_emi:,.0f}/month
    - After year {lc_chunk1_tenure}: Pay only ₹{lc_emi_chunk2:,.0f}/month
    - **Total interest: ₹{lc_total_interest_chunked:,.0f}**
    - **Savings: ₹{lc_savings:,.0f} ({(lc_savings/lc_interest_single)*100:.1f}% less!)**

    **Reality Check:**
    - Most Indian banks DON'T offer chunked loans
    - **Workaround:** Aggressive prepayment first {lc_chunk1_tenure} years
    - Target: Prepay ₹{lc_chunk1:,.0f} in {lc_chunk1_tenure} years
    - Monthly prepayment: ₹{(lc_combined_emi - lc_emi_single):,.0f}

    **Why It Works:**
    - Reduces principal faster
    - Less interest on remaining balance
    - Psychological win: Big chunk gone in {lc_chunk1_tenure} years
    """)


def show_bonus_deferral_calculator():
    """Bonus Deferral + Debt Fund Calculator"""
    st.markdown("""
    ### How It Works
    Defer annual bonus (if company allows), invest in debt fund, withdraw tax-efficiently.

    **The Tax Arbitrage:**
    - Bonus today: Taxed at 30% immediately
    - Defer → Invest in debt fund → Withdraw after 3 years
    - Benefit from indexation: Effective tax 5-10%
    - Use tax-saved amount for prepayment

    **The Catch:**
    - Very few companies allow bonus deferral
    - Need 3-year holding for indexation benefit
    - Only works in 30% tax bracket
    """)

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
        bd_annual_bonus = st.number_input("Annual Bonus (₹)", min_value=50000, max_value=5000000,
                                          value=300000, step=50000, key="bd_bonus")
        bd_tax_slab = st.selectbox("Tax Slab (%)", [20, 30], index=1, key="bd_slab")
        bd_debt_return = st.slider("Debt Fund Return (%)", 6.0, 10.0, 8.0, 0.5, key="bd_return")
        bd_years = st.slider("Investment Period (Years)", 3, 10, 5, key="bd_years",
                            help="Minimum 3 years for indexation")

    # Scenario A: Take bonus, pay tax, prepay
    bd_tax_immediate = bd_annual_bonus * (bd_tax_slab / 100)
    bd_available_prepay = bd_annual_bonus - bd_tax_immediate

    # Scenario B: Defer, invest, withdraw with indexation
    bd_corpus = 0
    for year in range(bd_years):
        bd_corpus = (bd_corpus + bd_annual_bonus) * (1 + bd_debt_return/100)

    # Indexation benefit (simplified: assume 5% inflation)
    bd_inflation = 0.05
    bd_indexed_cost = bd_annual_bonus * bd_years * ((1 + bd_inflation) ** bd_years)
    bd_gains = max(0, bd_corpus - bd_indexed_cost)
    bd_ltcg_tax = bd_gains * 0.20  # 20% with indexation
    bd_corpus_after_tax = bd_corpus - bd_ltcg_tax

    bd_tax_saved = (bd_tax_immediate * bd_years) - bd_ltcg_tax
    bd_extra_corpus = bd_corpus_after_tax - (bd_available_prepay * bd_years)

    with col2:
        st.metric("Immediate Tax (Per Year)", f"₹{bd_tax_immediate:,.0f}",
                 delta=f"{bd_tax_slab}% of ₹{bd_annual_bonus:,.0f}")
        st.metric("Deferred Investment Corpus", f"₹{bd_corpus:,.0f}",
                 help=f"After {bd_years} years @ {bd_debt_return}%")
        st.metric("Tax After Indexation", f"₹{bd_ltcg_tax:,.0f}",
                 delta=f"vs ₹{bd_tax_immediate * bd_years:,.0f} immediate")
        st.metric("Extra Amount Available", f"₹{bd_extra_corpus:,.0f}",
                 help="Additional corpus from deferral strategy")

    st.markdown(f"""
    **Bonus Deferral Strategy Results:**

    **Scenario A (Take bonus immediately):**
    - Annual bonus: ₹{bd_annual_bonus:,.0f}
    - Tax @ {bd_tax_slab}%: ₹{bd_tax_immediate:,.0f}
    - Available for prepayment: ₹{bd_available_prepay:,.0f}/year
    - {bd_years}-year total: ₹{bd_available_prepay * bd_years:,.0f}

    **Scenario B (Defer & invest in debt fund):**
    - Annual bonus invested: ₹{bd_annual_bonus:,.0f}
    - Corpus after {bd_years} years: ₹{bd_corpus:,.0f}
    - LTCG tax (with indexation): ₹{bd_ltcg_tax:,.0f}
    - Available after tax: ₹{bd_corpus_after_tax:,.0f}
    - **Extra amount: ₹{bd_extra_corpus:,.0f}**

    **The Tax Magic:**
    - Immediate tax: ₹{bd_tax_immediate * bd_years:,.0f} over {bd_years} years
    - Deferred tax: ₹{bd_ltcg_tax:,.0f} (with indexation benefit)
    - Tax saved: ₹{bd_tax_saved:,.0f}
    - Plus debt fund returns!

    **Reality Check:**
    - ⚠️ Very few companies allow bonus deferral
    - ⚠️ Need to hold debt fund 3+ years for indexation
    - ⚠️ Post-Budget 2024, indexation might change
    - ✅ Alternative: Take bonus, invest in debt fund anyway

    **Recommended Debt Funds:**
    - Banking & PSU Debt Funds
    - Corporate Bond Funds
    - Dynamic Bond Funds
    - Avoid: Ultra-short/Liquid (no LTCG benefit)
    """)


def show_debt_fund_swp_calculator():
    """Debt Fund SWP Calculator"""
    st.markdown("""
    ### How It Works
    Instead of prepaying loan, invest lumpsum in **debt fund** with **SWP for EMI**.

    **The Strategy:**
    - Have ₹20L lumpsum
    - Option A: Prepay loan immediately
    - Option B: Invest in debt fund, SWP monthly EMI amount
    - If fund return > loan rate → You win!

    **Why It Works:**
    - Debt funds: 7-9% returns
    - Loan interest: 8-9%
    - You maintain liquidity
    - Tax efficient withdrawals
    """)

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
        swp_loan = st.number_input("Loan Amount (₹)", min_value=500000, max_value=100000000,
                                   value=5000000, step=100000, key="swp_loan")
        swp_rate = st.number_input("Loan Interest Rate (%)", min_value=5.0, max_value=15.0,
                                   value=8.5, step=0.1, key="swp_rate")
        swp_lumpsum = st.number_input("Lumpsum Available (₹)", min_value=100000, max_value=10000000,
                                      value=2000000, step=100000, key="swp_lumpsum")
        swp_fund_return = st.slider("Debt Fund Return (%)", 6.0, 11.0, 8.5, 0.5, key="swp_fund_ret")
        swp_tenure = st.slider("Loan Tenure (Years)", 10, 30, 20, key="swp_tenure")

    # Scenario A: Prepay lumpsum
    swp_loan_after_prepay = swp_loan - swp_lumpsum
    swp_monthly_rate = swp_rate / (12 * 100)
    swp_emi = calculate_emi(swp_loan, swp_rate, swp_tenure * 12)

    swp_outstanding_prepay = swp_loan_after_prepay
    swp_interest_prepay = 0
    swp_years_prepay = 0

    while swp_outstanding_prepay > 0.01 and swp_years_prepay < swp_tenure:
        for month in range(12):
            if swp_outstanding_prepay <= 0.01:
                break
            interest = swp_outstanding_prepay * swp_monthly_rate
            principal = swp_emi - interest
            if principal > swp_outstanding_prepay:
                principal = swp_outstanding_prepay
            swp_outstanding_prepay -= principal
            swp_interest_prepay += interest
        swp_years_prepay += 1

    # Scenario B: Invest in debt fund with SWP
    swp_corpus = swp_lumpsum
    swp_monthly_fund_rate = swp_fund_return / (12 * 100)
    swp_outstanding_loan = swp_loan
    swp_interest_loan = 0
    swp_months_elapsed = 0

    while swp_outstanding_loan > 0.01 and swp_months_elapsed < swp_tenure * 12 and swp_corpus > swp_emi:
        # Loan interest
        interest = swp_outstanding_loan * swp_monthly_rate
        principal = swp_emi - interest
        if principal > swp_outstanding_loan:
            principal = swp_outstanding_loan
        swp_outstanding_loan -= principal
        swp_interest_loan += interest

        # Withdraw EMI from debt fund
        swp_corpus -= swp_emi

        # Remaining corpus earns return
        swp_corpus = swp_corpus * (1 + swp_monthly_fund_rate)

        swp_months_elapsed += 1

    swp_years_swp = swp_months_elapsed / 12
    swp_final_corpus = max(0, swp_corpus)

    with col2:
        st.metric("Option A: Prepay Now", f"{swp_years_prepay:.1f} years",
                 delta=f"₹{swp_interest_prepay:,.0f} interest paid")
        st.metric("Option B: Debt Fund SWP", f"{swp_years_swp:.1f} years",
                 delta=f"₹{swp_interest_loan:,.0f} interest paid")
        st.metric("Remaining Corpus (SWP)", f"₹{swp_final_corpus:,.0f}",
                 help="Amount left in debt fund after loan closes")
        st.metric("Net Benefit", f"₹{(swp_interest_prepay - swp_interest_loan + swp_final_corpus):,.0f}",
                 delta="SWP wins" if swp_fund_return >= swp_rate else "Prepay wins")

    st.markdown(f"""
    **Debt Fund SWP Strategy Results:**

    **Option A (Prepay ₹{swp_lumpsum:,.0f} now):**
    - Loan reduced to: ₹{swp_loan_after_prepay:,.0f}
    - EMI: ₹{swp_emi:,.0f}
    - Loan closes in: {swp_years_prepay:.1f} years
    - Total interest paid: ₹{swp_interest_prepay:,.0f}

    **Option B (Invest in debt fund, SWP for EMI):**
    - Initial corpus: ₹{swp_lumpsum:,.0f}
    - Monthly SWP: ₹{swp_emi:,.0f}
    - Fund return: {swp_fund_return}% p.a.
    - Loan closes when: Corpus depleted or loan cleared
    - Years to close: {swp_years_swp:.1f}
    - Interest paid: ₹{swp_interest_loan:,.0f}
    - **Remaining corpus: ₹{swp_final_corpus:,.0f}**

    **The Winner:**
    {'**Option B (SWP) wins!**' if swp_fund_return >= swp_rate else '**Option A (Prepay) wins!**'}

    **When SWP Works:**
    - Debt fund return ≥ Loan rate
    - You need liquidity access
    - Good fund selection (Banking & PSU, Corp Bond)
    - Long tenure (10+ years)

    **When Prepay Works:**
    - Loan rate > Fund return by 1%+
    - You want guaranteed savings
    - Prefer simplicity
    - Psychological benefit of lower principal

    **Tax Efficiency:**
    - SWP withdrawals: Tax-free up to capital portion
    - Only gains taxed (LTCG with indexation if held 3+ years)
    - Better than FD interest (taxed as income)
    """)


def show_salary_arbitrage_calculator():
    """Salary Account Arbitrage Calculator"""
    st.markdown("""
    ### How It Works
    Keep salary in **high-yield account/liquid fund** instead of regular savings account.

    **The Arbitrage:**
    - Regular savings: 3-4% interest
    - Liquid funds: 6-7% returns
    - Difference on ₹2L balance = ₹6K-8K/year
    - Over 20 years = ₹1.2L-2.5L extra!

    **Best Options:**
    - Liquid Mutual Funds (6-7%)
    - IndusInd Bank savings (6-7%)
    - RBL Bank savings (7%)
    - Kotak 811 SuperSaver (6%)
    """)

    st.markdown("---")
    st.markdown("### 🧮 Calculator")

    col1, col2 = st.columns(2)

    with col1:
        sa_avg_balance = st.number_input("Average Monthly Balance (₹)", min_value=50000, max_value=2000000,
                                         value=200000, step=10000, key="sa_balance",
                                         help="Typical balance maintained in salary account")
        sa_regular_rate = st.slider("Regular Savings Rate (%)", 2.5, 4.0, 3.5, 0.1, key="sa_reg_rate")
        sa_high_yield_rate = st.slider("High-Yield Rate (%)", 5.0, 8.0, 7.0, 0.5, key="sa_high_rate",
                                       help="Liquid fund or premium bank rate")
        sa_years = st.slider("Period (Years)", 5, 30, 20, key="sa_years")

    # Calculate earnings
    sa_regular_annual = sa_avg_balance * (sa_regular_rate / 100)
    sa_high_yield_annual = sa_avg_balance * (sa_high_yield_rate / 100)
    sa_annual_diff = sa_high_yield_annual - sa_regular_annual

    sa_total_regular = sa_regular_annual * sa_years
    sa_total_high_yield = sa_high_yield_annual * sa_years
    sa_total_benefit = sa_total_high_yield - sa_total_regular

    # With compounding
    sa_corpus_regular = sa_avg_balance * ((1 + sa_regular_rate/100) ** sa_years)
    sa_corpus_high_yield = sa_avg_balance * ((1 + sa_high_yield_rate/100) ** sa_years)
    sa_compounded_benefit = sa_corpus_high_yield - sa_corpus_regular

    with col2:
        st.metric("Regular Savings Interest", f"₹{sa_regular_annual:,.0f}/year",
                 delta=f"{sa_regular_rate}% on ₹{sa_avg_balance:,.0f}")
        st.metric("High-Yield Interest", f"₹{sa_high_yield_annual:,.0f}/year",
                 delta=f"{sa_high_yield_rate}% on ₹{sa_avg_balance:,.0f}")
        st.metric("Extra Income Per Year", f"₹{sa_annual_diff:,.0f}",
                 delta=f"{((sa_high_yield_rate - sa_regular_rate) / sa_regular_rate * 100):.0f}% more")
        st.metric(f"{sa_years}-Year Total Benefit", f"₹{sa_total_benefit:,.0f}")

    st.markdown(f"""
    **Salary Arbitrage Results:**

    **Your Current Setup:**
    - Average balance: ₹{sa_avg_balance:,.0f}
    - Regular savings rate: {sa_regular_rate}%
    - Annual interest: ₹{sa_regular_annual:,.0f}
    - {sa_years}-year total: ₹{sa_total_regular:,.0f}

    **High-Yield Alternative:**
    - Same balance: ₹{sa_avg_balance:,.0f}
    - High-yield rate: {sa_high_yield_rate}%
    - Annual interest: ₹{sa_high_yield_annual:,.0f}
    - {sa_years}-year total: ₹{sa_total_high_yield:,.0f}

    **Your Benefit:**
    - Extra income per year: ₹{sa_annual_diff:,.0f}
    - {sa_years}-year total benefit: ₹{sa_total_benefit:,.0f}
    - With compounding: ₹{sa_compounded_benefit:,.0f}

    **Best High-Yield Options (2025):**

    **1. Liquid Mutual Funds (Best)**
    - Returns: 6-7% typically
    - Instant redemption up to ₹50K
    - T+1 for larger amounts
    - Tax: LTCG with indexation after 3 years
    - Top funds: HDFC Liquid, ICICI Pru Liquid

    **2. Premium Bank Accounts**
    - IndusInd Indus Delite: 6-7%
    - RBL Bank Savings: 7%
    - Kotak 811 SuperSaver: 6%
    - AU Small Finance: 7%

    **3. Sweep-in FD**
    - Auto-sweep to FD when balance exceeds limit
    - Liquid up to threshold
    - Earn FD rates on surplus

    **Implementation:**
    - Keep 1 month expenses in regular savings
    - Move rest to liquid fund
    - Setup instant redemption
    - Use extra earnings for prepayment!

    **Use This Extra Income For:**
    - Prepay ₹{sa_annual_diff:,.0f}/year to home loan
    - Save {((sa_annual_diff / 40000) * 100):.0f}% of a ₹40K EMI
    - Over {sa_years} years: Significant loan reduction!
    """)
