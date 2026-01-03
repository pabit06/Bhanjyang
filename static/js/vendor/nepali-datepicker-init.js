/**
 * Nepali Datepicker Initialization
 * Automatically initializes Nepali datepicker on all inputs with class 'nepali-datepicker'
 * 
 * Usage:
 * - Add class 'nepali-datepicker' to any input field
 * - For date range, add class 'nepali-datepicker-range'
 * - For datetime, add class 'nepali-datepicker-datetime'
 */

(function() {
    'use strict';

    // Wait for NepaliDatePicker library to be available
    function waitForNepaliDatePicker(callback, maxAttempts = 200, interval = 50) {
        let attempts = 0;
        const checkLibrary = function() {
            // Check if library is available - check multiple ways
            if (typeof NepaliDatePicker !== 'undefined' || 
                (typeof window !== 'undefined' && window.NepaliDatePicker) ||
                (typeof HTMLElement !== 'undefined' && HTMLElement.prototype.NepaliDatePicker)) {
                // Library is loaded, execute callback
                callback();
            } else if (attempts < maxAttempts) {
                attempts++;
                setTimeout(checkLibrary, interval);
            } else {
                console.error('NepaliDatePicker library not loaded after ' + (maxAttempts * interval) + 'ms.');
                console.error('Please ensure nepali.datepicker.v5.0.6.min.js is loaded before this script.');
                console.error('Current window.NepaliDatePicker:', typeof window !== 'undefined' ? typeof window.NepaliDatePicker : 'window undefined');
            }
        };
        checkLibrary();
    }

    // Wait for DOM to be ready
    function initNepaliDatepickers() {
        // Check if NepaliDatePicker is available
        if (typeof NepaliDatePicker === 'undefined') {
            // Wait for library to load
            waitForNepaliDatePicker(function() {
                initializeDatepickers();
            });
            return;
        }
        
        initializeDatepickers();
    }
    
    function initializeDatepickers() {

        // Initialize standard date pickers with both AD and BS dates visible
        const dateInputs = document.querySelectorAll('.nepali-datepicker:not([data-nepali-init])');
        dateInputs.forEach(function(input) {
            try {
                input.NepaliDatePicker({
                    dateFormat: "YYYY-MM-DD",
                    language: "nepali",
                    ndpYear: true,
                    ndpMonth: true,
                    ndpYearCount: 10,
                    disableDaysAfter: null,
                    disableDaysBefore: null,
                    readOnlyInput: false,
                    miniEnglishDates: true, // Show English (AD) dates alongside Nepali (BS) dates
                    onChange: function() {
                        // Trigger change event for form validation
                        if (input.dispatchEvent) {
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                });
                input.setAttribute('data-nepali-init', 'true');
            } catch (e) {
                console.error('Error initializing Nepali datepicker:', e);
            }
        });

        // Initialize date range pickers
        const rangeInputs = document.querySelectorAll('.nepali-datepicker-range:not([data-nepali-init])');
        rangeInputs.forEach(function(input) {
            try {
                input.NepaliDatePicker({
                    range: true,
                    dateFormat: "YYYY-MM-DD",
                    language: "nepali"
                });
                input.setAttribute('data-nepali-init', 'true');
            } catch (e) {
                console.error('Error initializing Nepali datepicker range:', e);
            }
        });

        // Initialize datetime pickers (for DateTimeField) with both AD and BS dates
        const datetimeInputs = document.querySelectorAll('.nepali-datepicker-datetime:not([data-nepali-init])');
        datetimeInputs.forEach(function(input) {
            try {
                input.NepaliDatePicker({
                    dateFormat: "YYYY-MM-DD",
                    language: "nepali",
                    timepicker: true,
                    miniEnglishDates: true, // Show English (AD) dates alongside Nepali (BS) dates
                    onChange: function() {
                        // Trigger change event for form validation
                        if (input.dispatchEvent) {
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                });
                input.setAttribute('data-nepali-init', 'true');
            } catch (e) {
                console.error('Error initializing Nepali datetime picker:', e);
            }
        });
    }

    // Initialize on DOM ready - with additional wait for library
    function startInitialization() {
        // Always wait for library first, then check DOM
        waitForNepaliDatePicker(function() {
            // Library is loaded, now check DOM
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initializeDatepickers);
            } else {
                // DOM is ready, initialize immediately
                initializeDatepickers();
            }
        });
    }
    
    // Start initialization
    startInitialization();

    // Re-initialize for dynamically added elements (e.g., AJAX forms)
    window.initNepaliDatepicker = function(element) {
        if (element && element.classList && element.classList.contains('nepali-datepicker')) {
            if (!element.hasAttribute('data-nepali-init')) {
                try {
                    element.NepaliDatePicker({
                        dateFormat: "YYYY-MM-DD",
                        language: "nepali",
                        ndpYear: true,
                        ndpMonth: true,
                        ndpYearCount: 10,
                        miniEnglishDates: true, // Show English (AD) dates alongside Nepali (BS) dates
                        onChange: function() {
                            if (element.dispatchEvent) {
                                element.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        }
                    });
                    element.setAttribute('data-nepali-init', 'true');
                } catch (e) {
                    console.error('Error initializing Nepali datepicker:', e);
                }
            }
        }
    };

    // Export for use in other scripts
    window.NepaliDatepickerInit = {
        init: initNepaliDatepickers,
        initElement: window.initNepaliDatepicker
    };
})();

