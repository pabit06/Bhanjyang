/**
 * FormField Component
 * 
 * A reusable form field component with validation, error handling,
 * and accessibility features.
 */

class FormField extends Component {
    get defaultOptions() {
        return {
            validateOnBlur: true,
            validateOnInput: false,
            showErrorDelay: 300,
            errorClass: 'field-error',
            successClass: 'field-success',
            requiredClass: 'field-required',
            disabledClass: 'field-disabled'
        };
    }

    init() {
        this.input = this.element.querySelector('input, textarea, select');
        this.label = this.element.querySelector('label');
        this.errorElement = this.element.querySelector('.field-error-message');
        this.helpElement = this.element.querySelector('.field-help');
        
        if (!this.input) {
            console.warn('FormField: No input element found');
            return;
        }

        this.setupValidation();
        this.setupAccessibility();
        this.setupStyling();
        super.init();
    }

    setupValidation() {
        if (this.options.validateOnBlur) {
            this.input.addEventListener('blur', () => this.validate());
        }

        if (this.options.validateOnInput) {
            this.input.addEventListener('input', () => this.validate());
        }

        // Real-time validation for specific field types
        if (this.input.type === 'email') {
            this.input.addEventListener('input', () => this.validateEmail());
        }

        if (this.input.type === 'tel') {
            this.input.addEventListener('input', () => this.validatePhone());
        }
    }

    setupAccessibility() {
        // Ensure proper ARIA attributes
        if (this.input && !this.input.getAttribute('aria-describedby')) {
            const helpId = this.helpElement ? this.helpElement.id : null;
            const errorId = this.errorElement ? this.errorElement.id : null;
            
            if (helpId || errorId) {
                this.input.setAttribute('aria-describedby', 
                    [helpId, errorId].filter(Boolean).join(' '));
            }
        }

        // Add required indicator
        if (this.input.required) {
            this.addClass(this.options.requiredClass);
        }
    }

    setupStyling() {
        // Add disabled styling
        if (this.input.disabled) {
            this.addClass(this.options.disabledClass);
        }

        // Add focus styling
        this.input.addEventListener('focus', () => {
            this.element.classList.add('field-focused');
        });

        this.input.addEventListener('blur', () => {
            this.element.classList.remove('field-focused');
        });
    }

    validate() {
        const value = this.input.value.trim();
        const rules = this.getValidationRules();
        
        for (const rule of rules) {
            const result = rule.validate(value);
            if (!result.valid) {
                this.showError(result.message);
                return false;
            }
        }

        this.showSuccess();
        return true;
    }

    validateEmail() {
        const email = this.input.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            this.showError('Please enter a valid email address');
            return false;
        }
        
        this.clearError();
        return true;
    }

    validatePhone() {
        const phone = this.input.value.trim();
        const phoneRegex = /^\+?1?\d{9,15}$/;
        
        if (phone && !phoneRegex.test(phone)) {
            this.showError('Please enter a valid phone number');
            return false;
        }
        
        this.clearError();
        return true;
    }

    getValidationRules() {
        const rules = [];

        // Required validation
        if (this.input.required) {
            rules.push({
                validate: (value) => ({
                    valid: value.length > 0,
                    message: `${this.getFieldLabel()} is required`
                })
            });
        }

        // Min length validation
        if (this.input.minLength) {
            rules.push({
                validate: (value) => ({
                    valid: value.length >= this.input.minLength,
                    message: `${this.getFieldLabel()} must be at least ${this.input.minLength} characters`
                })
            });
        }

        // Max length validation
        if (this.input.maxLength) {
            rules.push({
                validate: (value) => ({
                    valid: value.length <= this.input.maxLength,
                    message: `${this.getFieldLabel()} must not exceed ${this.input.maxLength} characters`
                })
            });
        }

        // Pattern validation
        if (this.input.pattern) {
            const regex = new RegExp(this.input.pattern);
            rules.push({
                validate: (value) => ({
                    valid: !value || regex.test(value),
                    message: `${this.getFieldLabel()} format is invalid`
                })
            });
        }

        return rules;
    }

    getFieldLabel() {
        if (this.label) {
            return this.label.textContent.replace('*', '').trim();
        }
        return this.input.name || 'This field';
    }

    showError(message) {
        this.removeClass(this.options.successClass);
        this.addClass(this.options.errorClass);
        
        if (this.errorElement) {
            this.errorElement.textContent = message;
            this.errorElement.style.display = 'block';
        }

        this.input.setAttribute('aria-invalid', 'true');
        this.emit('field:error', { message });
    }

    showSuccess() {
        this.removeClass(this.options.errorClass);
        this.addClass(this.options.successClass);
        
        if (this.errorElement) {
            this.errorElement.style.display = 'none';
        }

        this.input.setAttribute('aria-invalid', 'false');
        this.emit('field:success');
    }

    clearError() {
        this.removeClass(this.options.errorClass);
        this.removeClass(this.options.successClass);
        
        if (this.errorElement) {
            this.errorElement.style.display = 'none';
        }

        this.input.setAttribute('aria-invalid', 'false');
    }

    setValue(value) {
        this.input.value = value;
        this.validate();
    }

    getValue() {
        return this.input.value;
    }

    setDisabled(disabled) {
        this.input.disabled = disabled;
        if (disabled) {
            this.addClass(this.options.disabledClass);
        } else {
            this.removeClass(this.options.disabledClass);
        }
    }

    focus() {
        this.input.focus();
    }

    reset() {
        this.input.value = '';
        this.clearError();
    }
}

// Auto-initialize form fields
document.addEventListener('DOMContentLoaded', () => {
    const formFields = document.querySelectorAll('.form-field');
    formFields.forEach(field => new FormField(field));
});

// Export for use in other modules
window.FormField = FormField;
