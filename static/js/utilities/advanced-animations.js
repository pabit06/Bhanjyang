/**
 * Advanced Animations and Micro-interactions for Gallery
 * Powered by GSAP and custom CSS animations
 */

class AdvancedAnimations {
    constructor() {
        this.gsapLoaded = false;
        this.animations = new Map();
        this.observers = new Map();
        this.init();
    }
    
    async init() {
        await this.loadGSAP();
        this.setupIntersectionObservers();
        this.setupScrollAnimations();
        this.setupHoverEffects();
        this.setupClickAnimations();
        this.setupLoadingAnimations();
        this.setupNotificationSystem();
        this.setupTooltipSystem();
        this.setupMagneticEffects();
        this.setupRippleEffects();
    }
    
    async loadGSAP() {
        try {
            // Load GSAP from CDN if not already loaded
            if (typeof gsap === 'undefined') {
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js';
                script.onload = () => {
                    this.gsapLoaded = true;
                    this.initGSAPAnimations();
                };
                document.head.appendChild(script);
            } else {
                this.gsapLoaded = true;
                this.initGSAPAnimations();
            }
        } catch (error) {
            console.warn('GSAP could not be loaded, using CSS animations only');
        }
    }
    
    initGSAPAnimations() {
        if (!this.gsapLoaded || typeof gsap === 'undefined') return;
        
        // Load ScrollTrigger if not already loaded
        if (typeof ScrollTrigger === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js';
            script.onload = () => {
                if (typeof ScrollTrigger !== 'undefined') {
                    gsap.registerPlugin(ScrollTrigger);
                }
                this.setupScrollAnimations();
            };
            document.head.appendChild(script);
        } else {
            // Register GSAP plugins if available
            try {
                if (typeof ScrollTrigger !== 'undefined') {
                    gsap.registerPlugin(ScrollTrigger);
                }
                if (typeof TextPlugin !== 'undefined') {
                    gsap.registerPlugin(TextPlugin);
                }
            } catch (e) {
                console.warn('GSAP plugin registration failed:', e);
            }
        }
        
        // Set default ease
        gsap.defaults({
            ease: "power2.out",
            duration: 0.6
        });
    }
    
    setupIntersectionObservers() {
        // Fade in animations
        this.createObserver('.fade-in', (element) => {
            gsap.fromTo(element, 
                { opacity: 0, y: 30 },
                { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }
            );
        });
        
        // Slide in animations
        this.createObserver('.slide-in-left', (element) => {
            gsap.fromTo(element,
                { opacity: 0, x: -100 },
                { opacity: 1, x: 0, duration: 0.6, ease: "power2.out" }
            );
        });
        
        this.createObserver('.slide-in-right', (element) => {
            gsap.fromTo(element,
                { opacity: 0, x: 100 },
                { opacity: 1, x: 0, duration: 0.6, ease: "power2.out" }
            );
        });
        
        this.createObserver('.slide-in-up', (element) => {
            gsap.fromTo(element,
                { opacity: 0, y: 50 },
                { opacity: 1, y: 0, duration: 0.6, ease: "power2.out" }
            );
        });
        
        // Scale animations
        this.createObserver('.scale-in', (element) => {
            gsap.fromTo(element,
                { opacity: 0, scale: 0.8 },
                { opacity: 1, scale: 1, duration: 0.4, ease: "back.out(1.7)" }
            );
        });
        
        // Bounce animations
        this.createObserver('.bounce-in', (element) => {
            gsap.fromTo(element,
                { opacity: 0, scale: 0.3 },
                { opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.7)" }
            );
        });
        
        // Rotate animations
        this.createObserver('.rotate-in', (element) => {
            gsap.fromTo(element,
                { opacity: 0, rotation: -180, scale: 0.8 },
                { opacity: 1, rotation: 0, scale: 1, duration: 0.6, ease: "power2.out" }
            );
        });
    }
    
    createObserver(selector, callback) {
        const elements = document.querySelectorAll(selector);
        if (elements.length === 0) return;
        
        // Check if GSAP is available for animations
        if (!this.gsapLoaded || typeof gsap === 'undefined') {
            // Fallback to CSS animations
            elements.forEach(element => {
                element.classList.add('animate-in');
            });
            return;
        }
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    callback(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        elements.forEach(element => observer.observe(element));
        this.observers.set(selector, observer);
    }
    
    setupScrollAnimations() {
        if (!this.gsapLoaded || typeof gsap === 'undefined') return;
        if (typeof ScrollTrigger === 'undefined') return;
        
        // Parallax effect for hero section (only if element exists)
        const galleryHero = document.querySelector('.gallery-hero');
        if (galleryHero) {
            const heroBefore = galleryHero.querySelector('::before');
            if (heroBefore) {
                gsap.to('.gallery-hero::before', {
                    yPercent: -50,
                    ease: "none",
                    scrollTrigger: {
                        trigger: '.gallery-hero',
                        start: "top bottom",
                        end: "bottom top",
                        scrub: true
                    }
                });
            }
        }
        
        // Stagger animations for gallery items (only if elements exist)
        const masonryItems = document.querySelectorAll('.masonry-item');
        const masonryGrid = document.querySelector('.masonry-grid');
        if (masonryItems.length > 0 && masonryGrid) {
            gsap.fromTo('.masonry-item',
                { opacity: 0, y: 50, scale: 0.9 },
                {
                    opacity: 1,
                    y: 0,
                    scale: 1,
                    duration: 0.6,
                    ease: "power2.out",
                    stagger: 0.1,
                    scrollTrigger: {
                        trigger: '.masonry-grid',
                        start: "top 80%",
                        end: "bottom 20%",
                        toggleActions: "play none none reverse"
                    }
                }
            );
        }
        
        // Floating animation for cards (only if elements exist)
        const floatingElements = document.querySelectorAll('.floating');
        if (floatingElements.length > 0) {
            gsap.to('.floating', {
                y: -10,
                duration: 3,
                ease: "power2.inOut",
                yoyo: true,
                repeat: -1
            });
        }
    }
    
    setupHoverEffects() {
        // Advanced hover effects for gallery items
        document.querySelectorAll('.gallery-item-advanced').forEach(item => {
            item.addEventListener('mouseenter', () => {
                gsap.to(item, {
                    scale: 1.05,
                    y: -10,
                    duration: 0.3,
                    ease: "power2.out"
                });
                
                gsap.to(item.querySelector('img'), {
                    scale: 1.1,
                    rotation: 1,
                    duration: 0.4,
                    ease: "power2.out"
                });
            });
            
            item.addEventListener('mouseleave', () => {
                gsap.to(item, {
                    scale: 1,
                    y: 0,
                    duration: 0.3,
                    ease: "power2.out"
                });
                
                gsap.to(item.querySelector('img'), {
                    scale: 1,
                    rotation: 0,
                    duration: 0.4,
                    ease: "power2.out"
                });
            });
        });
        
        // Button hover effects
        document.querySelectorAll('.btn-advanced').forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                gsap.to(btn, {
                    scale: 1.05,
                    y: -2,
                    duration: 0.2,
                    ease: "power2.out"
                });
            });
            
            btn.addEventListener('mouseleave', () => {
                gsap.to(btn, {
                    scale: 1,
                    y: 0,
                    duration: 0.2,
                    ease: "power2.out"
                });
            });
        });
    }
    
    setupClickAnimations() {
        // Click animations for buttons
        document.querySelectorAll('.btn-advanced').forEach(btn => {
            btn.addEventListener('click', (e) => {
                gsap.to(btn, {
                    scale: 0.95,
                    duration: 0.1,
                    yoyo: true,
                    repeat: 1,
                    ease: "power2.out"
                });
            });
        });
        
        // Card click animations
        document.querySelectorAll('.card-advanced').forEach(card => {
            card.addEventListener('click', (e) => {
                gsap.to(card, {
                    scale: 0.98,
                    duration: 0.1,
                    yoyo: true,
                    repeat: 1,
                    ease: "power2.out"
                });
            });
        });
    }
    
    setupLoadingAnimations() {
        // Loading spinner animation
        const spinner = document.querySelector('.loading-spinner-advanced');
        if (spinner) {
            gsap.to(spinner, {
                rotation: 360,
                duration: 1,
                ease: "none",
                repeat: -1
            });
        }
        
        // Skeleton loading animation
        document.querySelectorAll('.loading-skeleton').forEach(skeleton => {
            gsap.to(skeleton, {
                backgroundPosition: "200px 0",
                duration: 1.5,
                ease: "none",
                repeat: -1
            });
        });
    }
    
    setupNotificationSystem() {
        this.notificationContainer = document.createElement('div');
        this.notificationContainer.className = 'notification-container';
        this.notificationContainer.style.cssText = `
            position: fixed;
            top: 2rem;
            right: 2rem;
            z-index: 10000;
            pointer-events: none;
        `;
        document.body.appendChild(this.notificationContainer);
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification-advanced ${type}`;
        notification.textContent = message;
        
        this.notificationContainer.appendChild(notification);
        
        // Animate in
        gsap.fromTo(notification, 
            { x: 400, opacity: 0 },
            { x: 0, opacity: 1, duration: 0.4, ease: "back.out(1.7)" }
        );
        
        // Auto remove
        setTimeout(() => {
            gsap.to(notification, {
                x: 400,
                opacity: 0,
                duration: 0.3,
                ease: "power2.in",
                onComplete: () => {
                    this.notificationContainer.removeChild(notification);
                }
            });
        }, duration);
    }
    
    setupTooltipSystem() {
        document.querySelectorAll('.tooltip-advanced').forEach(element => {
            const tooltip = element.querySelector('.tooltip-text');
            if (!tooltip) return;
            
            element.addEventListener('mouseenter', () => {
                gsap.fromTo(tooltip,
                    { opacity: 0, y: 10 },
                    { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }
                );
            });
            
            element.addEventListener('mouseleave', () => {
                gsap.to(tooltip, {
                    opacity: 0,
                    y: 10,
                    duration: 0.3,
                    ease: "power2.in"
                });
            });
        });
    }
    
    setupMagneticEffects() {
        document.querySelectorAll('.magnetic').forEach(element => {
            element.addEventListener('mousemove', (e) => {
                const rect = element.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                
                gsap.to(element, {
                    x: x * 0.1,
                    y: y * 0.1,
                    duration: 0.3,
                    ease: "power2.out"
                });
            });
            
            element.addEventListener('mouseleave', () => {
                gsap.to(element, {
                    x: 0,
                    y: 0,
                    duration: 0.3,
                    ease: "power2.out"
                });
            });
        });
    }
    
    setupRippleEffects() {
        document.querySelectorAll('.ripple').forEach(element => {
            element.addEventListener('click', (e) => {
                const rect = element.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const ripple = document.createElement('div');
                ripple.style.cssText = `
                    position: absolute;
                    left: ${x}px;
                    top: ${y}px;
                    width: 0;
                    height: 0;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.3);
                    transform: translate(-50%, -50%);
                    pointer-events: none;
                `;
                
                element.appendChild(ripple);
                
                gsap.to(ripple, {
                    width: 300,
                    height: 300,
                    duration: 0.6,
                    ease: "power2.out",
                    onComplete: () => {
                        element.removeChild(ripple);
                    }
                });
            });
        });
    }
    
    // Public API methods
    animateElement(element, animation, options = {}) {
        if (!this.gsapLoaded) {
            // Fallback to CSS animations
            element.classList.add(animation);
            return;
        }
        
        const defaultOptions = {
            duration: 0.6,
            ease: "power2.out"
        };
        
        const config = { ...defaultOptions, ...options };
        
        switch (animation) {
            case 'fadeIn':
                gsap.fromTo(element, { opacity: 0 }, { opacity: 1, ...config });
                break;
            case 'slideInUp':
                gsap.fromTo(element, { opacity: 0, y: 50 }, { opacity: 1, y: 0, ...config });
                break;
            case 'scaleIn':
                gsap.fromTo(element, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, ...config });
                break;
            case 'bounceIn':
                gsap.fromTo(element, { opacity: 0, scale: 0.3 }, { opacity: 1, scale: 1, ease: "back.out(1.7)", ...config });
                break;
            default:
                console.warn(`Unknown animation: ${animation}`);
        }
    }
    
    staggerAnimation(elements, animation, delay = 0.1) {
        if (!this.gsapLoaded) return;
        
        gsap.fromTo(elements, 
            { opacity: 0, y: 50 },
            {
                opacity: 1,
                y: 0,
                duration: 0.6,
                ease: "power2.out",
                stagger: delay
            }
        );
    }
    
    destroy() {
        // Clean up observers
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
        
        // Clean up animations
        this.animations.clear();
        
        // Remove notification container
        if (this.notificationContainer) {
            document.body.removeChild(this.notificationContainer);
        }
    }
}

// Initialize animations when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.advancedAnimations = new AdvancedAnimations();
    
    // Add CSS classes for animations
    const style = document.createElement('style');
    style.textContent = `
        .gallery-item-advanced,
        .card-advanced,
        .btn-advanced,
        .filter-tab-advanced {
            will-change: transform;
        }
        
        .masonry-item {
            will-change: transform, opacity;
        }
        
        .notification-advanced {
            will-change: transform, opacity;
        }
        
        .tooltip-text {
            will-change: transform, opacity;
        }
    `;
    document.head.appendChild(style);
});

// Export for global access
window.AdvancedAnimations = AdvancedAnimations;
