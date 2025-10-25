/**
 * Toast Component
 * 
 * A modern toast notification system with smooth animations,
 * auto-dismiss functionality, and multiple types (success, error, warning, info).
 */

class Toast extends Component {
    get defaultOptions() {
        return {
            duration: 5000,
            position: 'top-right',
            animationDuration: 300,
            autoDismiss: true,
            showCloseButton: true,
            maxToasts: 5,
            types: {
                success: { icon: '✓', class: 'toast-success' },
                error: { icon: '✕', class: 'toast-error' },
                warning: { icon: '⚠', class: 'toast-warning' },
                info: { icon: 'ℹ', class: 'toast-info' }
            }
        };
    }

    init() {
        this.container = this.getOrCreateContainer();
        this.setupContainer();
        super.init();
    }

    getOrCreateContainer() {
        let container = document.querySelector('.toast-container');
        
        if (!container) {
            container = document.createElement('div');
            container.className = `toast-container toast-${this.options.position}`;
            document.body.appendChild(container);
        }
        
        return container;
    }

    setupContainer() {
        // Limit number of toasts
        const existingToasts = this.container.querySelectorAll('.toast');
        if (existingToasts.length >= this.options.maxToasts) {
            const oldestToast = existingToasts[0];
            this.removeToast(oldestToast);
        }
    }

    show(message, type = 'info', options = {}) {
        const toastOptions = { ...this.options, ...options };
        const toastElement = this.createToast(message, type, toastOptions);
        
        this.container.appendChild(toastElement);
        this.animateIn(toastElement);
        
        // Auto-dismiss
        if (toastOptions.autoDismiss) {
            setTimeout(() => {
                this.dismiss(toastElement);
            }, toastOptions.duration);
        }
        
        return toastElement;
    }

    createToast(message, type, options) {
        const toast = document.createElement('div');
        toast.className = `toast ${options.types[type]?.class || 'toast-info'}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'polite');
        
        const typeConfig = options.types[type] || options.types.info;
        
        toast.innerHTML = `
            <div class="toast-content">
                <div class="toast-icon">${typeConfig.icon}</div>
                <div class="toast-message">${message}</div>
                ${options.showCloseButton ? '<button class="toast-close" aria-label="Close notification">&times;</button>' : ''}
            </div>
            ${options.autoDismiss ? '<div class="toast-progress"></div>' : ''}
        `;
        
        // Add close button functionality
        const closeButton = toast.querySelector('.toast-close');
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                this.dismiss(toast);
            });
        }
        
        // Add click to dismiss
        toast.addEventListener('click', (e) => {
            if (e.target === toast || e.target.classList.contains('toast-message')) {
                this.dismiss(toast);
            }
        });
        
        return toast;
    }

    animateIn(toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        
        requestAnimationFrame(() => {
            toast.style.transition = `all ${this.options.animationDuration}ms ease-out`;
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
            
            // Start progress bar animation
            const progressBar = toast.querySelector('.toast-progress');
            if (progressBar) {
                progressBar.style.animation = `toast-progress ${this.options.duration}ms linear`;
            }
        });
    }

    dismiss(toast) {
        if (!toast || !toast.parentNode) return;
        
        toast.style.transition = `all ${this.options.animationDuration}ms ease-in`;
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            this.removeToast(toast);
        }, this.options.animationDuration);
    }

    removeToast(toast) {
        if (toast && toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }

    // Static methods for easy use
    static success(message, options = {}) {
        return Toast.getInstance().show(message, 'success', options);
    }

    static error(message, options = {}) {
        return Toast.getInstance().show(message, 'error', options);
    }

    static warning(message, options = {}) {
        return Toast.getInstance().show(message, 'warning', options);
    }

    static info(message, options = {}) {
        return Toast.getInstance().show(message, 'info', options);
    }

    static getInstance() {
        if (!Toast.instance) {
            Toast.instance = new Toast(document.createElement('div'));
        }
        return Toast.instance;
    }

    // Clear all toasts
    static clear() {
        const container = document.querySelector('.toast-container');
        if (container) {
            container.innerHTML = '';
        }
    }
}

// Auto-initialize toast system
document.addEventListener('DOMContentLoaded', () => {
    Toast.getInstance();
});

// Export for use in other modules
window.Toast = Toast;
