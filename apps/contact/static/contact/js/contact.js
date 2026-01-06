// Constants
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB in bytes
const MAP_LOAD_TIMEOUT = 800; // milliseconds
const VALIDATION_DEBOUNCE_DELAY = 300; // milliseconds

// Allowed file types (matching server-side validation)
const ALLOWED_FILE_EXTENSIONS = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'];
const ALLOWED_MIME_TYPES = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg',
    'image/jpg',
    'image/png'
];

// Global toast functions (wrappers for Toast system)
function showSuccess(message, title = 'Success') {
    if (typeof Toast !== 'undefined' && Toast.success) {
        Toast.success(title ? `${title}: ${message}` : message);
    } else {
        // Fallback if Toast is not available
        console.log('Success:', title, message);
    }
}

function showError(message, title = 'Error') {
    if (typeof Toast !== 'undefined' && Toast.error) {
        Toast.error(title ? `${title}: ${message}` : message);
    } else {
        // Fallback if Toast is not available
        console.error('Error:', title, message);
    }
}

// Debounce utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('contactForm');
    const submitButton = document.getElementById('submitButton');
    const buttonText = document.getElementById('buttonText');
    const buttonIcon = document.getElementById('buttonIcon');
    const loadingIcon = document.getElementById('loadingIcon');
    const formMessages = document.getElementById('form-messages');
    const successMessage = document.getElementById('success-message');
    const errorMessage = document.getElementById('error-message');
    const validationErrors = document.getElementById('validation-errors');
    const validationList = document.getElementById('validation-list');
    const errorDetails = document.getElementById('error-details');

    if (!form) return;

    // Real-time validation with debouncing
    const formFields = form.querySelectorAll('input, textarea, select');

    // Set up aria-describedby for all form fields
    formFields.forEach(field => {
        const errorId = field.id + '_error';
        const helpId = field.id + '_help';
        const errorElement = document.getElementById(errorId);
        const helpElement = document.getElementById(helpId);

        let describedBy = [];
        if (helpElement) describedBy.push(helpId);
        if (errorElement) describedBy.push(errorId);

        if (describedBy.length > 0) {
            field.setAttribute('aria-describedby', describedBy.join(' '));
        }

        // Set aria-required for required fields
        if (field.required) {
            field.setAttribute('aria-required', 'true');
        }
    });
    const debouncedValidate = debounce(function (field) {
        validateField(field);
    }, VALIDATION_DEBOUNCE_DELAY);

    formFields.forEach(field => {
        field.addEventListener('blur', function () {
            validateField(this);
        });

        field.addEventListener('input', function () {
            clearFieldError(this);
            // Debounced validation for real-time feedback
            if (this.type !== 'file') {
                debouncedValidate(this);
            }
        });

        // Special handling for file input
        if (field.type === 'file') {
            field.addEventListener('change', function () {
                try {
                    validateFileField(this);
                } catch (error) {
                    console.error('File validation error:', error);
                    showFieldError(this, 'An error occurred while validating the file. Please try again.');
                }
            });
        }

        // Character counter for message field
        if (field.name === 'message') {
            const charCountElement = document.getElementById(field.id + '_char_count');
            if (charCountElement) {
                field.addEventListener('input', function () {
                    const length = this.value.length;
                    const minLength = 10;
                    charCountElement.textContent = `${length} characters${length < minLength ? ` (minimum ${minLength})` : ''}`;
                    if (length < minLength) {
                        charCountElement.classList.add('text-yellow-600');
                        charCountElement.classList.remove('text-gray-500');
                    } else {
                        charCountElement.classList.remove('text-yellow-600');
                        charCountElement.classList.add('text-gray-500');
                    }
                });
            }
        }
    });

    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;

        clearFieldError(field);

        // Required field validation
        if (field.required && !value) {
            showFieldError(field, `${getFieldLabel(fieldName)} is required.`);
            return false;
        }

        // Specific field validations
        switch (fieldName) {
            case 'name':
                if (value && value.length < 2) {
                    showFieldError(field, 'Name must be at least 2 characters long.');
                    return false;
                }
                if (value && !/^[a-zA-Z\s\-'\.]+$/.test(value)) {
                    showFieldError(field, 'Name can only contain letters, spaces, hyphens, apostrophes, and periods.');
                    return false;
                }
                break;

            case 'email':
                if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                    showFieldError(field, 'Please enter a valid email address.');
                    return false;
                }
                break;

            case 'phone':
                if (value) {
                    const cleanedPhone = value.replace(/[^\d+]/g, '');
                    if (cleanedPhone.length < 7 || cleanedPhone.length > 15) {
                        showFieldError(field, 'Please enter a valid phone number.');
                        return false;
                    }
                }
                break;

            case 'message':
                if (value && value.length < 10) {
                    showFieldError(field, 'Message must be at least 10 characters long.');
                    return false;
                }
                break;
        }
        return true;
    }

    function validateFileField(field) {
        try {
            const file = field.files[0];
            if (file) {
                clearFieldError(field);

                // Check file size (5MB limit)
                if (file.size > MAX_FILE_SIZE) {
                    showFieldError(field, 'File size cannot exceed 5MB.');
                    return false;
                }

                // Check file extension (matching server-side validation)
                const fileExtension = '.' + file.name.toLowerCase().split('.').pop();
                if (!ALLOWED_FILE_EXTENSIONS.includes(fileExtension)) {
                    showFieldError(field, 'Please upload a valid file type (PDF, DOC, DOCX, JPG, PNG only).');
                    return false;
                }

                // Check MIME type (additional validation)
                if (file.type && !ALLOWED_MIME_TYPES.includes(file.type)) {
                    showFieldError(field, 'Please upload a valid file type (PDF, DOC, DOCX, JPG, PNG only).');
                    return false;
                }
            }
            return true;
        } catch (error) {
            console.error('File validation error:', error);
            showFieldError(field, 'An error occurred while validating the file. Please try again.');
            return false;
        }
    }

    function showFieldError(field, message) {
        const errorElement = field.parentElement.querySelector('.error-message') ||
            document.getElementById(field.id + '_error');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
            field.classList.add('border-red-500', 'focus:ring-red-500');
            field.classList.remove('border-gray-300', 'focus:ring-deuraligreen');
            // Ensure aria-describedby includes error element
            const describedBy = field.getAttribute('aria-describedby') || '';
            if (!describedBy.includes(errorElement.id)) {
                field.setAttribute('aria-describedby',
                    (describedBy ? describedBy + ' ' : '') + errorElement.id);
            }
            field.setAttribute('aria-invalid', 'true');
        }
    }

    function clearFieldError(field) {
        const errorElement = field.parentElement.querySelector('.error-message') ||
            document.getElementById(field.id + '_error');
        if (errorElement) {
            errorElement.classList.add('hidden');
            errorElement.textContent = '';
            field.classList.remove('border-red-500', 'focus:ring-red-500');
            field.classList.add('border-gray-300', 'focus:ring-deuraligreen');
            field.setAttribute('aria-invalid', 'false');
        }
    }

    function getFieldLabel(fieldName) {
        const labels = {
            'name': 'Name',
            'email': 'Email',
            'phone': 'Phone',
            'message': 'Message'
        };
        return labels[fieldName] || fieldName;
    }

    function hideAllMessages() {
        successMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');
        validationErrors.classList.add('hidden');
    }

    function showSuccessMessage() {
        hideAllMessages();
        successMessage.classList.remove('hidden');
        form.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Also show sticky notice
        showSuccess("Thank you! Your message has been sent successfully.", "Message Sent");
    }

    function showErrorMessage(message) {
        hideAllMessages();
        errorDetails.textContent = message;
        errorMessage.classList.remove('hidden');
        form.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Also show sticky notice
        showError(message, "Error");
    }

    function showValidationErrors(errors) {
        hideAllMessages();
        validationList.innerHTML = '';

        Object.keys(errors).forEach(field => {
            errors[field].forEach(error => {
                const li = document.createElement('li');
                li.textContent = `${getFieldLabel(field)}: ${error}`;
                validationList.appendChild(li);
            });
            // Also show field-level errors
            const fieldElement = form.querySelector(`[name="${field}"]`);
            if (fieldElement && errors[field].length > 0) {
                showFieldError(fieldElement, errors[field][0]);
            }
        });

        validationErrors.classList.remove('hidden');
        form.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function setLoadingState(loading) {
        if (loading) {
            submitButton.disabled = true;
            buttonText.textContent = 'Sending...';
            buttonIcon.classList.add('hidden');
            loadingIcon.classList.remove('hidden');
            submitButton.classList.add('opacity-75');
        } else {
            submitButton.disabled = false;
            buttonText.textContent = 'Send Message';
            buttonIcon.classList.remove('hidden');
            loadingIcon.classList.add('hidden');
            submitButton.classList.remove('opacity-75');
        }
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        try {
            // Validate all fields
            let isValid = true;
            const errors = {};

            formFields.forEach(field => {
                let fieldValid = true;
                try {
                    if (field.type === 'file') {
                        fieldValid = validateFileField(field);
                    } else {
                        fieldValid = validateField(field);
                    }
                } catch (error) {
                    console.error('Validation error for field:', field.name, error);
                    fieldValid = false;
                }

                if (!fieldValid) {
                    isValid = false;
                    const fieldName = field.name;
                    if (!errors[fieldName]) {
                        errors[fieldName] = [];
                    }
                    const errorElement = field.parentElement.querySelector('.error-message') ||
                        document.getElementById(field.id + '_error');
                    if (errorElement && !errorElement.classList.contains('hidden') && errorElement.textContent) {
                        errors[fieldName].push(errorElement.textContent);
                    }
                }
            });

            if (!isValid) {
                showValidationErrors(errors);
                return;
            }

            setLoadingState(true);
            hideAllMessages();

            const formData = new FormData(form);
            const csrftoken = form.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    // Check if response is JSON
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        return response.json();
                    } else {
                        return response.text().then(text => {
                            throw new Error('Server returned non-JSON response');
                        });
                    }
                })
                .then(data => {
                    if (data.success) {
                        showSuccessMessage();
                        // Explicitly clear file inputs
                        formFields.forEach(field => {
                            if (field.type === 'file') {
                                field.value = '';
                            }
                            clearFieldError(field);
                        });
                        form.reset();
                        // Clear character counter
                        const messageField = form.querySelector('[name="message"]');
                        if (messageField) {
                            const charCount = document.getElementById(messageField.id + '_char_count');
                            if (charCount) {
                                charCount.textContent = '';
                            }
                        }
                    } else {
                        if (data.errors) {
                            showValidationErrors(data.errors);
                        } else {
                            showErrorMessage(data.message || 'An error occurred while sending your message.');
                        }
                    }
                })
                .catch(error => {
                    console.error('Form submission error:', error);
                    showErrorMessage('Network error. Please check your connection and try again.');
                })
                .finally(() => {
                    setLoadingState(false);
                });
        } catch (error) {
            console.error('Form submission error:', error);
            setLoadingState(false);
            showErrorMessage('An unexpected error occurred. Please try again.');
        }
    });

    // Track form changes for beforeunload warning
    let formHasData = false;
    formFields.forEach(field => {
        field.addEventListener('input', function () {
            formHasData = true;
        });
    });

    window.addEventListener('beforeunload', function (e) {
        if (formHasData) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });

    // Reset formHasData flag after successful submission
    const originalShowSuccessMessage = showSuccessMessage;
    showSuccessMessage = function () {
        formHasData = false;
        originalShowSuccessMessage();
    };
});

// Modern Toggle Switch functionality for Map Locations (consolidated into main DOMContentLoaded)
document.addEventListener('DOMContentLoaded', function () {
    const mapToggleMain = document.getElementById('map-toggle-main');
    const mapToggleService = document.getElementById('map-toggle-service');
    const mapToggleSlider = document.getElementById('map-toggle-slider');
    const mapIframe = document.getElementById('location-map-iframe');
    const mapLoading = document.getElementById('map-loading');

    if (!mapToggleMain || !mapToggleService || !mapIframe) return;

    let currentLocation = 'main'; // Track current location

    // Map sources
    const mapSources = {
        main: 'https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d7037.612645021445!2d84.149533!3d28.121932!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3995a3aea5af600d%3A0xacb415d2023a9c80!2sBhanjyang%20Saving%20%26%20Credit%20Cooperative%20Society%20Ltd.!5e0!3m2!1sen!2snp!4v1760763305577!5m2!1sen!2snp',
        service: 'https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d14886.364800504987!2d84.20693577278259!3d28.108180724514312!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3995a1bd584f5877%3A0x8c71bcb5b99757ed!2sBhanjyang%20Saving%20%26%20Credit%20Cooperative%20Society%20Ltd.%20Polyang%20Branch!5e0!3m2!1sen!2snp!4v1760763359401!5m2!1sen!2snp'
    };

    function updateToggleState(location) {
        if (!mapToggleMain || !mapToggleService || !mapToggleSlider) return;

        currentLocation = location;
        const isMain = location === 'main';

        // Both buttons have fixed width, so use that for calculations
        const buttonWidth = mapToggleMain.offsetWidth || 160;

        // Update slider position with smooth animation
        if (isMain) {
            mapToggleSlider.style.transform = 'translateX(0)';
            mapToggleSlider.style.backgroundColor = '#059669'; // deuraligreen
        } else {
            // Move slider to the position of the Service Center button
            mapToggleSlider.style.transform = `translateX(${buttonWidth}px)`;
            mapToggleSlider.style.backgroundColor = '#dc2626'; // bhanjyangred
        }

        // Update button text colors for better contrast
        if (isMain) {
            mapToggleMain.classList.remove('text-gray-600');
            mapToggleMain.classList.add('text-white');
            mapToggleMain.setAttribute('aria-pressed', 'true');
            mapToggleService.classList.remove('text-white');
            mapToggleService.classList.add('text-gray-600');
            mapToggleService.setAttribute('aria-pressed', 'false');
        } else {
            mapToggleService.classList.remove('text-gray-600');
            mapToggleService.classList.add('text-white');
            mapToggleService.setAttribute('aria-pressed', 'true');
            mapToggleMain.classList.remove('text-white');
            mapToggleMain.classList.add('text-gray-600');
            mapToggleMain.setAttribute('aria-pressed', 'false');
        }
    }

    function switchMap(location) {
        if (!mapIframe || currentLocation === location) return;

        const newSrc = mapSources[location];
        if (newSrc && newSrc !== mapIframe.src) {
            // Show loading spinner
            if (mapLoading) {
                mapLoading.classList.remove('hidden');
                mapIframe.style.opacity = '0.3';
            }

            // Update toggle state
            updateToggleState(location);

            // Change map source
            mapIframe.src = newSrc;

            // Use iframe load event instead of fixed timeout
            const handleMapLoad = function () {
                if (mapLoading) {
                    mapLoading.classList.add('hidden');
                    mapIframe.style.opacity = '1';
                }
                mapIframe.removeEventListener('load', handleMapLoad);
            };

            mapIframe.addEventListener('load', handleMapLoad);

            // Fallback timeout in case load event doesn't fire
            setTimeout(() => {
                if (mapLoading && !mapLoading.classList.contains('hidden')) {
                    mapLoading.classList.add('hidden');
                    mapIframe.style.opacity = '1';
                }
            }, MAP_LOAD_TIMEOUT);
        }
    }

    // Event listeners for toggle buttons with keyboard support
    if (mapToggleMain) {
        mapToggleMain.setAttribute('role', 'button');
        mapToggleMain.setAttribute('aria-pressed', 'true');
        mapToggleMain.setAttribute('tabindex', '0');
        mapToggleMain.addEventListener('click', function () {
            switchMap('main');
        });
        mapToggleMain.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                switchMap('main');
            }
        });
    }

    if (mapToggleService) {
        mapToggleService.setAttribute('role', 'button');
        mapToggleService.setAttribute('aria-pressed', 'false');
        mapToggleService.setAttribute('tabindex', '0');
        mapToggleService.addEventListener('click', function () {
            switchMap('service');
        });
        mapToggleService.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                switchMap('service');
            }
        });
    }

    // Initialize with Main Office selected
    // Use setTimeout to ensure DOM is fully rendered before calculating widths
    setTimeout(() => {
        updateToggleState('main');
    }, 100);
});

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Register service worker from the root to control the whole app
        // Note: This requires a view to serve sw.js from /sw.js
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('✅ Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                // Fail silently, PWA is progressive enhancement
                console.log('Service Worker registration failed:', error);
            });
    });
}

// Google Analytics Tracking
function trackEvent(action, category, label, value) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': category,
            'event_label': label,
            'value': value
        });
    }
}

// Track contact form submissions
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('contactForm');
    if (form) {
        form.addEventListener('submit', function () {
            trackEvent('submit', 'Contact', 'Contact Form Submission');
        });
    }

    // Track email/phone clicks
    document.querySelectorAll('a[href^="mailto:"]').forEach(link => {
        link.addEventListener('click', function () {
            trackEvent('click', 'Contact', 'Email Click', link.href);
        });
    });

    document.querySelectorAll('a[href^="tel:"]').forEach(link => {
        link.addEventListener('click', function () {
            trackEvent('click', 'Contact', 'Phone Click', link.href);
        });
    });

    // Track map location toggles
    const mapToggleMain = document.getElementById('map-toggle-main');
    const mapToggleService = document.getElementById('map-toggle-service');

    if (mapToggleMain) {
        mapToggleMain.addEventListener('click', () => {
            trackEvent('click', 'Map', 'Switch Location', 'Main Office');
        });
    }

    if (mapToggleService) {
        mapToggleService.addEventListener('click', () => {
            trackEvent('click', 'Map', 'Switch Location', 'Service Center');
        });
    }
});
