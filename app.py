import gradio as gr
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import razorpay
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
import secrets
from policy_pages import (CONTACT_PAGE, TERMS_PAGE, PRIVACY_PAGE,
                          REFUND_PAGE, CANCELLATION_PAGE, SHIPPING_PAGE)

# Load environment variables
try:
    load_dotenv()
except:
    pass

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

# Initialize Razorpay client
try:
    if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    else:
        razorpay_client = None
except Exception as e:
    razorpay_client = None
    print(f"Error initializing Razorpay: {str(e)}")

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_CLIENT_SECRET')
APP_URL = os.getenv('APP_URL') or os.environ.get('APP_URL') or 'http://localhost:7860'
REDIRECT_URI = f"{APP_URL}/login/callback"

# Paid users database file
PAID_USERS_FILE = 'paid_users.json'

# Session management (simple in-memory store for demo)
user_sessions = {}

def is_admin(email):
    """Check if the given email is an admin"""
    if not email:
        return False
    return email.lower().strip() in [admin.lower() for admin in ADMIN_EMAILS]

def load_paid_users():
    """Load paid users from JSON file"""
    try:
        if os.path.exists(PAID_USERS_FILE):
            with open(PAID_USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"paid_users": [], "payments": []}
    except Exception as e:
        print(f"Error loading paid users: {e}")
        return {"paid_users": [], "payments": []}

def save_paid_user(email, payment_id, amount):
    """Save a paid user to the database"""
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

        with open(PAID_USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return True
    except Exception as e:
        print(f"Error saving payment: {e}")
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
            "callback_url": APP_URL,
            "callback_method": "get"
        }

        payment_link = razorpay_client.payment_link.create(payment_data)
        return payment_link, None
    except Exception as e:
        return None, str(e)

def get_google_auth_url():
    """Generate Google OAuth URL"""
    if not GOOGLE_CLIENT_ID:
        return None

    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline'
    }

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return auth_url

# ===== CALCULATOR FUNCTIONS =====

def calculate_biweekly_strategy(loan_amount, interest_rate, tenure_years):
    """Calculate Bi-Weekly Payment Hack strategy"""
    months = tenure_years * 12
    monthly_rate = interest_rate / (12 * 100)

    # Calculate regular EMI
    emi = loan_amount * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
    total_regular = emi * months
    interest_regular = total_regular - loan_amount

    # Simulate bi-weekly payment (13 EMIs per year)
    outstanding = loan_amount
    total_interest_biweekly = 0
    months_elapsed = 0

    while outstanding > 0 and months_elapsed < months:
        annual_payment = emi * 13
        for month in range(12):
            if outstanding <= 0:
                break
            interest = outstanding * monthly_rate
            principal = (annual_payment / 12) - interest
            outstanding -= principal
            total_interest_biweekly += interest
            months_elapsed += 1

    savings = interest_regular - total_interest_biweekly
    time_saved = months - months_elapsed

    return {
        "emi": emi,
        "biweekly_payment": emi / 2,
        "savings": savings,
        "time_saved_months": time_saved,
        "time_saved_years": time_saved / 12,
        "interest_regular": interest_regular,
        "interest_biweekly": total_interest_biweekly,
        "savings_percent": (savings / interest_regular) * 100
    }

def format_currency(amount):
    """Format amount as Indian currency"""
    return f"₹{amount:,.0f}"

# ===== GRADIO INTERFACE COMPONENTS =====

def create_home_tab():
    """Create the home/welcome tab"""
    with gr.Column():
        gr.Markdown("""
        # 🏠 Home Loan Toolkit - Complete Guide
        ## Everything You Need to Master Your Home Loan Journey

        ---

        ### 🎯 Your Complete Home Loan Command Center!

        - **12 Payment Strategies:** 1 FREE preview + 11 premium strategies (₹99)
        - **Interactive Calculators:** Real-time calculations for every strategy
        - **Transparent Pricing:** Try 1 free, unlock all 12 for just ₹99

        ---

        ### 📊 What You Get
        """)

        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ### 12
                **Payment Strategies**
                """)
            with gr.Column():
                gr.Markdown("""
                ### ₹8-25L
                **Potential Savings**
                """)
            with gr.Column():
                gr.Markdown("""
                ### 100%
                **Secure Payments**
                """)

        gr.Markdown("---")

        gr.Markdown("""
        ## 💰 Home Loan Payment Strategies

        ### 🎁 FREE PREVIEW STRATEGY - Try Before You Buy!

        Below is the complete **Bi-Weekly Payment Hack** strategy with full interactive calculator.
        Experience the power of our strategies for FREE. Unlock all 11 remaining strategies for just ₹99!

        ---

        ### Why Choose Our Strategies?

        #### 🏆 Proven Results
        - Save ₹8-25 Lakhs in interest
        - Finish loan 3-10 years early
        - Based on real Indian scenarios
        - Tested & verified methods

        #### 💳 Interactive Tools
        - Live calculators for each strategy
        - Compare all 12 strategies side-by-side
        - Personalized recommendations
        - Real-time calculations

        #### 📊 Complete Guide
        - Step-by-step implementation
        - Risk categorization
        - Requirements checklist
        - Best practices & tips

        ---

        ### 💯 100% Satisfaction Guaranteed
        One-time payment of ₹99 gives you lifetime access to all strategies, calculators, and future updates!
        """)

def create_free_strategy_tab():
    """Create the free strategy (Bi-Weekly) tab"""
    with gr.Column():
        gr.Markdown("""
        # 🆓 Strategy #1: Bi-Weekly Payment Hack (FREE)

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

        ---

        ## 🧮 Interactive Calculator
        """)

        with gr.Row():
            with gr.Column():
                loan_input = gr.Number(label="Loan Amount (₹)", value=5000000, minimum=500000, maximum=100000000)
                rate_input = gr.Number(label="Interest Rate (%)", value=8.5, minimum=5.0, maximum=15.0)
                tenure_input = gr.Slider(label="Tenure (Years)", minimum=5, maximum=30, value=20, step=1)
                calculate_btn = gr.Button("📊 Calculate Savings", variant="primary")

            with gr.Column():
                results_output = gr.Markdown("")

        def calculate_and_display(loan, rate, tenure):
            result = calculate_biweekly_strategy(loan, rate, tenure)

            output = f"""
### Results

**Regular Monthly EMI:** {format_currency(result['emi'])}

**Bi-Weekly Payment:** {format_currency(result['biweekly_payment'])} *(Pay this every 2 weeks)*

**Interest Saved:** {format_currency(result['savings'])} *({result['savings_percent']:.1f}% savings)*

**Time Saved:** {result['time_saved_years']:.1f} years *({result['time_saved_months']:.0f} months)*

---

### Your Detailed Results:

- **Regular EMI:** {format_currency(result['emi'])} × {int(tenure * 12)} months = {format_currency(result['interest_regular'])} interest
- **Bi-weekly:** Pay {format_currency(result['biweekly_payment'])} every 2 weeks
- **💰 Save {format_currency(result['savings'])} in interest + Close loan {result['time_saved_years']:.1f} years early!**

---

### Implementation (India-specific):

- Most banks don't support bi-weekly auto-debit
- **Workaround:** Manually prepay {format_currency(result['emi'])} once a year (mimics 13th EMI)
- Or set up automated prepayment every 6 months ({format_currency(result['biweekly_payment'])} × 2)
            """
            return output

        calculate_btn.click(
            fn=calculate_and_display,
            inputs=[loan_input, rate_input, tenure_input],
            outputs=results_output
        )

        gr.Markdown("""
        ---

        ### 🔒 Want More Strategies?

        **Unlock all 11 premium strategies for just ₹99!**

        Go to the **Checkout** tab to get full access to all strategies and calculators.
        """)

def create_premium_strategies_tab(user_email):
    """Create the premium strategies tab"""
    has_access = check_user_paid(user_email)

    with gr.Column():
        if not has_access:
            gr.Markdown("""
            # 🔒 Premium Strategies (Payment Required)

            ### Get Full Access for ₹99

            Sign in with Google and complete payment to unlock all 11 premium strategies!

            ---

            ### What's Locked:

            #### 🟢 Low Risk Strategies (3 strategies)

            1. **Step-Up EMI Strategy** - Save: ₹18-25L, Time saved: 7 years
            2. **Tax Refund Amplification** - Save: ₹5-8L extra
            3. **Rental Escalation Prepayment** - Save: Varies by rent growth

            #### 🟡 Medium Risk Strategies (4 strategies)

            4. **SIP Offset Strategy** ⭐ - Save: ₹15-30L surplus
            5. **Rental Arbitrage** - Save: ₹10-20L, Time saved: 5 years
            6. **Credit Card Float** - Save: ₹2.6L + cashback
            7. **Reverse FD Laddering** - Save: ₹8-15L, Time saved: 4 years

            #### 🔴 Advanced Strategies (4 strategies)

            8. **Loan Chunking** - Save: ₹14L on ₹50L loan
            9. **Bonus Deferral + Debt Fund** - Save: ₹15-25L
            10. **Debt Fund SWP** - Save: ₹5-10L + liquidity
            11. **Salary Account Arbitrage** - Save: ₹2.8L over 20 years

            ---

            ### 💳 Unlock All Strategies

            Go to the **Checkout** tab to complete payment and get instant access!
            """)
        else:
            gr.Markdown(f"""
            # ✅ Premium Strategies (Full Access)

            Welcome back, **{user_email}**! You have full access to all premium strategies.

            {"👑 **Admin Access Granted**" if is_admin(user_email) else "✅ **Payment Verified**"}

            ---

            ## All 11 Premium Strategies

            *Note: Full calculators and detailed guides for each strategy will be implemented in the next update.*

            ### 🟢 Low Risk Strategies

            1. **Step-Up EMI Strategy** - Save: ₹18-25L, Time saved: 7 years
            2. **Tax Refund Amplification** - Save: ₹5-8L extra
            3. **Rental Escalation Prepayment** - Save: Varies by rent growth

            ### 🟡 Medium Risk Strategies

            4. **SIP Offset Strategy** ⭐ - Save: ₹15-30L surplus
            5. **Rental Arbitrage** - Save: ₹10-20L, Time saved: 5 years
            6. **Credit Card Float** - Save: ₹2.6L + cashback
            7. **Reverse FD Laddering** - Save: ₹8-15L, Time saved: 4 years

            ### 🔴 Advanced Strategies

            8. **Loan Chunking** - Save: ₹14L on ₹50L loan
            9. **Bonus Deferral + Debt Fund** - Save: ₹15-25L
            10. **Debt Fund SWP** - Save: ₹5-10L + liquidity
            11. **Salary Account Arbitrage** - Save: ₹2.8L over 20 years

            ---

            *Interactive calculators for all premium strategies coming soon!*
            """)

def create_checkout_tab(user_email):
    """Create the checkout/payment tab"""
    with gr.Column():
        if not user_email:
            gr.Markdown("""
            # 💳 Checkout

            ### ⚠️ Please Sign In First

            You need to sign in with Google before making a payment.

            Click the **"Sign in with Google"** button at the top of the page.
            """)
        elif check_user_paid(user_email):
            gr.Markdown(f"""
            # ✅ Payment Already Completed

            **{user_email}** - You already have full access!

            Go to the **Premium Strategies** tab to access all content.
            """)
        else:
            gr.Markdown("""
            # 💳 Checkout - Get Full Access

            ### 🎁 Special Offer - Limited Time!
            Get lifetime access to all 12 home loan payment strategies for just **₹99** (One-time payment)

            ---

            ### 📦 What's Included

            - ✅ All 12 payment strategies
            - ✅ Interactive calculators
            - ✅ Lifetime access
            - ✅ Future updates FREE

            ---

            ### 💰 Order Summary

            **Home Loan Toolkit - Full Access**

            - 12 Payment Strategies: Included
            - Interactive Calculators: Included
            - Lifetime Access: Included
            - Future Updates: FREE

            **Total Amount: ₹99**

            ---
            """)

            payment_btn = gr.Button("💳 Proceed to Secure Payment (Razorpay)", variant="primary", size="lg")
            payment_output = gr.Markdown("")

            def create_payment(email):
                payment_link, error = create_razorpay_payment_link(email)

                if payment_link:
                    payment_url = payment_link.get('short_url', '')
                    return f"""
### ✅ Payment Link Created Successfully!

**Payment Details:**
- Amount: ₹{PAYMENT_AMOUNT / 100:.2f}
- Email: {email}
- Payment Link ID: {payment_link.get('id', 'N/A')}

### 🔗 Click the link below to complete payment:

[**💳 Pay ₹99 Now (Secure Razorpay)**]({payment_url})

**Direct Link:** {payment_url}

---

**After Payment:**
1. Complete the payment on Razorpay's secure page
2. You'll be redirected back to this website
3. Refresh this page and access all strategies

**Note:** Payment may take a few seconds to verify. If you don't get immediate access, please refresh the page or contact support.
                    """
                else:
                    return f"❌ **Error creating payment link:** {error}\n\nPlease contact dmcpexam2020@gmail.com for assistance."

            payment_btn.click(
                fn=lambda: create_payment(user_email),
                inputs=None,
                outputs=payment_output
            )

            gr.Markdown("""
            ---

            ### 🔒 Security & Trust

            - ✅ **Secure Payments:** PCI DSS Compliant, 256-bit SSL Encryption
            - ✅ **Instant Access:** Immediate delivery after payment
            - ✅ **Support:** Email: dmcpexam2020@gmail.com | Response within 24-48 hours
            """)

def create_main_interface():
    """Create the main Gradio interface"""

    # Economist-style theme with serif fonts
    economist_theme = gr.themes.Base(
        primary_hue="red",
        secondary_hue="gray"
    ).set(
        body_background_fill="#ffffff",
        body_text_color="#1a1a1a",
        body_text_size="*text_lg",
        button_primary_background_fill="#e3120b",
        button_primary_background_fill_hover="#c10f09",
        button_primary_text_color="#ffffff"
    )

    with gr.Blocks(title="Home Loan Toolkit", theme=economist_theme, css="""
        .gradio-container {
            font-family: Georgia, 'Times New Roman', serif !important;
            max-width: 1200px !important;
            margin: auto !important;
        }
        h1, h2, h3 {
            font-family: Georgia, 'Times New Roman', serif !important;
            font-weight: 600 !important;
            color: #1a1a1a !important;
        }
        .markdown-text {
            font-family: Georgia, 'Times New Roman', serif !important;
            font-size: 17px !important;
            line-height: 1.6 !important;
            color: #1a1a1a !important;
        }
    """) as app:
        # Session state for user
        user_email_state = gr.State("")

        # Header with auth buttons
        with gr.Row():
            gr.Markdown("# 🏠 Home Loan Toolkit")
            with gr.Column(scale=1):
                auth_status = gr.Markdown("**Not signed in**")
                with gr.Row():
                    signin_btn = gr.Button("🔐 Sign in with Google", size="sm", variant="primary")
                    signout_btn = gr.Button("Sign Out", size="sm", visible=False)

        gr.Markdown("---")

        # Main tabs
        with gr.Tabs():
            with gr.Tab("🏠 Home"):
                create_home_tab()

            with gr.Tab("🆓 Free Strategy"):
                create_free_strategy_tab()

            with gr.Tab("🔒 Premium Strategies"):
                premium_tab = gr.Column()

            with gr.Tab("💳 Checkout"):
                checkout_tab = gr.Column()

            with gr.Tab("📞 Contact"):
                gr.Markdown(CONTACT_PAGE)

            with gr.Tab("📋 Terms & Conditions"):
                gr.Markdown(TERMS_PAGE)

            with gr.Tab("🔒 Privacy Policy"):
                gr.Markdown(PRIVACY_PAGE)

            with gr.Tab("↩️ Refund Policy"):
                gr.Markdown(REFUND_PAGE)

            with gr.Tab("❌ Cancellation Policy"):
                gr.Markdown(CANCELLATION_PAGE)

            with gr.Tab("📦 Shipping & Delivery"):
                gr.Markdown(SHIPPING_PAGE)

        # Footer
        gr.Markdown("""
        ---

        **💡 Tip:** Combine multiple strategies for maximum impact on your home loan!

        Made with ❤️ for smart home loan management | All Rights Reserved © 2025

        **Contact:** dmcpexam2020@gmail.com | +91 7021761291
        """)

        # Auth button handlers
        def handle_signin():
            auth_url = get_google_auth_url()
            if auth_url:
                return f"**Click here to sign in:** [Sign in with Google]({auth_url})"
            else:
                return "**Error:** Google OAuth not configured"

        signin_btn.click(fn=handle_signin, outputs=auth_status)

        def handle_signout():
            return "", "**Not signed in**", gr.Button(visible=True), gr.Button(visible=False)

        signout_btn.click(
            fn=handle_signout,
            outputs=[user_email_state, auth_status, signin_btn, signout_btn]
        )

    return app

# ===== MAIN ENTRY POINT =====

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app = create_main_interface()

    print(f"Starting Home Loan Toolkit on port {port}")
    print(f"Admin emails: {', '.join(ADMIN_EMAILS)}")
    print(f"Google OAuth configured: {bool(GOOGLE_CLIENT_ID)}")
    print(f"Razorpay configured: {bool(razorpay_client)}")

    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False
    )
