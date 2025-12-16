/**
 * Home Page Logic
 * Handles Swiper slider, Newsletter signup, and Quick Contact form.
 */

// Wait for Swiper to load and DOM to be ready
function initSwiper() {
    if (typeof Swiper === 'undefined') {
        setTimeout(initSwiper, 100);
        return;
    }

    try {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const swiper = new Swiper('.swiper-container', {
            loop: true,
            autoplay: prefersReducedMotion ? false : {
                delay: 6000,
                disableOnInteraction: false,
                pauseOnMouseEnter: true
            },
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            a11y: {
                enabled: true,
                prevSlideMessage: 'Previous slide',
                nextSlideMessage: 'Next slide',
                firstSlideMessage: 'This is the first slide',
                lastSlideMessage: 'This is the last slide'
            },
            speed: prefersReducedMotion ? 0 : 700,
            effect: 'slide',
            on: {
                init: function () {
                    const activeSlide = this.slides[this.activeIndex];
                    activeSlide.querySelectorAll('.animated-element').forEach(el => {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    });
                },
                slideChangeTransitionStart: function () {
                    this.slides.forEach((slide, index) => {
                        if (index !== this.activeIndex) {
                            slide.querySelectorAll('.animated-element').forEach(el => {
                                el.style.opacity = '0';
                                el.style.transform = 'translateY(30px)';
                                el.style.animation = 'none';
                            });
                        }
                    });
                },
                slideChangeTransitionEnd: function () {
                    const activeSlide = this.slides[this.activeIndex];
                    activeSlide.querySelectorAll('.animated-element').forEach(el => {
                        el.style.animation = '';
                        el.style.opacity = '0';
                        el.style.transform = 'translateY(30px)';
                        setTimeout(() => {
                            el.style.animation = getComputedStyle(el).animation;
                        }, 10);
                    });
                }
            }
        });
    } catch (error) {
        console.error('Swiper initialization error:', error);
    }
}

// Initialize Swiper when DOM and script are ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
        initSwiper();
    });
} else {
    initSwiper();
}

document.addEventListener('DOMContentLoaded', function () {
    // Newsletter signup form
    const newsletterForm = document.getElementById('newsletter-form');
    const newsletterMessage = document.getElementById('newsletter-message');

    if (newsletterForm) {
        const emailInput = document.getElementById('newsletter-email');
        const errorDiv = document.getElementById('newsletter-error');
        const submitButton = newsletterForm.querySelector('button[type="submit"]');

        // Real-time validation
        if (emailInput) {
            emailInput.addEventListener('blur', function () {
                const email = this.value.trim();
                if (email && !this.validity.valid) {
                    this.setAttribute('aria-invalid', 'true');
                    if (errorDiv) {
                        errorDiv.textContent = 'Please enter a valid email address';
                        errorDiv.classList.remove('sr-only');
                    }
                } else {
                    this.setAttribute('aria-invalid', 'false');
                    if (errorDiv) {
                        errorDiv.textContent = '';
                        errorDiv.classList.add('sr-only');
                    }
                }
            });

            emailInput.addEventListener('input', function () {
                if (this.validity.valid) {
                    this.setAttribute('aria-invalid', 'false');
                    if (errorDiv) {
                        errorDiv.textContent = '';
                        errorDiv.classList.add('sr-only');
                    }
                }
            });
        }

        newsletterForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const email = formData.get('email');

            // Client-side validation
            if (!email || !emailInput.validity.valid) {
                emailInput.setAttribute('aria-invalid', 'true');
                if (errorDiv) {
                    errorDiv.textContent = 'Please enter a valid email address';
                    errorDiv.classList.remove('sr-only');
                }
                emailInput.focus();
                return;
            }

            // Disable submit button during request
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Subscribing...';
            }

            try {
                // Get URL from form action attribute or default to home:newsletter_signup
                // Note: We need the URL to be passed from template if it varies
                // For now assuming the fetch URL is relative or handled by Django URL tag in HTML
                const submitUrl = this.getAttribute('action') || '/newsletter/signup/';
                // Wait, 'home:newsletter_signup' is a Django URL pattern.
                // In separate JS file we can't use {% url %}.
                // SOLUTION: We will read the URL from a data attribute on the form.

                const response = await fetch(submitUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();

                newsletterMessage.textContent = data.message;
                newsletterMessage.className = data.success ? 'mt-4 text-green-100' : 'mt-4 text-red-100';
                newsletterMessage.classList.remove('hidden');

                if (data.success) {
                    this.reset();
                    emailInput.setAttribute('aria-invalid', 'false');
                    if (errorDiv) {
                        errorDiv.textContent = '';
                        errorDiv.classList.add('sr-only');
                    }
                } else {
                    emailInput.setAttribute('aria-invalid', 'true');
                    if (errorDiv) {
                        errorDiv.textContent = data.message || 'Please enter a valid email address';
                        errorDiv.classList.remove('sr-only');
                    }
                }
            } catch (error) {
                console.error('Newsletter signup error:', error);
                newsletterMessage.textContent = 'Sorry, there was an error. Please try again.';
                newsletterMessage.className = 'mt-4 text-red-100';
                newsletterMessage.classList.remove('hidden');
                emailInput.setAttribute('aria-invalid', 'true');
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Subscribe';
                }
            }
        });
    }

    // Quick contact form
    const contactForm = document.getElementById('quick-contact-form');
    const contactMessage = document.getElementById('contact-message');

    if (contactForm) {
        const nameInput = document.getElementById('quick-contact-name');
        const emailInput = document.getElementById('quick-contact-email');
        const messageInput = document.getElementById('quick-contact-message');
        const submitButton = contactForm.querySelector('button[type="submit"]');

        // Real-time validation
        [nameInput, emailInput, messageInput].forEach(input => {
            if (input) {
                input.addEventListener('blur', function () {
                    const errorId = this.id + '-error';
                    const errorDiv = document.getElementById(errorId);

                    if (!this.value.trim() && this.required) {
                        this.setAttribute('aria-invalid', 'true');
                        if (errorDiv) {
                            errorDiv.textContent = 'This field is required';
                            errorDiv.classList.remove('hidden');
                        }
                    } else if (this.type === 'email' && this.value && !this.validity.valid) {
                        this.setAttribute('aria-invalid', 'true');
                        if (errorDiv) {
                            errorDiv.textContent = 'Please enter a valid email address';
                            errorDiv.classList.remove('hidden');
                        }
                    } else {
                        this.setAttribute('aria-invalid', 'false');
                        if (errorDiv) {
                            errorDiv.textContent = '';
                            errorDiv.classList.add('hidden');
                        }
                    }
                });

                input.addEventListener('input', function () {
                    if (this.validity.valid && this.value.trim()) {
                        this.setAttribute('aria-invalid', 'false');
                        const errorId = this.id + '-error';
                        const errorDiv = document.getElementById(errorId);
                        if (errorDiv) {
                            errorDiv.textContent = '';
                            errorDiv.classList.add('hidden');
                        }
                    }
                });
            }
        });

        contactForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Client-side validation
            let isValid = true;
            [nameInput, emailInput, messageInput].forEach(input => {
                if (input) {
                    const errorId = input.id + '-error';
                    const errorDiv = document.getElementById(errorId);

                    if (!input.value.trim() && input.required) {
                        isValid = false;
                        input.setAttribute('aria-invalid', 'true');
                        if (errorDiv) {
                            errorDiv.textContent = 'This field is required';
                            errorDiv.classList.remove('hidden');
                        }
                    } else if (input.type === 'email' && input.value && !input.validity.valid) {
                        isValid = false;
                        input.setAttribute('aria-invalid', 'true');
                        if (errorDiv) {
                            errorDiv.textContent = 'Please enter a valid email address';
                            errorDiv.classList.remove('hidden');
                        }
                    }
                }
            });

            if (!isValid) {
                // Focus first invalid field
                const firstInvalid = contactForm.querySelector('[aria-invalid="true"]');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
                return;
            }

            const formData = new FormData(this);
            formData.append('subject', 'Quick Contact Inquiry');
            formData.append('inquiry_type', 'general');

            // Disable submit button during request
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Sending...';
            }

            try {
                // Get URL from form action attribute
                const submitUrl = this.getAttribute('action') || '/contact/submit/';

                const response = await fetch(submitUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();

                contactMessage.textContent = data.message;
                contactMessage.className = data.success ? 'mt-4 text-green-600' : 'mt-4 text-red-600';
                contactMessage.classList.remove('hidden');

                if (data.success) {
                    this.reset();
                    // Clear all error states
                    [nameInput, emailInput, messageInput].forEach(input => {
                        if (input) {
                            input.setAttribute('aria-invalid', 'false');
                            const errorId = input.id + '-error';
                            const errorDiv = document.getElementById(errorId);
                            if (errorDiv) {
                                errorDiv.textContent = '';
                                errorDiv.classList.add('hidden');
                            }
                        }
                    });
                }
            } catch (error) {
                console.error('Contact form error:', error);
                contactMessage.textContent = 'Sorry, there was an error. Please try again.';
                contactMessage.className = 'mt-4 text-red-600';
                contactMessage.classList.remove('hidden');
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Send Message';
                }
            }
        });
    }

    // Fix Django Debug Toolbar checkboxes missing id/name attributes
    function fixDebugToolbarCheckboxes() {
        const checkboxes = document.querySelectorAll('#djDebugToolbar input[type="checkbox"]:not([id]):not([name])');
        checkboxes.forEach(function (checkbox, index) {
            const dataCookie = checkbox.getAttribute('data-cookie');
            if (dataCookie) {
                const uniqueId = 'djdt-' + dataCookie.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
                checkbox.id = uniqueId;
                checkbox.name = uniqueId;
            } else {
                const uniqueId = 'djdt-checkbox-' + Date.now() + '-' + index;
                checkbox.id = uniqueId;
                checkbox.name = uniqueId;
            }
        });

        // Also fix checkboxes that have only one of id or name
        const checkboxesMissingId = document.querySelectorAll('#djDebugToolbar input[type="checkbox"][name]:not([id])');
        checkboxesMissingId.forEach(function (checkbox) {
            checkbox.id = checkbox.name || 'djdt-' + Date.now();
        });

        const checkboxesMissingName = document.querySelectorAll('#djDebugToolbar input[type="checkbox"][id]:not([name])');
        checkboxesMissingName.forEach(function (checkbox) {
            checkbox.name = checkbox.id;
        });
    }

    // Run immediately and also after a delay to catch dynamically loaded elements
    fixDebugToolbarCheckboxes();
    setTimeout(fixDebugToolbarCheckboxes, 500);
    setTimeout(fixDebugToolbarCheckboxes, 1000);

    // Also watch for dynamically added elements
    const observer = new MutationObserver(function (mutations) {
        fixDebugToolbarCheckboxes();
    });

    const debugToolbar = document.getElementById('djDebugToolbar');
    if (debugToolbar) {
        observer.observe(debugToolbar, {
            childList: true,
            subtree: true
        });
    }
});
