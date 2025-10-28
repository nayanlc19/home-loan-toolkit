import streamlit as st
import streamlit.components.v1 as components
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import razorpay
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Load environment variables (optional - works without .env file)
try:
    load_dotenv()
except:
    pass

# Admin Configuration - admins get free access to all strategies
ADMIN_EMAILS = [
    "razorpay@razorpay.com",
    "nayanlc19@gmail.com"
]

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID') or os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET') or os.environ.get('RAZORPAY_KEY_SECRET')
PAYMENT_AMOUNT = int(os.getenv('PAYMENT_AMOUNT') or os.environ.get('PAYMENT_AMOUNT') or '9900')
PAYMENT_CURRENCY = os.getenv('PAYMENT_CURRENCY') or os.environ.get('PAYMENT_CURRENCY') or 'INR'

# Initialize Razorpay client
try:
    if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    else:
        razorpay_client = None
        st.warning("Razorpay credentials not found. Payment functionality will be limited.")
except Exception as e:
    razorpay_client = None
    st.error(f"Error initializing Razorpay: {str(e)}")

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_CLIENT_SECRET')
APP_URL = os.getenv('APP_URL') or os.environ.get('APP_URL') or 'http://localhost:8501'
REDIRECT_URI = f"{APP_URL}"

# Paid users database file
PAID_USERS_FILE = 'paid_users.json'

def is_admin(email):
    """Check if the given email is an admin"""
    return email.lower().strip() in [admin.lower() for admin in ADMIN_EMAILS]

def load_paid_users():
    """Load paid users from JSON file"""
    try:
        if os.path.exists(PAID_USERS_FILE):
            with open(PAID_USERS_FILE, 'r') as f:
                return json.load(f)
        return {"paid_users": [], "payments": []}
    except Exception as e:
        st.error(f"Error loading paid users: {e}")
        return {"paid_users": [], "payments": []}

def save_paid_user(email, payment_id, amount):
    """Save a paid user to the database"""
    try:
        data = load_paid_users()

        # Add to paid users list if not already there
        email_lower = email.lower().strip()
        if email_lower not in data["paid_users"]:
            data["paid_users"].append(email_lower)

        # Add payment record
        payment_record = {
            "email": email_lower,
            "payment_id": payment_id,
            "amount": amount,
            "currency": PAYMENT_CURRENCY,
            "timestamp": datetime.now().isoformat()
        }
        data["payments"].append(payment_record)

        # Save to file
        with open(PAID_USERS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return True
    except Exception as e:
        st.error(f"Error saving payment: {e}")
        return False

def check_user_paid(email):
    """Check if user has paid"""
    if not email:
        return False

    email_lower = email.lower().strip()

    # Admins get free access
    if is_admin(email_lower):
        return True

    # Check if user in paid list
    data = load_paid_users()
    return email_lower in data["paid_users"]

def create_razorpay_payment_link(user_email):
    """Create a Razorpay payment link for the user"""
    try:
        if not razorpay_client:
            return None, "Razorpay is not configured"

        payment_data = {
            "amount": PAYMENT_AMOUNT,
            "currency": PAYMENT_CURRENCY,
            "description": "Home Loan Toolkit - Full Access Payment",
            "customer": {
                "name": "Customer",
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
            "callback_url": os.getenv('APP_URL', 'https://home-loan-toolkit.onrender.com'),
            "callback_method": "get"
        }

        payment_link = razorpay_client.payment_link.create(payment_data)
        return payment_link, None
    except Exception as e:
        return None, str(e)

# Page configuration
st.set_page_config(
    page_title="Home Loan Toolkit - Complete Guide",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .category-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        color: white;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .category-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.3);
    }
    .category-card.loans {
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
    }
    .category-card.business {
        background: linear-gradient(135deg, #F57C00 0%, #FFB74D 100%);
    }
    .category-card.investments {
        background: linear-gradient(135deg, #1976D2 0%, #64B5F6 100%);
    }
    .category-card.taxes {
        background: linear-gradient(135deg, #C62828 0%, #EF5350 100%);
    }
    .category-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    .category-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .category-desc {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    .category-count {
        font-size: 0.9rem;
        opacity: 0.8;
        font-style: italic;
    }
    .info-banner {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #1976D2;
        margin: 2rem 0;
    }
    .stats-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin: 1rem 0;
    }
    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
    }
    .stats-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None

def main():
    """Main application entry point"""

    # Check for payment callback parameters in URL
    query_params = st.query_params

    # Check for Google OAuth code callback
    code = query_params.get('code', None)
    if code and GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        try:
            import requests
            # Exchange code for token
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
                    st.session_state.user_picture = id_info.get('picture', '')
                    st.query_params.clear()
                    st.success(f"✅ Signed in as {email_from_google}")
                    st.rerun()
        except Exception as e:
            st.error(f"Sign-in error: {str(e)}")
    if 'razorpay_payment_link_id' in query_params or 'razorpay_payment_id' in query_params:
        st.success("🎉 Payment verification in progress...")
        user_email = st.session_state.get('user_email', '')

        if user_email and check_user_paid(user_email):
            st.balloons()
            st.success(f"✅ Payment successful! Welcome, {user_email}!")
            st.info("You now have full access to all 12 strategies. Click 'Home Loan Strategies' below to get started.")
        else:
            st.info("⏳ Your payment is being verified. This may take a few moments. Please check back shortly or contact support if you don't get access within 10 minutes.")

    # Top navigation with auth
    col1, col2, col3 = st.columns([3, 4, 2])

    with col1:
        st.markdown('<div class="main-header">🏠 Home Loan Toolkit</div>', unsafe_allow_html=True)

    with col3:
        user_email = st.session_state.get('user_email', '')
        if user_email:
            user_name = st.session_state.get('user_name', '')
            st.write(f"👤 {user_name or user_email}")
            if st.button("Sign Out", key="top_signout"):
                st.session_state.clear()
                st.rerun()
        else:
            # Create a button that links to Google OAuth
            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&redirect_uri={APP_URL}&response_type=code&scope=openid%20email%20profile&access_type=offline"
            st.markdown(f'<a href="{auth_url}" target="_self"><button style="background:#4285f4;color:white;border:none;padding:8px 16px;border-radius:4px;cursor:pointer;font-size:14px;">🔐 Sign in with Google</button></a>', unsafe_allow_html=True)

    st.markdown('<div class="sub-header">Everything You Need to Master Your Home Loan Journey</div>', unsafe_allow_html=True)

    # Info banner
    st.markdown("""
    <div class="info-banner">
        <strong>🎯 Your Complete Home Loan Command Center!</strong><br>
        • <strong>12 Payment Strategies:</strong> 1 FREE preview + 11 premium strategies (₹99)<br>
        • <strong>Interactive Calculators:</strong> Real-time calculations for every strategy<br>
        • <strong>Transparent Pricing:</strong> Try 1 free, unlock all 12 for just ₹99
    </div>
    """, unsafe_allow_html=True)

    # Quick stats
    st.markdown("### 📊 What You Get")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">12</div>
            <div class="stats-label">Payment Strategies</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">₹8-25L</div>
            <div class="stats-label">Potential Savings</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stats-box">
            <div class="stats-number">100%</div>
            <div class="stats-label">Secure Payments</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 💰 Home Loan Payment Strategies")

    # FREE STRATEGY - Show the full calculator
    st.markdown("""
    <div class="success-box">
        <strong>🎁 FREE PREVIEW STRATEGY - Try Before You Buy!</strong><br>
        Below is the complete <strong>Bi-Weekly Payment Hack</strong> strategy with full interactive calculator.<br>
        Experience the power of our strategies for FREE. Unlock all 11 remaining strategies for just ₹99!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🆓 Strategy #1: Bi-Weekly Payment Hack (FREE)")

    # Display the bi-weekly calculator inline (avoiding import conflicts)
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

    st.markdown("---")
    st.markdown("### 🔒 11 Premium Strategies - Unlock All for ₹99")

    st.info("💳 **Get full access to all 12 strategies (including advanced calculators & comparison tools) for a one-time payment of ₹99**")

    # Show locked strategies in a grid
    st.markdown("#### 🟢 Low Risk Strategies (3 more locked)")
    lock_col1, lock_col2, lock_col3 = st.columns(3)

    with lock_col1:
        st.markdown("""
        **🔒 2. Step-Up EMI Strategy**
        - Save: ₹18-25L
        - Time saved: 7 years
        - Complexity: ⭐⭐ Moderate

        *Increase EMI with salary hikes*
        """)

    with lock_col2:
        st.markdown("""
        **🔒 3. Tax Refund Amplification**
        - Save: ₹5-8L extra
        - Complexity: ⭐ Simple
        - Best for: 30% tax bracket

        *Compound your tax savings*
        """)

    with lock_col3:
        st.markdown("""
        **🔒 4. Rental Escalation Prepayment**
        - Save: Varies by rent growth
        - Complexity: ⭐ Simple
        - Requirement: Rental property

        *Use rent increases to prepay*
        """)

    st.markdown("#### 🟡 Medium Risk Strategies (4 locked)")
    lock_col4, lock_col5, lock_col6, lock_col7 = st.columns(4)

    with lock_col4:
        st.markdown("""
        **🔒 5. SIP Offset Strategy ⭐**
        - Save: ₹15-30L surplus
        - Best for: Age < 35

        *Invest instead of prepay*
        """)

    with lock_col5:
        st.markdown("""
        **🔒 6. Rental Arbitrage**
        - Save: ₹10-20L
        - Time saved: 5 years

        *Live cheaply, prepay difference*
        """)

    with lock_col6:
        st.markdown("""
        **🔒 7. Credit Card Float**
        - Save: ₹2.6L + cashback
        - Complexity: ⭐⭐ Moderate

        *45-day float strategy*
        """)

    with lock_col7:
        st.markdown("""
        **🔒 8. Reverse FD Laddering**
        - Save: ₹8-15L
        - Time saved: 4 years

        *Forced prepayment discipline*
        """)

    st.markdown("#### 🔴 Advanced Strategies (4 locked)")
    lock_col8, lock_col9, lock_col10, lock_col11 = st.columns(4)

    with lock_col8:
        st.markdown("""
        **🔒 9. Loan Chunking**
        - Save: ₹14L on ₹50L loan
        - Complexity: ⭐⭐⭐ Complex

        *Split into multiple tenures*
        """)

    with lock_col9:
        st.markdown("""
        **🔒 10. Bonus Deferral + Debt Fund**
        - Save: ₹15-25L
        - Complexity: ⭐⭐⭐⭐ Very Complex

        *Tax-efficient prepayment*
        """)

    with lock_col10:
        st.markdown("""
        **🔒 11. Debt Fund SWP**
        - Save: ₹5-10L + liquidity
        - Complexity: ⭐⭐⭐ Complex

        *Maintain emergency fund*
        """)

    with lock_col11:
        st.markdown("""
        **🔒 12. Salary Account Arbitrage**
        - Save: ₹2.8L over 20 years
        - Complexity: ⭐ Simple

        *Earn while you wait (7% vs 3.5%)*
        """)

    st.markdown("---")

    # Pricing section
    col_price1, col_price2, col_price3 = st.columns([1, 2, 1])

    with col_price2:
        st.markdown("""
        <div class="category-card loans" style="text-align: center;">
            <div class="category-icon">🎁</div>
            <div class="category-title">Limited Time Offer</div>
            <div style="font-size: 3rem; font-weight: bold; margin: 1rem 0;">₹99</div>
            <div class="category-desc">One-time payment • Lifetime access • All 12 strategies</div>
            <div class="category-count">✅ Interactive Calculators • ✅ Comparison Tools • ✅ Implementation Guides</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔓 Unlock All Strategies for ₹99 →", key="btn_pay", use_container_width=True, type="primary"):
            st.session_state.selected_category = "checkout"
            st.rerun()

    # Benefits section
    st.markdown("---")
    st.markdown("## ⭐ Why Choose Our Strategies?")

    benefit_col1, benefit_col2, benefit_col3 = st.columns(3)

    with benefit_col1:
        st.markdown("""
        ### 🏆 Proven Results
        - Save ₹8-25 Lakhs in interest
        - Finish loan 3-10 years early
        - Based on real Indian scenarios
        - Tested & verified methods
        """)

    with benefit_col2:
        st.markdown("""
        ### 💳 Interactive Tools
        - Live calculators for each strategy
        - Compare all 12 strategies side-by-side
        - Personalized recommendations
        - Real-time calculations
        """)

    with benefit_col3:
        st.markdown("""
        ### 📊 Complete Guide
        - Step-by-step implementation
        - Risk categorization
        - Requirements checklist
        - Best practices & tips
        """)

    st.markdown("---")
    st.markdown("### 💯 100% Satisfaction Guaranteed")
    st.info("One-time payment of ₹99 gives you lifetime access to all strategies, calculators, and future updates!")

    # Footer
    st.markdown("---")

    # Footer navigation
    footer_col1, footer_col2, footer_col3, footer_col4 = st.columns(4)

    with footer_col1:
        if st.button("📞 Contact Us", use_container_width=True):
            st.session_state.selected_category = "contact"
            st.rerun()
        if st.button("📋 Terms & Conditions", use_container_width=True):
            st.session_state.selected_category = "terms"
            st.rerun()

    with footer_col2:
        if st.button("🔒 Privacy Policy", use_container_width=True):
            st.session_state.selected_category = "privacy"
            st.rerun()
        if st.button("↩️ Refund Policy", use_container_width=True):
            st.session_state.selected_category = "refund"
            st.rerun()

    with footer_col3:
        if st.button("❌ Cancellation Policy", use_container_width=True):
            st.session_state.selected_category = "cancellation"
            st.rerun()
        if st.button("💳 Checkout", use_container_width=True):
            st.session_state.selected_category = "checkout"
            st.rerun()

    with footer_col4:
        if st.button("📦 Shipping Policy", use_container_width=True):
            st.session_state.selected_category = "shipping"
            st.rerun()
        st.markdown("")
        st.markdown("")

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <strong>💡 Tip:</strong> Combine multiple strategies for maximum impact on your home loan!<br>
        Made with ❤️ for smart home loan management | All Rights Reserved © 2025
    </div>
    """, unsafe_allow_html=True)

    # User Login Section (at bottom of page)
    st.markdown("---")
    st.markdown("### 👤 User Login / Admin Access")
    login_col1, login_col2, login_col3 = st.columns([1, 2, 1])

    with login_col2:
        user_email = st.text_input(
            "Email Address",
            value=st.session_state.get('user_email', ''),
            placeholder="Enter your email for access",
            help="Admin emails get free access to all strategies. Regular users need to pay ₹99.",
            key="user_login_email"
        )

        if user_email:
            st.session_state.user_email = user_email
            if is_admin(user_email):
                st.success("👑 Admin Access Granted! You have free access to all 12 strategies.")
            else:
                st.info("💳 Payment of ₹99 required for full access to all strategies.")

def route_to_category():
    """Route to the selected category"""
    if st.session_state.selected_category == "loans":
        # Check if user is admin or has paid
        user_email = st.session_state.get('user_email', '')
        is_admin_user = is_admin(user_email)
        has_paid = check_user_paid(user_email)

        if is_admin_user or has_paid:
            # Import and run home loan strategies
            import home_loan_strategies
            if st.sidebar.button("← Back to Home", key="back_from_loans"):
                st.session_state.selected_category = None
                st.rerun()

            # Show admin badge if admin
            if is_admin_user:
                st.sidebar.success(f"👑 Admin Access: {user_email}")

            home_loan_strategies.main()
        else:
            # Show payment required message
            st.title("🔒 Payment Required")
            st.warning("Please complete payment of ₹99 to access all strategies and calculators.")
            if st.button("Go to Checkout"):
                st.session_state.selected_category = "checkout"
                st.rerun()
            if st.button("← Back to Home"):
                st.session_state.selected_category = None
                st.rerun()

    elif st.session_state.selected_category == "contact":
        show_contact_page()

    elif st.session_state.selected_category == "terms":
        show_terms_page()

    elif st.session_state.selected_category == "privacy":
        show_privacy_policy_page()

    elif st.session_state.selected_category == "refund":
        show_refund_policy_page()

    elif st.session_state.selected_category == "cancellation":
        show_cancellation_policy_page()

    elif st.session_state.selected_category == "shipping":
        show_shipping_policy_page()

    elif st.session_state.selected_category == "checkout":
        show_checkout_page()

    else:
        main()

def show_contact_page():
    """Contact Us page with professional details"""
    st.title("📞 Contact Us")

    # Prominent Contact Display
    st.markdown("""
    <div class="success-box" style="text-align: center; padding: 2rem;">
        <h2 style="margin: 0;">📞 Contact Information</h2>
        <h1 style="color: #2E7D32; margin: 1rem 0;">📧 dmcpexam2020@gmail.com</h1>
        <h1 style="color: #2E7D32; margin: 0.5rem 0;">📱 +91 7021761291</h1>
        <p style="font-size: 1.1rem; margin: 1rem 0;">We typically respond within 24-48 hours</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-banner">
        <strong>Get in Touch</strong><br>
        We're here to help you with your home loan journey. Feel free to reach out!
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📧 Contact Details")
        st.markdown("**Email:** dmcpexam2020@gmail.com")
        st.markdown("**Phone:** +91 7021761291")
        st.markdown("**Response Time:** Within 24-48 hours")
        st.markdown("**Business Hours:** Mon-Fri, 9 AM - 6 PM IST")

    with col2:
        st.markdown("### 🏢 Business Information")
        st.markdown("""
        **Home Loan Toolkit**

        Online Educational Platform
        Providing Home Loan Strategies & Financial Tools
        """)

        st.markdown("### 🔐 Authentication")
        st.markdown("Secure login via Google Auth (powered by Render)")

    st.markdown("---")
    st.markdown("### ✉️ Send Us a Message")

    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        subject = st.text_input("Subject")
        message = st.text_area("Message")

        if st.form_submit_button("Send Message to dmcpexam2020@gmail.com"):
            st.success("Thank you! We'll respond to dmcpexam2020@gmail.com within 24-48 hours.")

    if st.button("← Back to Home"):
        st.session_state.selected_category = None
        st.rerun()

def show_terms_page():
    """Terms & Conditions page"""
    st.title("📋 Terms & Conditions")

    st.markdown("""
    **Last Updated:** October 26, 2025

    ## 1. Acceptance of Terms

    By accessing and using Home Loan Toolkit ("the Service"), you accept and agree to be bound by the terms and conditions of this agreement.

    ## 2. Description of Service

    Home Loan Toolkit provides:
    - Educational content and calculators for home loan payment strategies
    - Guides for setting up payment gateways for rental income collection
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

    ## 8. Third-Party Links

    The Service may contain links to third-party websites. We are not responsible for the content or practices of these external sites.

    ## 9. Changes to Terms

    We reserve the right to modify these terms at any time. Continued use of the Service after changes constitutes acceptance of the modified terms.

    ## 10. Governing Law

    These terms shall be governed by the laws of India.

    ## 11. Contact Information

    For questions about these Terms & Conditions, please contact:
    - Email: dmcpexam2020@gmail.com

    ---

    **By using Home Loan Toolkit, you acknowledge that you have read, understood, and agree to be bound by these Terms & Conditions.**
    """)

    if st.button("← Back to Home"):
        st.session_state.selected_category = None
        st.rerun()

def show_privacy_policy_page():
    """Privacy Policy page"""
    st.title("🔒 Privacy Policy")

    st.markdown("""
    **Last Updated:** October 26, 2025

    ## 1. Introduction

    Home Loan Toolkit ("we", "our", or "us") respects your privacy and is committed to protecting your personal data. This privacy policy explains how we collect, use, and safeguard your information.

    ## 2. Information We Collect

    We may collect the following types of information:

    ### 2.1 Information You Provide
    - Contact details (name, email, phone) when you reach out to us
    - Financial inputs you enter into our calculators (stored locally, not on our servers)

    ### 2.2 Automatically Collected Information
    - Browser type and version
    - Time zone setting and location
    - Operating system and platform
    - Pages visited and time spent on pages

    ### 2.3 Cookies and Tracking
    - Session cookies to maintain your calculator inputs
    - Analytics cookies to understand how visitors use our Service

    ## 3. How We Use Your Information

    We use your information to:
    - Respond to your inquiries and provide customer support
    - Improve our Service based on usage patterns
    - Send important updates about our Service (if you've opted in)
    - Analyze and improve our calculators and tools

    ## 4. Data Storage and Security

    - Calculator inputs are stored locally in your browser and not transmitted to our servers
    - Contact form submissions are encrypted during transmission
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
    - Opt-out of marketing communications
    - Withdraw consent at any time

    ## 7. Third-Party Services

    Our Service may use third-party payment gateways for payment processing. These services have their own privacy policies, and we encourage you to review them.

    ## 8. Children's Privacy

    Our Service is not intended for individuals under 18 years of age. We do not knowingly collect data from children.

    ## 9. International Data Transfers

    Your data is primarily stored and processed in India. If transferred internationally, we ensure appropriate safeguards are in place.

    ## 10. Changes to Privacy Policy

    We may update this policy from time to time. We will notify you of significant changes by posting a notice on our Service.

    ## 11. Contact Us

    For privacy-related questions or to exercise your rights, contact:
    - Email: dmcpexam2020@gmail.com

    ---

    **By using Home Loan Toolkit, you consent to this Privacy Policy.**
    """)

    if st.button("← Back to Home"):
        st.session_state.selected_category = None
        st.rerun()

def show_refund_policy_page():
    """Refund Policy page"""
    st.title("↩️ Refund Policy")

    st.markdown("""
    **Last Updated:** October 26, 2025

    ## No Refund Policy

    **IMPORTANT:** All payments made through our platform are **FINAL and NON-REFUNDABLE**.

    ## Service Nature

    Home Loan Toolkit provides:
    - Digital educational content (delivered instantly)
    - Interactive calculators and tools (immediate access)
    - Payment gateway setup guides (instant download)

    ## Why No Refunds?

    Due to the **digital and instant nature** of our services:
    - Content is delivered immediately upon payment
    - Information cannot be "returned" once accessed
    - Calculators and tools are accessed instantly
    - This prevents misuse of our educational content

    ## Payment Processing

    All payments are processed through secure payment gateways that are:
    - Encrypted and PCI-DSS compliant
    - Support multiple payment methods
    - Fully secure and trusted

    ## Before You Purchase

    Please ensure you:
    - Review service descriptions carefully
    - Understand what you're purchasing
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

    ---

    **By making a payment, you acknowledge and accept this No Refund Policy.**
    """)

    if st.button("← Back to Home"):
        st.session_state.selected_category = None
        st.rerun()

def show_cancellation_policy_page():
    """Cancellation Policy page"""
    st.title("❌ Cancellation Policy")

    st.markdown("""
    **Last Updated:** October 26, 2025

    ## No Cancellation Policy

    **IMPORTANT:** Once a payment is made and content/service is delivered, **NO CANCELLATIONS are allowed**.

    ## Service Nature

    Home Loan Toolkit provides **instant-access digital services**:
    - Educational content delivered immediately
    - Calculator tools activated instantly upon payment
    - Guides available for immediate download

    ## Why No Cancellations?

    Due to the **instant delivery nature** of digital services:
    - Content is accessed immediately after payment
    - Information and tools cannot be "undelivered"
    - All services are non-reversible once accessed
    - Immediate value is provided at the time of payment

    ## Payment Processing

    All payments through our secure payment gateway are:
    - Processed instantly
    - Final and binding
    - Non-cancellable once transaction is complete

    ## Before Making Payment

    Please ensure to:
    - Carefully review what you're purchasing
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

    - Login is managed via **Google Auth** (powered by Render)
    - Secure and encrypted authentication
    - No password storage on our platform

    ## Contact Us

    For questions about this policy, contact:
    - Email: dmcpexam2020@gmail.com

    ---

    **By making a payment, you acknowledge that NO CANCELLATIONS are permitted once service is delivered.**
    """)

    if st.button("← Back to Home"):
        st.session_state.selected_category = None
        st.rerun()

def show_shipping_policy_page():
    """Shipping & Delivery Policy page"""
    st.title("📦 Shipping & Delivery Policy")

    st.markdown("""
    **Last Updated:** October 27, 2025

    ## Digital Product - Instant Delivery

    **IMPORTANT:** Home Loan Toolkit is a **100% DIGITAL PRODUCT**. There is NO physical shipping involved.

    ## How You Get Access

    ### ✅ Instant Access After Payment

    Once your payment is successfully processed:

    1. **Immediate Activation**: Your account is activated instantly
    2. **No Waiting**: Access all 12 strategies immediately
    3. **Instant Delivery**: All calculators, tools, and content available right away
    4. **Email Confirmation**: You'll receive a payment confirmation email

    ### 📧 Access Details

    - **Delivery Method**: Online access through website (https://home-loan-toolkit.onrender.com/)
    - **Delivery Time**: Instant (within seconds of payment confirmation)
    - **Access Duration**: Lifetime access
    - **Downloads**: No downloads required - all tools are web-based

    ## What You Get Access To

    After successful payment, you will immediately get access to:

    - ✅ All 12 Home Loan Payment Strategies
    - ✅ Interactive Calculators for each strategy
    - ✅ Comparison Tools
    - ✅ Implementation Guides
    - ✅ Property Business Tools
    - ✅ All future updates (FREE)

    ## Payment Processing

    - Payment is processed through secure payment gateway
    - Once payment is successful, access is granted automatically
    - No manual activation required
    - No shipping address needed (digital product)

    ## Accessing Your Purchase

    **Steps to Access:**

    1. Complete payment of ₹99 through checkout
    2. Payment gateway processes your payment
    3. You receive instant access to all strategies
    4. Login with your email to access all content
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

    if st.button("← Back to Home"):
        st.session_state.selected_category = None
        st.rerun()

def show_checkout_page():
    """Checkout/Payment page"""
    st.title("💳 Checkout")

    st.markdown("""
    <div class="success-box">
        <strong>🎁 Special Offer - Limited Time!</strong><br>
        Get lifetime access to all 12 home loan payment strategies for just ₹99 (One-time payment)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📦 What's Included")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 💰 12 Strategies
        **Included:**
        - All payment strategies
        - Low, Medium & Advanced risk
        - Detailed implementation guides
        - Risk categorization
        """)

    with col2:
        st.markdown("""
        #### 🧮 Interactive Calculators
        **Included:**
        - Live calculations
        - Comparison tools
        - Personalized recommendations
        - Real-time results
        """)

    with col3:
        st.markdown("""
        #### 📚 Lifetime Access
        **Included:**
        - One-time payment
        - Lifetime access
        - Future updates FREE
        - All calculators
        """)

    st.markdown("---")
    st.markdown("### 💳 Payment Methods")

    st.markdown("""
    Our secure payment gateway supports:
    - 💳 **Credit & Debit Cards** - All major cards accepted
    - 📱 **UPI** - Google Pay, PhonePe, Paytm, and more
    - 🏦 **Net Banking** - All major Indian banks
    - 💰 **Wallets** - Multiple wallet options
    - 💳 **EMI Options** - Available for select cards

    🔒 **Security Features:**
    - ✅ PCI DSS Compliant
    - ✅ 256-bit SSL Encryption
    - ✅ Bank-grade Security
    - ✅ Compliant with Indian banking regulations
    """)

    st.markdown("---")
    st.markdown("### 💰 Order Summary")

    # Pricing box
    col_summary1, col_summary2, col_summary3 = st.columns([1, 2, 1])

    with col_summary2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <h3 style="text-align: center;">Home Loan Toolkit - Full Access</h3>
            <hr>
            <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                <span>12 Payment Strategies</span>
                <span><strong>Included</strong></span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                <span>Interactive Calculators</span>
                <span><strong>Included</strong></span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                <span>Lifetime Access</span>
                <span><strong>Included</strong></span>
            </div>
            <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                <span>Future Updates</span>
                <span><strong>FREE</strong></span>
            </div>
            <hr>
            <div style="display: flex; justify-content: space-between; font-size: 1.5rem; font-weight: bold; margin-top: 1.5rem;">
                <span>Total Amount:</span>
                <span style="color: #2E7D32;">₹99</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # Get user email
        user_email = st.session_state.get('user_email', '')

        if not user_email:
            # User not signed in - prompt to sign in
            st.warning("⚠️ Please sign in with Google to continue with payment.")
            st.info("Click the **'Sign in with Google'** button at the top-right of this page to proceed.")

            if st.button("🔙 Back to Home", use_container_width=True):
                st.session_state.selected_category = None
                st.rerun()
        elif check_user_paid(user_email):
            st.success(f"✅ Payment already completed for {user_email}! You have full access to all strategies.")
            if st.button("🚀 Access All Strategies", use_container_width=True, type="primary"):
                st.session_state.selected_category = "loans"
                st.rerun()
        else:
            # Payment button
            if st.button("💳 Proceed to Secure Payment", use_container_width=True, type="primary"):
                with st.spinner("Creating your secure payment link..."):
                    payment_link, error = create_razorpay_payment_link(user_email)

                    if payment_link:
                        st.success("✅ Payment link created successfully!")
                        st.markdown(f"""
                        ### 🔗 Your Secure Payment Link

                        Click the button below to complete your payment:
                        """)

                        # Display payment link details
                        st.info(f"""
                        **Payment Details:**
                        - Amount: ₹{PAYMENT_AMOUNT / 100:.2f}
                        - Email: {user_email}
                        - Payment Link ID: {payment_link.get('id', 'N/A')}
                        """)

                        # Create a clickable link
                        payment_url = payment_link.get('short_url', '')
                        if payment_url:
                            st.markdown(f"""
                            <div style="text-align: center; margin: 2rem 0;">
                                <a href="{payment_url}" target="_blank">
                                    <button style="
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white;
                                        padding: 1rem 3rem;
                                        font-size: 1.2rem;
                                        border: none;
                                        border-radius: 10px;
                                        cursor: pointer;
                                        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                                    ">
                                        💳 Pay ₹99 Now (Secure Razorpay)
                                    </button>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"**Direct Link:** {payment_url}")

                        st.markdown("""
                        ---
                        **After Payment:**
                        1. Complete the payment on Razorpay's secure page
                        2. You'll be redirected back to this website
                        3. Refresh this page and access all strategies

                        **Note:** Payment may take a few seconds to verify. If you don't get immediate access, please refresh the page or contact support.
                        """)
                    else:
                        st.error(f"❌ Error creating payment link: {error}")
                        st.info("Please contact dmcpexam2020@gmail.com for assistance.")

    st.markdown("---")
    st.markdown("### 🔒 Security & Trust")

    sec_col1, sec_col2, sec_col3 = st.columns(3)

    with sec_col1:
        st.markdown("""
        **✅ Secure Payments**
        - PCI DSS Compliant
        - 256-bit SSL Encryption
        - No card details stored
        """)

    with sec_col2:
        st.markdown("""
        **✅ Instant Access**
        - Immediate delivery
        - Secure transactions
        - Email confirmation
        """)

    with sec_col3:
        st.markdown("""
        **✅ Support**
        - Email: dmcpexam2020@gmail.com
        - Response within 24-48 hours
        - Google Auth login
        """)

    if st.button("🏠 Return to Home"):
        st.session_state.selected_category = None
        st.rerun()

if __name__ == "__main__":
    route_to_category()
