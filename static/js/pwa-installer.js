// Progressive Web App (PWA) Implementation
class PWAInstaller {
    constructor() {
        this.deferredPrompt = null;
        this.installButton = null;
        this.isInstalled = false;
        this.init();
    }

    init() {
        this.checkInstallationStatus();
        this.bindEvents();
        this.createInstallButton();
        this.registerServiceWorker();
    }

    checkInstallationStatus() {
        // Check if app is already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            console.log('PWA: App is running in standalone mode');
        }

        // Check if app is installed on iOS
        if (window.navigator.standalone === true) {
            this.isInstalled = true;
            console.log('PWA: App is installed on iOS');
        }
    }

    bindEvents() {
        // Listen for beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('PWA: Install prompt available');
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        // Listen for appinstalled event
        window.addEventListener('appinstalled', () => {
            console.log('PWA: App installed successfully');
            this.isInstalled = true;
            this.hideInstallButton();
            this.showInstallSuccessMessage();
        });

        // Listen for service worker updates
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('controllerchange', () => {
                console.log('PWA: Service worker updated');
                this.showUpdateNotification();
            });
        }
    }

    createInstallButton() {
        // Create install button
        this.installButton = document.createElement('button');
        this.installButton.id = 'pwa-install-btn';
        this.installButton.className = 'pwa-install-btn';
        this.installButton.innerHTML = `
            <i class="fas fa-download mr-2"></i>
            Install App
        `;
        this.installButton.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: #059669;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 12px 20px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
            transition: all 0.3s ease;
            display: none;
        `;

        // Add hover effects
        this.installButton.addEventListener('mouseenter', () => {
            this.installButton.style.transform = 'translateY(-2px)';
            this.installButton.style.boxShadow = '0 6px 16px rgba(5, 150, 105, 0.4)';
        });

        this.installButton.addEventListener('mouseleave', () => {
            this.installButton.style.transform = 'translateY(0)';
            this.installButton.style.boxShadow = '0 4px 12px rgba(5, 150, 105, 0.3)';
        });

        // Add click handler
        this.installButton.addEventListener('click', () => {
            this.installApp();
        });

        document.body.appendChild(this.installButton);
    }

    showInstallButton() {
        if (!this.isInstalled && this.installButton) {
            this.installButton.style.display = 'block';
            
            // Animate in
            setTimeout(() => {
                this.installButton.style.opacity = '1';
                this.installButton.style.transform = 'translateY(0)';
            }, 100);
        }
    }

    hideInstallButton() {
        if (this.installButton) {
            this.installButton.style.opacity = '0';
            this.installButton.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                this.installButton.style.display = 'none';
            }, 300);
        }
    }

    async installApp() {
        if (!this.deferredPrompt) {
            this.showIOSInstallInstructions();
            return;
        }

        try {
            // Show the install prompt
            this.deferredPrompt.prompt();
            
            // Wait for the user to respond
            const { outcome } = await this.deferredPrompt.userChoice;
            
            console.log(`PWA: User choice: ${outcome}`);
            
            if (outcome === 'accepted') {
                console.log('PWA: User accepted the install prompt');
            } else {
                console.log('PWA: User dismissed the install prompt');
            }
            
            // Clear the deferred prompt
            this.deferredPrompt = null;
            this.hideInstallButton();
            
        } catch (error) {
            console.error('PWA: Error during installation', error);
        }
    }

    showIOSInstallInstructions() {
        // Show iOS-specific install instructions
        const modal = document.createElement('div');
        modal.className = 'ios-install-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        `;

        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; padding: 24px; max-width: 400px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 16px;">📱</div>
                <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 16px; color: #059669;">Install Bhanjyang Cooperative</h3>
                <p style="color: #666; margin-bottom: 20px; line-height: 1.5;">
                    To install this app on your iOS device, tap the Share button and then "Add to Home Screen".
                </p>
                <div style="display: flex; gap: 12px; margin-bottom: 20px;">
                    <div style="flex: 1; padding: 12px; background: #f3f4f6; border-radius: 8px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">📤</div>
                        <div style="font-size: 14px; font-weight: 500;">Tap Share</div>
                    </div>
                    <div style="flex: 1; padding: 12px; background: #f3f4f6; border-radius: 8px;">
                        <div style="font-size: 24px; margin-bottom: 8px;">➕</div>
                        <div style="font-size: 14px; font-weight: 500;">Add to Home Screen</div>
                    </div>
                </div>
                <button id="close-ios-modal" style="background: #059669; color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 500; cursor: pointer;">
                    Got it!
                </button>
            </div>
        `;

        document.body.appendChild(modal);

        // Close modal
        modal.querySelector('#close-ios-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    showInstallSuccessMessage() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 16px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            z-index: 10000;
            font-weight: 500;
            animation: slideInRight 0.3s ease;
        `;
        notification.innerHTML = `
            <i class="fas fa-check-circle mr-2"></i>
            App installed successfully!
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    showUpdateNotification() {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #3b82f6;
            color: white;
            padding: 16px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
            z-index: 10000;
            font-weight: 500;
            animation: slideInRight 0.3s ease;
        `;
        notification.innerHTML = `
            <i class="fas fa-sync-alt mr-2"></i>
            New version available! <button id="reload-app" style="background: rgba(255,255,255,0.2); border: none; color: white; padding: 4px 8px; border-radius: 4px; margin-left: 8px; cursor: pointer;">Reload</button>
        `;

        document.body.appendChild(notification);

        // Reload button
        notification.querySelector('#reload-app').addEventListener('click', () => {
            window.location.reload();
        });

        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => {
                    if (document.body.contains(notification)) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }
        }, 10000);
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                console.log('PWA: Service worker registered successfully', registration);

                // Check for updates
                registration.addEventListener('updatefound', () => {
                    console.log('PWA: Service worker update found');
                    const newWorker = registration.installing;
                    
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            console.log('PWA: New service worker installed');
                            this.showUpdateNotification();
                        }
                    });
                });

            } catch (error) {
                console.error('PWA: Service worker registration failed', error);
            }
        }
    }

    // Public methods
    isAppInstalled() {
        return this.isInstalled;
    }

    canInstall() {
        return this.deferredPrompt !== null;
    }
}

// PWA Analytics
class PWAAnalytics {
    constructor() {
        this.events = [];
        this.init();
    }

    init() {
        this.trackAppLaunch();
        this.trackInstallPrompt();
        this.trackOfflineUsage();
    }

    trackAppLaunch() {
        const launchData = {
            event: 'app_launch',
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            displayMode: window.matchMedia('(display-mode: standalone)').matches ? 'standalone' : 'browser',
            platform: this.getPlatform()
        };

        this.events.push(launchData);
        console.log('PWA Analytics: App launch tracked', launchData);
    }

    trackInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            const promptData = {
                event: 'install_prompt_shown',
                timestamp: new Date().toISOString(),
                platform: this.getPlatform()
            };

            this.events.push(promptData);
            console.log('PWA Analytics: Install prompt tracked', promptData);
        });
    }

    trackOfflineUsage() {
        window.addEventListener('offline', () => {
            const offlineData = {
                event: 'offline_mode_entered',
                timestamp: new Date().toISOString()
            };

            this.events.push(offlineData);
            console.log('PWA Analytics: Offline mode tracked', offlineData);
        });

        window.addEventListener('online', () => {
            const onlineData = {
                event: 'online_mode_restored',
                timestamp: new Date().toISOString()
            };

            this.events.push(onlineData);
            console.log('PWA Analytics: Online mode tracked', onlineData);
        });
    }

    getPlatform() {
        const userAgent = navigator.userAgent.toLowerCase();
        
        if (userAgent.includes('android')) return 'android';
        if (userAgent.includes('iphone') || userAgent.includes('ipad')) return 'ios';
        if (userAgent.includes('windows')) return 'windows';
        if (userAgent.includes('mac')) return 'mac';
        if (userAgent.includes('linux')) return 'linux';
        
        return 'unknown';
    }

    getEvents() {
        return this.events;
    }
}

// Initialize PWA when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.pwaInstaller = new PWAInstaller();
    window.pwaAnalytics = new PWAAnalytics();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PWAInstaller, PWAAnalytics };
}
