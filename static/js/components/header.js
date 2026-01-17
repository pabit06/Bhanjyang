// Header Component Behavior
// Encapsulates logic for Search Toggle, Mobile Menu, and Dropdowns

document.addEventListener('DOMContentLoaded', function () {
    // Search Toggle Functionality
    const searchToggle = document.getElementById('search-toggle');
    const searchContainer = document.getElementById('search-container');
    const searchClose = document.getElementById('search-close');
    const searchInput = document.getElementById('search-input');

    if (searchToggle && searchContainer) {
        // Ensure search container is hidden by default
        searchContainer.classList.add('hidden', 'pointer-events-none');
        searchContainer.classList.remove('opacity-100', 'translate-y-0', 'scale-100', 'pointer-events-auto');
        searchContainer.classList.add('opacity-0', 'translate-y-2', 'scale-95');
        
        // Function to open search with animation
        function openSearch() {
            searchContainer.classList.remove('hidden', 'pointer-events-none');
            searchContainer.classList.add('pointer-events-auto');
            searchToggle.setAttribute('aria-expanded', 'true');
            // Trigger animation after removing hidden
            setTimeout(() => {
                searchContainer.classList.remove('opacity-0', 'translate-y-2', 'scale-95');
                searchContainer.classList.add('opacity-100', 'translate-y-0', 'scale-100');
                if (searchInput) {
                    searchInput.focus();
                }
            }, 10);
        }

        // Function to close search with animation
        function closeSearch() {
            searchContainer.classList.remove('opacity-100', 'translate-y-0', 'scale-100', 'pointer-events-auto');
            searchContainer.classList.add('opacity-0', 'translate-y-2', 'scale-95', 'pointer-events-none');
            searchToggle.setAttribute('aria-expanded', 'false');
            setTimeout(() => {
                searchContainer.classList.add('hidden');
                searchToggle.focus(); // Return focus to toggle button
            }, 300);
        }

        // Toggle search on icon click
        searchToggle.addEventListener('click', function () {
            if (searchContainer.classList.contains('hidden')) {
                openSearch();
            } else {
                closeSearch();
            }
        });

        // Close search on close button
        if (searchClose) {
            searchClose.addEventListener('click', function () {
                closeSearch();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function (e) {
            // Ctrl/Cmd + K to open search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                if (searchContainer.classList.contains('hidden')) {
                    openSearch();
                } else {
                    closeSearch();
                }
            }

            // Escape to close search
            if (e.key === 'Escape' && !searchContainer.classList.contains('hidden')) {
                closeSearch();
            }
        });

        // Close search when clicking outside
        document.addEventListener('click', function (e) {
            if (searchContainer && !searchContainer.classList.contains('hidden')) {
                if (!searchContainer.contains(e.target) && !searchToggle.contains(e.target)) {
                    closeSearch();
                }
            }
        });
    }

    // Mobile Menu Toggle Functionality
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileMenuClose = document.getElementById('mobile-menu-close');

    if (mobileMenuButton && mobileMenu) {
        // Open mobile menu
        mobileMenuButton.addEventListener('click', function () {
            mobileMenu.classList.remove('hidden', '-translate-x-full');
            mobileMenu.classList.add('translate-x-0');
            mobileMenuButton.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';

            // Focus trap or move focus to first focusable element in menu
            const firstLink = mobileMenu.querySelector('a, button');
            if (firstLink) firstLink.focus();
        });

        // Close mobile menu
        if (mobileMenuClose) {
            mobileMenuClose.addEventListener('click', function () {
                closeMobileMenu();
            });
        }

        // Close mobile menu function
        function closeMobileMenu() {
            mobileMenu.classList.remove('translate-x-0');
            mobileMenu.classList.add('-translate-x-full');
            mobileMenuButton.setAttribute('aria-expanded', 'false');
            setTimeout(() => {
                mobileMenu.classList.add('hidden');
                mobileMenuButton.focus(); // Return focus
            }, 300);
            document.body.style.overflow = '';
        }

        // Close on outside click
        mobileMenu.addEventListener('click', function (e) {
            if (e.target === mobileMenu) {
                closeMobileMenu();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && !mobileMenu.classList.contains('hidden')) {
                closeMobileMenu();
            }
        });

        // Close menu when clicking on menu links
        const mobileMenuLinks = mobileMenu.querySelectorAll('a');
        mobileMenuLinks.forEach(link => {
            link.addEventListener('click', function () {
                closeMobileMenu();
            });
        });

        // Mobile About Us Dropdown Toggle
        const mobileAboutToggle = document.getElementById('mobile-about-toggle');
        const mobileAboutSubmenu = document.getElementById('mobile-about-submenu');
        const mobileAboutIcon = document.getElementById('mobile-about-icon');

        if (mobileAboutToggle && mobileAboutSubmenu && mobileAboutIcon) {
            mobileAboutToggle.addEventListener('click', function (e) {
                e.preventDefault();
                mobileAboutSubmenu.classList.toggle('hidden');
                mobileAboutIcon.classList.toggle('rotate-180');
                const isExpanded = mobileAboutToggle.getAttribute('aria-expanded') === 'true';
                mobileAboutToggle.setAttribute('aria-expanded', !isExpanded);
            });
        }

        // Mobile Services Dropdown Toggle
        const mobileServicesToggle = document.getElementById('mobile-services-toggle');
        const mobileServicesSubmenu = document.getElementById('mobile-services-submenu');
        const mobileServicesIcon = document.getElementById('mobile-services-icon');

        if (mobileServicesToggle && mobileServicesSubmenu && mobileServicesIcon) {
            mobileServicesToggle.addEventListener('click', function (e) {
                e.preventDefault();
                mobileServicesSubmenu.classList.toggle('hidden');
                mobileServicesIcon.classList.toggle('rotate-180');
                const isExpanded = mobileServicesToggle.getAttribute('aria-expanded') === 'true';
                mobileServicesToggle.setAttribute('aria-expanded', !isExpanded);
            });
        }
    }
});
