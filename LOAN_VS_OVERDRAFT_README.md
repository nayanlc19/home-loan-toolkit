# 💰 Loan vs Overdraft Comparison Tool

A comprehensive, research-backed Streamlit application that provides **actual cost comparisons** between personal loans and overdraft facilities in India, cutting through marketing claims to show real numbers.

## 🎯 Purpose

This tool helps borrowers make informed decisions by:
- Calculating **real costs** based on actual usage patterns
- Comparing **all major banks** in India
- Revealing **hidden charges** often missed in marketing materials
- Providing **scenario-based recommendations**
- Exposing the reality: **Overdraft may have higher interest rates but can cost less overall**

## 🔍 Key Features

### 1. Comprehensive Cost Calculation
- **Personal Loans**: Includes processing fees, interest, prepayment charges
- **Overdraft Against Salary**: Daily interest calculation on utilized amount only
- **Overdraft Against FD**: Net cost after considering FD interest earnings

### 2. Real Bank Data (October 2025)

**Personal Loans (7 Banks)**
- HDFC Bank, ICICI Bank, Axis Bank, SBI
- Bajaj Finserv, IDFC First Bank, Tata Capital
- Interest rates: 10.49% - 13.00%
- Processing fees: 1.5% - 3.5%

**Overdraft Against Salary (4 Banks)**
- HDFC Bank, ICICI Bank, Axis Bank, SBI
- Interest rates: 13.50% - 14.50%
- Renewal fees: ₹250 - ₹500/year

**Overdraft Against FD (4 Banks)**
- Interest = FD Rate + 1.5% to 2.0% spread
- Zero processing fees
- FD continues earning interest

### 3. Accurate Overdraft Calculations

Unlike simple calculators, this tool factors in:
- **Utilization percentage**: How much of the limit you actually use
- **Days used per month**: Interest is calculated daily
- **Renewal fees**: Annual charges for maintaining the facility
- **FD interest earnings**: For FD-backed overdrafts

### 4. Visual Comparisons

- Total cost breakdown by component
- Monthly cash flow comparison
- Impact of utilization patterns
- Interactive charts using Plotly

### 5. All Banks Comparison Tables

Side-by-side comparison of:
- Interest rates
- Processing fees
- EMI/Monthly interest
- Total costs

### 6. Hidden Charges Awareness

**Personal Loan Hidden Costs**
- Processing fee (1.5% - 3.5% + 18% GST)
- Prepayment charges (0% - 6%)
- Late payment penalties
- Bounce charges
- Documentation fees
- Stamp duty

**Overdraft Hidden Costs**
- Annual renewal fees
- Over-limit charges
- Non-utilization fees (some banks)
- Statement charges
- Limit enhancement fees

## 📊 Example Scenario

**Borrowing Requirement**: ₹1,00,000 for 12 months

### Personal Loan (HDFC @ 10.50%)
- Monthly EMI: ₹8,840
- Total Interest: ₹6,080
- Processing Fee: ₹2,360
- **Total Cost: ₹8,440**

### Overdraft Against Salary (ICICI @ 13.86%)
- Average Utilization: 50% (₹50,000)
- Days Used: 15/month
- Monthly Interest: ₹854
- **Total Cost: ₹10,548**
- **But**: Only if you use 50% for 15 days/month

### Overdraft Against FD (ICICI)
- OD Rate: 8.60% (6.60% FD + 2%)
- FD Interest Earned: ₹7,260
- OD Interest Paid: ₹1,672
- **Net Cost: -₹5,588** (You actually earn!)

## 🚨 Reality Check: Why Overdraft Can Be Cheaper Despite Higher Rates

### The Math Marketing Doesn't Show

**Personal Loan**: Interest charged on **₹1,00,000 × 30 days × 12 months**

**Overdraft**: Interest charged on **₹50,000 × 15 days × 12 months** (if 50% utilized for 15 days)

This is why an overdraft at 14% can cost LESS than a loan at 10.5%!

### The Catches

1. **Only if you don't use full limit**: At 100% utilization for 30 days, overdraft becomes expensive
2. **Renewal fees add up**: ₹250-₹500 annually
3. **Requires discipline**: Easy to over-utilize
4. **Variable interest**: Some banks have floating rates

## 🎓 When to Choose What

### Choose Personal Loan If:
- ✅ You need the **full amount immediately**
- ✅ You want **fixed, predictable EMIs**
- ✅ You'll use **90-100%** of borrowed amount
- ✅ You prefer **longer tenure** (24-60 months)
- ✅ You value **simplicity** over flexibility
- ✅ You're from Jan 2026 onwards (0% prepayment charges)

### Choose Overdraft If:
- ✅ Your need is **variable** or uncertain
- ✅ You'll use only **30-70%** of limit on average
- ✅ You need funds for **short, intermittent periods**
- ✅ You want **flexibility** in withdrawals/repayments
- ✅ You can **repay quickly** when you have surplus
- ✅ You have **FD for collateral** (lowest effective cost)

## 🏦 Key Differences

| Feature | Personal Loan | Overdraft |
|---------|--------------|-----------|
| **Interest Calculation** | Entire amount from day 1 | Only on utilized amount, daily |
| **Interest Rate** | 10% - 20% p.a. | 13% - 15% p.a. |
| **Processing Fee** | 1.5% - 3.5% + GST | 0% - 1% |
| **Disbursement** | 1-7 days | Instant (if limit approved) |
| **Repayment** | Fixed EMI only | Very flexible |
| **Prepayment** | 0% - 6% (0% from Jan 2026) | None |
| **Best For** | Full amount needed | Variable/short-term needs |

## 📅 Important RBI Update (July 2025)

**From January 1, 2026**, RBI mandates:
- **Zero prepayment/foreclosure charges** on personal loans for individual borrowers
- Applies to both floating AND fixed rate loans
- Applies even if there's a co-borrower

This makes personal loans more attractive for those who might want to close early!

## 🛠️ Installation & Usage

### Requirements
```bash
pip install -r requirements_loan_app.txt
```

**Dependencies**:
- streamlit==1.39.0
- pandas==2.2.2
- plotly==5.24.1
- numpy==1.26.4

### Run the App
```bash
streamlit run loan_vs_overdraft_app.py
```

The app will open in your browser at `http://localhost:8501`

### Input Parameters

**In the sidebar, configure:**
1. **Amount Required**: ₹10,000 - ₹1,00,00,000
2. **Tenure**: 3 - 60 months
3. **Average Utilization**: 10% - 100% (for overdraft)
4. **Days Used Per Month**: 1 - 30 (for overdraft)
5. **Banks to Compare**: Select from dropdowns

The app will instantly recalculate all comparisons!

## 📈 Features Breakdown

### 1. Cost Comparison Summary
- Side-by-side metrics for all three options
- Total cost, monthly payment, interest rates
- Clear visual cards

### 2. Detailed Cost Breakdown
- Tabbed interface for each option
- Component-wise cost breakdown
- Key points and considerations

### 3. Visual Charts
- **Cost Component Breakdown**: Bar chart comparing fees, interest, other charges
- **Monthly Outflow**: Line chart showing monthly payments over tenure
- **Utilization Impact**: How usage percentage affects overdraft costs

### 4. Scenario-Based Recommendations
- Automated best option detection
- Savings calculations
- Situational guidance

### 5. All Banks Comparison
- Complete data tables for all banks
- Sort and compare across parameters
- Make informed bank selection

### 6. Hidden Charges Documentation
- Comprehensive list of often-missed fees
- Bank-specific charges
- Regulatory updates

## 🔬 Calculation Methodology

### Personal Loan EMI Formula
```
EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)

Where:
P = Principal amount
r = Monthly interest rate (Annual rate / 12 / 100)
n = Tenure in months
```

### Overdraft Interest Calculation
```
Monthly Interest = Utilized Amount × (Annual Rate / 365) × Days Used

Total Cost = Sum of Monthly Interest + Processing Fee + Renewal Fees
```

### Overdraft Against FD Net Cost
```
OD Interest = Utilized Amount × ((FD Rate + Spread) / 365) × Days Used
FD Interest Earned = FD Amount × (FD Rate / 100) × (Tenure / 12)

Net Cost = Total OD Interest - FD Interest Earned + Processing Fee
```

## 📚 Data Sources

Research conducted from official bank websites and financial portals (October 2025):
- HDFC Bank (hdfcbank.com)
- ICICI Bank (icicibank.com)
- Axis Bank (axisbank.com)
- State Bank of India (sbi.co.in)
- Bajaj Finserv (bajajfinserv.in)
- IDFC First Bank (idfcfirstbank.com)
- Tata Capital (tatacapital.com)
- RBI Guidelines (rbi.org.in)
- BankBazaar, PaisaBazaar, MoneyView (comparison portals)

## ⚠️ Disclaimers

1. **Rate Variations**: Actual rates vary based on:
   - Your credit score (750+ gets best rates)
   - Banking relationship (existing customers may get discounts)
   - Loan amount and tenure
   - Current market conditions
   - Promotional offers

2. **Assumptions**: Calculations assume:
   - Regular, timely repayments
   - No defaults or late payments
   - Stable credit score
   - Current regulatory environment

3. **Verification Required**: Always verify current rates with the bank before making decisions

4. **Not Financial Advice**: This tool is for comparison and educational purposes only

## 🎯 Use Cases

### Use Case 1: Emergency Fund
**Scenario**: Need ₹2 lakhs for medical emergency, will repay in 3 months

**Analysis**:
- Personal Loan @ 11%: EMI ₹67,500, Total Cost ₹5,000
- Overdraft @ 14%: If used fully for 90 days, Cost ₹6,900

**Recommendation**: Personal Loan (smaller cost, predictable)

### Use Case 2: Business Working Capital
**Scenario**: Need up to ₹5 lakhs for inventory, usage varies 30-70%, 12 months

**Analysis**:
- Personal Loan: ₹44,000 monthly EMI, Total Cost ₹28,000
- Overdraft: Avg ₹50,000 interest/month if 50% utilized, Total Cost ₹30,000 + renewal

**Recommendation**: Overdraft (flexibility worth the slight extra cost)

### Use Case 3: Debt Consolidation
**Scenario**: Consolidate ₹3 lakhs credit card debt, need 24 months

**Analysis**:
- Personal Loan @ 10.5%: Total Interest ₹33,000
- Overdraft: Would cost ₹84,000 if used fully

**Recommendation**: Personal Loan (much cheaper for long-term, full utilization)

## 🚀 Future Enhancements

Potential additions:
- [ ] Export comparison report as PDF
- [ ] Add credit score impact simulator
- [ ] Include tax benefits (if any)
- [ ] Add more banks and NBFCs
- [ ] Regional bank data
- [ ] Business loan comparisons
- [ ] Loan EMI vs SIP returns comparison
- [ ] Integration with live bank APIs

## 📞 Support

This is a research and comparison tool. For specific loan applications:
- Visit bank websites directly
- Consult a certified financial advisor
- Check your credit score before applying
- Read all terms and conditions carefully

## 📜 License

This tool is provided as-is for educational and comparison purposes.

---

**Last Updated**: October 2025
**Version**: 1.0
**Disclaimer**: Always verify current rates with banks before making financial decisions.

---

**Remember**: The cheapest option on paper may not be the best for your situation. Consider:
- Your cash flow stability
- Risk tolerance
- Need for flexibility
- Financial discipline
- Future income projections

Make informed decisions, not impulsive ones! 💪
