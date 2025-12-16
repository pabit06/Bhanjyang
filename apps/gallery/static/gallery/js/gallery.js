document.addEventListener('DOMContentLoaded', function () {
    console.log('Gallery page loaded');

    // Parse gallery data from JSON
    const galleryDataElement = document.getElementById('gallery-data');
    if (!galleryDataElement) {
        console.error('Gallery data element not found!');
        return;
    }

    let galleryData;
    try {
        galleryData = JSON.parse(galleryDataElement.textContent);
        console.log('Gallery data parsed successfully');
        console.log('Images count:', galleryData.images.length);
        console.log('Albums count:', Object.keys(galleryData.albums).length);
    } catch (error) {
        console.error('Error parsing gallery data:', error);
        return;
    }

    // Advanced Gallery Manager
    class AdvancedGalleryManager {
        constructor() {
            console.log('AdvancedGalleryManager constructor called');
            this.currentFilter = 'all';
            this.currentAlbum = null;
            this.currentSearch = '';
            this.currentIndex = 0;
            this.imagesPerLoad = 12;
            this.filteredImages = [...galleryData.images];
            this.currentLightboxIndex = 0;
            this.lightboxImages = [];

            console.log('filteredImages initialized with', this.filteredImages.length, 'images');
            this.init();
        }

        init() {
            // Version from template: {{ timestamp }} - cannot use in JS file.
            console.log('init() called');
            this.setupElements();
            this.setupEventListeners();
            this.renderGallery();
            this.setupIntersectionObserver();
            console.log('init() completed');
        }

        setupIntersectionObserver() {
            // Setup intersection observer for album cards animation
            const animatedElements = document.querySelectorAll('.animated-element');

            if ('IntersectionObserver' in window) {
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0)';
                        }
                    });
                }, {
                    threshold: 0.1,
                    rootMargin: '0px 0px -50px 0px'
                });

                animatedElements.forEach(el => {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(30px)';
                    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    observer.observe(el);
                });
            } else {
                // Fallback for browsers without IntersectionObserver
                animatedElements.forEach(el => {
                    el.style.opacity = '1';
                    el.style.transform = 'translateY(0)';
                });
            }
        }

        setupElements() {
            console.log('setupElements called');
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

            console.log('masonryGrid found:', this.masonryGrid);
            console.log('loadMoreBtn found:', this.loadMoreBtn);
        }

        setupEventListeners() {
            // Search functionality
            if (this.searchInput) {
                this.searchInput.addEventListener('input', (e) => {
                    this.currentSearch = e.target.value.toLowerCase();
                    this.filterImages();
                });
            }

            // Clear search
            if (this.clearSearchBtn) {
                this.clearSearchBtn.addEventListener('click', () => {
                    if (this.searchInput) this.searchInput.value = '';
                    this.currentSearch = '';
                    this.filterImages();
                });
            }

            // Filter tabs
            this.filterTabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    this.filterTabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    this.currentFilter = tab.dataset.filter;
                    this.filterImages();
                });
            });

            // Load more button
            if (this.loadMoreBtn) {
                this.loadMoreBtn.addEventListener('click', () => {
                    this.renderGallery();
                });
            }

            // Lightbox events
            if (this.lightboxClose) {
                this.lightboxClose.addEventListener('click', () => {
                    this.closeLightbox();
                });
            }

            if (this.lightboxPrev) {
                this.lightboxPrev.addEventListener('click', () => {
                    this.previousImage();
                });
            }

            if (this.lightboxNext) {
                this.lightboxNext.addEventListener('click', () => {
                    this.nextImage();
                });
            }

            // Keyboard navigation
            document.addEventListener('keydown', (e) => {
                if (this.lightbox && this.lightbox.classList.contains('active')) {
                    if (e.key === 'Escape') this.closeLightbox();
                    if (e.key === 'ArrowLeft') this.previousImage();
                    if (e.key === 'ArrowRight') this.nextImage();
                }
            });
        }

        filterImages() {
            this.filteredImages = galleryData.images.filter(image => {
                const matchesFilter = this.currentFilter === 'all' || image.category === this.currentFilter;
                const matchesSearch = this.currentSearch === '' ||
                    image.title.toLowerCase().includes(this.currentSearch) ||
                    image.caption.toLowerCase().includes(this.currentSearch) ||
                    image.albumName.toLowerCase().includes(this.currentSearch) ||
                    image.category.toLowerCase().includes(this.currentSearch);
                return matchesFilter && matchesSearch;
            });

            this.currentIndex = 0;
            if (this.masonryGrid) this.masonryGrid.innerHTML = '';
            this.renderGallery();
        }

        renderGallery() {
            console.log('renderGallery called');

            if (!this.masonryGrid) return;

            const endIndex = Math.min(this.currentIndex + this.imagesPerLoad, this.filteredImages.length);
            console.log('Rendering from', this.currentIndex, 'to', endIndex);

            for (let i = this.currentIndex; i < endIndex; i++) {
                const item = this.createMasonryItem(this.filteredImages[i], i);
                this.masonryGrid.appendChild(item);
            }

            this.currentIndex = endIndex;

            // Update load more button
            if (this.loadMoreBtn) {
                if (this.currentIndex >= this.filteredImages.length) {
                    this.loadMoreBtn.style.display = 'none';
                } else {
                    this.loadMoreBtn.style.display = 'block';
                }
            }

            // Trigger masonry layout (if using a library like Masonry.js, otherwise CSS grid might suffice or we need to implement JS layout)
            // The original code called this.initMasonry() but it wasn't defined in the visible snippet.
            // I'll assume it might be needed if using a library, but here we can try to rely on CSS.
            if (typeof this.initMasonry === 'function') {
                this.initMasonry();
            }
        }

        createMasonryItem(image, index) {
            const item = document.createElement('div');
            item.className = 'masonry-item gallery-item-advanced magnetic ripple fade-in-up';
            item.dataset.index = index;

            item.innerHTML = `
                <picture>
                    <source media="(max-width: 480px)" srcset="${image.mobileSrc}">
                    <source media="(max-width: 768px)" srcset="${image.tabletSrc}">
                    <img src="${image.src}" alt="${image.alt}" loading="lazy">
                </picture>
                <div class="image-overlay">
                    <h3 class="image-title">${image.title}</h3>
                    <p class="image-category">${image.category}</p>
                </div>
            `;

            item.addEventListener('click', () => {
                this.openLightbox(this.filteredImages.indexOf(image));
            });

            return item;
        }

        openLightbox(index) {
            this.currentLightboxIndex = index;
            this.updateLightboxContent();
            this.lightbox.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        closeLightbox() {
            this.lightbox.classList.remove('active');
            document.body.style.overflow = '';
        }

        previousImage() {
            if (this.currentLightboxIndex > 0) {
                this.currentLightboxIndex--;
                this.updateLightboxContent();
            }
        }

        nextImage() {
            if (this.currentLightboxIndex < this.filteredImages.length - 1) {
                this.currentLightboxIndex++;
                this.updateLightboxContent();
            }
        }

        updateLightboxContent() {
            const image = this.filteredImages[this.currentLightboxIndex];
            this.lightboxImage.src = image.src;
            this.lightboxTitle.textContent = image.title;
            this.lightboxDescription.textContent = image.caption;
        }
    }

    // Initialize
    new AdvancedGalleryManager();
});

// Helper function for album viewing defined in HTML
function showAlbum(albumId) {
    // Navigate to album details page
    window.location.href = `/gallery/album/${albumId}/`;
}
