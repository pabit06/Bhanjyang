/**
 * Back to Top Button Module
 * Smooth scroll to top functionality with analytics tracking
 */
(function() {
    'use strict';
    
    const btn = document.getElementById('back-to-top');
    if (!btn) return;
    
    // Show/hide button based on scroll position
    const toggleButton = () => {
        if (window.scrollY > 300) {
            btn.classList.remove('opacity-0', 'invisible');
            btn.setAttribute('aria-hidden', 'false');
        } else {
            btn.classList.add('opacity-0', 'invisible');
            btn.setAttribute('aria-hidden', 'true');
        }
    };
    
    // Use passive event listener for better performance
    window.addEventListener('scroll', toggleButton, { passive: true });
    
   // Initial check
    toggleButton();
    
    // Smooth scroll to top on click
    btn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
        
        // Track analytics event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'back_to_top_click', {
                'event_category': 'navigation',
                'event_label': 'homepage'
            });
        }
        
        // Focus on main content for accessibility
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.focus();
        }
    });
})();
