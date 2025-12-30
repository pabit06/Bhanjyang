/**
 * Remittance Services Scripts
 * Handles Hero Slider, Exchange Rate Widget, and Partner Carousel
 */

document.addEventListener('DOMContentLoaded', function () {
    // -----------------------------------------
    // Hero Background Images
    // -----------------------------------------
    var bgElements = document.querySelectorAll('.hero-slide-bg, .pattern-bg');
    bgElements.forEach(function (element) {
        var bgImage = element.getAttribute('data-bg-image');
        if (bgImage) {
            element.style.backgroundImage = 'url(' + bgImage + ')';
        }
    });

    // -----------------------------------------
    // Hero Slider (Swiper)
    // -----------------------------------------
    if (document.querySelector(".heroSwiper")) {
        var swiper = new Swiper(".heroSwiper", {
            spaceBetween: 0,
            effect: "fade",
            speed: 2000,
            autoplay: {
                delay: 5000,
                disableOnInteraction: false,
            },
            loop: true,
            allowTouchMove: false,
        });
    }

    // -----------------------------------------
    // Exchange Rate Calculator
    // -----------------------------------------
    if (document.querySelector('.exchange-rate-widget')) {
        var exchangeRateWidget = {
            fromAmount: 1000,
            fromCurrency: 'USD',
            toCurrency: 'NPR',
            currentRate: null,

            init: function () {
                // console.log('Initializing exchange rate widget'); 
                var widget = document.querySelector('.exchange-rate-widget');
                if (!widget) return;
                this.loadExchangeRate();
                this.setupEventListeners();
            },

            loadExchangeRate: function () {
                var self = this;
                // console.log('Loading exchange rate for', self.fromCurrency);
                fetch('/api/v1/exchange-rates/current/?currency=' + self.fromCurrency + '&type=mid')
                    .then(function (response) {
                        if (!response.ok) throw new Error('Failed to fetch rate: ' + response.status);
                        return response.json();
                    })
                    .then(function (data) {
                        // console.log('Exchange rate loaded:', data);
                        self.currentRate = parseFloat(data.rate);
                        self.updateDisplay();
                    })
                    .catch(function (error) {
                        console.error('Error loading exchange rate:', error);
                        // Fallback to default rate if API fails
                        self.currentRate = 135.0; // Default USD to NPR rate
                        self.updateDisplay();
                    });
            },

            setupEventListeners: function () {
                var self = this;

                // Button to refresh rate from NRB
                var checkRateBtn = document.querySelector('.exchange-rate-widget button');
                if (checkRateBtn) {
                    checkRateBtn.addEventListener('click', function () {
                        checkRateBtn.disabled = true;
                        checkRateBtn.textContent = 'Fetching from NRB...';

                        // First fetch from NRB API
                        fetch('/api/v1/exchange-rates/fetch_nrb/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': self.getCsrfToken()
                            }
                        })
                            .then(function (response) {
                                if (!response.ok) throw new Error('Failed to fetch from NRB');
                                return response.json();
                            })
                            .then(function (data) {
                                // console.log('NRB fetch result:', data);
                                // After fetching from NRB, reload the display
                                self.loadExchangeRate();
                                checkRateBtn.textContent = 'Rate Updated!';
                                checkRateBtn.classList.add('bg-green-500');
                                setTimeout(function () {
                                    checkRateBtn.disabled = false;
                                    checkRateBtn.textContent = 'Check Today\'s Rate';
                                    checkRateBtn.classList.remove('bg-green-500');
                                }, 2000);
                            })
                            .catch(function (error) {
                                console.error('Error fetching from NRB:', error);
                                // Still reload display even if NRB fetch fails
                                self.loadExchangeRate();
                                checkRateBtn.textContent = 'Using Cached Rate';
                                checkRateBtn.classList.add('bg-yellow-500');
                                setTimeout(function () {
                                    checkRateBtn.disabled = false;
                                    checkRateBtn.textContent = 'Check Today\'s Rate';
                                    checkRateBtn.classList.remove('bg-yellow-500');
                                }, 2000);
                            });
                    });
                }

                // Input field for amount
                var amountInput = document.querySelector('.exchange-rate-widget .from-amount-input');
                if (amountInput) {
                    amountInput.addEventListener('input', function () {
                        var value = parseFloat(this.value) || 0;
                        if (value > 0) {
                            self.fromAmount = value;
                            self.updateDisplay();
                        }
                    });

                    amountInput.addEventListener('blur', function () {
                        if (!this.value || parseFloat(this.value) <= 0) {
                            this.value = 1000;
                            self.fromAmount = 1000;
                            self.updateDisplay();
                        }
                    });
                }
            },

            updateDisplay: function () {
                if (this.currentRate === null) {
                    // console.warn('No exchange rate available yet');
                    return;
                }

                var fromAmount = this.fromAmount;
                var toAmount = fromAmount * this.currentRate;

                // Format numbers with commas
                var formattedTo = this.formatNumber(toAmount);

                // Update input field value
                var amountInput = document.querySelector('.exchange-rate-widget .from-amount-input');
                if (amountInput && parseFloat(amountInput.value) !== fromAmount) {
                    amountInput.value = fromAmount;
                }

                // Update display
                var toAmountEl = document.getElementById('to-amount-display');
                if (toAmountEl) {
                    toAmountEl.textContent = formattedTo;
                    // Add animation effect
                    toAmountEl.style.transform = 'scale(1.05)';
                    setTimeout(function () {
                        toAmountEl.style.transform = 'scale(1)';
                    }, 200);
                } else {
                    // Fallback selector
                    var fallbackEl = document.querySelector('.exchange-rate-widget .to-amount');
                    if (fallbackEl) {
                        fallbackEl.textContent = formattedTo;
                    }
                }

                // console.log('Display updated:', fromAmount, 'USD =', formattedTo, 'NPR');
            },

            formatNumber: function (num) {
                return num.toLocaleString('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 0
                });
            },

            getCsrfToken: function () {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    if (cookie.startsWith('csrftoken=')) {
                        return cookie.substring('csrftoken='.length);
                    }
                }
            }
        };

        exchangeRateWidget.init();
    }
});

// -----------------------------------------
// Partner Carousel Scroll (Global Function)
// -----------------------------------------
function scrollCarousel(direction) {
    const carousel = document.getElementById('partners-carousel');
    if (!carousel) return;

    const scrollAmount = 200;
    if (direction === 'left') {
        carousel.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    } else {
        carousel.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
}
