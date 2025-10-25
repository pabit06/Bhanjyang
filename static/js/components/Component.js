/**
 * Professional UI Component Library for Bhanjyang Cooperative
 * 
 * This library provides reusable, accessible, and modern UI components
 * following enterprise-grade standards and best practices.
 * 
 * Features:
 * - Responsive design
 * - Accessibility (WCAG 2.1 AA)
 * - Dark mode support
 * - Smooth animations
 * - Form validation
 * - Error handling
 * - Loading states
 */

// Component base class
class Component {
    constructor(element, options = {}) {
        this.element = element;
        this.options = { ...this.defaultOptions, ...options };
        this.init();
    }

    get defaultOptions() {
        return {};
    }

    init() {
        this.bindEvents();
        this.render();
    }

    bindEvents() {
        // Override in subclasses
    }

    render() {
        // Override in subclasses
    }

    destroy() {
        // Cleanup logic
        if (this.element) {
            this.element.removeEventListener('click', this.handleClick);
        }
    }

    // Utility methods
    addClass(className) {
        this.element.classList.add(className);
    }

    removeClass(className) {
        this.element.classList.remove(className);
    }

    toggleClass(className) {
        this.element.classList.toggle(className);
    }

    hasClass(className) {
        return this.element.classList.contains(className);
    }

    emit(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail,
            bubbles: true,
            cancelable: true
        });
        this.element.dispatchEvent(event);
    }

    on(eventName, handler) {
        this.element.addEventListener(eventName, handler);
    }

    off(eventName, handler) {
        this.element.removeEventListener(eventName, handler);
    }
}

// Export for use in other modules
window.Component = Component;
