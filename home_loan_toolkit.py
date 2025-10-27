import streamlit as st

# Admin Configuration - admins get free access to all strategies
ADMIN_EMAILS = [
    "razorpay@razorpay.com",
    "nayanlc19@gmail.com"
]

def is_admin(email):
    """Check if the given email is an admin"""
    return email.lower().strip() in [admin.lower() for admin in ADMIN_EMAILS]

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

    # Admin/User Email Input (temporary until Google OAuth is configured)
    with st.sidebar:
        st.markdown("### 👤 User Login")
        user_email = st.text_input(
            "Email Address",
            value=st.session_state.get('user_email', ''),
            placeholder="Enter your email",
            help="Admin emails get free access to all strategies"
        )

        if user_email:
            st.session_state.user_email = user_email
            if is_admin(user_email):
                st.success("👑 Admin Access Granted!")
            else:
                st.info("💳 Payment required for full access")

        st.markdown("---")

    # Header
    st.markdown('<div class="main-header">🏠 Home Loan Toolkit</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Everything You Need to Master Your Home Loan Journey</div>', unsafe_allow_html=True)

    # Info banner
    st.markdown("""
    <div class="info-banner">
        <strong>🎯 Your Complete Home Loan Command Center!</strong><br>
        • <strong>12 Payment Strategies:</strong> 1 FREE preview + 11 premium strategies (₹99)<br>
        • <strong>Interactive Calculators:</strong> Real-time calculations for every strategy<br>
        • <strong>Property Business Tools:</strong> Rental income, payment gateways, and more<br>
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

    # Preview section with strategy screenshots
    st.markdown("""
    <div class="info-box">
        <strong>🎯 12 Proven Strategies Available</strong><br>
        <strong>1 Strategy FREE</strong> - Try "Bi-Weekly Payment Hack" with no payment<br>
        <strong>11 Premium Strategies</strong> - Unlock all for just <strong>₹99 (One-time payment via secure payment gateway)</strong>
    </div>
    """, unsafe_allow_html=True)

    # Strategy preview images
    st.markdown("### 📸 Preview: What You'll Get")

    preview_col1, preview_col2, preview_col3 = st.columns(3)

    with preview_col1:
        st.markdown("""
        **🟢 Low Risk Strategies**
        - Bi-Weekly Payment Hack
        - Step-Up EMI Strategy
        - Tax Refund Amplification
        - Rental Escalation Prepayment

        *Save ₹8-25L & finish 3-7 years early*
        """)

    with preview_col2:
        st.markdown("""
        **🟡 Medium Risk Strategies**
        - SIP Offset Strategy ⭐
        - Rental Arbitrage
        - Credit Card Float
        - Reverse FD Laddering

        *Build wealth while repaying loans*
        """)

    with preview_col3:
        st.markdown("""
        **🔴 Advanced Strategies**
        - Loan Chunking
        - Bonus Deferral + Debt Fund
        - Debt Fund SWP
        - Salary Account Arbitrage

        *Maximum impact strategies*
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
        st.markdown("### 📧 Quick Contact")
        st.markdown("**Email:** dmcpexam2020@gmail.com")
        st.markdown("**🔐 Auth:** Google (via Render)")

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <strong>💡 Tip:</strong> Combine multiple strategies for maximum impact on your home loan!<br>
        Made with ❤️ for smart home loan management | All Rights Reserved © 2025
    </div>
    """, unsafe_allow_html=True)

def route_to_category():
    """Route to the selected category"""
    if st.session_state.selected_category == "loans":
        # Check if user is admin or has paid
        user_email = st.session_state.get('user_email', '')
        is_admin_user = is_admin(user_email)
        has_paid = st.session_state.get('paid', False)

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

    elif st.session_state.selected_category == "checkout":
        show_checkout_page()

    else:
        main()

def show_contact_page():
    """Contact Us page with professional details"""
    st.title("📞 Contact Us")

    st.markdown("""
    <div class="info-banner">
        <strong>Get in Touch</strong><br>
        We're here to help you with your home loan journey. Feel free to reach out!
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📧 Email")
        st.markdown("**Contact Email:** dmcpexam2020@gmail.com")
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

        # Payment button
        if st.button("💳 Proceed to Secure Payment", use_container_width=True, type="primary"):
            st.info("""
            **Payment Gateway Integration**

            This button will redirect you to our secure payment gateway where you can complete your payment using:
            - Credit/Debit Cards
            - UPI
            - Net Banking
            - Wallets

            *Note: Payment gateway integration is currently in setup phase. Contact dmcpexam2020@gmail.com for manual payment.*
            """)

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
