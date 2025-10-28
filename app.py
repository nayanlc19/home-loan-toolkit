import os
import json
import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from dotenv import load_dotenv
import razorpay
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
REDIRECT_URI = f"{APP_URL}/login/callback"

# Razorpay Configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
PAYMENT_AMOUNT = int(os.environ.get('PAYMENT_AMOUNT', 9900))  # Rs 99 in paise
PAYMENT_CURRENCY = os.environ.get('PAYMENT_CURRENCY', 'INR')

# Admin emails
ADMIN_EMAILS = ['razorpay@razorpay.com', 'nayanlc19@gmail.com']

# Paid users database
PAID_USERS_FILE = 'paid_users.json'

def load_paid_users():
    """Load paid users from JSON file"""
    if os.path.exists(PAID_USERS_FILE):
        with open(PAID_USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_paid_users(paid_users):
    """Save paid users to JSON file"""
    with open(PAID_USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(paid_users, f, indent=2)

def is_paid_user(email):
    """Check if user has paid or is admin"""
    if email in ADMIN_EMAILS:
        return True
    paid_users = load_paid_users()
    return email in paid_users

def get_user_email():
    """Get current user's email from session"""
    return session.get('user_email')

def get_user_name():
    """Get current user's name from session"""
    return session.get('user_name', session.get('user_email', 'Guest'))

# Routes
@app.route('/')
def index():
    """Home page with all strategies"""
    user_email = get_user_email()
    user_name = get_user_name()
    is_authenticated = user_email is not None
    has_paid = is_paid_user(user_email) if user_email else False

    return render_template('index.html',
                         user_email=user_email,
                         user_name=user_name,
                         is_authenticated=is_authenticated,
                         has_paid=has_paid)

@app.route('/login')
def login():
    """Redirect to Google OAuth"""
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [REDIRECT_URI]
                }
            },
            scopes=['openid', 'email', 'profile'],
            redirect_uri=REDIRECT_URI
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        session['state'] = state
        return redirect(authorization_url)
    except Exception as e:
        return f"Error initiating login: {str(e)}", 500

@app.route('/login/callback')
def oauth_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        if not code:
            return "Error: No authorization code received", 400

        # Exchange code for tokens
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [REDIRECT_URI]
                }
            },
            scopes=['openid', 'email', 'profile'],
            redirect_uri=REDIRECT_URI
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        # Verify the ID token
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Extract user info
        email = id_info.get('email')
        name = id_info.get('name', email)

        if email:
            session['user_email'] = email
            session['user_name'] = name
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return "Error: Could not retrieve email from Google", 400

    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        return f"Authentication error: {str(e)}", 500

@app.route('/logout')
def logout():
    """Log out user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/checkout')
def checkout():
    """Create Razorpay payment link"""
    user_email = get_user_email()

    if not user_email:
        return jsonify({'error': 'Please sign in first'}), 401

    if is_paid_user(user_email):
        return jsonify({'error': 'You already have access to all strategies'}), 400

    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

        payment_link_data = {
            "amount": PAYMENT_AMOUNT,
            "currency": PAYMENT_CURRENCY,
            "description": "Home Loan Toolkit - All 12 Strategies",
            "customer": {
                "email": user_email,
                "name": get_user_name()
            },
            "notify": {
                "email": True
            },
            "reminder_enable": True,
            "callback_url": f"{APP_URL}/payment/verify",
            "callback_method": "get"
        }

        payment_link = client.payment_link.create(payment_link_data)
        return jsonify({'payment_url': payment_link['short_url']})

    except Exception as e:
        print(f"Payment link creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/payment/verify')
def verify_payment():
    """Verify Razorpay payment"""
    user_email = get_user_email()

    if not user_email:
        return "Please sign in first", 401

    # Get payment details from query parameters
    payment_id = request.args.get('razorpay_payment_id')
    payment_link_id = request.args.get('razorpay_payment_link_id')
    payment_status = request.args.get('razorpay_payment_link_status')

    if payment_status == 'paid' and payment_id:
        try:
            # Verify payment with Razorpay
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            payment = client.payment.fetch(payment_id)

            if payment['status'] == 'captured':
                # Add user to paid users
                paid_users = load_paid_users()
                paid_users[user_email] = {
                    'payment_id': payment_id,
                    'payment_link_id': payment_link_id,
                    'amount': payment['amount'],
                    'currency': payment['currency'],
                    'timestamp': datetime.now().isoformat(),
                    'name': get_user_name()
                }
                save_paid_users(paid_users)

                return redirect(url_for('index') + '?payment=success')
        except Exception as e:
            print(f"Payment verification error: {str(e)}")
            return redirect(url_for('index') + '?payment=error')

    return redirect(url_for('index') + '?payment=failed')

# Policy pages
@app.route('/contact')
def contact():
    return render_template('policy.html',
                         title='Contact Us',
                         content=get_contact_content(),
                         user_email=get_user_email(),
                         user_name=get_user_name(),
                         is_authenticated=get_user_email() is not None)

@app.route('/terms')
def terms():
    return render_template('policy.html',
                         title='Terms & Conditions',
                         content=get_terms_content(),
                         user_email=get_user_email(),
                         user_name=get_user_name(),
                         is_authenticated=get_user_email() is not None)

@app.route('/privacy')
def privacy():
    return render_template('policy.html',
                         title='Privacy Policy',
                         content=get_privacy_content(),
                         user_email=get_user_email(),
                         user_name=get_user_name(),
                         is_authenticated=get_user_email() is not None)

@app.route('/refund')
def refund():
    return render_template('policy.html',
                         title='Refund Policy',
                         content=get_refund_content(),
                         user_email=get_user_email(),
                         user_name=get_user_name(),
                         is_authenticated=get_user_email() is not None)

@app.route('/cancellation')
def cancellation():
    return render_template('policy.html',
                         title='Cancellation Policy',
                         content=get_cancellation_content(),
                         user_email=get_user_email(),
                         user_name=get_user_name(),
                         is_authenticated=get_user_email() is not None)

@app.route('/shipping')
def shipping():
    return render_template('policy.html',
                         title='Shipping & Delivery Policy',
                         content=get_shipping_content(),
                         user_email=get_user_email(),
                         user_name=get_user_name(),
                         is_authenticated=get_user_email() is not None)

# Policy content functions
def get_contact_content():
    return """
    <h2>Contact Information</h2>
    <p><strong>Email:</strong> dmcpexam2020@gmail.com</p>
    <p><strong>Phone:</strong> +91 7021761291</p>
    <p><strong>Response Time:</strong> Within 24-48 hours</p>
    <p><strong>Business Hours:</strong> Mon-Fri, 9 AM - 6 PM IST</p>

    <h2>Get in Touch</h2>
    <p>We're here to help you with your home loan journey. Feel free to reach out!</p>

    <h3>Business Information</h3>
    <p><strong>Home Loan Toolkit</strong><br>
    Online Educational Platform<br>
    Providing Home Loan Strategies & Financial Tools</p>

    <h3>Authentication</h3>
    <p>Secure login via Google Auth (powered by Render)</p>
    """

def get_terms_content():
    return """
    <p><strong>Last Updated:</strong> October 28, 2025</p>

    <h2>1. Acceptance of Terms</h2>
    <p>By accessing and using Home Loan Toolkit ("the Service"), you accept and agree to be bound by the terms and conditions of this agreement.</p>

    <h2>2. Description of Service</h2>
    <p>Home Loan Toolkit provides:</p>
    <ul>
        <li>Educational content and calculators for home loan payment strategies</li>
        <li>Interactive tools to help users make informed financial decisions</li>
    </ul>

    <h2>3. User Responsibilities</h2>
    <p>You agree to:</p>
    <ul>
        <li>Provide accurate information when using our calculators</li>
        <li>Use the Service for lawful purposes only</li>
        <li>Not attempt to gain unauthorized access to any part of the Service</li>
        <li>Seek professional financial advice before making major financial decisions</li>
    </ul>

    <h2>4. Disclaimer</h2>
    <p>The information provided through the Service is for educational purposes only and should not be considered as financial, legal, or tax advice. We recommend consulting with qualified professionals before making any financial decisions.</p>

    <h2>5. No Warranties</h2>
    <p>The Service is provided "as is" without any warranties, express or implied. We do not guarantee:</p>
    <ul>
        <li>The accuracy or completeness of the information</li>
        <li>That the Service will be uninterrupted or error-free</li>
        <li>Specific results from using our strategies or tools</li>
    </ul>

    <h2>6. Limitation of Liability</h2>
    <p>Home Loan Toolkit shall not be liable for any:</p>
    <ul>
        <li>Financial losses resulting from use of our calculators or strategies</li>
        <li>Decisions made based on information provided through the Service</li>
        <li>Technical issues or data loss</li>
    </ul>

    <h2>7. Intellectual Property</h2>
    <p>All content, including but not limited to text, graphics, logos, and software, is the property of Home Loan Toolkit and protected by copyright laws.</p>

    <h2>8. Changes to Terms</h2>
    <p>We reserve the right to modify these terms at any time. Continued use of the Service after changes constitutes acceptance of the modified terms.</p>

    <h2>9. Governing Law</h2>
    <p>These terms shall be governed by the laws of India.</p>

    <h2>10. Contact Information</h2>
    <p>For questions about these Terms & Conditions, please contact:<br>
    Email: dmcpexam2020@gmail.com</p>

    <p><strong>By using Home Loan Toolkit, you acknowledge that you have read, understood, and agree to be bound by these Terms & Conditions.</strong></p>
    """

def get_privacy_content():
    return """
    <p><strong>Last Updated:</strong> October 28, 2025</p>

    <h2>1. Introduction</h2>
    <p>Home Loan Toolkit ("we", "our", or "us") respects your privacy and is committed to protecting your personal data. This privacy policy explains how we collect, use, and safeguard your information.</p>

    <h2>2. Information We Collect</h2>
    <h3>2.1 Information You Provide</h3>
    <ul>
        <li>Contact details (name, email) when you sign in with Google</li>
        <li>Financial inputs you enter into our calculators (stored locally, not on our servers)</li>
    </ul>

    <h3>2.2 Automatically Collected Information</h3>
    <ul>
        <li>Browser type and version</li>
        <li>Time zone setting and location</li>
        <li>Operating system and platform</li>
        <li>Pages visited and time spent on pages</li>
    </ul>

    <h2>3. How We Use Your Information</h2>
    <p>We use your information to:</p>
    <ul>
        <li>Provide access to premium strategies after payment verification</li>
        <li>Respond to your inquiries and provide customer support</li>
        <li>Improve our Service based on usage patterns</li>
        <li>Analyze and improve our calculators and tools</li>
    </ul>

    <h2>4. Data Storage and Security</h2>
    <ul>
        <li>Calculator inputs are processed in real-time and not stored on our servers</li>
        <li>Google OAuth handles authentication securely</li>
        <li>Payment information is processed by Razorpay (we don't store card details)</li>
        <li>We implement appropriate technical and organizational measures to protect your data</li>
    </ul>

    <h2>5. Data Sharing</h2>
    <p>We do NOT:</p>
    <ul>
        <li>Sell your personal data to third parties</li>
        <li>Share your financial calculation data with anyone</li>
        <li>Use your data for marketing purposes without explicit consent</li>
    </ul>

    <p>We MAY share data with:</p>
    <ul>
        <li>Service providers who help us operate the Service (under strict confidentiality)</li>
        <li>Law enforcement if legally required</li>
    </ul>

    <h2>6. Your Rights</h2>
    <p>You have the right to:</p>
    <ul>
        <li>Access your personal data</li>
        <li>Request correction of inaccurate data</li>
        <li>Request deletion of your data</li>
        <li>Opt-out of communications</li>
        <li>Withdraw consent at any time</li>
    </ul>

    <h2>7. Third-Party Services</h2>
    <p>Our Service uses:</p>
    <ul>
        <li><strong>Google OAuth</strong> for authentication</li>
        <li><strong>Razorpay</strong> for payment processing</li>
    </ul>
    <p>These services have their own privacy policies, and we encourage you to review them.</p>

    <h2>8. Changes to Privacy Policy</h2>
    <p>We may update this policy from time to time. We will notify you of significant changes by posting a notice on our Service.</p>

    <h2>9. Contact Us</h2>
    <p>For privacy-related questions or to exercise your rights, contact:<br>
    Email: dmcpexam2020@gmail.com</p>

    <p><strong>By using Home Loan Toolkit, you consent to this Privacy Policy.</strong></p>
    """

def get_refund_content():
    return """
    <p><strong>Last Updated:</strong> October 28, 2025</p>

    <h2>No Refund Policy</h2>
    <p><strong>IMPORTANT:</strong> All payments made through our platform are <strong>FINAL and NON-REFUNDABLE</strong>.</p>

    <h2>Service Nature</h2>
    <p>Home Loan Toolkit provides:</p>
    <ul>
        <li>Digital educational content (delivered instantly)</li>
        <li>Interactive calculators and tools (immediate access)</li>
        <li>Payment strategy guides (instant access)</li>
    </ul>

    <h2>Why No Refunds?</h2>
    <p>Due to the <strong>digital and instant nature</strong> of our services:</p>
    <ul>
        <li>Content is delivered immediately upon payment</li>
        <li>Information cannot be "returned" once accessed</li>
        <li>Calculators and tools are accessed instantly</li>
        <li>This prevents misuse of our educational content</li>
    </ul>

    <h2>Payment Processing</h2>
    <p>All payments are processed through secure Razorpay gateway that is:</p>
    <ul>
        <li>Encrypted and PCI-DSS compliant</li>
        <li>Supports multiple payment methods</li>
        <li>Fully secure and trusted</li>
    </ul>

    <h2>Before You Purchase</h2>
    <p>Please ensure you:</p>
    <ul>
        <li>Review service descriptions carefully</li>
        <li>Understand what you're purchasing</li>
        <li>Try the FREE strategy first before buying premium access</li>
        <li>Contact us with any questions BEFORE making payment</li>
        <li>Verify your payment details</li>
    </ul>

    <h2>Exceptions</h2>
    <p>Refunds may be considered ONLY in the following cases:</p>
    <ul>
        <li>Duplicate payment due to technical error</li>
        <li>Payment debited but service not delivered (verified by our team)</li>
        <li>Unauthorized transaction (with police complaint)</li>
    </ul>

    <h2>Contact Us</h2>
    <p>For questions about payments or this policy, contact:<br>
    Email: dmcpexam2020@gmail.com<br>
    Phone: +91 7021761291</p>

    <p><strong>By making a payment, you acknowledge and accept this No Refund Policy.</strong></p>
    """

def get_cancellation_content():
    return """
    <p><strong>Last Updated:</strong> October 28, 2025</p>

    <h2>No Cancellation Policy</h2>
    <p><strong>IMPORTANT:</strong> Once a payment is made and content/service is delivered, <strong>NO CANCELLATIONS are allowed</strong>.</p>

    <h2>Service Nature</h2>
    <p>Home Loan Toolkit provides <strong>instant-access digital services</strong>:</p>
    <ul>
        <li>Educational content delivered immediately</li>
        <li>Calculator tools activated instantly upon payment</li>
        <li>Guides available for immediate access</li>
    </ul>

    <h2>Why No Cancellations?</h2>
    <p>Due to the <strong>instant delivery nature</strong> of digital services:</p>
    <ul>
        <li>Content is accessed immediately after payment</li>
        <li>Information and tools cannot be "undelivered"</li>
        <li>All services are non-reversible once accessed</li>
        <li>Immediate value is provided at the time of payment</li>
    </ul>

    <h2>Payment Processing</h2>
    <p>All payments through our secure Razorpay gateway are:</p>
    <ul>
        <li>Processed instantly</li>
        <li>Final and binding</li>
        <li>Non-cancellable once transaction is complete</li>
    </ul>

    <h2>Before Making Payment</h2>
    <p>Please ensure to:</p>
    <ul>
        <li>Carefully review what you're purchasing</li>
        <li>Try the FREE Bi-Weekly strategy first</li>
        <li>Verify the service description</li>
        <li>Check pricing and payment details</li>
        <li>Contact us with questions BEFORE paying</li>
        <li>Confirm you want to proceed with the purchase</li>
    </ul>

    <h2>Account Management</h2>
    <p>If you have an account with us:</p>
    <ul>
        <li>You can stop using the service anytime</li>
        <li>Account data can be deleted upon request</li>
        <li>Email dmcpexam2020@gmail.com for data deletion</li>
        <li>We process deletion requests within 30 days</li>
    </ul>

    <h2>Authentication</h2>
    <ul>
        <li>Login is managed via <strong>Google Auth</strong></li>
        <li>Secure and encrypted authentication</li>
        <li>No password storage on our platform</li>
    </ul>

    <h2>Contact Us</h2>
    <p>For questions about this policy, contact:<br>
    Email: dmcpexam2020@gmail.com<br>
    Phone: +91 7021761291</p>

    <p><strong>By making a payment, you acknowledge that NO CANCELLATIONS are permitted once service is delivered.</strong></p>
    """

def get_shipping_content():
    return """
    <p><strong>Last Updated:</strong> October 28, 2025</p>

    <h2>Digital Product - Instant Delivery</h2>
    <p><strong>IMPORTANT:</strong> Home Loan Toolkit is a <strong>100% DIGITAL PRODUCT</strong>. There is NO physical shipping involved.</p>

    <h2>How You Get Access</h2>
    <h3>Instant Access After Payment</h3>
    <p>Once your payment is successfully processed:</p>
    <ol>
        <li><strong>Immediate Activation:</strong> Your account is activated instantly</li>
        <li><strong>No Waiting:</strong> Access all 12 strategies immediately</li>
        <li><strong>Instant Delivery:</strong> All calculators, tools, and content available right away</li>
        <li><strong>Email Confirmation:</strong> You'll receive a payment confirmation from Razorpay</li>
    </ol>

    <h3>Access Details</h3>
    <ul>
        <li><strong>Delivery Method:</strong> Online access through website</li>
        <li><strong>Delivery Time:</strong> Instant (within seconds of payment confirmation)</li>
        <li><strong>Access Duration:</strong> Lifetime access</li>
        <li><strong>Downloads:</strong> No downloads required - all tools are web-based</li>
    </ul>

    <h2>What You Get Access To</h2>
    <p>After successful payment, you will immediately get access to:</p>
    <ul>
        <li>All 12 Home Loan Payment Strategies</li>
        <li>Interactive Calculators for each strategy</li>
        <li>Comparison Tools</li>
        <li>Implementation Guides</li>
        <li>All future updates (FREE)</li>
    </ul>

    <h2>Payment Processing</h2>
    <ul>
        <li>Payment is processed through secure Razorpay gateway</li>
        <li>Once payment is successful, access is granted automatically</li>
        <li>No manual activation required</li>
        <li>No shipping address needed (digital product)</li>
    </ul>

    <h2>Accessing Your Purchase</h2>
    <p><strong>Steps to Access:</strong></p>
    <ol>
        <li>Sign in with your Google account</li>
        <li>Complete payment of Rs 99 through checkout</li>
        <li>Razorpay processes your payment</li>
        <li>You receive instant access to all strategies</li>
        <li>Start using tools immediately</li>
    </ol>

    <h2>No Physical Delivery</h2>
    <ul>
        <li>This is a digital-only service</li>
        <li>No courier/postal delivery</li>
        <li>No shipping charges</li>
        <li>No shipping address required</li>
        <li>Instant online access only</li>
    </ul>

    <h2>Support</h2>
    <p>If you face any issues accessing your purchase after payment:</p>
    <ul>
        <li><strong>Email:</strong> dmcpexam2020@gmail.com</li>
        <li><strong>Phone:</strong> +91 7021761291</li>
        <li><strong>Response Time:</strong> Within 24-48 hours</li>
        <li><strong>We'll resolve:</strong> Any access issues immediately</li>
    </ul>

    <h2>Summary</h2>
    <p><strong>Digital Product = Instant Access</strong></p>
    <ul>
        <li>Pay Rs 99 → Get instant access → Start using immediately</li>
        <li>No waiting, no shipping, no delays</li>
        <li>100% online, 100% instant</li>
    </ul>

    <p><strong>By making a purchase, you understand this is a digital product with instant online access and no physical shipping.</strong></p>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Home Loan Toolkit on port {port}")
    print(f"Google OAuth: {'Configured' if GOOGLE_CLIENT_ID else 'NOT configured'}")
    print(f"Razorpay: {'Configured' if RAZORPAY_KEY_ID else 'NOT configured'}")
    print(f"Admin emails: {', '.join(ADMIN_EMAILS)}")
    app.run(host='0.0.0.0', port=port, debug=False)
