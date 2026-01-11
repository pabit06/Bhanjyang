// ============================================
// ENHANCED JAVASCRIPT - BHANJYANG COOPERATIVE
// ============================================

(function () {
    'use strict';

    // Check for reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Initialize AOS with error handling
    if (typeof AOS !== 'undefined') {
        try {
            AOS.init({
                once: true,
                offset: 100,
                duration: prefersReducedMotion ? 0 : 800,
                easing: 'ease-out-cubic',
                delay: 0,
                disable: prefersReducedMotion ? 'mobile' : false
            });
        } catch (error) {
            console.warn('AOS initialization failed:', error);
        }
    }

    // Enhanced Swiper initialization with error handling
    let heroSwiper = null;
    try {
        const heroSwiperEl = document.querySelector('.swiper-container');
        if (heroSwiperEl && typeof Swiper !== 'undefined') {
            heroSwiper = new Swiper('.swiper-container', {
                effect: 'slide',
                speed: prefersReducedMotion ? 0 : 1000,
                autoplay: prefersReducedMotion ? false : {
                    delay: 5000,
                    disableOnInteraction: false,
                    pauseOnMouseEnter: true,
                },
                grabCursor: true,
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                    dynamicBullets: true,
                },
                keyboard: {
                    enabled: true,
                },
                a11y: {
                    prevSlideMessage: 'Previous slide',
                    nextSlideMessage: 'Next slide',
                },
                on: {
                    init: function () {
                        // Animate first slide elements immediately
                        requestAnimationFrame(() => {
                            if (this.slides && this.slides.length > this.activeIndex) {
                                const activeSlide = this.slides[this.activeIndex];
                                animateSlideElements(activeSlide);
                            }
                        });
                    },
                    slideChangeTransitionStart: function () {
                        // Reset animations
                        if (this.slides) {
                            this.slides.forEach(slide => {
                                const elements = slide.querySelectorAll('.animate-fade-in-up');
                                elements.forEach(el => {
                                    el.style.opacity = '0';
                                    el.style.transform = 'translateY(20px)';
                                });
                            });
                        }
                    },
                    slideChangeTransitionEnd: function () {
                        // Animate active slide
                        if (this.slides && this.slides.length > this.activeIndex) {
                            const activeSlide = this.slides[this.activeIndex];
                            animateSlideElements(activeSlide);
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Swiper initialization failed:', error);
    }

    // Helper function for slide animations
    function animateSlideElements(slide) {
        if (!slide) return;
        const elements = slide.querySelectorAll('.animate-fade-in-up');
        elements.forEach((el, index) => {
            el.style.transition = `all 0.8s ease-out ${index * 0.2}s`;
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        });
    }

    // Stats Counter Animation (Intersection Observer)
    const counters = document.querySelectorAll('.counter');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    if (counters.length > 0) {
        const counterObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const targetText = counter.getAttribute('data-target') || counter.innerText;
                    const target = parseInt(targetText.replace(/,/g, ''), 10);

                    if (!isNaN(target)) {
                        animateCounter(counter, target);
                    }
                    observer.unobserve(counter);
                }
            });
        }, observerOptions);

        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }

    function animateCounter(el, target) {
        let current = 0;
        const increment = Math.ceil(target / 50); // Adjust speed
        if (target === 0) {
            el.innerText = '0';
            return;
        }
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                el.innerText = target.toLocaleString() + '+';
                clearInterval(timer);
            } else {
                el.innerText = current.toLocaleString();
            }
        }, 20);
    }

    // ==========================================
    // FORM HANDLING (Merged from home.js)
    // ==========================================

    // Newsletter Signup (Real Implementation)
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        const emailInput = document.getElementById('newsletter-email');
        const errorDiv = document.getElementById('newsletter-error');
        const submitButton = newsletterForm.querySelector('button[type="submit"]');
        const newsletterMessage = document.getElementById('newsletter-message');

        // Real-time validation
        if (emailInput) {
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
            if (emailInput && (!email || !emailInput.validity.valid)) {
                emailInput.setAttribute('aria-invalid', 'true');
                if (errorDiv) {
                    errorDiv.textContent = 'Please enter a valid email address';
                    errorDiv.classList.remove('sr-only');
                }
                emailInput.focus();
                return;
            }

            // Disable submit button
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Subscribing...';
            }

            try {
                // Determine URL (default to known endpoint if action not set)
                const submitUrl = this.getAttribute('action') || '/ajax/newsletter/signup/';

                const response = await fetch(submitUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) throw new Error('Network response was not ok');

                const data = await response.json();

                if (newsletterMessage) {
                    newsletterMessage.textContent = data.message;
                    newsletterMessage.className = data.success ? 'mt-4 text-green-100' : 'mt-4 text-red-100';
                    newsletterMessage.classList.remove('hidden');
                }

                if (data.success) {
                    this.reset();
                    if (emailInput) emailInput.setAttribute('aria-invalid', 'false');
                }
            } catch (error) {
                console.error('Newsletter signup error:', error);
                if (newsletterMessage) {
                    newsletterMessage.textContent = 'Sorry, there was an error. Please try again.';
                    newsletterMessage.className = 'mt-4 text-red-100';
                    newsletterMessage.classList.remove('hidden');
                }
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Subscribe';
                }
            }
        });
    }

    // Quick Contact Form (Real Implementation)
    const contactForm = document.getElementById('quick-contact-form');
    if (contactForm) {
        const contactMessage = document.getElementById('contact-message');
        const submitButton = contactForm.querySelector('button[type="submit"]');

        contactForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            if (!formData.has('subject') || !formData.get('subject')) {
                formData.append('subject', 'Quick Contact Inquiry');
            }

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Sending...';
            }

            try {
                const submitUrl = this.getAttribute('action') || '/ajax/contact/submit/';

                const response = await fetch(submitUrl, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) throw new Error('Network response was not ok');

                const data = await response.json();

                if (contactMessage) {
                    contactMessage.textContent = data.message;
                    contactMessage.className = data.success ? 'mt-4 text-green-600' : 'mt-4 text-red-600';
                    contactMessage.classList.remove('hidden');
                }

                if (data.success) {
                    this.reset();
                    // Clear error states if any custom validation logic was added
                    const inputs = this.querySelectorAll('[aria-invalid="true"]');
                    inputs.forEach(input => input.setAttribute('aria-invalid', 'false'));
                }
            } catch (error) {
                console.error('Contact form error:', error);
                if (contactMessage) {
                    contactMessage.textContent = 'Sorry, there was an error. Please try again.';
                    contactMessage.className = 'mt-4 text-red-600';
                    contactMessage.classList.remove('hidden');
                }
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Send Message';
                }
            }
        });
    }

    // Fix Django Debug Toolbar checkboxes (copied from home.js)
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
    }
    // Run fix
    setTimeout(fixDebugToolbarCheckboxes, 1000);

})();
