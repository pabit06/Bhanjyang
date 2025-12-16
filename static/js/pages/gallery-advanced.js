/**
 * Advanced Gallery JavaScript
 * Next-level frontend features for the gallery app
 */

class AdvancedGalleryManager {
    constructor() {
        this.currentFilter = 'all';
        this.currentAlbum = null;
        this.currentSearch = '';
        this.currentIndex = 0;
        this.imagesPerLoad = 12;
        this.filteredImages = [];
        this.currentLightboxIndex = 0;
        this.lightboxImages = [];
        this.isLoading = false;
        this.intersectionObserver = null;
        this.searchDebounceTimer = null;
        
        this.init();
    }
    
    init() {
        this.setupElements();
        this.setupEventListeners();
        this.setupIntersectionObserver();
        this.setupKeyboardShortcuts();
        this.setupTouchGestures();
        this.loadInitialData();
        this.setupPerformanceOptimizations();
    }
    
    setupElements() {
        this.masonryGrid = document.getElementById('masonry-gallery');
        this.searchInput = document.getElementById('gallery-search');
        this.clearSearchBtn = document.getElementById('clear-search');
        this.loadMoreBtn = document.getElementById('load-more-btn');
        this.loadingSpinner = document.getElementById('loading-spinner');
        this.lightbox = document.getElementById('lightbox');
        this.lightboxImage = document.getElementById('lightbox-image');
        this.lightboxTitle = document.getElementById('lightbox-title');
        this.lightboxDescription = document.getElementById('lightbox-description');
        this.lightboxClose = document.getElementById('lightbox-close');
        this.lightboxPrev = document.getElementById('lightbox-prev');
        this.lightboxNext = document.getElementById('lightbox-next');
        this.filterTabs = document.querySelectorAll('.filter-tab');
        
        // Performance tracking elements
        this.performanceMetrics = {
            renderStart: 0,
            renderEnd: 0,
            imageLoadTimes: []
        };
    }
    
    setupEventListeners() {
        // Search with debouncing
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(this.searchDebounceTimer);
            this.searchDebounceTimer = setTimeout(() => {
                this.currentSearch = e.target.value.toLowerCase();
                this.filterImages();
            }, 300);
        });
        
        this.clearSearchBtn.addEventListener('click', () => {
            this.searchInput.value = '';
            this.currentSearch = '';
            this.filterImages();
        });
        
        // Filter tabs with animation
        this.filterTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.setActiveFilter(tab);
                this.currentFilter = tab.dataset.filter;
                this.currentAlbum = null;
                this.filterImages();
            });
        });
        
        // Load more with loading state
        this.loadMoreBtn.addEventListener('click', () => {
            if (!this.isLoading) {
                this.loadMoreImages();
            }
        });
        
        // Lightbox controls
        this.lightboxClose.addEventListener('click', () => this.closeLightbox());
        this.lightboxPrev.addEventListener('click', () => this.previousImage());
        this.lightboxNext.addEventListener('click', () => this.nextImage());
        
        // Click outside to close lightbox
        this.lightbox.addEventListener('click', (e) => {
            if (e.target === this.lightbox) {
                this.closeLightbox();
            }
        });
        
        // Image load tracking
        this.lightboxImage.addEventListener('load', () => {
            this.trackImageLoadTime();
        });
    }
    
    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.1
        };
        
        this.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                    
                    // Lazy load images
                    const img = entry.target.querySelector('img');
                    if (img && img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                }
            });
        }, options);
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (this.lightbox.classList.contains('active')) {
                switch(e.key) {
                    case 'Escape':
                        this.closeLightbox();
                        break;
                    case 'ArrowLeft':
                        this.previousImage();
                        break;
                    case 'ArrowRight':
                        this.nextImage();
                        break;
                    case 'f':
                    case 'F':
                        this.toggleFullscreen();
                        break;
                }
            } else {
                switch(e.key) {
                    case '/':
                        e.preventDefault();
                        this.searchInput.focus();
                        break;
                    case 'Escape':
                        this.clearSearch();
                        break;
                }
            }
        });
    }
    
    setupTouchGestures() {
        let startX = 0;
        let startY = 0;
        let endX = 0;
        let endY = 0;
        
        this.lightbox.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        this.lightbox.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Horizontal swipe for navigation
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
                if (deltaX > 0) {
                    this.previousImage();
                } else {
                    this.nextImage();
                }
            }
            
            // Vertical swipe to close
            if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > 100) {
                if (deltaY > 0) {
                    this.closeLightbox();
                }
            }
        });
    }
    
    setupPerformanceOptimizations() {
        // Preload next images
        this.preloadImages = new Set();
        
        // Use requestAnimationFrame for smooth animations
        this.animationFrame = null;
        
        // Implement virtual scrolling for large datasets
        this.virtualScrolling = {
            enabled: false,
            itemHeight: 300,
            visibleItems: 10,
            scrollTop: 0
        };
    }
    
    loadInitialData() {
        this.performanceMetrics.renderStart = performance.now();
        
        // Load gallery data from Django template
        if (window.galleryData) {
            this.filteredImages = [...window.galleryData.images];
            this.renderGallery();
        }
        
        this.performanceMetrics.renderEnd = performance.now();
        console.log(`Gallery render time: ${this.performanceMetrics.renderEnd - this.performanceMetrics.renderStart}ms`);
    }
    
    setActiveFilter(activeTab) {
        // Animate filter change
        this.filterTabs.forEach(tab => {
            tab.classList.remove('active');
            tab.style.transform = 'scale(0.95)';
        });
        
        setTimeout(() => {
            activeTab.classList.add('active');
            activeTab.style.transform = 'scale(1)';
        }, 100);
    }
    
    filterImages() {
        this.performanceMetrics.renderStart = performance.now();
        
        this.filteredImages = window.galleryData.images.filter(image => {
            let matchesFilter = true;
            let matchesAlbum = true;
            let matchesSearch = true;
            
            // Category filter
            if (this.currentFilter !== 'all') {
                matchesFilter = image.category === this.currentFilter;
            }
            
            // Album filter
            if (this.currentAlbum !== null) {
                matchesAlbum = image.album === this.currentAlbum;
            }
            
            // Search filter
            if (this.currentSearch) {
                matchesSearch = image.title.toLowerCase().includes(this.currentSearch) ||
                              image.caption.toLowerCase().includes(this.currentSearch) ||
                              image.category.toLowerCase().includes(this.currentSearch) ||
                              image.albumName.toLowerCase().includes(this.currentSearch);
            }
            
            return matchesFilter && matchesAlbum && matchesSearch;
        });
        
        this.currentIndex = 0;
        this.masonryGrid.innerHTML = '';
        this.renderGallery();
        
        this.performanceMetrics.renderEnd = performance.now();
        console.log(`Filter render time: ${this.performanceMetrics.renderEnd - this.performanceMetrics.renderStart}ms`);
    }
    
    createMasonryItem(image, index) {
        const item = document.createElement('div');
        item.className = 'masonry-item';
        item.dataset.index = index;
        
        // Add staggered animation delay
        item.style.animationDelay = `${index * 0.1}s`;
        
        item.innerHTML = `
            <img src="${image.src}" alt="${image.alt}" loading="lazy" 
                 onerror="this.onerror=null;this.src='{% static 'images/default-news-placeholder.png' %}'">
            <div class="image-overlay">
                <div class="image-title">${image.title}</div>
                <div class="image-category">${this.getCategoryIcon(image.category)} ${this.getCategoryName(image.category)}</div>
                <div class="image-actions">
                    <button class="btn-gradient btn-sm" onclick="event.stopPropagation(); this.shareImage('${image.id}')">
                        <i class="fas fa-share"></i>
                    </button>
                    <button class="btn-gradient btn-sm" onclick="event.stopPropagation(); this.downloadImage('${image.src}')">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
        `;
        
        item.addEventListener('click', () => this.openLightbox(index));
        
        // Add intersection observer
        this.intersectionObserver.observe(item);
        
        return item;
    }
    
    getCategoryIcon(category) {
        const icons = {
            'events': '📅',
            'team': '👥',
            'office': '🏢',
            'community': '❤️',
            'awards': '🏆'
        };
        return icons[category] || '📷';
    }
    
    getCategoryName(category) {
        const names = {
            'events': 'Events',
            'team': 'Team',
            'office': 'Office',
            'community': 'Community',
            'awards': 'Awards'
        };
        return names[category] || 'Other';
    }
    
    renderGallery() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        
        this.animationFrame = requestAnimationFrame(() => {
            const endIndex = Math.min(this.currentIndex + this.imagesPerLoad, this.filteredImages.length);
            
            for (let i = this.currentIndex; i < endIndex; i++) {
                const item = this.createMasonryItem(this.filteredImages[i], i);
                this.masonryGrid.appendChild(item);
            }
            
            this.currentIndex = endIndex;
            
            // Update load more button
            if (this.currentIndex >= this.filteredImages.length) {
                this.loadMoreBtn.style.display = 'none';
            } else {
                this.loadMoreBtn.style.display = 'block';
            }
            
            // Preload next batch
            this.preloadNextBatch();
        });
    }
    
    loadMoreImages() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.loadingSpinner.style.display = 'block';
        this.loadMoreBtn.style.display = 'none';
        
        // Simulate loading delay for better UX
        setTimeout(() => {
            this.renderGallery();
            this.loadingSpinner.style.display = 'none';
            this.isLoading = false;
        }, 500);
    }
    
    preloadNextBatch() {
        const nextBatch = this.filteredImages.slice(this.currentIndex, this.currentIndex + this.imagesPerLoad);
        
        nextBatch.forEach(image => {
            if (!this.preloadImages.has(image.src)) {
                const img = new Image();
                img.src = image.src;
                this.preloadImages.add(image.src);
            }
        });
    }
    
    openLightbox(index) {
        this.currentLightboxIndex = index;
        this.lightboxImages = this.filteredImages;
        
        const image = this.lightboxImages[index];
        this.lightboxImage.src = image.src;
        this.lightboxImage.alt = image.alt;
        this.lightboxTitle.textContent = image.title;
        this.lightboxDescription.textContent = image.caption || 'No description available';
        
        this.lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Preload adjacent images
        this.preloadAdjacentImages();
        
        // Track lightbox usage
        this.trackLightboxUsage();
    }
    
    closeLightbox() {
        this.lightbox.classList.remove('active');
        document.body.style.overflow = 'auto';
    }
    
    previousImage() {
        if (this.currentLightboxIndex > 0) {
            this.currentLightboxIndex--;
        } else {
            this.currentLightboxIndex = this.lightboxImages.length - 1;
        }
        this.updateLightboxImage();
    }
    
    nextImage() {
        if (this.currentLightboxIndex < this.lightboxImages.length - 1) {
            this.currentLightboxIndex++;
        } else {
            this.currentLightboxIndex = 0;
        }
        this.updateLightboxImage();
    }
    
    updateLightboxImage() {
        const image = this.lightboxImages[this.currentLightboxIndex];
        
        // Add loading state
        this.lightboxImage.style.opacity = '0.5';
        
        this.lightboxImage.src = image.src;
        this.lightboxImage.alt = image.alt;
        this.lightboxTitle.textContent = image.title;
        this.lightboxDescription.textContent = image.caption || 'No description available';
        
        // Remove loading state when image loads
        this.lightboxImage.onload = () => {
            this.lightboxImage.style.opacity = '1';
        };
        
        // Preload adjacent images
        this.preloadAdjacentImages();
    }
    
    preloadAdjacentImages() {
        const prevIndex = this.currentLightboxIndex > 0 ? this.currentLightboxIndex - 1 : this.lightboxImages.length - 1;
        const nextIndex = this.currentLightboxIndex < this.lightboxImages.length - 1 ? this.currentLightboxIndex + 1 : 0;
        
        [prevIndex, nextIndex].forEach(index => {
            const image = this.lightboxImages[index];
            if (!this.preloadImages.has(image.src)) {
                const img = new Image();
                img.src = image.src;
                this.preloadImages.add(image.src);
            }
        });
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            this.lightbox.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }
    
    shareImage(imageId) {
        if (navigator.share) {
            navigator.share({
                title: 'Gallery Image',
                text: 'Check out this image from Bhanjyang Cooperative',
                url: window.location.href
            });
        } else {
            // Fallback to clipboard
            navigator.clipboard.writeText(window.location.href);
            this.showNotification('Link copied to clipboard!', 'success');
        }
    }
    
    downloadImage(imageSrc) {
        const link = document.createElement('a');
        link.href = imageSrc;
        link.download = imageSrc.split('/').pop();
        link.click();
    }
    
    clearSearch() {
        this.searchInput.value = '';
        this.currentSearch = '';
        this.filterImages();
    }
    
    trackImageLoadTime() {
        const loadTime = performance.now() - this.performanceMetrics.renderStart;
        this.performanceMetrics.imageLoadTimes.push(loadTime);
        
        if (this.performanceMetrics.imageLoadTimes.length > 10) {
            this.performanceMetrics.imageLoadTimes.shift();
        }
    }
    
    trackLightboxUsage() {
        // Track analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'lightbox_open', {
                'event_category': 'gallery',
                'event_label': 'image_view'
            });
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // Public API methods
    getPerformanceMetrics() {
        return {
            ...this.performanceMetrics,
            averageImageLoadTime: this.performanceMetrics.imageLoadTimes.reduce((a, b) => a + b, 0) / this.performanceMetrics.imageLoadTimes.length
        };
    }
    
    refresh() {
        this.currentIndex = 0;
        this.masonryGrid.innerHTML = '';
        this.filterImages();
    }
    
    destroy() {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
        
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        
        clearTimeout(this.searchDebounceTimer);
    }
}

// Album functionality
function showAlbum(albumId) {
    const galleryManager = window.galleryManager;
    galleryManager.currentAlbum = parseInt(albumId);
    galleryManager.currentFilter = 'all';
    
    // Update UI with animation
    document.querySelectorAll('.album-card').forEach(card => {
        card.classList.remove('ring-2', 'ring-bhanjyangred');
    });
    
    const activeCard = document.querySelector(`[data-album-id="${albumId}"]`);
    if (activeCard) {
        activeCard.classList.add('ring-2', 'ring-bhanjyangred');
        activeCard.style.transform = 'scale(1.05)';
        setTimeout(() => {
            activeCard.style.transform = 'scale(1)';
        }, 200);
    }
    
    // Reset filter tabs
    galleryManager.filterTabs.forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector('[data-filter="all"]').classList.add('active');
    
    galleryManager.filterImages();
}

// Initialize gallery when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        .animate-fade-in {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animate-fade-in-up {
            animation: fadeInUp 0.8s ease forwards;
        }
        
        .image-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            opacity: 0;
            transform: translateY(10px);
            transition: all 0.3s ease;
        }
        
        .masonry-item:hover .image-actions {
            opacity: 1;
            transform: translateY(0);
        }
        
        .btn-sm {
            padding: 0.5rem;
            font-size: 0.875rem;
        }
    `;
    document.head.appendChild(style);
    
    // Initialize gallery manager
    window.galleryManager = new AdvancedGalleryManager();
    
    // Add global keyboard shortcuts info
    const shortcutsInfo = document.createElement('div');
    shortcutsInfo.className = 'fixed bottom-4 right-4 bg-white p-4 rounded-lg shadow-lg text-sm opacity-0 pointer-events-none transition-opacity duration-300';
    shortcutsInfo.innerHTML = `
        <div class="font-semibold mb-2">Keyboard Shortcuts:</div>
        <div>/ - Focus search</div>
        <div>← → - Navigate lightbox</div>
        <div>F - Toggle fullscreen</div>
        <div>Esc - Close/clear</div>
    `;
    document.body.appendChild(shortcutsInfo);
    
    // Show shortcuts on first visit
    let shortcutsShown = localStorage.getItem('gallery-shortcuts-shown');
    if (!shortcutsShown) {
        setTimeout(() => {
            shortcutsInfo.classList.remove('opacity-0');
            shortcutsInfo.classList.add('opacity-100');
            setTimeout(() => {
                shortcutsInfo.classList.remove('opacity-100');
                shortcutsInfo.classList.add('opacity-0');
            }, 5000);
            localStorage.setItem('gallery-shortcuts-shown', 'true');
        }, 2000);
    }
});

// Export for global access
window.AdvancedGalleryManager = AdvancedGalleryManager;
