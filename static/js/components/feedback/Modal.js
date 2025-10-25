/**
 * Modal Component
 * 
 * A modern modal dialog component with smooth animations,
 * focus management, and accessibility features.
 */

class Modal extends Component {
    get defaultOptions() {
        return {
            animationDuration: 300,
            backdropClose: true,
            escapeClose: true,
            focusTrap: true,
            restoreFocus: true,
            backdropClass: 'modal-backdrop',
            modalClass: 'modal-dialog',
            showClass: 'modal-show',
            hideClass: 'modal-hide',
            bodyScrollLock: true
        };
    }

    init() {
        this.backdrop = this.createBackdrop();
        this.setupModal();
        this.setupAccessibility();
        super.init();
    }

    createBackdrop() {
        const backdrop = document.createElement('div');
        backdrop.className = this.options.backdropClass;
        backdrop.setAttribute('aria-hidden', 'true');
        return backdrop;
    }

    setupModal() {
        // Add modal classes
        this.addClass(this.options.modalClass);
        
        // Set ARIA attributes
        this.element.setAttribute('role', 'dialog');
        this.element.setAttribute('aria-modal', 'true');
        this.element.setAttribute('tabindex', '-1');
        
        // Find focusable elements
        this.focusableElements = this.getFocusableElements();
        
        // Set initial focus
        if (this.focusableElements.length > 0) {
            this.focusableElements[0].focus();
        } else {
            this.element.focus();
        }
    }

    setupAccessibility() {
        // Store original focus
        this.originalFocus = document.activeElement;
        
        // Handle escape key
        if (this.options.escapeClose) {
            this.handleEscape = (e) => {
                if (e.key === 'Escape') {
                    this.close();
                }
            };
            document.addEventListener('keydown', this.handleEscape);
        }
        
        // Handle backdrop click
        if (this.options.backdropClose) {
            this.backdrop.addEventListener('click', () => {
                this.close();
            });
        }
        
        // Prevent backdrop click from closing modal when clicking inside
        this.element.addEventListener('click', (e) => {
            e.stopPropagation();
        });
        
        // Focus trap
        if (this.options.focusTrap) {
            this.setupFocusTrap();
        }
        
        // Body scroll lock
        if (this.options.bodyScrollLock) {
            this.lockBodyScroll();
        }
    }

    setupFocusTrap() {
        this.handleTabKey = (e) => {
            if (e.key !== 'Tab') return;
            
            const firstElement = this.focusableElements[0];
            const lastElement = this.focusableElements[this.focusableElements.length - 1];
            
            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };
        
        this.element.addEventListener('keydown', this.handleTabKey);
    }

    getFocusableElements() {
        const selector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        return Array.from(this.element.querySelectorAll(selector))
            .filter(el => !el.disabled && el.offsetParent !== null);
    }

    lockBodyScroll() {
        document.body.style.overflow = 'hidden';
    }

    unlockBodyScroll() {
        document.body.style.overflow = '';
    }

    show() {
        // Add to DOM
        document.body.appendChild(this.backdrop);
        document.body.appendChild(this.element);
        
        // Trigger animation
        requestAnimationFrame(() => {
            this.addClass(this.options.showClass);
        });
        
        // Emit event
        this.emit('modal:show');
        
        return this;
    }

    close() {
        this.addClass(this.options.hideClass);
        
        setTimeout(() => {
            this.hide();
        }, this.options.animationDuration);
        
        return this;
    }

    hide() {
        // Remove from DOM
        if (this.backdrop.parentNode) {
            this.backdrop.parentNode.removeChild(this.backdrop);
        }
        
        if (this.element.parentNode) {
            this.element.parentNode.removeChild(this.element);
        }
        
        // Restore focus
        if (this.options.restoreFocus && this.originalFocus) {
            this.originalFocus.focus();
        }
        
        // Unlock body scroll
        this.unlockBodyScroll();
        
        // Clean up event listeners
        this.cleanup();
        
        // Emit event
        this.emit('modal:hide');
        
        return this;
    }

    cleanup() {
        if (this.handleEscape) {
            document.removeEventListener('keydown', this.handleEscape);
        }
        
        if (this.handleTabKey) {
            this.element.removeEventListener('keydown', this.handleTabKey);
        }
    }

    // Public API methods
    setTitle(title) {
        const titleElement = this.element.querySelector('.modal-title');
        if (titleElement) {
            titleElement.textContent = title;
        }
        return this;
    }

    setContent(content) {
        const contentElement = this.element.querySelector('.modal-content');
        if (contentElement) {
            contentElement.innerHTML = content;
        }
        return this;
    }

    addButton(text, className = '', onClick = null) {
        const footer = this.element.querySelector('.modal-footer');
        if (!footer) return this;
        
        const button = document.createElement('button');
        button.textContent = text;
        button.className = `btn ${className}`;
        
        if (onClick) {
            button.addEventListener('click', onClick);
        }
        
        footer.appendChild(button);
        return this;
    }

    // Static methods for easy use
    static confirm(message, options = {}) {
        const modal = new Modal(document.createElement('div'));
        
        modal.element.innerHTML = `
            <div class="modal-content">
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" data-action="cancel">Cancel</button>
                    <button class="btn btn-primary" data-action="confirm">Confirm</button>
                </div>
            </div>
        `;
        
        return new Promise((resolve) => {
            modal.element.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                if (action === 'confirm') {
                    modal.close();
                    resolve(true);
                } else if (action === 'cancel') {
                    modal.close();
                    resolve(false);
                }
            });
            
            modal.show();
        });
    }

    static alert(message, options = {}) {
        const modal = new Modal(document.createElement('div'));
        
        modal.element.innerHTML = `
            <div class="modal-content">
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" data-action="ok">OK</button>
                </div>
            </div>
        `;
        
        return new Promise((resolve) => {
            modal.element.addEventListener('click', (e) => {
                if (e.target.dataset.action === 'ok') {
                    modal.close();
                    resolve();
                }
            });
            
            modal.show();
        });
    }
}

// Auto-initialize modals
document.addEventListener('DOMContentLoaded', () => {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => new Modal(modal));
});

// Export for use in other modules
window.Modal = Modal;
