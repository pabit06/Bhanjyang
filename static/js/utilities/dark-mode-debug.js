// Dark Mode Debug Script
// This script helps diagnose dark mode issues

console.log('🌙 Dark Mode Debug Script Loaded');

document.addEventListener('DOMContentLoaded', () => {
    console.log('🌙 DOM Content Loaded - Checking dark mode status');

    // Check if dark mode instance exists
    setTimeout(() => {
        if (window.darkMode) {
            console.log('✅ Dark mode instance found:', window.darkMode);
            console.log('Current theme:', window.darkMode.getTheme());
            console.log('HTML data-theme attribute:', document.documentElement.getAttribute('data-theme'));
        } else {
            console.error('❌ Dark mode instance NOT found!');
        }

        // Check if toggle buttons exist
        const headerToggle = document.getElementById('theme-toggle-header');
        const mobileToggle = document.getElementById('theme-toggle-mobile');
        const mobileMenuToggle = document.getElementById('theme-toggle-mobile-menu');

        console.log('Toggle buttons:', {
            header: headerToggle ? '✅ Found' : '❌ Not found',
            mobile: mobileToggle ? '✅ Found' : '❌ Not found',
            mobileMenu: mobileMenuToggle ? '✅ Found' : '❌ Not found'
        });

        // Check localStorage
        const savedTheme = localStorage.getItem('theme-preference');
        console.log('Saved theme in localStorage:', savedTheme || 'None');

        // Check CSS variables
        const computedStyle = getComputedStyle(document.documentElement);
        console.log('CSS Variables:', {
            '--bg-primary': computedStyle.getPropertyValue('--bg-primary'),
            '--text-primary': computedStyle.getPropertyValue('--text-primary')
        });

        // Add click listener to test
        if (headerToggle) {
            headerToggle.addEventListener('click', () => {
                console.log('🖱️ Header toggle clicked!');
                setTimeout(() => {
                    console.log('New theme:', window.darkMode?.getTheme());
                    console.log('HTML data-theme:', document.documentElement.getAttribute('data-theme'));
                }, 100);
            });
        }
    }, 1000);
});
