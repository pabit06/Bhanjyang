// Interactive JavaScript for About Page
document.addEventListener('DOMContentLoaded', function() {
    
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Observe all animated elements
    document.querySelectorAll('.animate-in-up').forEach(el => {
        observer.observe(el);
    });

    // Smooth scrolling for anchor links
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

    // Counter animation for statistics
    function animateCounter(element, start, end, duration) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const current = Math.floor(progress * (end - start) + start);
            element.textContent = current.toLocaleString();
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Animate statistics when they come into view
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statValue = entry.target.querySelector('.stat-value');
                if (statValue) {
                    const finalValue = parseInt(statValue.textContent.replace(/[^\d]/g, ''));
                    if (finalValue > 0) {
                        animateCounter(statValue, 0, finalValue, 2000);
                    }
                }
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.statistic-card').forEach(card => {
        statsObserver.observe(card);
    });

    // Parallax effect for hero section
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }

    // Throttle parallax updates for performance
    let ticking = false;
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(() => {
                updateParallax();
                ticking = false;  // Reset inside the callback
            });
            ticking = true;
        }
    }

    window.addEventListener('scroll', requestTick);

    // Image lazy loading
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('loading-skeleton');
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        img.classList.add('loading-skeleton');
        imageObserver.observe(img);
    });

    // Mobile menu toggle (if exists)
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            this.classList.toggle('active');
        });
    }

    // Form validation and submission code removed - no forms needed in about app

    // Search functionality (if search input exists)
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            const searchableElements = document.querySelectorAll('.searchable');
            
            searchableElements.forEach(element => {
                const text = element.textContent.toLowerCase();
                if (text.includes(query)) {
                    element.style.display = 'block';
                } else {
                    element.style.display = 'none';
                }
            });
        });
    }

    // Keyboard navigation improvements
    document.addEventListener('keydown', function(e) {
        // ESC key to close modals or menus
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.open');
            openModals.forEach(modal => {
                modal.classList.remove('open');
            });
        }
    });

    // Performance optimization: Debounce resize events
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Recalculate layouts if needed
            updateParallax();
        }, 250);
    });

    // Accessibility: Skip to main content
    const skipLink = document.querySelector('.skip-link');
    if (skipLink) {
        skipLink.addEventListener('click', function(e) {
            e.preventDefault();
            const mainContent = document.querySelector('main');
            if (mainContent) {
                mainContent.focus();
                mainContent.scrollIntoView();
            }
        });
    }

    // Print optimization
    window.addEventListener('beforeprint', function() {
        // Hide interactive elements when printing
        document.querySelectorAll('.no-print').forEach(el => {
            el.style.display = 'none';
        });
    });

    window.addEventListener('afterprint', function() {
        // Restore interactive elements after printing
        document.querySelectorAll('.no-print').forEach(el => {
            el.style.display = '';
        });
    });

    // Format Our Story text into paragraphs
    function formatOurStoryText() {
        const ourStoryElement = document.getElementById('our-story-text');
        if (!ourStoryElement) return;
        
        let text = ourStoryElement.textContent || ourStoryElement.innerText;
        if (!text || text.trim().length === 0) return;
        
        // Split by Nepali period (।) - handle both with and without space
        // First normalize: replace '। ' with '।' then split by '।'
        text = text.replace(/।\s+/g, '।').trim();
        
        // Split by Nepali period
        const sentences = text.split('।').filter(s => s.trim().length > 0);
        
        if (sentences.length === 0) return;
        
        // Group sentences into paragraphs (2-3 sentences per paragraph)
        const paragraphs = [];
        let currentParagraph = [];
        let currentLength = 0;
        
        sentences.forEach((sentence, index) => {
            const trimmedSentence = sentence.trim();
            if (!trimmedSentence) return;
            
            // Add period back (except for last sentence)
            const fullSentence = trimmedSentence + (index < sentences.length - 1 ? '।' : '');
            
            currentParagraph.push(fullSentence);
            currentLength += fullSentence.length;
            
            // Create a paragraph if:
            // 1. We have 2-3 sentences and paragraph is getting long (>150 chars), OR
            // 2. Current paragraph is very long (>300 chars), OR
            // 3. This is the last sentence
            if ((currentParagraph.length >= 2 && currentLength > 150) || 
                currentLength > 300 || 
                index === sentences.length - 1) {
                paragraphs.push(currentParagraph.join(' '));
                currentParagraph = [];
                currentLength = 0;
            }
        });
        
        // Clear the element and add formatted paragraphs
        ourStoryElement.innerHTML = '';
        paragraphs.forEach(paragraph => {
            const p = document.createElement('p');
            p.className = 'mb-4';
            p.textContent = paragraph;
            ourStoryElement.appendChild(p);
        });
    }
    
    // Format Our Story text on page load
    formatOurStoryText();

    // About page interactive features loaded
});
