# MCP Integration Guide - Home Loan Toolkit
**Razorpay Payments + Render Deployment**

---

## 🎯 Overview

This guide shows how to use the Razorpay and Render MCP servers to:
1. **Accept payments** for your Home Loan Toolkit (₹99 one-time fee)
2. **Deploy your app** to Render hosting platform
3. **Manage infrastructure** with natural language commands

---

## ✅ Configuration Status

Both MCP servers are configured and ready to use!

### Configured MCP Servers

**1. Razorpay Payment Gateway**
- Status: ✅ Active
- Endpoint: `https://mcp.razorpay.com/mcp`
- Mode: Live (Production)
- Credentials: See `D:\Claude\API_KEYS.md` (user-level)

**2. Render Hosting Platform**
- Status: ✅ Active
- Endpoint: `https://mcp.render.com/mcp`
- Credentials: See `D:\Claude\API_KEYS.md` (user-level)

Configuration file: `D:\Claude\.claude\settings.json`

---

## 🚀 Available MCP Tools

### Razorpay Tools (50+ tools)

#### Payment Operations
- `create_payment_link` - Create payment links for ₹99 toolkit access
- `fetch_payment` - Retrieve payment details
- `capture_payment` - Capture authorized payments
- `update_payment` - Update payment information

#### Payment Links (Best for your use case)
- `create_payment_link` - Standard payment links
- `create_upi_payment_link` - UPI-specific links
- `fetch_payment_link` - Get link details
- `send_payment_link_notification` - Send via SMS/Email
- `update_payment_link` - Modify existing links

#### Orders
- `create_order` - Create payment orders
- `fetch_order` - Get order details
- `fetch_order_payments` - List payments for an order

#### Refunds
- `fetch_refund` - Get refund details
- `update_refund` - Modify refund info

#### QR Codes
- `create_qr_code` - Generate payment QR codes
- `fetch_qr_code` - Retrieve QR details
- `close_qr_code` - Deactivate QR codes

### Render Tools

#### Workspace Management
- List workspaces
- Set active workspace
- Fetch workspace details

#### Service Management
- **Create web services** - Deploy Streamlit app
- **Create static sites** - Host static content
- List services
- Retrieve service details
- Update environment variables

#### Deployment
- List deploy history
- Get specific deploy details

#### Monitoring
- **Fetch logs** - Debug issues
- **Get metrics** - CPU, memory, bandwidth, response times
- Filter logs by level/time

#### Database (Postgres)
- Create databases
- Run read-only queries
- List databases
- Get database details

#### Key-Value Store
- Create KV instances
- List instances
- Get details

---

## 💡 Example Use Cases

### For Home Loan Toolkit

#### 1. Accept Payments

**Create a Payment Link for ₹99:**
```
Create a Razorpay payment link for ₹99 with description "Home Loan Toolkit - Full Access"
and reference ID "toolkit-2025-001"
```

**Send Payment Link to Customer:**
```
Send payment link [link_id] to customer at dmcpexam2020@gmail.com via email
```

**Check Payment Status:**
```
Fetch payment details for payment ID [payment_id]
```

#### 2. Deploy to Render

**Deploy Streamlit App:**
```
Create a new web service on Render named "home-loan-toolkit"
using the GitHub repository at https://github.com/YOUR_USERNAME/home-loan-toolkit
with Python runtime and command "streamlit run home_loan_toolkit.py --server.port=$PORT"
```

**Check App Status:**
```
What's the status of my home-loan-toolkit service?
```

**View Logs:**
```
Show me the latest error logs from home-loan-toolkit service
```

#### 3. Monitor & Troubleshoot

**Check Traffic:**
```
What was the busiest traffic day for my service this month?
```

**Check Performance:**
```
What was my service's CPU and memory usage yesterday?
```

**Debug Errors:**
```
Pull the most recent error-level logs for my home-loan-toolkit service
```

#### 4. Update Configuration

**Set Environment Variables:**
```
Update my home-loan-toolkit service environment variables to add
RAZORPAY_KEY_ID=rzp_live_RYmXpTJIWI1cMg
```

---

## 📋 Step-by-Step Integration

### Phase 1: Setup Payment Gateway (Razorpay)

**Step 1: Create Payment Link Template**
```
Create a Razorpay payment link for ₹99 with:
- Title: "Home Loan Toolkit - Premium Access"
- Description: "Unlock all 12 strategies + calculators + lifetime access"
- Accept UPI, Cards, NetBanking, Wallets
- Send receipt to customer email
- Callback URL: https://home-loan-toolkit.onrender.com/payment-success
```

**Step 2: Integrate into Streamlit App**

Update `home_loan_toolkit.py` checkout page (line 1094-1106):

```python
# Replace the payment button section with:
if st.button("💳 Proceed to Secure Payment", use_container_width=True, type="primary"):
    # User email from session state
    user_email = st.session_state.get('user_email', '')

    if user_email:
        # Ask Claude to create payment link via MCP
        st.info(f"""
        Creating secure payment link for {user_email}...

        Use Claude Code MCP to execute:
        "Create a Razorpay payment link for ₹99 with email {user_email}
        and send notification"
        """)
    else:
        st.warning("Please enter your email address first")
```

**Step 3: Handle Payment Success**

Create a webhook handler or callback page to mark users as paid.

### Phase 2: Deploy to Render

**Step 1: Create GitHub Repository**
```
Create a GitHub repository for the home loan toolkit and push the code
```

**Step 2: Prepare for Deployment**

Create `requirements.txt`:
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.17.0
```

Create `render.yaml` (optional):
```yaml
services:
  - type: web
    name: home-loan-toolkit
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run home_loan_toolkit.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

**Step 3: Deploy via MCP**
```
Deploy a new Streamlit web service on Render named "home-loan-toolkit"
from my GitHub repository with Python 3.11
and start command "streamlit run home_loan_toolkit.py --server.port=$PORT --server.address=0.0.0.0"
```

**Step 4: Configure Custom Domain (Optional)**
```
Set up custom domain home-loan-toolkit.com for my service
```

### Phase 3: Production Monitoring

**Daily Health Check:**
```
Show me today's traffic, errors, and performance metrics for home-loan-toolkit
```

**Payment Monitoring:**
```
List all payments from the last 24 hours with status "captured"
```

**User Analytics:**
```
How many payment links were created this week?
```

---

## 🔐 Security Best Practices

1. **API Keys**
   - ✅ Stored in `API_KEYS.md` (gitignored)
   - ✅ Never commit to version control
   - ✅ Use live keys only for production
   - ⚠️ Consider test/sandbox keys for development

2. **Payment Verification**
   - Always verify payment status server-side
   - Use webhook signatures to validate callbacks
   - Never trust client-side payment confirmations

3. **Render Security**
   - Use environment variables for secrets
   - Enable HTTPS (automatic on Render)
   - Implement rate limiting for payment endpoints

4. **User Data**
   - Store minimal user data
   - Comply with payment card industry standards
   - Use Razorpay's hosted checkout for PCI compliance

---

## 🧪 Testing the MCP Servers

### Test Razorpay MCP

**Simple test:**
```
List my Razorpay payment links from the last 7 days
```

**Create test payment link:**
```
Create a Razorpay payment link for ₹1 (test) with description "Test Link"
```

### Test Render MCP

**List services:**
```
Show me all my Render services
```

**Check active workspace:**
```
What's my current Render workspace?
```

---

## 📊 Analytics & Reporting

### Payment Analytics via Razorpay MCP

**Monthly Revenue:**
```
Fetch all captured payments from January 2025 and calculate total revenue
```

**Conversion Rate:**
```
Compare payment links created vs. payments captured this month
```

### App Analytics via Render MCP

**Uptime Monitoring:**
```
What was my service's uptime percentage last month?
```

**Performance Trends:**
```
Show me the average response time trend for the last 7 days
```

---

## 🛠️ Troubleshooting

### Razorpay Issues

**Payment not captured:**
```
Fetch payment [payment_id] and check its status and error description
```

**Link not working:**
```
Fetch payment link [link_id] and verify it's active and not expired
```

### Render Issues

**App not loading:**
```
Show me the latest 50 logs from home-loan-toolkit service filtered by level ERROR
```

**Deployment failed:**
```
Get the latest deploy details for home-loan-toolkit and show build logs
```

**High memory usage:**
```
Show me memory metrics for the last 24 hours for home-loan-toolkit
```

---

## 📞 Support Resources

### Razorpay
- Dashboard: https://dashboard.razorpay.com/
- Docs: https://razorpay.com/docs/
- Support: support@razorpay.com

### Render
- Dashboard: https://dashboard.render.com/
- Docs: https://render.com/docs
- Support: support@render.com

### Your App
- Email: dmcpexam2020@gmail.com
- Phone: +91 7021761291

---

## 🎉 Quick Start Commands

### Just say (in natural language):

**Payments:**
- "Create a payment link for ₹99 for the home loan toolkit"
- "Show me all successful payments from today"
- "Send payment link to customer at user@example.com"

**Deployment:**
- "Deploy my Streamlit app to Render"
- "Show me the logs from my app"
- "What's the current status of my service?"

**Monitoring:**
- "How many users accessed my app today?"
- "Show me any errors from the last hour"
- "What's my app's response time?"

---

**Last Updated**: 2025-10-28

**MCP Servers Active**: ✅ Razorpay | ✅ Render
