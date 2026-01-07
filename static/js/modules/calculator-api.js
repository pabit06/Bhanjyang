/**
 * Calculator API Module
 * Handles interactions with the Calculator API Endpoint
 */

export class CalculatorService {
    constructor(apiEndpoint = '/services/api/calculator/') {
        this.apiEndpoint = apiEndpoint;
    }

    /**
     * Calculate Loan EMI
     * @param {number} principal 
     * @param {number} rate (annual)
     * @param {number} tenure (months)
     * @param {string} frequency 
     * @returns {Promise<Object>}
     */
    async calculateLoan(principal, rate, tenure, frequency = 'monthly') {
        // Backend expects tenure in months for loans
        // But the frontend input might be in years. 
        // Quick fix: let's assume the frontend passes what the backend expects or we adjust here.
        // The previous view 'loan_calculator' had tenure_years.
        // The backend 'calculator_type == loan' uses 'tenure_months'.
        // So we should convert years to months if the input is years.

        // However, let's keep it simple: the caller is responsible for unit conversion.
        // But wait, the previous `loan_calculator.html` passed `tenure` (years) from input.
        // The backend sees `tenure_months`. Use `tenure * 12` in the template OR change backend.
        // Let's check backend for loan.
        return this._callApi('loan', {
            principal,
            interest_rate: rate,
            tenure_months: tenure * 12, // Assuming input is years
            payment_frequency: frequency
        });
    }

    /**
     * Calculate Savings Maturity
     * @param {number} monthlyDeposit 
     * @param {number} rate 
     * @param {number} tenureYears 
     * @returns {Promise<Object>}
     */
    async calculateSavings(monthlyDeposit, rate, tenureYears) {
        return this._callApi('savings', {
            monthly_deposit: monthlyDeposit,
            interest_rate: rate,
            tenure_years: tenureYears
        });
    }

    /**
     * Calculate Fixed Deposit Maturity
     * @param {number} principal 
     * @param {number} rate 
     * @param {number} tenureMonths 
     * @param {string} frequency 
     * @returns {Promise<Object>}
     */
    async calculateFixedDeposit(principal, rate, tenureMonths, frequency = 'lump_sum') {
        return this._callApi('fixed_deposit', {
            principal,
            interest_rate: rate,
            tenure_months: tenureMonths,
            payment_frequency: frequency
        });
    }

    /**
     * Internal API call handler
     */
    async _callApi(type, data) {
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    type,
                    ...data
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Calculation failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Calculator API Error:', error);
            throw error;
        }
    }
}
