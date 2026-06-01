/**
 * Remittance Services Scripts
 * Handles Hero Slider, Exchange Rate Widget, Partner Carousel, and Enhanced Interactions
 */

document.addEventListener('DOMContentLoaded', function () {
    // -----------------------------------------
    // Hero Background Images (memory-friendly: only active slide)
    // -----------------------------------------
    function setActiveSlideBackground(swiperInstance) {
        if (!swiperInstance || !swiperInstance.slides) return;
        // Use activeIndex (DOM position), not realIndex: with loop:true Swiper inserts
        // duplicate slides so realIndex no longer matches slides[i].
        var activeIndex = swiperInstance.activeIndex;
        var slides = swiperInstance.slides;
        for (var i = 0; i < slides.length; i++) {
            var bgEl = slides[i].querySelector('.hero-slide-bg');
            if (!bgEl) continue;
            var bgImage = bgEl.getAttribute('data-bg-image');
            if (i === activeIndex && bgImage) {
                bgEl.style.backgroundImage = 'url(' + bgImage + ')';
            } else {
                bgEl.style.backgroundImage = '';
            }
        }
    }
    function setPatternBgOnly() {
        var patternEls = document.querySelectorAll('.pattern-bg[data-bg-image]');
        patternEls.forEach(function (el) {
            var bgImage = el.getAttribute('data-bg-image');
            if (bgImage) el.style.backgroundImage = 'url(' + bgImage + ')';
        });
    }
    setPatternBgOnly();

    // -----------------------------------------
    // Hero Slider (Swiper) - lazy-load slide backgrounds to reduce memory
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
            on: {
                init: function () {
                    setActiveSlideBackground(this);
                },
                slideChangeTransitionEnd: function () {
                    setActiveSlideBackground(this);
                }
            }
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
                console.log('Initializing exchange rate widget'); 
                var widget = document.querySelector('.exchange-rate-widget');
                if (!widget) return;
                this.loadExchangeRate();
                this.setupEventListeners();
                
                // Try to fetch from NRB on page load if no rate is available after 2 seconds
                var self = this;
                setTimeout(function() {
                    if (self.currentRate === null || self.currentRate === 135.0) {
                        console.log('No valid rate found, attempting to fetch from NRB...');
                        // Silently try to fetch from NRB
                        var csrfToken = self.getCsrfToken();
                        if (csrfToken) {
                            fetch('/api/v1/exchange-rates/fetch_nrb/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrfToken
                                },
                                credentials: 'same-origin'
                            })
                            .then(function (response) {
                                if (response.ok) {
                                    return response.json();
                                }
                                throw new Error('NRB fetch failed');
                            })
                            .then(function (data) {
                                console.log('Auto-fetched from NRB:', data);
                                setTimeout(function() {
                                    self.loadExchangeRate();
                                }, 500);
                            })
                            .catch(function (error) {
                                console.log('Auto-fetch from NRB failed, using cached/default rate');
                            });
                        }
                    }
                }, 2000);
            },

            showLoading: function() {
                var loadingEl = document.querySelector('.exchange-rate-widget .exchange-rate-loading');
                var errorEl = document.querySelector('.exchange-rate-widget .exchange-rate-error');
                if (loadingEl) loadingEl.classList.remove('hidden');
                if (errorEl) errorEl.classList.add('hidden');
            },

            hideLoading: function() {
                var loadingEl = document.querySelector('.exchange-rate-widget .exchange-rate-loading');
                if (loadingEl) loadingEl.classList.add('hidden');
            },

            showError: function(message) {
                var loadingEl = document.querySelector('.exchange-rate-widget .exchange-rate-loading');
                var errorEl = document.querySelector('.exchange-rate-widget .exchange-rate-error');
                var errorMsgEl = document.querySelector('.exchange-rate-widget .exchange-rate-error-message');
                if (loadingEl) loadingEl.classList.add('hidden');
                if (errorEl) errorEl.classList.remove('hidden');
                if (errorMsgEl) errorMsgEl.textContent = message || 'Unable to load exchange rates';
            },

            hideError: function() {
                var errorEl = document.querySelector('.exchange-rate-widget .exchange-rate-error');
                if (errorEl) errorEl.classList.add('hidden');
            },

            loadExchangeRate: function () {
                var self = this;
                console.log('Loading exchange rate for', self.fromCurrency);
                self.showLoading();
                
                fetch('/api/v1/exchange-rates/current/?currency=' + self.fromCurrency + '&type=buy')
                    .then(function (response) {
                        if (!response.ok) {
                            return response.json().then(function(err) {
                                throw new Error('Failed to fetch rate: ' + response.status + ' - ' + (err.error || err.message || 'Unknown error'));
                            }).catch(function() {
                                throw new Error('Failed to fetch rate: ' + response.status);
                            });
                        }
                        return response.json();
                    })
                    .then(function (data) {
                        console.log('Exchange rate loaded:', data);
                        console.log('Rate details - Buy:', data.buy_rate, 'Sell:', data.sell_rate, 'Mid:', data.mid_rate, 'Using:', data.rate_type, '=', data.rate);
                        if (data.rate) {
                            self.currentRate = parseFloat(data.rate);
                            self.updateDisplay();
                            self.hideLoading();
                            self.hideError();
                        } else {
                            throw new Error('No rate in response');
                        }
                    })
                    .catch(function (error) {
                        console.error('Error loading exchange rate:', error);
                        self.hideLoading();
                        // Fallback to default rate if API fails
                        if (!self.currentRate) {
                            self.currentRate = 135.0; // Default USD to NPR rate
                            self.updateDisplay();
                            self.showError('Using default rate. ' + error.message);
                        } else {
                            self.showError('Failed to update rate. ' + error.message);
                        }
                    });
            },

            setupEventListeners: function () {
                var self = this;

                // Retry button for error state
                var retryBtn = document.querySelector('.exchange-rate-widget .retry-load-rate');
                if (retryBtn) {
                    retryBtn.addEventListener('click', function() {
                        self.hideError();
                        self.loadExchangeRate();
                    });
                }

                // Currency selector dropdown
                var currencySelector = document.querySelector('.exchange-rate-widget .currency-selector');
                var currencyDropdown = document.querySelector('.exchange-rate-widget .currency-dropdown');
                var currencyOptions = document.querySelectorAll('.exchange-rate-widget .currency-option');
                
                if (currencySelector && currencyDropdown) {
                    // Toggle dropdown
                    currencySelector.addEventListener('click', function(e) {
                        e.stopPropagation();
                        currencyDropdown.classList.toggle('hidden');
                    });
                    
                    // Close dropdown when clicking outside
                    document.addEventListener('click', function(e) {
                        if (!currencySelector.contains(e.target) && !currencyDropdown.contains(e.target)) {
                            currencyDropdown.classList.add('hidden');
                        }
                    });
                    
                    // Handle currency selection
                    currencyOptions.forEach(function(option) {
                        option.addEventListener('click', function(e) {
                            e.stopPropagation();
                            var newCurrency = this.getAttribute('data-currency');
                            self.changeCurrency(newCurrency);
                            currencyDropdown.classList.add('hidden');
                        });
                    });
                }

                // Button to refresh rate from NRB - make sure we get the button inside the widget
                var checkRateBtn = document.querySelector('.exchange-rate-widget button');
                if (!checkRateBtn) {
                    // Try alternative selector
                    checkRateBtn = document.querySelector('.exchange-rate-widget').querySelector('button');
                }
                if (checkRateBtn) {
                    checkRateBtn.addEventListener('click', function () {
                        checkRateBtn.disabled = true;
                        checkRateBtn.textContent = 'Fetching from NRB...';

                        // Get CSRF token
                        var csrfToken = self.getCsrfToken();
                        if (!csrfToken) {
                            console.error('CSRF token not found');
                            checkRateBtn.disabled = false;
                            checkRateBtn.textContent = 'Error: CSRF token missing';
                            checkRateBtn.classList.add('bg-red-500');
                            setTimeout(function () {
                                checkRateBtn.textContent = 'Check Today\'s Rate';
                                checkRateBtn.classList.remove('bg-red-500');
                            }, 3000);
                            return;
                        }

                        // First fetch from NRB API
                        try {
                            fetch('/api/v1/exchange-rates/fetch_nrb/', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': csrfToken
                                },
                                credentials: 'same-origin'
                            })
                                .then(function (response) {
                                    console.log('NRB fetch response status:', response.status);
                                    if (!response.ok) {
                                        // Try to get error message from response
                                        return response.text().then(function(text) {
                                            var errorMsg = 'Unknown error';
                                            try {
                                                var errData = JSON.parse(text);
                                                errorMsg = errData.error || errData.message || text.substring(0, 100);
                                            } catch(e) {
                                                errorMsg = text.substring(0, 100) || 'HTTP ' + response.status;
                                            }
                                            throw new Error('Failed to fetch from NRB: ' + response.status + ' - ' + errorMsg);
                                        });
                                    }
                                    return response.json();
                                })
                                .then(function (data) {
                                    console.log('NRB fetch result:', data);
                                    // After fetching from NRB, reload the display
                                    setTimeout(function() {
                                        self.loadExchangeRate();
                                    }, 1000); // Increased delay to ensure data is saved
                                    var successMsg = data.message || (data.count > 0 ? 'Successfully fetched ' + data.count + ' rate(s)' : 'Rate Updated!');
                                    checkRateBtn.textContent = successMsg;
                                    checkRateBtn.classList.add('bg-green-500');
                                    setTimeout(function () {
                                        checkRateBtn.disabled = false;
                                        checkRateBtn.textContent = 'Check Today\'s Rate';
                                        checkRateBtn.classList.remove('bg-green-500');
                                    }, 3000);
                                })
                                .catch(function (error) {
                                    console.error('Error fetching from NRB:', error);
                                    console.error('Error details:', error.stack);
                                    // Still reload display even if NRB fetch fails
                                    self.loadExchangeRate();
                                    var errorText = error.message || 'Network error';
                                    if (errorText.length > 40) {
                                        errorText = errorText.substring(0, 37) + '...';
                                    }
                                    checkRateBtn.textContent = 'Error: ' + errorText;
                                    checkRateBtn.classList.add('bg-red-500');
                                    setTimeout(function () {
                                        checkRateBtn.disabled = false;
                                        checkRateBtn.textContent = 'Check Today\'s Rate';
                                        checkRateBtn.classList.remove('bg-red-500');
                                    }, 5000);
                                });
                        } catch (error) {
                            console.error('Exception in fetch:', error);
                            checkRateBtn.disabled = false;
                            checkRateBtn.textContent = 'Error: ' + (error.message || 'Unknown error');
                            checkRateBtn.classList.add('bg-red-500');
                            setTimeout(function () {
                                checkRateBtn.textContent = 'Check Today\'s Rate';
                                checkRateBtn.classList.remove('bg-red-500');
                            }, 5000);
                        }
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
                
                // Log for debugging JPY
                if (this.fromCurrency === 'JPY') {
                    console.log('JPY Conversion:', fromAmount, 'JPY *', this.currentRate, '=', toAmount, 'NPR');
                }

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

            changeCurrency: function (newCurrency) {
                var self = this;
                self.fromCurrency = newCurrency;
                
                // Update currency display
                var currencyCode = document.querySelector('.exchange-rate-widget .currency-code');
                var currencyLabel = document.querySelector('.exchange-rate-widget .currency-label');
                var currencyFlag = document.querySelector('.exchange-rate-widget .currency-flag');
                var currencySelector = document.querySelector('.exchange-rate-widget .currency-selector');
                var amountInput = document.querySelector('.exchange-rate-widget .from-amount-input');
                
                if (currencyCode) currencyCode.textContent = newCurrency;
                if (currencyLabel) currencyLabel.textContent = newCurrency;
                if (currencySelector) currencySelector.setAttribute('data-currency', newCurrency);
                
                // Update flag
                var flagMap = {
                    'USD': 'us', 'EUR': 'eu', 'GBP': 'gb', 'AUD': 'au', 'CAD': 'ca',
                    'JPY': 'jp', 'INR': 'in', 'AED': 'ae', 'SAR': 'sa', 'QAR': 'qa',
                    'SGD': 'sg', 'MYR': 'my', 'THB': 'th', 'CHF': 'ch', 'CNY': 'cn',
                    'KWD': 'kw', 'BHD': 'bh', 'OMR': 'om', 'HKD': 'hk'
                };
                
                if (currencyFlag && flagMap[newCurrency]) {
                    currencyFlag.src = 'https://flagcdn.com/w40/' + flagMap[newCurrency] + '.png';
                    currencyFlag.alt = newCurrency;
                }
                
                // Adjust default amount for JPY (typically larger amounts)
                if (newCurrency === 'JPY' && amountInput) {
                    var currentValue = parseFloat(amountInput.value) || 1000;
                    // If amount is less than 10000, set to 10000 for JPY
                    if (currentValue < 10000) {
                        amountInput.value = 10000;
                        self.fromAmount = 10000;
                    }
                } else if (amountInput && newCurrency !== 'JPY') {
                    // For other currencies, if amount is very large (like JPY amounts), reset to 1000
                    var currentValue = parseFloat(amountInput.value) || 1000;
                    if (currentValue >= 10000) {
                        amountInput.value = 1000;
                        self.fromAmount = 1000;
                    }
                }
                
                // Reload exchange rate for new currency
                self.loadExchangeRate();
            },

            getCsrfToken: function () {
                // Try to get from meta tag first (Django's standard way)
                var metaTag = document.querySelector('meta[name="csrf-token"]');
                if (metaTag) {
                    return metaTag.getAttribute('content');
                }
                
                // Fallback to cookie
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    if (cookie.startsWith('csrftoken=')) {
                        return cookie.substring('csrftoken='.length);
                    }
                }
                
                // Try alternative cookie name
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    if (cookie.startsWith('csrfmiddlewaretoken=')) {
                        return cookie.substring('csrfmiddlewaretoken='.length);
                    }
                }
                
                return null;
            }
        };

        exchangeRateWidget.init();
    }

    // -----------------------------------------
    // Scroll Reveal Animations (Intersection Observer)
    // -----------------------------------------
    function initScrollReveal() {
        // Check if user prefers reduced motion
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (prefersReducedMotion) return;

        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    // Optional: unobserve after animation to improve performance
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe all scroll-reveal elements
        const revealElements = document.querySelectorAll('.scroll-reveal, .scroll-reveal-left, .scroll-reveal-right, .scroll-reveal-scale');
        revealElements.forEach(function(el) {
            observer.observe(el);
        });
    }

    // -----------------------------------------
    // Lazy Loading Images
    // -----------------------------------------
    function initLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver(function(entries, observer) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.add('loaded');
                            img.classList.remove('lazy-load');
                            observer.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px'
            });

            const lazyImages = document.querySelectorAll('img[data-src]');
            lazyImages.forEach(function(img) {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for browsers without IntersectionObserver
            const lazyImages = document.querySelectorAll('img[data-src]');
            lazyImages.forEach(function(img) {
                img.src = img.dataset.src;
                img.classList.add('loaded');
            });
        }
    }

    // -----------------------------------------
    // Enhanced Card Interactions
    // -----------------------------------------
    function initCardInteractions() {
        const cards = document.querySelectorAll('.service-card-enhanced, .service-card-premium');
        cards.forEach(function(card) {
            // Add ripple effect on click
            card.addEventListener('click', function(e) {
                const ripple = document.createElement('span');
                const rect = card.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple');
                
                card.appendChild(ripple);
                
                setTimeout(function() {
                    ripple.remove();
                }, 600);
            });

            // Parallax effect on mouse move (desktop only)
            if (window.innerWidth > 768) {
                card.addEventListener('mousemove', function(e) {
                    const rect = card.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    const centerX = rect.width / 2;
                    const centerY = rect.height / 2;
                    const rotateX = (y - centerY) / 10;
                    const rotateY = (centerX - x) / 10;
                    
                    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-12px) scale(1.02)`;
                });

                card.addEventListener('mouseleave', function() {
                    card.style.transform = '';
                });
            }
        });
    }

    // -----------------------------------------
    // Smooth Scroll with Offset
    // -----------------------------------------
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
            anchor.addEventListener('click', function(e) {
                const href = anchor.getAttribute('href');
                if (href === '#') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const offset = 80; // Header height
                    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // -----------------------------------------
    // Performance: Debounce function
    // -----------------------------------------
    function debounce(func, wait) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                func.apply(context, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // -----------------------------------------
    // Initialize all enhancements
    // -----------------------------------------
    initScrollReveal();
    initLazyLoading();
    initCardInteractions();
    initSmoothScroll();

    // Performance: Throttle scroll events
    let ticking = false;
    window.addEventListener('scroll', debounce(function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                // Any scroll-based animations here
                ticking = false;
            });
            ticking = true;
        }
    }, 16)); // ~60fps
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

