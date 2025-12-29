/**
 * Language Toggle Utility
 * Handles English/Nepali language switching across the site
 */
class LanguageToggle {
    constructor() {
        this.currentLanguage = localStorage.getItem('site_language') || 'en';
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateLanguage(this.currentLanguage, false); // Update without triggering events
    }

    bindEvents() {
        // Try to bind immediately
        this.attemptBind();
        
        // Also try after a short delay in case DOM isn't fully ready
        setTimeout(() => {
            this.attemptBind();
        }, 100);
        
        // Fallback: try again after longer delay if still not found
        setTimeout(() => {
            this.attemptBind();
        }, 500);
    }
    
    attemptBind() {
        // Desktop language toggle
        const languageToggle = document.getElementById('language-toggle');
        if (languageToggle && !languageToggle.dataset.bound) {
            languageToggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleLanguage();
            });
            languageToggle.dataset.bound = 'true';
            console.log('Language toggle button bound (desktop)');
        }

        // Mobile language toggle
        const languageToggleMobile = document.getElementById('language-toggle-mobile');
        if (languageToggleMobile && !languageToggleMobile.dataset.bound) {
            languageToggleMobile.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleLanguage();
            });
            languageToggleMobile.dataset.bound = 'true';
            console.log('Language toggle button bound (mobile)');
        }
    }

    toggleLanguage() {
        // Get current language from Django (check cookie or default to 'ne')
        const currentLang = this.getCurrentDjangoLanguage();
        const newLang = currentLang === 'en' ? 'ne' : 'en';
        console.log('Toggling language from', currentLang, 'to', newLang);
        this.switchDjangoLanguage(newLang);
    }

    getCurrentDjangoLanguage() {
        // Try to get from cookie first
        const cookieLang = this.getCookie('django_language');
        if (cookieLang) {
            return cookieLang;
        }
        // Default to Nepali (as per settings)
        return 'ne';
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    switchDjangoLanguage(lang) {
        // Use Django's set_language view to switch language
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/i18n/setlang/';
        
        // Add CSRF token
        const csrfToken = this.getCookie('csrftoken') || this.getCSRFToken();
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);
        
        // Add language input
        const langInput = document.createElement('input');
        langInput.type = 'hidden';
        langInput.name = 'language';
        langInput.value = lang;
        form.appendChild(langInput);
        
        // Add next URL (current page)
        const nextInput = document.createElement('input');
        nextInput.type = 'hidden';
        nextInput.name = 'next';
        nextInput.value = window.location.pathname + window.location.search;
        form.appendChild(nextInput);
        
        // Submit form
        document.body.appendChild(form);
        form.submit();
    }

    getCSRFToken() {
        // Try to get CSRF token from meta tag or cookie
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        // Fallback: try to get from cookie
        return this.getCookie('csrftoken');
    }

    updateLanguage(lang, saveToStorage = true) {
        // This method is kept for backward compatibility
        // But now we use Django's language switching
        this.currentLanguage = lang;
        
        if (saveToStorage) {
            localStorage.setItem('site_language', lang);
        }

        // Update all elements with data-en and data-ne attributes (for client-side only elements)
        const elementsToUpdate = document.querySelectorAll('[data-en][data-ne]');
        console.log('Found', elementsToUpdate.length, 'elements to update');
        elementsToUpdate.forEach(element => {
            if (lang === 'ne') {
                element.textContent = element.getAttribute('data-ne');
            } else {
                element.textContent = element.getAttribute('data-en');
            }
        });

        // Update placeholders for contact form
        this.updateFormPlaceholders(lang);

        // Dispatch custom event for other scripts to listen
        document.dispatchEvent(new CustomEvent('languageChanged', { 
            detail: { language: lang } 
        }));
    }

    updateFormPlaceholders(lang) {
        const placeholders = {
            'en': {
                'name': 'Enter full name',
                'email': 'your.email@example.com',
                'phone': '+977-XXXXXXXXXX',
                'subject': 'Subject of your message',
                'message': 'Your message here...'
            },
            'ne': {
                'name': 'पूरा नाम प्रविष्ट गर्नुहोस्',
                'email': 'तपाईंको.इमेल@example.com',
                'phone': '+977-XXXXXXXXXX',
                'subject': 'तपाईंको सन्देशको विषय',
                'message': 'तपाईंको सन्देश यहाँ...'
            }
        };

        const form = document.getElementById('contactForm');
        if (form) {
            const nameField = form.querySelector('[name="name"]');
            const emailField = form.querySelector('[name="email"]');
            const phoneField = form.querySelector('[name="phone"]');
            const subjectField = form.querySelector('[name="subject"]');
            const messageField = form.querySelector('[name="message"]');

            if (nameField) nameField.placeholder = placeholders[lang].name;
            if (emailField) emailField.placeholder = placeholders[lang].email;
            if (phoneField) phoneField.placeholder = placeholders[lang].phone;
            if (subjectField) subjectField.placeholder = placeholders[lang].subject;
            if (messageField) messageField.placeholder = placeholders[lang].message;
        }
    }

    getCurrentLanguage() {
        return this.currentLanguage;
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Initializing LanguageToggle...');
        window.languageToggle = new LanguageToggle();
    });
} else {
    // DOM is already ready
    console.log('DOM already ready, initializing LanguageToggle...');
    window.languageToggle = new LanguageToggle();
}

