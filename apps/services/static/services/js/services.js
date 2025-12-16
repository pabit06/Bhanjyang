/**
 * Quick Calculators for Services Page
 */

function calculateQuickLoan() {
    const amount = parseFloat(document.getElementById('quick-loan-amount').value);
    const rate = parseFloat(document.getElementById('quick-loan-rate').value);
    const tenure = parseInt(document.getElementById('quick-loan-tenure').value);

    if (!amount || !rate || !tenure) {
        // Optional: Add UI feedback if needed, but alerting might be annoying on typing
        // alert('Please fill in all fields');
        return;
    }

    const monthlyRate = rate / 1200;
    const tenureMonths = tenure * 12;
    const emi = (amount * monthlyRate * Math.pow(1 + monthlyRate, tenureMonths)) /
        (Math.pow(1 + monthlyRate, tenureMonths) - 1);

    document.getElementById('quick-emi-amount').textContent = 'NPR ' + emi.toLocaleString('en-IN', { maximumFractionDigits: 0 });
    document.getElementById('quick-loan-result').classList.remove('hidden');
}

function calculateQuickSavings() {
    const deposit = parseFloat(document.getElementById('quick-savings-deposit').value);
    const rate = parseFloat(document.getElementById('quick-savings-rate').value);
    const period = parseInt(document.getElementById('quick-savings-period').value);

    if (!deposit || !rate || !period) {
        return;
    }

    const monthlyRate = rate / 1200;
    const totalMonths = period * 12;
    // Future Value of a Series of Annuities (Regular Deposits)
    // Formula: PMT * (((1 + r)^n - 1) / r) * (1+r) [for beginning of period] or without (1+r) [for end]
    // Simplified version used in valid code:
    const maturityAmount = deposit * (((1 + monthlyRate) ** totalMonths - 1) / monthlyRate);

    document.getElementById('quick-maturity-amount').textContent = 'NPR ' + maturityAmount.toLocaleString('en-IN', { maximumFractionDigits: 0 });
    document.getElementById('quick-savings-result').classList.remove('hidden');
}

function calculateQuickFD() {
    const amount = parseFloat(document.getElementById('quick-fd-amount').value);
    const rate = parseFloat(document.getElementById('quick-fd-rate').value);
    const duration = parseInt(document.getElementById('quick-fd-duration').value);

    if (!amount || !rate || !duration) {
        return;
    }

    const annualRate = rate / 100;
    const maturityAmount = amount * Math.pow(1 + annualRate, duration);

    document.getElementById('quick-fd-maturity').textContent = 'NPR ' + maturityAmount.toLocaleString('en-IN', { maximumFractionDigits: 0 });
    document.getElementById('quick-fd-result').classList.remove('hidden');
}

// Auto-calculate on input change
document.addEventListener('DOMContentLoaded', function () {
    // Loan calculator auto-update
    const loanInputs = ['quick-loan-amount', 'quick-loan-rate', 'quick-loan-tenure'];
    loanInputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', function () {
                if (document.getElementById('quick-loan-amount').value &&
                    document.getElementById('quick-loan-rate').value &&
                    document.getElementById('quick-loan-tenure').value) {
                    calculateQuickLoan();
                }
            });
        }
    });

    // Savings calculator auto-update
    const savingsInputs = ['quick-savings-deposit', 'quick-savings-rate', 'quick-savings-period'];
    savingsInputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', function () {
                if (document.getElementById('quick-savings-deposit').value &&
                    document.getElementById('quick-savings-rate').value &&
                    document.getElementById('quick-savings-period').value) {
                    calculateQuickSavings();
                }
            });
        }
    });

    // FD calculator auto-update
    const fdInputs = ['quick-fd-amount', 'quick-fd-rate', 'quick-fd-duration'];
    fdInputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', function () {
                if (document.getElementById('quick-fd-amount').value &&
                    document.getElementById('quick-fd-rate').value &&
                    document.getElementById('quick-fd-duration').value) {
                    calculateQuickFD();
                }
            });
        }
    });
});
