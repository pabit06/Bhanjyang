// Gallery Lightbox JavaScript
class GalleryLightbox {
    constructor() {
        this.currentIndex = 0;
        this.images = [];
        this.lightbox = null;
        this.init();
    }

    init() {
        this.createLightboxHTML();
        this.bindEvents();
        this.setupKeyboardNavigation();
        this.setupTouchGestures();
    }

    createLightboxHTML() {
        // Create lightbox HTML structure
        const lightboxHTML = `
            <div id="lightbox" class="lightbox" role="dialog" aria-modal="true" aria-label="Image gallery">
                <div class="lightbox-content">
                    <span class="lightbox-close" aria-label="Close gallery">&times;</span>
                    <img class="lightbox-image" alt="" />
                    <div class="lightbox-caption"></div>
                    <div class="lightbox-nav lightbox-prev" aria-label="Previous image">&#8249;</div>
                    <div class="lightbox-nav lightbox-next" aria-label="Next image">&#8250;</div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', lightboxHTML);
        this.lightbox = document.getElementById('lightbox');
    }

    bindEvents() {
        // Close lightbox events
        this.lightbox.querySelector('.lightbox-close').addEventListener('click', () => this.close());
        this.lightbox.addEventListener('click', (e) => {
            if (e.target === this.lightbox) this.close();
        });

        // Navigation events
        this.lightbox.querySelector('.lightbox-prev').addEventListener('click', () => this.previous());
        this.lightbox.querySelector('.lightbox-next').addEventListener('click', () => this.next());

        // Gallery item clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.gallery-item')) {
                e.preventDefault();
                const galleryItem = e.target.closest('.gallery-item');
                this.openFromGallery(galleryItem);
            }
        });
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (!this.lightbox.classList.contains('active')) return;

            switch(e.key) {
                case 'Escape':
                    this.close();
                    break;
                case 'ArrowLeft':
                    this.previous();
                    break;
                case 'ArrowRight':
                    this.next();
                    break;
                case ' ':
                    e.preventDefault();
                    this.next();
                    break;
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
            this.handleSwipe();
        });

        this.handleSwipe = () => {
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            const minSwipeDistance = 50;

            // Only handle horizontal swipes
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
                if (deltaX > 0) {
                    this.previous();
                } else {
                    this.next();
                }
            }
        };
    }

    openFromGallery(galleryItem) {
        // Get all gallery items
        const gallery = galleryItem.closest('.gallery-grid');
        this.images = Array.from(gallery.querySelectorAll('.gallery-item'));
        this.currentIndex = this.images.indexOf(galleryItem);

        this.open();
    }

    open() {
        if (this.images.length === 0) return;

        this.updateImage();
        this.lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus management for accessibility
        this.lightbox.focus();
        
        // Preload adjacent images
        this.preloadAdjacentImages();
    }

    close() {
        this.lightbox.classList.remove('active');
        document.body.style.overflow = '';
        
        // Return focus to the gallery item that was clicked
        if (this.images[this.currentIndex]) {
            this.images[this.currentIndex].focus();
        }
    }

    updateImage() {
        const currentImage = this.images[this.currentIndex];
        const img = this.lightbox.querySelector('.lightbox-image');
        const caption = this.lightbox.querySelector('.lightbox-caption');

        // Get image source and caption
        const imgSrc = currentImage.querySelector('img').src;
        const imgAlt = currentImage.querySelector('img').alt;
        const imgCaption = currentImage.querySelector('.gallery-caption')?.textContent || imgAlt;

        // Update image
        img.src = imgSrc;
        img.alt = imgAlt;
        caption.textContent = imgCaption;

        // Update navigation visibility
        this.updateNavigation();
    }

    updateNavigation() {
        const prevBtn = this.lightbox.querySelector('.lightbox-prev');
        const nextBtn = this.lightbox.querySelector('.lightbox-next');

        prevBtn.style.display = this.currentIndex > 0 ? 'flex' : 'none';
        nextBtn.style.display = this.currentIndex < this.images.length - 1 ? 'flex' : 'none';
    }

    previous() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updateImage();
            this.preloadAdjacentImages();
        }
    }

    next() {
        if (this.currentIndex < this.images.length - 1) {
            this.currentIndex++;
            this.updateImage();
            this.preloadAdjacentImages();
        }
    }

    preloadAdjacentImages() {
        // Preload previous and next images for smoother navigation
        const preloadIndices = [this.currentIndex - 1, this.currentIndex + 1];
        
        preloadIndices.forEach(index => {
            if (index >= 0 && index < this.images.length) {
                const img = new Image();
                img.src = this.images[index].querySelector('img').src;
            }
        });
    }
}

// Initialize gallery lightbox when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.galleryLightbox = new GalleryLightbox();
});

// Gallery lazy loading
class LazyGallery {
    constructor() {
        this.imageObserver = null;
        this.init();
    }

    init() {
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadImage(entry.target);
                        this.imageObserver.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            this.observeImages();
        } else {
            // Fallback for browsers without IntersectionObserver
            this.loadAllImages();
        }
    }

    observeImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => this.imageObserver.observe(img));
    }

    loadImage(img) {
        const src = img.dataset.src;
        if (src) {
            img.src = src;
            img.removeAttribute('data-src');
            img.classList.remove('lazy');
            img.classList.add('loaded');
        }
    }

    loadAllImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => this.loadImage(img));
    }
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', () => {
    window.lazyGallery = new LazyGallery();
});

// Gallery search functionality
class GallerySearch {
    constructor() {
        this.searchInput = null;
        this.galleryItems = [];
        this.init();
    }

    init() {
        this.searchInput = document.querySelector('#gallery-search');
        if (this.searchInput) {
            this.galleryItems = document.querySelectorAll('.gallery-item');
            this.bindEvents();
        }
    }

    bindEvents() {
        this.searchInput.addEventListener('input', (e) => {
            this.filterImages(e.target.value.toLowerCase());
        });
    }

    filterImages(searchTerm) {
        this.galleryItems.forEach(item => {
            const caption = item.querySelector('.gallery-caption')?.textContent.toLowerCase() || '';
            const alt = item.querySelector('img').alt.toLowerCase() || '';
            
            if (caption.includes(searchTerm) || alt.includes(searchTerm)) {
                item.style.display = 'block';
                item.classList.add('search-match');
            } else {
                item.style.display = 'none';
                item.classList.remove('search-match');
            }
        });

        // Show/hide no results message
        const visibleItems = Array.from(this.galleryItems).filter(item => 
            item.style.display !== 'none'
        );

        this.toggleNoResultsMessage(visibleItems.length === 0 && searchTerm.length > 0);
    }

    toggleNoResultsMessage(show) {
        let noResultsMsg = document.querySelector('.gallery-no-results');
        
        if (show && !noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.className = 'gallery-no-results';
            noResultsMsg.textContent = 'No images found matching your search.';
            noResultsMsg.style.cssText = `
                text-align: center;
                padding: 40px;
                color: #666;
                font-size: 18px;
                grid-column: 1 / -1;
            `;
            
            const gallery = document.querySelector('.gallery-grid');
            if (gallery) {
                gallery.appendChild(noResultsMsg);
            }
        } else if (!show && noResultsMsg) {
            noResultsMsg.remove();
        }
    }
}

// Initialize gallery search
document.addEventListener('DOMContentLoaded', () => {
    window.gallerySearch = new GallerySearch();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GalleryLightbox, LazyGallery, GallerySearch };
}
