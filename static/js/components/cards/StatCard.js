/**
 * StatCard Component
 * 
 * An animated statistics card component with smooth number counting,
 * trend indicators, and interactive hover effects.
 */

class StatCard extends Component {
    get defaultOptions() {
        return {
            animationDuration: 2000,
            animationEasing: 'easeOutCubic',
            showTrend: true,
            trendClass: 'stat-trend-up',
            trendDownClass: 'stat-trend-down',
            trendNeutralClass: 'stat-trend-neutral',
            hoverEffect: true,
            hoverClass: 'stat-card-hover',
            loadingClass: 'stat-card-loading',
            errorClass: 'stat-card-error'
        };
    }

    init() {
        this.valueElement = this.element.querySelector('.stat-value');
        this.labelElement = this.element.querySelector('.stat-label');
        this.trendElement = this.element.querySelector('.stat-trend');
        this.iconElement = this.element.querySelector('.stat-icon');
        this.loadingElement = this.element.querySelector('.stat-loading');
        
        this.currentValue = 0;
        this.targetValue = this.parseValue(this.valueElement?.textContent || '0');
        
        this.setupAnimation();
        this.setupHoverEffect();
        this.setupAccessibility();
        super.init();
    }

    setupAnimation() {
        // Animate to target value on load
        if (this.targetValue > 0) {
            this.animateValue(0, this.targetValue);
        }
    }

    setupHoverEffect() {
        if (!this.options.hoverEffect) return;

        this.element.addEventListener('mouseenter', () => {
            this.addClass(this.options.hoverClass);
        });

        this.element.addEventListener('mouseleave', () => {
            this.removeClass(this.options.hoverClass);
        });
    }

    setupAccessibility() {
        // Add ARIA attributes
        this.element.setAttribute('role', 'region');
        this.element.setAttribute('aria-label', this.getAriaLabel());
        
        // Make value focusable for screen readers
        if (this.valueElement) {
            this.valueElement.setAttribute('tabindex', '0');
            this.valueElement.setAttribute('aria-live', 'polite');
        }
    }

    getAriaLabel() {
        const label = this.labelElement?.textContent || 'Statistics';
        const value = this.formatValue(this.targetValue);
        return `${label}: ${value}`;
    }

    parseValue(value) {
        // Remove formatting and parse number
        const cleanValue = value.replace(/[^\d.-]/g, '');
        return parseFloat(cleanValue) || 0;
    }

    formatValue(value) {
        // Format number with appropriate suffixes
        if (value >= 1000000) {
            return (value / 1000000).toFixed(1) + 'M';
        } else if (value >= 1000) {
            return (value / 1000).toFixed(1) + 'K';
        } else {
            return Math.round(value).toLocaleString();
        }
    }

    animateValue(start, end) {
        const startTime = performance.now();
        const duration = this.options.animationDuration;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Apply easing function
            const easedProgress = this.easeOutCubic(progress);
            
            const currentValue = start + (end - start) * easedProgress;
            this.updateValue(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                this.currentValue = end;
                this.emit('animation:complete', { value: end });
            }
        };
        
        requestAnimationFrame(animate);
    }

    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    updateValue(value) {
        this.currentValue = value;
        
        if (this.valueElement) {
            this.valueElement.textContent = this.formatValue(value);
        }
    }

    setValue(value, animate = true) {
        const newValue = this.parseValue(value);
        
        if (animate && newValue !== this.targetValue) {
            this.targetValue = newValue;
            this.animateValue(this.currentValue, newValue);
        } else {
            this.targetValue = newValue;
            this.currentValue = newValue;
            this.updateValue(newValue);
        }
        
        this.updateAriaLabel();
    }

    setTrend(trend) {
        if (!this.trendElement || !this.options.showTrend) return;

        // Remove existing trend classes
        this.removeClass(this.options.trendClass);
        this.removeClass(this.options.trendDownClass);
        this.removeClass(this.options.trendNeutralClass);

        // Add appropriate trend class
        if (trend > 0) {
            this.addClass(this.options.trendClass);
            this.trendElement.textContent = `+${trend}%`;
        } else if (trend < 0) {
            this.addClass(this.options.trendDownClass);
            this.trendElement.textContent = `${trend}%`;
        } else {
            this.addClass(this.options.trendNeutralClass);
            this.trendElement.textContent = '0%';
        }
    }

    setLabel(label) {
        if (this.labelElement) {
            this.labelElement.textContent = label;
        }
        this.updateAriaLabel();
    }

    setIcon(icon) {
        if (this.iconElement) {
            this.iconElement.textContent = icon;
        }
    }

    showLoading() {
        this.addClass(this.options.loadingClass);
        if (this.loadingElement) {
            this.loadingElement.style.display = 'block';
        }
    }

    hideLoading() {
        this.removeClass(this.options.loadingClass);
        if (this.loadingElement) {
            this.loadingElement.style.display = 'none';
        }
    }

    showError(message) {
        this.addClass(this.options.errorClass);
        this.emit('stat:error', { message });
    }

    hideError() {
        this.removeClass(this.options.errorClass);
    }

    updateAriaLabel() {
        this.element.setAttribute('aria-label', this.getAriaLabel());
    }

    // Public API methods
    getValue() {
        return this.targetValue;
    }

    getCurrentValue() {
        return this.currentValue;
    }

    refresh() {
        this.animateValue(0, this.targetValue);
    }

    // Data loading methods
    loadData(url, options = {}) {
        this.showLoading();
        
        return fetch(url, options)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load data: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                this.setValue(data.value);
                if (data.trend !== undefined) {
                    this.setTrend(data.trend);
                }
                if (data.label) {
                    this.setLabel(data.label);
                }
                this.hideLoading();
                return data;
            })
            .catch(error => {
                this.showError(error.message);
                this.hideLoading();
                throw error;
            });
    }
}

// Auto-initialize stat cards
document.addEventListener('DOMContentLoaded', () => {
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => new StatCard(card));
});

// Export for use in other modules
window.StatCard = StatCard;
