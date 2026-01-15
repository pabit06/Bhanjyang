# 🚀 Quick Test Guide (15 Minutes)

## ⚡ Fast Test Checklist

### ✅ Pre-Flight Check (1 minute)
- [ ] Django server is running (`py manage.py runserver`)
- [ ] Browser DevTools open (F12)
- [ ] Console tab visible (check for errors)

---

## 📋 Test Sequence

### 1. List Pages Test (5 minutes)

#### Remittance Services (`/services/remittance/`)
- [ ] **Hero Section**: 3 slides auto-play every 5 seconds
- [ ] **Exchange Rate Widget**: 
  - Currency dropdown opens
  - Select different currency (USD → EUR)
  - Click "Check Today's Rate" button
  - Rate displays correctly
- [ ] **Scroll Down**: Watch for scroll animations
- [ ] **Partner Logos**: Marquee scrolls horizontally
- [ ] **Service Cards**: Hover shows shadow/elevation
- [ ] **Click Card**: Navigates to detail page

#### Digital Services (`/services/digital-services/`)
- [ ] **Hero Section**: 3 slides auto-play
- [ ] **Scroll Down**: Watch animations
- [ ] **Service Cards**: Hover effects work
- [ ] **Mobile Banking Section**: App download buttons visible

#### Loan Services (`/services/loans/`)
- [ ] **Hero Section**: Displays correctly
- [ ] **Featured Loans**: Cards display
- [ ] **All Loans Grid**: 4-column layout (desktop)
- [ ] **Scroll Animations**: Elements fade in

#### Member Relief (`/services/member-relief/`)
- [ ] **Hero Section**: Purple gradient displays
- [ ] **Program Cards**: Display by category
- [ ] **Application Process**: 4 steps visible
- [ ] **Scroll Animations**: Work smoothly

#### Savings Accounts (`/services/savings/`)
- [ ] **Hero Section**: Green gradient displays
- [ ] **Featured Accounts**: Cards display
- [ ] **Fixed Deposit Table**: Scrolls horizontally (mobile)
- [ ] **Categories**: Regular, Optional, Recurring, Periodic

---

### 2. Detail Pages Test (7 minutes)

#### Loan Detail (`/services/loans/{any-loan-slug}/`)
- [ ] **Hero Section**: Red gradient, stats display
- [ ] **EMI Calculator**:
  - Enter: Amount = 100000, Tenure = 5 years
  - Select: Monthly payment
  - Click "Calculate EMI"
  - ✅ Results show: EMI Amount, Total Amount, Interest Amount
- [ ] **Sidebar**: Loan information displays
- [ ] **Benefits Section**: Shows checkmarks

#### Savings Detail (`/services/savings/{any-savings-slug}/`)
- [ ] **Hero Section**: Green gradient displays
- [ ] **Returns Calculator**:
  - Enter: Monthly Deposit = 5000, Years = 3
  - Click "Calculate Returns"
  - ✅ Results show: Maturity Amount, Total Deposits, Interest Earned
- [ ] **Sidebar**: Service information displays

#### Fixed Deposit Detail (`/services/fixed-deposit/{any-fd-slug}/`)
- [ ] **Hero Section**: Orange gradient displays
- [ ] **FD Calculator**:
  - Enter: Deposit Amount = 100000
  - Click "Calculate Returns"
  - ✅ Results show: Maturity Amount, Principal, Interest Earned
- [ ] **Sidebar**: Deposit information displays

#### Remittance Detail (`/services/remittance/{any-remittance-slug}/`)
- [ ] **Hero Section**: Service-specific background
- [ ] **Service Logo**: Displays correctly
- [ ] **Payout Methods**: 3 cards display
- [ ] **Scroll Animations**: Work on scroll

#### Digital Detail (`/services/digital/{any-digital-slug}/`)
- [ ] **Hero Section**: Green gradient displays
- [ ] **Service Details**: Description displays
- [ ] **Features Section**: Lists features
- [ ] **Mobile Banking Promo**: App download buttons

#### Member Relief Detail (`/services/member-relief/{any-relief-slug}/`)
- [ ] **Hero Section**: Purple gradient displays
- [ ] **Eligibility**: Green card displays
- [ ] **Benefits**: Blue card displays
- [ ] **Application Process**: Steps visible

---

### 3. Mobile Responsiveness (3 minutes)

1. **Open DevTools** (F12)
2. **Toggle Device Toolbar** (Ctrl+Shift+M or Cmd+Shift+M)
3. **Test at 375px width**:
   - [ ] Layout stacks vertically
   - [ ] Text is readable
   - [ ] Buttons are tappable (min 44px)
   - [ ] Cards stack properly
   - [ ] Tables scroll horizontally

4. **Test at 768px width**:
   - [ ] 2-column grids work
   - [ ] Sidebars stack if needed
   - [ ] Text remains readable

5. **Test at 1920px width**:
   - [ ] Full layouts display
   - [ ] Multi-column grids work
   - [ ] Hover effects work

---

## 🔍 Quick Issues Check

### Console Errors
- [ ] Open Console (F12 → Console)
- [ ] Reload page
- [ ] ✅ No red errors
- [ ] ⚠️ Warnings are acceptable

### Network Errors
- [ ] Open Network tab (F12 → Network)
- [ ] Reload page
- [ ] ✅ No 404 errors
- [ ] ✅ Images load
- [ ] ✅ CSS/JS files load

### Visual Issues
- [ ] Pattern backgrounds too dark? → Adjust opacity
- [ ] Text unreadable? → Check contrast
- [ ] Cards overlapping? → Check grid
- [ ] Images not loading? → Check paths

---

## ⚡ Quick Fixes

### If Scroll Animations Don't Work:
```javascript
// Check if remittance.js is loaded
// In console, type:
document.querySelector('.scroll-reveal')
// Should return an element
```

### If Calculators Don't Work:
```javascript
// Check if inputs exist
document.getElementById('loan-amount')
// Should return input element
```

### If Pattern Backgrounds Don't Show:
```css
/* Check if CSS is loaded */
/* In DevTools → Elements → Styles */
/* Look for background-image with pattern URLs */
```

---

## ✅ Quick Sign-off

**Tested Pages**: ☐ All List ☐ All Detail  
**Calculators**: ☐ Loan ☐ Savings ☐ FD  
**Mobile**: ☐ Responsive  
**Console**: ☐ No Errors  
**Status**: ☐ Pass ☐ Fail ☐ Needs Review

**Time Taken**: ________ minutes  
**Issues Found**: ________  
**Ready for Production**: ☐ Yes ☐ No

---

## 🐛 Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Animations not working | Check `remittance.js` is loaded |
| Calculator not calculating | Check input values are numbers |
| Pattern too dark | Reduce opacity in CSS |
| Mobile layout broken | Check grid classes |
| Images not loading | Verify static file paths |

---

**Start Testing Now!** 🚀

