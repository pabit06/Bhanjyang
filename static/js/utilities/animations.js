/**
 * Bhanjyang Cooperative Animations
 * Handles scroll-triggered animations, interactive effects, and smooth transitions
 */

class BhanjyangAnimations {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollAnimations();
        this.setupTypingEffect();
        this.setupCounterAnimations();
        this.setupParallaxEffects();
        this.setupHeroSlideshow();
        this.setupImageReveal();
        this.setupTextReveal();
        this.setupButtonEffects();
        this.setupCardAnimations();
        this.setupLoadingStates();
        this.setupSmoothScrolling();
        this.setupMobileMenuAnimations();
        this.setupDesktopDropdownNavigation();
        this.setupFormAnimations();
        this.setupToastNotifications();
        // NEW: Advanced animation features
        this.setupAdvancedAnimations();
        this.setupTeamCardAnimations();
        this.setupNewsCardAnimations();
        this.setupContactFormAnimations();
        this.setupNavigationAnimations();
        this.setupPageTransitions();
        this.setupInteractiveElements();
        this.setupMorphingEffects();
        this.setupGlitchEffects();
        this.setupRippleEffects();
        this.setupFloatingElements();
        this.setupScrollProgress();
        this.setupCursorEffects();
    }

    /**
     * Setup scroll-triggered animations using Intersection Observer
     */
    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                    
                    // Add staggered animations for child elements
                    const staggerElements = entry.target.querySelectorAll('.stagger-animate');
                    staggerElements.forEach((el, index) => {
                        setTimeout(() => {
                            el.classList.add('animate');
                        }, index * 100);
                    });
                }
            });
        }, observerOptions);

        // Observe all elements with scroll-animate or animated-element classes
        document.querySelectorAll('.scroll-animate, .animated-element').forEach(el => {
            observer.observe(el);
        });
        
        // SPECIAL FIX: Ensure contact form is visible
        setTimeout(() => {
            const contactForm = document.querySelector('#contactForm');
            if (contactForm) {
                const formContainer = contactForm.parentElement;
                if (formContainer && formContainer.classList.contains('animated-element')) {
                    // Force visibility if not already animated
                    if (!formContainer.classList.contains('animate')) {
                        formContainer.classList.add('animate');
                        formContainer.style.opacity = '1';
                        formContainer.style.transform = 'translateY(0)';
                    }
                }
            }
        }, 500);
    }

    /**
     * Setup typing effect for text elements
     */
    setupTypingEffect() {
        const typingElements = document.querySelectorAll('.typing-effect');
        
        typingElements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            element.style.borderRight = '2px solid';
            
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 100);
                } else {
                    element.style.borderRight = 'none';
                }
            };
            
            // Start typing when element comes into view
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        typeWriter();
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            observer.observe(element);
        });
    }

    /**
     * Setup counter animations for numbers
     */
    setupCounterAnimations() {
        const counters = document.querySelectorAll('.counter');
        const statsContainer = document.querySelector('.stats-landscape');
        
        counters.forEach(counter => {
            // Prefer explicit data-target; else parse numeric from textContent
            let targetAttr = counter.getAttribute('data-target');
            let target = 0;
            if (targetAttr) {
                target = parseInt(String(targetAttr).replace(/[^\d]/g, '')) || 0;
            } else {
                const numericText = String(counter.textContent).replace(/[^\d]/g, '');
                target = parseInt(numericText) || 0;
            }

            // Bail if no numeric target
            if (!target || target <= 0) {
                return;
            }

            const duration = 2000; // 2 seconds
            const increment = Math.max(1, Math.floor(target / (duration / 16))); // ensure progress
            let current = 0;

            const updateCounter = () => {
                if (current < target) {
                    current = Math.min(target, current + increment);
                    counter.textContent = current.toLocaleString();
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target.toLocaleString();
                    counter.classList.add('animate');
                }
            };
            
            // Start counting when element comes into view (supports horizontal scroll containers)
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !counter.dataset.started) {
                        counter.dataset.started = 'true';
                        updateCounter();
                        observer.unobserve(entry.target);
                    }
                });
            }, { root: statsContainer || null, threshold: 0.3 });
            
            observer.observe(counter);
        });
    }

    /**
     * Setup parallax effects for background elements
     */
    setupParallaxEffects() {
        const parallaxElements = document.querySelectorAll('.parallax');
        
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            
            parallaxElements.forEach(element => {
                const speed = element.dataset.speed || 0.5;
                const yPos = -(scrolled * speed);
                element.style.transform = `translateY(${yPos}px)`;
            });
        });
    }

    /**
     * NEW: Setup hero background slideshow (home page)
     * Looks for .hero-slideshow with .hero-slide children, rotates them
     */
    setupHeroSlideshow() {
        const slideshow = document.querySelector('.hero-section .hero-slideshow');
        
        if (!slideshow) {
            return;
        }

        const slides = Array.from(slideshow.querySelectorAll('.hero-slide'));
        
        if (slides.length === 0) {
            return;
        }

        let currentIndex = slides.findIndex(slide => slide.classList.contains('active'));
        if (currentIndex < 0) {
            currentIndex = 0;
            slides[currentIndex].classList.add('active');
        }

        const intervalMs = 5000;
        let timerId = null;

        const tick = () => {
            const prevIndex = currentIndex;
            currentIndex = (currentIndex + 1) % slides.length;
            slides[prevIndex].classList.remove('active');
            slides[currentIndex].classList.add('active');
        };

        // Start rotation after a short delay to ensure first render
        timerId = setInterval(tick, intervalMs);

        // Pause on hover for better UX
        slideshow.addEventListener('mouseenter', () => {
            if (timerId) {
                clearInterval(timerId);
            }
        });
        slideshow.addEventListener('mouseleave', () => {
            timerId = setInterval(tick, intervalMs);
        });
    }

    /**
     * Setup image reveal animations
     */
    setupImageReveal() {
        const imageElements = document.querySelectorAll('.image-reveal');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                }
            });
        });
        
        imageElements.forEach(el => observer.observe(el));
    }

    /**
     * Setup text reveal animations
     */
    setupTextReveal() {
        const textElements = document.querySelectorAll('.text-reveal');
        
        textElements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            
            // Wrap each character in a span
            text.split('').forEach(char => {
                const span = document.createElement('span');
                span.textContent = char === ' ' ? '\u00A0' : char;
                element.appendChild(span);
            });
        });
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate');
                }
            });
        });
        
        textElements.forEach(el => observer.observe(el));
    }

    /**
     * Setup button hover effects and animations
     */
    setupButtonEffects() {
        const buttons = document.querySelectorAll('.btn-animate');
        
        buttons.forEach(button => {
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'scale(1.05)';
            });
            
            button.addEventListener('mouseleave', () => {
                button.style.transform = 'scale(1)';
            });
            
            button.addEventListener('click', () => {
                button.classList.add('animate-shake');
                setTimeout(() => {
                    button.classList.remove('animate-shake');
                }, 800);
            });
        });
    }

    /**
     * Setup card flip animations
     */
    setupCardAnimations() {
        const flipCards = document.querySelectorAll('.card-flip');
        
        flipCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.querySelector('.card-flip-inner').style.transform = 'rotateY(180deg)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.querySelector('.card-flip-inner').style.transform = 'rotateY(0deg)';
            });
        });
    }

    /**
     * Setup loading states and skeleton screens
     */
    setupLoadingStates() {
        // Simulate loading for demo purposes
        const loadingElements = document.querySelectorAll('.loading-skeleton');
        
        loadingElements.forEach(element => {
            setTimeout(() => {
                element.classList.remove('loading-skeleton');
                element.classList.add('animate-fade-in');
            }, 2000);
        });
    }

    /**
     * Setup smooth scrolling for anchor links
     */
    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Setup mobile menu animations with accessibility features
     */
    setupMobileMenuAnimations() {
        // Check for reduced motion preference
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        // Use a small delay to ensure DOM is fully ready
        setTimeout(() => {
            const menuButton = document.getElementById('mobile-menu-button');
            const mobileMenu = document.getElementById('mobile-menu');
            const closeButton = document.getElementById('mobile-menu-close');
            
            if (!menuButton || !mobileMenu) {
                return;
            }
            
            // Store focusable elements for focus trap
            const getFocusableElements = () => {
                const focusableSelectors = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
                return Array.from(mobileMenu.querySelectorAll(focusableSelectors))
                    .filter(el => !el.disabled && el.offsetParent !== null);
            };
            
            // Focus trap management
            let firstFocusableElement = null;
            let lastFocusableElement = null;
            let previousActiveElement = null;
            
            const updateFocusableElements = () => {
                const focusableElements = getFocusableElements();
                firstFocusableElement = focusableElements[0];
                lastFocusableElement = focusableElements[focusableElements.length - 1];
            };
            
            const trapFocus = (e) => {
                if (e.key !== 'Tab') return;
                
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusableElement) {
                        e.preventDefault();
                        lastFocusableElement?.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusableElement) {
                        e.preventDefault();
                        firstFocusableElement?.focus();
                    }
                }
            };
            
            const openMenu = () => {
                if (!mobileMenu || !menuButton) return;
                
                try {
                    // Store the element that had focus before opening menu
                    previousActiveElement = document.activeElement;
                    
                    // Remove hidden class and show menu
                    mobileMenu.classList.remove('hidden');
                    mobileMenu.classList.add('mobile-menu-open');
                    
                    // Update ARIA attributes
                    menuButton.setAttribute('aria-expanded', 'true');
                    mobileMenu.setAttribute('aria-hidden', 'false');
                    
                    // Prevent body scroll when menu is open
                    document.body.classList.add('overflow-hidden');
                    
                    // Update focusable elements and set focus
                    updateFocusableElements();
                    setTimeout(() => {
                        closeButton?.focus();
                    }, prefersReducedMotion ? 0 : 100);
                    
                    // Add focus trap
                    mobileMenu.addEventListener('keydown', trapFocus);
                } catch (error) {
                    console.error('Error opening mobile menu:', error);
                }
            };
            
            const closeMenu = () => {
                if (!mobileMenu || !menuButton) return;
                
                try {
                    // Animate out using CSS class
                    mobileMenu.classList.remove('mobile-menu-open');
                    mobileMenu.classList.add('mobile-menu-closing');
                    
                    const animationDuration = prefersReducedMotion ? 0 : 300;
                    
                    setTimeout(() => {
                        if (mobileMenu) {
                            mobileMenu.classList.add('hidden');
                            mobileMenu.classList.remove('mobile-menu-closing');
                        }
                    }, animationDuration);
                    
                    // Update ARIA attributes
                    menuButton.setAttribute('aria-expanded', 'false');
                    mobileMenu.setAttribute('aria-hidden', 'true');
                    
                    // Restore body scroll when menu is closed
                    document.body.classList.remove('overflow-hidden');
                    
                    // Remove focus trap
                    mobileMenu.removeEventListener('keydown', trapFocus);
                    
                    // Restore focus to previous element
                    if (previousActiveElement && typeof previousActiveElement.focus === 'function') {
                        previousActiveElement.focus();
                    }
                } catch (error) {
                    console.error('Error closing mobile menu:', error);
                }
            };
            
            // Toggle mobile dropdown menu
            const setupMobileDropdown = () => {
                const dropdownToggle = mobileMenu.querySelector('.mobile-dropdown-toggle');
                const dropdown = mobileMenu.querySelector('#mobile-about-dropdown');
                
                if (dropdownToggle && dropdown) {
                    dropdownToggle.addEventListener('click', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const isExpanded = dropdownToggle.getAttribute('aria-expanded') === 'true';
                        const icon = dropdownToggle.querySelector('i');
                        
                        if (isExpanded) {
                            dropdown.classList.add('hidden');
                            dropdownToggle.setAttribute('aria-expanded', 'false');
                            if (icon) icon.classList.remove('rotate-180');
                        } else {
                            dropdown.classList.remove('hidden');
                            dropdownToggle.setAttribute('aria-expanded', 'true');
                            if (icon) icon.classList.add('rotate-180');
                        }
                    });
                    
                    // Keyboard support for mobile dropdown
                    dropdownToggle.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            dropdownToggle.click();
                        }
                    });
                }
            };
            
            // Add click event listener with proper event handling
            menuButton.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const isExpanded = menuButton.getAttribute('aria-expanded') === 'true';
                
                if (!isExpanded) {
                    openMenu();
                } else {
                    closeMenu();
                }
            }, { passive: false });
            
            if (closeButton) {
                closeButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    closeMenu();
                }, { passive: false });
            }
            
            // Close menu when clicking outside
            mobileMenu.addEventListener('click', (e) => {
                if (e.target === mobileMenu) {
                    closeMenu();
                }
            });
            
            // Close menu on Escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
                    closeMenu();
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
            // Setup mobile dropdown
            setupMobileDropdown();
        }, 100);
    }
    
    /**
     * Setup desktop dropdown keyboard navigation
     */
    setupDesktopDropdownNavigation() {
        const dropdownTrigger = document.getElementById('about-dropdown-trigger');
        const dropdownMenu = dropdownTrigger?.parentElement?.querySelector('[role="menu"]');
        
        if (!dropdownTrigger || !dropdownMenu) return;
        
        let isOpen = false;
        const menuItems = Array.from(dropdownMenu.querySelectorAll('[role="menuitem"]'));
        
        const openDropdown = () => {
            isOpen = true;
            dropdownTrigger.setAttribute('aria-expanded', 'true');
            dropdownTrigger.parentElement.classList.add('group');
            menuItems[0]?.focus();
        };
        
        const closeDropdown = () => {
            isOpen = false;
            dropdownTrigger.setAttribute('aria-expanded', 'false');
            dropdownTrigger.parentElement.classList.remove('group');
        };
        
        // Keyboard navigation on trigger
        dropdownTrigger.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if (isOpen) {
                    closeDropdown();
                } else {
                    openDropdown();
                }
            } else if (e.key === 'ArrowDown' && !isOpen) {
                e.preventDefault();
                openDropdown();
            } else if (e.key === 'Escape' && isOpen) {
                e.preventDefault();
                closeDropdown();
                dropdownTrigger.focus();
            }
        });
        
        // Keyboard navigation within menu
        menuItems.forEach((item, index) => {
            item.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const nextIndex = (index + 1) % menuItems.length;
                    menuItems[nextIndex]?.focus();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const prevIndex = (index - 1 + menuItems.length) % menuItems.length;
                    menuItems[prevIndex]?.focus();
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    closeDropdown();
                    dropdownTrigger.focus();
                } else if (e.key === 'Home') {
                    e.preventDefault();
                    menuItems[0]?.focus();
                } else if (e.key === 'End') {
                    e.preventDefault();
                    menuItems[menuItems.length - 1]?.focus();
                }
            });
        });
        
        // Close on blur (when focus leaves the dropdown area)
        dropdownTrigger.parentElement.addEventListener('focusout', (e) => {
            if (!dropdownTrigger.parentElement.contains(e.relatedTarget)) {
                setTimeout(() => {
                    if (!dropdownTrigger.parentElement.contains(document.activeElement)) {
                        closeDropdown();
                    }
                }, 100);
            }
        });
    }

    /**
     * Setup form animations
     */
    setupFormAnimations() {
        const formInputs = document.querySelectorAll('input, textarea, select');
        
        formInputs.forEach(input => {
            // Focus animation
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('animate-pulse');
            });
            
            // Blur animation
            input.addEventListener('blur', () => {
                input.parentElement.classList.remove('animate-pulse');
            });
            
            // Input animation
            input.addEventListener('input', () => {
                if (input.value.length > 0) {
                    input.classList.add('animate-scale-in');
                } else {
                    input.classList.remove('animate-scale-in');
                }
            });
        });
    }

    /**
     * Setup toast notification system
     */
    setupToastNotifications() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(toastContainer);
        }
    }

    /**
     * NEW: Setup advanced animations
     */
    setupAdvancedAnimations() {
        // Keep advanced features but do not force morphing background here

        // Add floating action button (temporarily disabled)
        // this.createFloatingActionButton();
    }

    /**
     * NEW: Setup team card animations
     */
    setupTeamCardAnimations() {
        const teamCards = document.querySelectorAll('.team-card');
        
        teamCards.forEach((card, index) => {
            // Add staggered entrance animation
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('scroll-animate');
            
            // Add 3D hover effects
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) rotateX(5deg) rotateY(5deg)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) rotateX(0) rotateY(0)';
            });
        });
    }

    /**
     * NEW: Setup news card animations
     */
    setupNewsCardAnimations() {
        const newsCards = document.querySelectorAll('.news-card');
        
        newsCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.15}s`;
            card.classList.add('scroll-animate');
            
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    /**
     * NEW: Setup contact form animations
     */
    setupContactFormAnimations() {
        const formGroups = document.querySelectorAll('.form-group');
        
        formGroups.forEach((group, index) => {
            group.style.animationDelay = `${index * 0.1}s`;
            group.classList.add('scroll-animate');
            
            const input = group.querySelector('input, textarea, select');
            if (input) {
                input.addEventListener('focus', () => {
                    group.classList.add('animate-pulse');
                });
                
                input.addEventListener('blur', () => {
                    group.classList.remove('animate-pulse');
                });
            }
        });
    }

    /**
     * NEW: Setup navigation animations
     */
    setupNavigationAnimations() {
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach((item, index) => {
            item.style.animationDelay = `${index * 0.05}s`;
            item.classList.add('animate-fade-in-down');
            
            // Add hover underline effect
            item.addEventListener('mouseenter', () => {
                item.style.transform = 'translateY(-2px)';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.transform = 'translateY(0)';
            });
        });
    }

    /**
     * NEW: Setup page transitions
     */
    setupPageTransitions() {
        // Add page transition class to main content
        const mainContent = document.querySelector('#main-content');
        if (mainContent) {
            mainContent.classList.add('page-transition');
        }
        
        // Handle page transitions
        window.addEventListener('beforeunload', () => {
            document.body.classList.add('page-transition-out');
        });
    }

    /**
     * NEW: Setup interactive elements
     */
    setupInteractiveElements() {
        const interactiveElements = document.querySelectorAll('.interactive-element');
        
        interactiveElements.forEach(element => {
            element.addEventListener('click', () => {
                element.classList.add('animate-tada');
                setTimeout(() => {
                    element.classList.remove('animate-tada');
                }, 1000);
            });
        });
    }

    /**
     * NEW: Setup morphing effects
     */
    setupMorphingEffects() {
        const morphingElements = document.querySelectorAll('.morphing-element');
        
        morphingElements.forEach(element => {
            element.classList.add('animate-morphing');
        });
    }

    /**
     * NEW: Setup glitch effects
     */
    setupGlitchEffects() {
        const glitchElements = document.querySelectorAll('.glitch');
        
        glitchElements.forEach(element => {
            const text = element.textContent;
            element.setAttribute('data-text', text);
            
            // Trigger glitch effect on hover
            element.addEventListener('mouseenter', () => {
                element.style.animation = 'glitch-1 0.5s infinite, glitch-2 0.5s infinite';
            });
            
            element.addEventListener('mouseleave', () => {
                element.style.animation = '';
            });
        });
    }

    /**
     * NEW: Setup ripple effects
     */
    setupRippleEffects() {
        const rippleElements = document.querySelectorAll('.ripple');
        
        rippleElements.forEach(element => {
            element.addEventListener('click', (e) => {
                const ripple = document.createElement('span');
                const rect = element.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = x + 'px';
                ripple.style.top = y + 'px';
                ripple.classList.add('ripple-effect');
                
                element.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }

    /**
     * NEW: Setup floating elements
     */
    setupFloatingElements() {
        const floatingElements = document.querySelectorAll('.floating-element');
        
        floatingElements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.5}s`;
            element.classList.add('animate-float');
        });
    }

    /**
     * NEW: Setup scroll progress indicator
     */
    setupScrollProgress() {
        const progressBar = document.createElement('div');
        progressBar.className = 'fixed top-0 left-0 w-0 h-1 bg-gradient-to-r from-deuraligreen to-bhanjyangred z-50 transition-all duration-300';
        progressBar.id = 'scroll-progress';
        document.body.appendChild(progressBar);
        
        window.addEventListener('scroll', () => {
            const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
            progressBar.style.width = scrolled + '%';
        });
    }

    /**
     * NEW: Setup custom cursor effects
     */
    setupCursorEffects() {
        const cursor = document.createElement('div');
        cursor.className = 'fixed w-6 h-6 bg-deuraligreen rounded-full pointer-events-none z-50 mix-blend-difference transition-transform duration-200';
        cursor.id = 'custom-cursor';
        document.body.appendChild(cursor);
        
        document.addEventListener('mousemove', (e) => {
            cursor.style.left = e.clientX - 12 + 'px';
            cursor.style.top = e.clientY - 12 + 'px';
        });
        
        // Add hover effects for interactive elements
        const interactiveElements = document.querySelectorAll('a, button, .interactive-element');
        interactiveElements.forEach(element => {
            element.addEventListener('mouseenter', () => {
                cursor.style.transform = 'scale(2)';
            });
            
            element.addEventListener('mouseleave', () => {
                cursor.style.transform = 'scale(1)';
            });
        });
    }

    /**
     * NEW: Create floating action button
     */
    createFloatingActionButton() {
        const fab = document.createElement('div');
        fab.className = 'fab';
        fab.innerHTML = '<i class="fas fa-arrow-up"></i>';
        fab.title = 'Back to Top';
        
        fab.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            
            fab.classList.add('animate-bounce');
            setTimeout(() => {
                fab.classList.remove('animate-bounce');
            }, 1000);
        });
        
        document.body.appendChild(fab);
        
        // Show/hide based on scroll position
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                fab.style.opacity = '1';
                fab.style.pointerEvents = 'auto';
            } else {
                fab.style.opacity = '0';
                fab.style.pointerEvents = 'none';
            }
        });
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info', duration = 3000) {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        toast.className = `${colors[type]} text-white px-4 py-3 rounded-lg shadow-lg transform translate-x-full transition-all duration-300`;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, duration);
    }

    /**
     * Animate element on scroll
     */
    animateOnScroll(element, animationClass, delay = 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add(animationClass);
                    }, delay);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(element);
    }

    /**
     * Create staggered animation for multiple elements
     */
    staggerAnimation(elements, animationClass, staggerDelay = 100) {
        elements.forEach((element, index) => {
            setTimeout(() => {
                element.classList.add(animationClass);
            }, index * staggerDelay);
        });
    }

    /**
     * NEW: Trigger success animation
     */
    triggerSuccess(element) {
        element.classList.add('success-animation');
        setTimeout(() => {
            element.classList.remove('success-animation');
        }, 2000);
    }

    /**
     * NEW: Trigger error animation
     */
    triggerError(element) {
        element.classList.add('error-animation');
        setTimeout(() => {
            element.classList.remove('error-animation');
        }, 1000);
    }

    /**
     * NEW: Add morphing background
     */
    addMorphingBackground(element) {
        element.classList.add('morphing-bg');
    }

    /**
     * NEW: Remove morphing background
     */
    removeMorphingBackground(element) {
        element.classList.remove('morphing-bg');
    }
}

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.bhanjyangAnimations = new BhanjyangAnimations();
    
    // Add page load animations
    document.body.classList.add('animate-fade-in');
    
    // Animate header elements
    const headerElements = document.querySelectorAll('header *');
    window.bhanjyangAnimations.staggerAnimation(headerElements, 'animate-fade-in-down', 50);
    
    // CONTACT FORM FIX: Ensure form is always visible
    setTimeout(() => {
        const contactForm = document.querySelector('#contactForm');
        if (contactForm) {
            const formContainer = contactForm.parentElement;
            if (formContainer && formContainer.classList.contains('animated-element')) {
                // Force visibility immediately
                formContainer.style.opacity = '1';
                formContainer.style.transform = 'translateY(0)';
                formContainer.classList.add('animate');
            }
        }
    }, 1000);
    
    // Additional fallback for contact form
    setTimeout(() => {
        const contactForm = document.querySelector('#contactForm');
        if (contactForm) {
            const formContainer = contactForm.parentElement;
            if (formContainer && formContainer.classList.contains('animated-element')) {
                if (!formContainer.classList.contains('animate')) {
                    formContainer.style.opacity = '1';
                    formContainer.style.transform = 'translateY(0)';
                    formContainer.classList.add('animate');
                }
            }
        }
    }, 2000);
    
    // ULTIMATE FALLBACK: CSS-based fallback after 3 seconds
    setTimeout(() => {
        const contactForm = document.querySelector('#contactForm');
        if (contactForm) {
            const formContainer = contactForm.parentElement;
            if (formContainer && formContainer.classList.contains('animated-element')) {
                if (!formContainer.classList.contains('animate')) {
                    formContainer.classList.add('contact-form-fallback');
                }
            }
        }
    }, 3000);
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BhanjyangAnimations;
}
