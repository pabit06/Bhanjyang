# 🧪 Step-by-Step Testing Guide

## ✅ Pre-Test Status
- **Remittance Services**: 6 available
- **Loan Services**: 6 available  
- **Savings Accounts**: 6 available
- **Member Relief**: 4 available
- **Digital Services**: 2 available

---

## 🚀 Start Testing (15 Minutes)

### Step 1: Open Test Dashboard (30 seconds)
1. Open `test_pages.html` in your browser
2. Or go directly to: `http://127.0.0.1:8000/services/remittance/`
3. **Open DevTools** (Press F12)
4. **Go to Console tab** (should be empty or minimal)

---

### Step 2: Test Remittance List Page (2 minutes)

**URL**: `http://127.0.0.1:8000/services/remittance/`

#### Visual Check:
- [ ] Hero section shows 3 slides (auto-plays every 5 seconds)
- [ ] Green gradient background visible
- [ ] Pattern overlay is subtle (not too dark)
- [ ] Text "विदेशको कमाई..." is readable
- [ ] Stats section shows (24/7 Available, 100% Secure)

#### Exchange Rate Widget:
- [ ] Widget is visible below hero
- [ ] Currency dropdown shows "USD" by default
- [ ] Click dropdown → Select "EUR"
- [ ] Flag changes to European flag
- [ ] Click "Check Today's Rate" button
- [ ] Loading spinner appears briefly
- [ ] Rate displays (e.g., "1 EUR = XXX NPR")
- [ ] No error messages

#### Scroll Test:
- [ ] Scroll down slowly
- [ ] Watch "Partners Section" fade in
- [ ] Watch "How It Works" section animate
- [ ] Watch service cards scale in

#### Interactive Elements:
- [ ] Hover over service cards → Shadow increases
- [ ] Click a service card → Navigates to detail page
- [ ] Partner logos marquee scrolls (if present)

**Console Check**: 
- [ ] No red errors
- [ ] Should see: "Initializing exchange rate widget"
- [ ] Should see: "Loading exchange rate for USD"

---

### Step 3: Test Loan List Page (1 minute)

**URL**: `http://127.0.0.1:8000/services/loans/`

#### Visual Check:
- [ ] Hero section with red gradient
- [ ] Stats show: "10.5%", "6+ Loan Types", "24/7"
- [ ] Pattern backgrounds visible (subtle)

#### Scroll Test:
- [ ] Scroll down → Featured loans fade in
- [ ] Scroll more → All loans grid displays
- [ ] Cards have hover effects

#### Click Test:
- [ ] Click any loan card
- [ ] Should navigate to loan detail page

**Console Check**: 
- [ ] No errors

---

### Step 4: Test Loan Detail Page - Calculator (2 minutes)

**URL**: Navigate from loan list or use: `http://127.0.0.1:8000/services/loans/{any-loan-slug}/`

#### Visual Check:
- [ ] Hero section displays loan name
- [ ] Stats show interest rate, min/max amounts
- [ ] Scroll to calculator section

#### Calculator Test:
1. **Enter Values**:
   - Loan Amount: `100000`
   - Tenure: `5` years
   - Payment Frequency: `Monthly`

2. **Click "Calculate EMI"**:
   - [ ] Results section appears
   - [ ] Shows "EMI Amount" (e.g., "NPR 2,XXX")
   - [ ] Shows "Total Amount" (e.g., "NPR 1XX,XXX")
   - [ ] Shows "Interest Amount" (e.g., "NPR XX,XXX")

3. **Change Values**:
   - Change amount to `200000`
   - [ ] Results update automatically (if auto-calculate enabled)

**Console Check**:
- [ ] No calculation errors
- [ ] No JavaScript exceptions

---

### Step 5: Test Savings Detail Page - Calculator (2 minutes)

**URL**: Navigate from savings list

#### Calculator Test:
1. **Enter Values**:
   - Monthly Deposit: `5000`
   - Savings Period: `3` years

2. **Click "Calculate Returns"**:
   - [ ] Results appear
   - [ ] Shows "Maturity Amount"
   - [ ] Shows "Total Deposits" (should be 5000 × 36 = 180,000)
   - [ ] Shows "Interest Earned"

3. **Auto-Calculate**:
   - Change monthly deposit
   - [ ] Results update automatically

---

### Step 6: Test Fixed Deposit Detail Page - Calculator (2 minutes)

**URL**: Navigate from savings list → Fixed Deposit section

#### Calculator Test:
1. **Enter Deposit Amount**: `100000`
2. **Click "Calculate Returns"**:
   - [ ] Results appear
   - [ ] Shows "Maturity Amount"
   - [ ] Shows "Principal Amount" (100,000)
   - [ ] Shows "Interest Earned"

---

### Step 7: Mobile Responsiveness Test (3 minutes)

1. **Open DevTools** (F12)
2. **Toggle Device Toolbar** (Ctrl+Shift+M or Cmd+Shift+M)
3. **Select "iPhone 12 Pro"** (390px width)

#### Test Remittance Page:
- [ ] Layout stacks vertically
- [ ] Hero text is readable
- [ ] Exchange rate widget fits
- [ ] Service cards stack (1 column)
- [ ] Text is not too small
- [ ] Buttons are tappable (min 44px height)

#### Test Loan Detail Page:
- [ ] Calculator form stacks
- [ ] Results display below form
- [ ] Sidebar stacks below content
- [ ] All text readable

#### Test at Tablet Size (768px):
- [ ] 2-column grids work
- [ ] Cards display in grid
- [ ] Layout adapts properly

---

### Step 8: Console & Network Check (2 minutes)

#### Console Check:
1. **Open Console** (F12 → Console)
2. **Reload each page**
3. **Check for**:
   - [ ] No red errors
   - [ ] Warnings are acceptable
   - [ ] Exchange rate logs appear (on remittance page)

#### Network Check:
1. **Open Network tab** (F12 → Network)
2. **Reload page**
3. **Check for**:
   - [ ] No 404 errors (red entries)
   - [ ] CSS files load (remittance.css)
   - [ ] JS files load (remittance.js)
   - [ ] Images load (patterns, heroes)
   - [ ] CDN assets load (Swiper, Font Awesome)

---

## 🐛 Common Issues & Quick Fixes

### Issue: Scroll Animations Not Working
**Check**: 
```javascript
// In console, type:
document.querySelector('.scroll-reveal')
// Should return an element
```
**Fix**: Verify `remittance.js` is loaded

### Issue: Calculator Not Calculating
**Check**:
```javascript
// In console, type:
document.getElementById('loan-amount')
// Should return input element
```
**Fix**: Verify input IDs match JavaScript selectors

### Issue: Pattern Backgrounds Too Dark
**Fix**: Adjust opacity in CSS (currently 3-20%)

### Issue: Exchange Rate Widget Not Loading
**Check**: 
- API endpoint is accessible
- CSRF token is present
- Network tab shows API call

---

## ✅ Test Results Log

### Remittance List
- Hero: ☐ Pass ☐ Fail
- Exchange Widget: ☐ Pass ☐ Fail
- Animations: ☐ Pass ☐ Fail
- Mobile: ☐ Pass ☐ Fail

### Loan Detail
- Calculator: ☐ Pass ☐ Fail
- Results: ☐ Pass ☐ Fail
- Mobile: ☐ Pass ☐ Fail

### Savings Detail
- Calculator: ☐ Pass ☐ Fail
- Results: ☐ Pass ☐ Fail

### Fixed Deposit Detail
- Calculator: ☐ Pass ☐ Fail
- Results: ☐ Pass ☐ Fail

### Overall
- Console Errors: ☐ None ☐ Some
- Network Errors: ☐ None ☐ Some
- Mobile Responsive: ☐ Yes ☐ No
- **Status**: ☐ Ready ☐ Needs Fixes

---

## 📝 Issues Found

1. 
2. 
3. 

---

**Time Taken**: ________ minutes  
**Ready for Production**: ☐ Yes ☐ No

