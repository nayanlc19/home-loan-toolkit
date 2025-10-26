import streamlit as st
import pandas as pd

# Custom CSS for business guides
st.markdown("""
<style>
    .guide-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #F57C00;
        text-align: center;
        margin-bottom: 1rem;
    }
    .guide-card {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .guide-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    .guide-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #E65100;
        margin-bottom: 0.5rem;
    }
    .guide-desc {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .guide-meta {
        font-size: 0.9rem;
        color: #888;
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
    .video-badge {
        display: inline-block;
        background: #FF0000;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        font-size: 0.9rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_guide' not in st.session_state:
    st.session_state.selected_guide = None

# Guide definitions
GUIDES = {
    "razorpay_approval": {
        "name": "Razorpay for Rental Payments",
        "tagline": "Setup Online Payment Collection for Rent - 100% Approval Guaranteed",
        "difficulty": "⭐⭐ Moderate",
        "time": "2-3 days",
        "success_rate": "100% (if followed correctly)",
        "icon": "💳"
    }
}

def main():
    """Main entry point for business setup guides"""

    st.markdown('<div class="guide-header">🏘️ Property & Rental Business Guides</div>', unsafe_allow_html=True)

    # Check if a specific guide is selected
    if st.session_state.selected_guide:
        show_guide_detail(st.session_state.selected_guide)
    else:
        show_guides_landing()

def show_guides_landing():
    """Show landing page with all guides"""

    st.markdown("""
    <div class="info-box">
        <strong>🎯 Property Business Setup Resources</strong><br>
        Whether you're renting out your property or running a rental business, these guides help you set up
        professional payment collection, maximize rental income, and manage your property business efficiently.
        Perfect for homeowners with rental income or property investors.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📚 Featured Guide")

    # Display guide cards
    for guide_id, guide in GUIDES.items():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"""
            <div class="guide-card">
                <div class="guide-title">{guide['icon']} {guide['name']}</div>
                <div class="guide-desc">{guide['tagline']}</div>
                <div class="guide-meta">
                    ⏱️ Time: {guide['time']} | 🎯 Difficulty: {guide['difficulty']} | ✅ Success: {guide['success_rate']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("Read Complete Guide →", key=f"btn_{guide_id}", use_container_width=True, type="primary"):
                st.session_state.selected_guide = guide_id
                st.rerun()

    # Quick tips section
    st.markdown("---")
    st.markdown("### 💡 Quick Tips for Property Owners")

    tip_col1, tip_col2, tip_col3 = st.columns(3)

    with tip_col1:
        st.markdown("""
        <div class="success-box">
            <strong>✅ Automate Rent Collection</strong><br>
            Use payment gateways like Razorpay for automatic monthly rent collection with UPI AutoPay
        </div>
        """, unsafe_allow_html=True)

    with tip_col2:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Tax Implications</strong><br>
            Rental income is taxable - maintain proper records and claim eligible deductions
        </div>
        """, unsafe_allow_html=True)

    with tip_col3:
        st.markdown("""
        <div class="info-box">
            <strong>🎯 Pro Tip</strong><br>
            Use rental arbitrage strategy from the Payment Strategies section to prepay your home loan faster
        </div>
        """, unsafe_allow_html=True)

def show_guide_detail(guide_id):
    """Show detailed guide based on ID"""

    if guide_id == "razorpay_approval":
        show_razorpay_approval_guide()
    else:
        st.info("This guide is coming soon!")

    if st.button("← Back to All Guides", key="back_to_guides"):
        st.session_state.selected_guide = None
        st.rerun()

def show_razorpay_approval_guide():
    """Complete Razorpay approval guide"""

    st.title("💳 Razorpay for Rental Payment Collection")

    st.markdown("""
    <div class="video-badge">📺 Based on YouTube Video Guide</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="success-box">
        <strong>✅ 100% Success Rate for Property Owners</strong><br>
        This guide helps landlords and property owners set up professional rent collection through Razorpay.
        Get approval in ~2 hours after following these steps - even without GST or company registration!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Introduction
    st.markdown("## 📖 Overview")
    st.markdown("""
    Perfect for **property owners wanting to collect rent online** through UPI, cards, or automatic payments.
    This guide will help you get your **Razorpay account approved** even **without GST or company certificate**.

    **Why Razorpay for Rent Collection?**
    - Accept UPI, Cards, Net Banking - all in one place
    - UPI AutoPay for automatic monthly rent collection
    - Professional payment links and invoices
    - Instant settlements to your bank account
    - Track all rental payments in one dashboard

    **Key Success Factors:**
    - Professional website (mandatory - can be simple property listing page)
    - Proper policy pages (customized for rental business)
    - Matching business category ("Property Rental/Real Estate")
    - Professional contact details
    - Being prepared for verification call
    """)

    # Step 1: Professional Website
    st.markdown("---")
    st.markdown("""
    <div class="step-card">
        <span class="step-number">1</span>
        <div class="step-title">Professional Website is MANDATORY</div>
        <div class="step-content">
            <strong>Why it matters:</strong> Applying without a website significantly increases rejection chances.<br><br>

            <strong>Website Requirements:</strong><br>
            ✅ Professional-looking design (doesn't need to be fancy, but must be clean)<br>
            ✅ Clear and singular theme - focus on ONE type of product/service<br>
            ✅ Working navigation and pages<br>
            ✅ Mobile-responsive design<br>
            ✅ Fast loading speed<br><br>

            <strong>❌ Common Mistakes to Avoid:</strong><br>
            • Listing multiple conflicting products (e.g., e-commerce + courses + services)<br>
            • Generic template websites without customization<br>
            • Broken links or incomplete pages<br>
            • Using free subdomain (use custom domain like yourbusiness.com)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Step 2: Essential Pages
    st.markdown("""
    <div class="step-card">
        <span class="step-number">2</span>
        <div class="step-title">Essential Website Pages & Policies</div>
        <div class="step-content">
            <strong>Mandatory Pages (All Required):</strong><br><br>

            <strong>📞 Contact Us Page</strong><br>
            Must include:<br>
            • Working phone number (will be verified via call)<br>
            • Professional domain-based email (contact@yourdomain.com, NOT Gmail)<br>
            • Physical address matching your KYC documents (Aadhaar/DL)<br>
            • Optional: Business hours, social media links<br><br>

            <strong>📋 Terms & Conditions</strong><br>
            • Customize for YOUR specific product/service<br>
            • Include your business name and contact details<br>
            • Cover user agreements, limitations, and dispute resolution<br><br>

            <strong>🔒 Privacy Policy</strong><br>
            • Explain what data you collect and how you use it<br>
            • GDPR/data protection compliance<br>
            • Include your contact email for privacy concerns<br><br>

            <strong>↩️ Refund Policy</strong><br>
            • If refunds apply: clearly state process and timelines<br>
            • If NO refunds (e.g., digital products): explicitly state "No refunds available"<br>
            • Don't leave generic text that contradicts your business model<br><br>

            <strong>❌ Cancellation Policy</strong><br>
            • Cancellation terms if applicable<br>
            • If not applicable: state clearly "Cancellations not applicable"<br><br>

            <strong>⚠️ CRITICAL WARNING:</strong><br>
            Razorpay agents READ these policies in detail! Do NOT copy-paste templates without modification.
            Generic or contradictory policies will lead to instant rejection.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Step 3: Category Matching
    st.markdown("""
    <div class="step-card">
        <span class="step-number">3</span>
        <div class="step-title">Category Matching is CRITICAL</div>
        <div class="step-content">
            <strong>The Golden Rule:</strong> Your website content MUST match the Razorpay application category.<br><br>

            <strong>Example Scenarios:</strong><br>

            ✅ <strong>CORRECT:</strong><br>
            • Website sells online courses → Application category: "Education/E-learning"<br>
            • Website offers consulting services → Application category: "Professional Services"<br>
            • Website sells physical products → Application category: "E-commerce"<br><br>

            ❌ <strong>WRONG (Leads to Rejection):</strong><br>
            • Website sells courses → Application category: "E-commerce" ❌<br>
            • Website shows multiple types → Unclear category ❌<br>
            • Website under construction → Any category ❌<br><br>

            <strong>💡 Pro Tip:</strong> If you plan to sell multiple product types eventually, start with ONE category,
            get approved, then expand your offerings later.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Step 4: Checkout Page
    st.markdown("""
    <div class="step-card">
        <span class="step-number">4</span>
        <div class="step-title">Add Checkout/Payment Page</div>
        <div class="step-content">
            <strong>Why needed:</strong> Razorpay verification team will specifically ask for a checkout page.<br><br>

            <strong>What to include:</strong><br>
            ✅ Clear "Buy Now" or "Checkout" button on product/service pages<br>
            ✅ Shopping cart (for e-commerce)<br>
            ✅ Payment method options page (can show "Credit Card, Debit Card, UPI" etc.)<br>
            ✅ Order summary page<br><br>

            <strong>Note:</strong> The payment buttons don't need to be functional yet (since you're waiting for
            Razorpay approval), but the FLOW and PAGES must be visible to show you're serious about accepting payments.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Step 5: Application Details
    st.markdown("""
    <div class="step-card">
        <span class="step-number">5</span>
        <div class="step-title">Fill Razorpay Application Correctly</div>
        <div class="step-content">
            <strong>Personal/Individual Application:</strong><br>
            • No GST required for individual accounts<br>
            • Use your personal PAN card<br>
            • KYC: Aadhaar or Driving License<br>
            • Bank account: Can be savings account (current account preferred but not mandatory)<br><br>

            <strong>Business Details:</strong><br>
            • Business name: Can be your personal name or brand name<br>
            • Business type: Individual/Proprietorship<br>
            • Website URL: Your professional website (must be live and accessible)<br>
            • Business category: MUST match your website content<br>
            • Expected monthly volume: Be realistic, you can increase later<br><br>

            <strong>Contact Details:</strong><br>
            • Email: Use your domain email (contact@yourbusiness.com)<br>
            • Phone: Number you actively use (they WILL call for verification)<br>
            • Address: Must match your KYC documents exactly
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Step 6: Verification Call
    st.markdown("""
    <div class="step-card">
        <span class="step-number">6</span>
        <div class="step-title">Ace the Verification Call</div>
        <div class="step-content">
            <strong>When to expect:</strong> Razorpay will call you within 24-48 hours of application submission.<br><br>

            <strong>What they will ask:</strong><br>
            • What product/service do you offer?<br>
            • Who are your target customers?<br>
            • How do you plan to accept payments?<br>
            • Business model and pricing<br>
            • Expected transaction volume<br><br>

            <strong>How to prepare:</strong><br>
            ✅ Be knowledgeable about YOUR business - speak confidently<br>
            ✅ Keep it simple - use non-technical language<br>
            ✅ Show genuine intent - ask them relevant questions<br>
            ✅ Questions you can ask them:<br>
            &nbsp;&nbsp;&nbsp;• "Do you support international payments?"<br>
            &nbsp;&nbsp;&nbsp;• "What are the transaction charges?"<br>
            &nbsp;&nbsp;&nbsp;• "Is there TDS on transactions?"<br>
            &nbsp;&nbsp;&nbsp;• "How long does settlement take?"<br><br>

            <strong>💡 Pro Tip:</strong> Asking questions shows you're a serious business owner, not a fake application.
            This builds trust with the verification agent.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Step 7: Re-application After Rejection
    st.markdown("""
    <div class="step-card">
        <span class="step-number">7</span>
        <div class="step-title">Re-Applying After Rejection</div>
        <div class="step-content">
            <strong>If your application was rejected, don't worry! Follow these steps:</strong><br><br>

            <strong>🔄 Change These Details:</strong><br>
            ✅ Use NEW email ID (different from rejected application)<br>
            ✅ Use NEW phone number (different from rejected application)<br>
            ✅ Same KYC documents are OK (no need to change)<br>
            ✅ Same website is OK (but fix issues that caused rejection)<br><br>

            <strong>✅ Fix These Issues:</strong><br>
            • Update website to match application category<br>
            • Customize all policy pages properly<br>
            • Add professional contact email (domain-based)<br>
            • Ensure address matches KYC documents<br>
            • Add clear checkout/payment flow pages<br><br>

            <strong>Timeline:</strong> After fixing issues and reapplying with new contact details,
            approval typically comes within 2-24 hours of successful verification call.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Checklist
    st.markdown("---")
    st.markdown("## ✅ Pre-Application Checklist")

    st.markdown("""
    Use this checklist before submitting your Razorpay application:
    """)

    checklist_data = [
        {"item": "Professional website is live and accessible", "category": "Website"},
        {"item": "Website focuses on ONE clear product/service type", "category": "Website"},
        {"item": "Website has Contact Us page with phone + domain email + address", "category": "Website"},
        {"item": "All policy pages are added and customized (not copy-pasted)", "category": "Policies"},
        {"item": "Refund/Cancellation policies match my business model", "category": "Policies"},
        {"item": "Checkout/payment flow pages are visible on website", "category": "Website"},
        {"item": "Application category matches website content exactly", "category": "Application"},
        {"item": "Contact email is domain-based (not Gmail)", "category": "Application"},
        {"item": "Address matches KYC documents (Aadhaar/DL)", "category": "Application"},
        {"item": "I'm prepared to answer verification call questions", "category": "Verification"},
    ]

    checklist_df = pd.DataFrame(checklist_data)

    for category in ["Website", "Policies", "Application", "Verification"]:
        st.markdown(f"### {category}")
        category_items = checklist_df[checklist_df['category'] == category]
        for _, row in category_items.iterrows():
            st.markdown(f"""
            <div class="checklist-item">
                <input type="checkbox" id="{row['item'][:20]}" style="margin-right: 10px; transform: scale(1.3);">
                <label for="{row['item'][:20]}" style="font-size: 1.05rem;">{row['item']}</label>
            </div>
            """, unsafe_allow_html=True)

    # Common Mistakes Section
    st.markdown("---")
    st.markdown("## ⚠️ Common Mistakes That Lead to Rejection")

    mistake_col1, mistake_col2 = st.columns(2)

    with mistake_col1:
        st.markdown("""
        <div class="warning-box">
            <strong>❌ Website Issues</strong><br>
            • No website or website under construction<br>
            • Multiple conflicting product types<br>
            • Generic template without customization<br>
            • Broken links or incomplete pages<br>
            • Using free subdomain instead of custom domain
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="warning-box">
            <strong>❌ Policy Issues</strong><br>
            • Copy-pasted generic policy templates<br>
            • Policies don't match business model<br>
            • Missing required policy pages<br>
            • Generic email (dummy@example.com) in policies<br>
            • Contradictory information in policies
        </div>
        """, unsafe_allow_html=True)

    with mistake_col2:
        st.markdown("""
        <div class="warning-box">
            <strong>❌ Application Issues</strong><br>
            • Category doesn't match website content<br>
            • Using Gmail instead of domain email<br>
            • Address doesn't match KYC documents<br>
            • Incomplete or vague business description<br>
            • No checkout/payment flow on website
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="warning-box">
            <strong>❌ Verification Call Issues</strong><br>
            • Not answering the verification call<br>
            • Being unprepared or vague about business<br>
            • Using technical jargon that confuses agent<br>
            • Seeming fake or not genuine<br>
            • Not asking any questions back to agent
        </div>
        """, unsafe_allow_html=True)

    # Success Stories
    st.markdown("---")
    st.markdown("## 🎉 Success Timeline")

    timeline_data = {
        "Day": ["Day 0", "Day 0-1", "Day 1-2", "Day 2", "Day 2"],
        "Event": [
            "Application Submitted",
            "Application Under Review",
            "Verification Call Received",
            "Second Verification Call (sometimes)",
            "Approval Received! 🎉"
        ],
        "What to Do": [
            "Double-check all details before submitting",
            "Keep phone accessible, monitor email",
            "Answer confidently, ask questions, be genuine",
            "Provide any additional clarifications if needed",
            "Start integrating Razorpay into your website"
        ]
    }

    timeline_df = pd.DataFrame(timeline_data)
    st.table(timeline_df)

    st.markdown("""
    <div class="success-box">
        <strong>✅ Typical Approval Timeline:</strong> 2-24 hours after successful verification call<br>
        <strong>📞 Number of Calls:</strong> Usually 1-2 verification calls<br>
        <strong>⏱️ Total Process:</strong> 2-3 days from application to approval
    </div>
    """, unsafe_allow_html=True)

    # Video Reference
    st.markdown("---")
    st.markdown("## 📺 Video Reference")

    st.video("http://www.youtube.com/watch?v=cCIimQHUmCs")

    st.markdown("""
    <div class="info-box">
        <strong>Video Credit:</strong> <a href="http://www.youtube.com/watch?v=cCIimQHUmCs" target="_blank">
        Get Razorpay Approval (100% Guaranteed) | Razorpay Account Rejected - Fix Now | Lokesh Gocher</a><br>
        This guide is based on the real experience shared in the video above.
    </div>
    """, unsafe_allow_html=True)

    # Additional Resources
    st.markdown("---")
    st.markdown("## 🔗 Additional Resources")

    resource_col1, resource_col2 = st.columns(2)

    with resource_col1:
        st.markdown("""
        ### Helpful Links
        - [Razorpay Official](https://razorpay.com)
        - [Razorpay Pricing](https://razorpay.com/pricing/)
        - [Razorpay Support](https://razorpay.com/support/)
        - [Razorpay Docs](https://razorpay.com/docs/)
        """)

    with resource_col2:
        st.markdown("""
        ### Next Steps After Approval
        - ✅ Integration documentation
        - ✅ Payment button setup
        - ✅ Test mode transactions
        - ✅ Go live checklist
        """)

    # Final Tips
    st.markdown("---")
    st.markdown("""
    <div class="success-box">
        <strong>💡 Final Pro Tips for 100% Success:</strong><br>
        1️⃣ Don't rush the application - take time to set up website properly<br>
        2️⃣ Be genuine and honest in verification call - they can detect fake businesses<br>
        3️⃣ Ask intelligent questions during call - shows you're serious<br>
        4️⃣ If rejected, fix ALL issues before reapplying with new contact details<br>
        5️⃣ Keep your phone accessible for 48 hours after application<br>
        6️⃣ Have your website open during verification call for quick reference
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
