// GSAP CDN loader for Django templates
// Place this in your base template or include as a static file
// Example GSAP usage for fade-in and slide-up effects
document.addEventListener('DOMContentLoaded', function() {
  // CRITICAL: Ensure footer is always visible before any animations
  const footer = document.querySelector('footer');
  if (footer) {
    footer.style.opacity = '1';
    footer.style.visibility = 'visible';
    footer.style.display = 'block';
  }

  if (typeof window.gsap === 'undefined') {
    return; // Safeguard: skip if GSAP CDN failed to load
  }
  // Fade in all elements with .gsap-fade-in (excluding footer)
  gsap.utils.toArray('.gsap-fade-in').forEach(function(el) {
    // Skip footer elements to prevent hiding
    if (el.tagName !== 'FOOTER' && !el.closest('footer')) {
      gsap.from(el, { opacity: 0, y: 40, duration: 1, ease: 'power2.out' });
    }
  });

  // Slide up effect for .gsap-slide-up (excluding footer)
  gsap.utils.toArray('.gsap-slide-up').forEach(function(el) {
    // Skip footer elements to prevent hiding
    if (el.tagName !== 'FOOTER' && !el.closest('footer')) {
      gsap.from(el, { y: 80, opacity: 0, duration: 1.2, ease: 'power3.out' });
    }
  });

  // Example: Animate nav bar on scroll
  var nav = document.querySelector('.gsap-navbar');
  if (nav) {
    // Temporarily disabled to fix z-index issues
    // gsap.from(nav, { y: -50, opacity: 0, duration: 1, ease: 'power2.out' });
  }
});
