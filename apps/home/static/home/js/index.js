// ============================================
// ENHANCED JAVASCRIPT - BHANJYANG COOPERATIVE
// ============================================

(function() {
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
                    init: function() {
                        // Animate first slide elements immediately
                        requestAnimationFrame(() => {
                            if (this.slides && this.slides.length > this.activeIndex) {
                                const activeSlide = this.slides[this.activeIndex];
                                animateSlideElements(activeSlide);
                            }
                        });
                    },
                    slideChangeTransitionStart: function() {
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
                    slideChangeTransitionEnd: function() {
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

    // Form validation scripts (Quick Contact & Newsletter)
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add your newsletter submission logic here
            // Validating...
            const msgEl = document.getElementById('newsletter-message');
            if (msgEl) {
                msgEl.classList.remove('hidden');
                msgEl.innerText = 'Thank you for subscribing!';
                msgEl.classList.add('text-green-600');
                setTimeout(() => msgEl.classList.add('hidden'), 3000);
            }
        });
    }
    
    const contactForm = document.getElementById('quick-contact-form');
        if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            // Add your contact submission logic here
            const msgEl = document.getElementById('contact-message');
            if (msgEl) {
                msgEl.classList.remove('hidden');
                msgEl.innerText = 'Message sent successfully!';
                msgEl.classList.add('text-green-600');
                setTimeout(() => msgEl.classList.add('hidden'), 3000);
            }
        });
    }

})();
