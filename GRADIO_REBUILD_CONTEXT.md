# Gradio Rebuild Context - Home Loan Toolkit

**Date:** 2025-10-28
**Task:** Rebuild entire Home Loan Toolkit from Streamlit to Gradio
**URL Must Remain:** https://home-loan-toolkit.onrender.com/

## Why Rebuilding?

After 6+ hours, Streamlit has persistent issues:
1. HTML/JavaScript components not rendering (Google Sign-In button invisible)
2. OAuth 400 errors
3. Sidebar layout problems
4. User frustrated with lack of progress

## Current App Overview

**File:** `home_loan_toolkit.py` (Streamlit)
- 1419 lines of code
- 12 payment strategies (1 free, 11 premium at ₹99)
- Interactive calculators for each strategy
- Razorpay payment integration (working)
- Google OAuth (NOT working properly)
- Admin emails: razorpay@razorpay.com, nayanlc19@gmail.com

## Key Features to Port

### 1. Authentication
- Google Sign Up / Sign In buttons at TOP (not sidebar)
- User profile display when logged in
- Sign Out functionality
- Admin bypass for free users

### 2. Payment System
- Razorpay integration (already working)
- Payment link generation
- User payment tracking via `paid_users.json`
- ₹99 one-time payment

### 3. Strategies (All 12)
1. Bi-Weekly Payment Hack (FREE)
2. Round-Up Revolution
3. Lump Sum Accelerator
4. Re-Amortization Reset
5. Split Loan Arbitrage
6. Offset Account Optimizer
7. Redraw Facility Refinement
8. Interest-Only Initial Phase
9. Principal Pre-Payment Blitz
10. Loan Portability Play
11. Top-Up Loan Leverage
12. Balloon Payment Gambit

### 4. Calculators
Each strategy has interactive calculator with:
- Loan amount input
- Interest rate input
- Tenure slider
- Real-time calculations
- Comparison with standard EMI
- Savings display

## Environment Variables (Already Set on Render)

```
GOOGLE_CLIENT_ID=<configured on Render>
GOOGLE_CLIENT_SECRET=<configured on Render>
RAZORPAY_KEY_ID=<configured on Render>
RAZORPAY_KEY_SECRET=<configured on Render>
APP_URL=https://home-loan-toolkit.onrender.com
PAYMENT_AMOUNT=9900
PAYMENT_CURRENCY=INR
PYTHON_VERSION=3.11.9
```

## Gradio Requirements

### New Dependencies
```
gradio>=4.0.0
google-auth==2.27.0
google-auth-oauthlib==1.2.0
razorpay==1.4.1
requests==2.31.0
python-dotenv==1.0.0
pandas==2.1.4
numpy==1.26.3
plotly==5.18.0
```

### Render Configuration
- **Start Command:** `python app.py` (instead of streamlit run)
- **Port:** Gradio uses environment variable `PORT` automatically
- **Python Version:** 3.11.9 (already set)

## Gradio App Structure

```python
# app.py
import gradio as gr
import os
from google_auth_oauthlib.flow import Flow
import razorpay

# 1. Authentication setup
# 2. Payment functions (reuse from Streamlit)
# 3. Calculator functions (reuse logic)
# 4. Gradio interface with tabs
# 5. Launch with server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860))
```

## Google OAuth Setup for Gradio

**Authorized Redirect URIs in Google Console:**
- https://home-loan-toolkit.onrender.com/callback
- http://localhost:7860/callback

**OAuth Flow:**
1. User clicks "Sign in with Google" button
2. Redirect to Google authorization URL
3. Google redirects back to `/callback`
4. Exchange code for token
5. Get user email and name
6. Store in session/state

## Critical Requirements

1. ✅ Sign Up / Sign In buttons VISIBLE at top
2. ✅ Google OAuth MUST work (no 400 errors)
3. ✅ Same URL: https://home-loan-toolkit.onrender.com/
4. ✅ All 12 strategies with calculators
5. ✅ Razorpay payment flow
6. ✅ Better UI/UX than Streamlit
7. ✅ NO sidebar (user doesn't want it)

## Files to Keep
- `paid_users.json` - payment tracking database
- `.env` - local environment variables
- `requirements.txt` - update for Gradio
- `runtime.txt` - keep Python 3.11.9

## Files to Create
- `app.py` - new Gradio application
- `auth.py` - Google OAuth helpers (optional)
- `payment.py` - Razorpay helpers (optional)

## Testing Checklist
- [ ] Google Sign-In button visible at top
- [ ] OAuth flow completes without errors
- [ ] User profile shows after sign-in
- [ ] Sign Out works
- [ ] Free strategy accessible
- [ ] Premium strategies locked
- [ ] Checkout creates payment link
- [ ] Payment verification works
- [ ] Admin emails get free access
- [ ] UI looks better than Streamlit

## Next Steps

1. Backup current Streamlit app
2. Create new `app.py` with Gradio
3. Implement Google OAuth properly
4. Port all strategies and calculators
5. Update requirements.txt
6. Update Render start command via API
7. Deploy and test thoroughly before claiming success

**DO NOT CLAIM SUCCESS WITHOUT VERIFYING VISUALLY**

---

Created: 2025-10-28 by Claude Code
Session ended at 127k tokens - resuming in new session
