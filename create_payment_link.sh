#!/bin/bash
# Quick script to create payment links manually
# Usage: ./create_payment_link.sh user@email.com

USER_EMAIL=$1

if [ -z "$USER_EMAIL" ]; then
    echo "Usage: ./create_payment_link.sh user@email.com"
    exit 1
fi

curl -k -X POST https://api.razorpay.com/v1/payment_links \
  -u "rzp_live_RYmXpTJIWI1cMg:Oy7e2KsXnLvqRzABm43puF85" \
  -H "Content-Type: application/json" \
  -d "{
    \"amount\": 9900,
    \"currency\": \"INR\",
    \"description\": \"Home Loan Toolkit - Full Access Payment\",
    \"customer\": {
      \"name\": \"Customer\",
      \"email\": \"$USER_EMAIL\"
    },
    \"notify\": {
      \"sms\": false,
      \"email\": true
    },
    \"reminder_enable\": true,
    \"notes\": {
      \"product\": \"Home Loan Toolkit\",
      \"user_email\": \"$USER_EMAIL\"
    }
  }" | jq '.short_url'

echo ""
echo "Payment link created for: $USER_EMAIL"
