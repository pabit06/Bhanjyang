// Service Worker for Bhanjyang Cooperative PWA
const CACHE_NAME = 'bhanjyang-coop-v1';
const STATIC_CACHE_NAME = 'bhanjyang-static-v1';
const DYNAMIC_CACHE_NAME = 'bhanjyang-dynamic-v1';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/',
    '/about/',
    '/about/team/',
    '/about/contact/',
    '/gallery/',
    '/static/css/dist/output.css',
    '/static/css/about-animations.css',
    '/static/css/advanced-animations.css',
    '/static/css/dark-mode.css',
    '/static/css/gallery-lightbox.css',
    '/static/js/about-interactive.js',
    '/static/js/advanced-animations.js',
    '/static/js/dark-mode.js',
    '/static/js/gallery-lightbox.js',
    '/static/favicon/favicon-32x32.png',
    '/static/favicon/favicon-16x16.png',
    '/static/images/slider1.jpg',
    '/static/images/slider2.jpg',
    '/static/images/slider3.jpg',
    '/static/images/slider4.jpg',
    '/static/images/slider5.jpg',
    '/static/images/banner.jpg'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE_NAME)
            .then((cache) => {
                console.log('Service Worker: Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Service Worker: Installation complete');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Service Worker: Installation failed', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== STATIC_CACHE_NAME && cacheName !== DYNAMIC_CACHE_NAME) {
                            console.log('Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activation complete');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip external requests
    if (url.origin !== location.origin) {
        return;
    }
    
    event.respondWith(
        caches.match(request)
            .then((cachedResponse) => {
                // Return cached version if available
                if (cachedResponse) {
                    console.log('Service Worker: Serving from cache', request.url);
                    return cachedResponse;
                }
                
                // Otherwise, fetch from network
                return fetch(request)
                    .then((response) => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response
                        const responseToCache = response.clone();
                        
                        // Cache dynamic content
                        caches.open(DYNAMIC_CACHE_NAME)
                            .then((cache) => {
                                cache.put(request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch((error) => {
                        console.log('Service Worker: Network request failed', request.url);
                        
                        // Return offline page for navigation requests
                        if (request.destination === 'document') {
                            return caches.match('/offline.html');
                        }
                        
                        // Return cached version of the same resource if available
                        return caches.match(request);
                    });
            })
    );
});

// Background sync for form submissions
self.addEventListener('sync', (event) => {
    console.log('Service Worker: Background sync triggered', event.tag);
    
    if (event.tag === 'contact-form') {
        event.waitUntil(syncContactForm());
    } else if (event.tag === 'newsletter-signup') {
        event.waitUntil(syncNewsletterSignup());
    }
});

// Sync contact form submissions
async function syncContactForm() {
    try {
        const pendingForms = await getPendingForms('contact-forms');
        
        for (const form of pendingForms) {
            try {
                const response = await fetch('/about/contact/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(form.data)
                });
                
                if (response.ok) {
                    await removePendingForm('contact-forms', form.id);
                    console.log('Service Worker: Contact form synced successfully');
                }
            } catch (error) {
                console.error('Service Worker: Failed to sync contact form', error);
            }
        }
    } catch (error) {
        console.error('Service Worker: Error syncing contact forms', error);
    }
}

// Sync newsletter signups
async function syncNewsletterSignup() {
    try {
        const pendingSignups = await getPendingForms('newsletter-signups');
        
        for (const signup of pendingSignups) {
            try {
                const response = await fetch('/about/api/newsletter-signup/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(signup.data)
                });
                
                if (response.ok) {
                    await removePendingForm('newsletter-signups', signup.id);
                    console.log('Service Worker: Newsletter signup synced successfully');
                }
            } catch (error) {
                console.error('Service Worker: Failed to sync newsletter signup', error);
            }
        }
    } catch (error) {
        console.error('Service Worker: Error syncing newsletter signups', error);
    }
}

// Get pending forms from IndexedDB
async function getPendingForms(storeName) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('BhanjyangCoopDB', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = () => resolve(getAllRequest.result);
            getAllRequest.onerror = () => reject(getAllRequest.error);
        };
        
        request.onupgradeneeded = () => {
            const db = request.result;
            
            if (!db.objectStoreNames.contains('contact-forms')) {
                db.createObjectStore('contact-forms', { keyPath: 'id', autoIncrement: true });
            }
            
            if (!db.objectStoreNames.contains('newsletter-signups')) {
                db.createObjectStore('newsletter-signups', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

// Remove pending form from IndexedDB
async function removePendingForm(storeName, id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('BhanjyangCoopDB', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Service Worker: Push notification received');
    
    const options = {
        body: 'New update available from Bhanjyang Cooperative',
        icon: '/static/favicon/android-chrome-192x192.png',
        badge: '/static/favicon/favicon-32x32.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Explore',
                icon: '/static/favicon/favicon-32x32.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/favicon/favicon-32x32.png'
            }
        ]
    };
    
    if (event.data) {
        const data = event.data.json();
        options.body = data.body || options.body;
        options.title = data.title || 'Bhanjyang Cooperative';
    }
    
    event.waitUntil(
        self.registration.showNotification('Bhanjyang Cooperative', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Service Worker: Notification clicked');
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/about/')
        );
    } else if (event.action === 'close') {
        // Just close the notification
    } else {
        // Default action - open the app
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message handling from main thread
self.addEventListener('message', (event) => {
    console.log('Service Worker: Message received', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(STATIC_CACHE_NAME)
                .then((cache) => {
                    return cache.addAll(event.data.urls);
                })
        );
    }
});

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
    console.log('Service Worker: Periodic sync triggered', event.tag);
    
    if (event.tag === 'content-sync') {
        event.waitUntil(syncContent());
    }
});

// Sync content updates
async function syncContent() {
    try {
        // Check for updates to static content
        const response = await fetch('/api/content-updates/');
        if (response.ok) {
            const updates = await response.json();
            console.log('Service Worker: Content updates available', updates);
            
            // Notify the main thread about updates
            const clients = await self.clients.matchAll();
            clients.forEach(client => {
                client.postMessage({
                    type: 'CONTENT_UPDATES',
                    updates: updates
                });
            });
        }
    } catch (error) {
        console.error('Service Worker: Error syncing content', error);
    }
}

console.log('Service Worker: Script loaded');
