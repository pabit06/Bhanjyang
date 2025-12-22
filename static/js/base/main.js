/**
 * Main JavaScript file for Bhanjyang Cooperative
 * Consolidates all inline scripts from base.html for better performance and caching
 */

(function() {
    'use strict';

    // ============================================
    // Mobile Menu Functionality
    // ============================================
    function openMobileMenu() {
        const mobileMenu = document.getElementById('mobile-menu');
        const menuButton = document.getElementById('mobile-menu-button');
        if (!mobileMenu || !menuButton) return;
        
        // Remove hidden and closing classes first
        mobileMenu.classList.remove('hidden');
        mobileMenu.classList.remove('mobile-menu-closing');
        
        // Hide the menu button when menu is open
        menuButton.style.display = 'none';
        
        // Use requestAnimationFrame to ensure smooth animation
        requestAnimationFrame(function() {
            mobileMenu.classList.add('mobile-menu-open');
            menuButton.setAttribute('aria-expanded', 'true');
            mobileMenu.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        });
    }
    
    function closeMobileMenu() {
        const mobileMenu = document.getElementById('mobile-menu');
        const menuButton = document.getElementById('mobile-menu-button');
        if (!mobileMenu || !menuButton) return;
        
        // Remove focus from any element inside the menu before hiding
        const activeElement = document.activeElement;
        if (mobileMenu.contains(activeElement) && activeElement !== document.body) {
            activeElement.blur();
            // Return focus to the menu button
            menuButton.focus();
        }
        
        mobileMenu.classList.remove('mobile-menu-open');
        mobileMenu.classList.add('mobile-menu-closing');
        menuButton.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        
        // Show the menu button again when menu is closed
        menuButton.style.display = '';
        
        // Set aria-hidden after removing focus and starting animation
        setTimeout(function() {
            if (mobileMenu) {
                mobileMenu.setAttribute('aria-hidden', 'true');
            }
        }, 50);
        
        setTimeout(function() {
            if (mobileMenu) {
                mobileMenu.classList.add('hidden');
                mobileMenu.classList.remove('mobile-menu-closing');
            }
        }, 300);
    }
    
    // Global toggle function for inline onclick
    window.toggleMobileMenu = function(e) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
        const mobileMenu = document.getElementById('mobile-menu');
        if (!mobileMenu) return;
        
        const isHidden = mobileMenu.classList.contains('hidden');
        const isOpen = mobileMenu.classList.contains('mobile-menu-open');
        
        if (isHidden || !isOpen) {
            openMobileMenu();
        } else {
            closeMobileMenu();
        }
    };
    
    function setupMobileMenu() {
        const menuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        const closeButton = document.getElementById('mobile-menu-close');
        
        if (!menuButton || !mobileMenu) {
            return false;
        }
        
        // Add event listener (in addition to inline onclick)
        menuButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            window.toggleMobileMenu(e);
        }, { passive: false });
        
        if (closeButton) {
            closeButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                closeMobileMenu();
            }, { passive: false });
        }
        
        // Close on backdrop click (only if clicking the backdrop itself, not the panel)
        const panel = mobileMenu.querySelector('.mobile-menu-panel');
        if (panel) {
            // Prevent clicks on panel from bubbling to backdrop
            panel.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        }
        
        mobileMenu.addEventListener('click', function(e) {
            // Only close if clicking directly on the backdrop div (mobile-menu), not on the panel
            if (e.target === mobileMenu) {
                e.preventDefault();
                e.stopPropagation();
                closeMobileMenu();
            }
        }, { passive: false });
        
        // Close on Escape key (only add once)
        if (!window.mobileMenuEscapeHandler) {
            window.mobileMenuEscapeHandler = function(e) {
                const menu = document.getElementById('mobile-menu');
                if (menu && e.key === 'Escape' && !menu.classList.contains('hidden')) {
                    closeMobileMenu();
                }
            };
            document.addEventListener('keydown', window.mobileMenuEscapeHandler);
        }
        
        // Mobile dropdown
        const dropdownToggle = mobileMenu.querySelector('.mobile-dropdown-toggle');
        const dropdown = mobileMenu.querySelector('#mobile-about-dropdown');
        if (dropdownToggle && dropdown) {
            dropdownToggle.addEventListener('click', function(e) {
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
        }
        
        return true;
    }

    // ============================================
    // Desktop Dropdown Click/Touch Support
    // ============================================
    function setupDesktopDropdown() {
        const dropdownTrigger = document.getElementById('about-dropdown-trigger');
        const dropdownMenu = document.getElementById('about-dropdown-menu');
        const dropdownContainer = document.getElementById('about-dropdown-container');
        const dropdownIcon = document.getElementById('about-dropdown-icon');
        
        if (!dropdownTrigger || !dropdownMenu || !dropdownContainer) return;
        
        let isOpen = false;
        let hoverTimeout = null;
        
        // Check if device supports hover (desktop) or is touch device
        const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        const prefersHover = window.matchMedia('(hover: hover)').matches;
        
        // Toggle dropdown function
        function toggleDropdown(open) {
            const shouldOpen = open !== undefined ? open : !isOpen;
            isOpen = shouldOpen;
            
            if (shouldOpen) {
                // Use visible/invisible instead of hidden for smooth transitions
                dropdownMenu.classList.remove('invisible', 'opacity-0', '-translate-y-2');
                dropdownMenu.classList.add('visible', 'opacity-100', 'translate-y-0');
                dropdownContainer.classList.add('group');
                dropdownTrigger.setAttribute('aria-expanded', 'true');
                if (dropdownIcon) {
                    dropdownIcon.classList.add('rotate-180');
                }
            } else {
                dropdownMenu.classList.remove('visible', 'opacity-100', 'translate-y-0');
                dropdownMenu.classList.add('invisible', 'opacity-0', '-translate-y-2');
                dropdownContainer.classList.remove('group');
                dropdownTrigger.setAttribute('aria-expanded', 'false');
                if (dropdownIcon) {
                    dropdownIcon.classList.remove('rotate-180');
                }
            }
        }
        
        // Click/Touch handler for dropdown trigger
        dropdownTrigger.addEventListener('click', function(e) {
            // Only handle click if it's a touch device or user explicitly clicked
            // For desktop with hover, we'll let hover work naturally
            if (isTouchDevice || !prefersHover) {
                e.preventDefault();
                e.stopPropagation();
                toggleDropdown();
            }
        });
        
        // For desktop: enhance hover with click toggle
        if (prefersHover && !isTouchDevice) {
            dropdownTrigger.addEventListener('click', function(e) {
                // On desktop, clicking should also toggle
                e.preventDefault();
                e.stopPropagation();
                toggleDropdown();
            });
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (isOpen && !dropdownContainer.contains(e.target)) {
                toggleDropdown(false);
            }
        });
        
        // Handle hover for desktop (keep existing behavior)
        if (prefersHover && !isTouchDevice) {
            // Clear any pending timeout
            const clearHoverTimeout = () => {
                if (hoverTimeout) {
                    clearTimeout(hoverTimeout);
                    hoverTimeout = null;
                }
            };
            
            // On mouse enter, ensure dropdown can show via hover
            dropdownContainer.addEventListener('mouseenter', function() {
                clearHoverTimeout();
                // Let CSS hover handle it, but ensure state is correct
                if (!isOpen) {
                    // Don't force open, let CSS handle it
                }
            });
            
            // On mouse leave, close after small delay
            dropdownContainer.addEventListener('mouseleave', function() {
                clearHoverTimeout();
                hoverTimeout = setTimeout(() => {
                    if (isOpen) {
                        toggleDropdown(false);
                    }
                }, 150);
            });
        }
        
        // Close on Escape key
        dropdownTrigger.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isOpen) {
                toggleDropdown(false);
                dropdownTrigger.focus();
            }
        });
    }

    // ============================================
    // Debug Toolbar Fix (Development Only)
    // ============================================
    function fixDebugToolbarCheckboxes() {
        const debugToolbar = document.getElementById('djDebugToolbar');
        if (!debugToolbar) return;
        
        const checkboxes = debugToolbar.querySelectorAll('input[type="checkbox"]:not([id]):not([name])');
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

        // Fix checkboxes missing only id
        debugToolbar.querySelectorAll('input[type="checkbox"][name]:not([id])').forEach(function (checkbox) {
            checkbox.id = checkbox.name || 'djdt-' + Date.now();
        });

        // Fix checkboxes missing only name
        debugToolbar.querySelectorAll('input[type="checkbox"][id]:not([name])').forEach(function (checkbox) {
            checkbox.name = checkbox.id;
        });
    }

    // ============================================
    // Initialization
    // ============================================
    function init() {
        // Setup mobile menu
        if (!setupMobileMenu()) {
            // Retry if DOM not ready
            setTimeout(init, 100);
            setTimeout(init, 500);
            return;
        }
        
        // Setup desktop dropdown
        setupDesktopDropdown();
        
        // Fix debug toolbar (only in development)
        // This will be conditionally called from base.html
        if (window.DEBUG_MODE) {
            fixDebugToolbarCheckboxes();
            
            // Run after delays to catch dynamically loaded elements
            setTimeout(fixDebugToolbarCheckboxes, 500);
            setTimeout(fixDebugToolbarCheckboxes, 1000);

            // Watch for dynamically added elements
            const debugToolbar = document.getElementById('djDebugToolbar');
            if (debugToolbar) {
                const observer = new MutationObserver(fixDebugToolbarCheckboxes);
                observer.observe(debugToolbar, {
                    childList: true,
                    subtree: true
                });
            }
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

