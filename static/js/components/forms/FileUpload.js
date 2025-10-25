/**
 * FileUpload Component
 * 
 * A modern file upload component with drag-and-drop support,
 * file validation, progress tracking, and preview functionality.
 */

class FileUpload extends Component {
    get defaultOptions() {
        return {
            accept: '*/*',
            maxSize: 5 * 1024 * 1024, // 5MB
            maxFiles: 1,
            allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'],
            showPreview: true,
            showProgress: true,
            dragDropClass: 'file-upload-drag-over',
            errorClass: 'file-upload-error',
            successClass: 'file-upload-success',
            progressClass: 'file-upload-progress'
        };
    }

    init() {
        this.input = this.element.querySelector('input[type="file"]');
        this.dropZone = this.element.querySelector('.file-upload-dropzone');
        this.preview = this.element.querySelector('.file-upload-preview');
        this.progress = this.element.querySelector('.file-upload-progress');
        this.errorMessage = this.element.querySelector('.file-upload-error-message');
        this.fileList = this.element.querySelector('.file-upload-list');
        
        if (!this.input) {
            console.warn('FileUpload: No file input found');
            return;
        }

        this.setupDragDrop();
        this.setupFileInput();
        this.setupValidation();
        super.init();
    }

    setupDragDrop() {
        if (!this.dropZone) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.addClass(this.options.dragDropClass);
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.removeClass(this.options.dragDropClass);
            }, false);
        });

        // Handle dropped files
        this.dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        }, false);
    }

    setupFileInput() {
        this.input.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });
    }

    setupValidation() {
        // Set input attributes based on options
        if (this.options.accept !== '*/*') {
            this.input.accept = this.options.accept;
        }

        if (this.options.maxFiles > 1) {
            this.input.multiple = true;
        }
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleFiles(files) {
        if (files.length === 0) return;

        // Validate file count
        if (files.length > this.options.maxFiles) {
            this.showError(`Maximum ${this.options.maxFiles} file(s) allowed`);
            return;
        }

        // Process each file
        Array.from(files).forEach(file => {
            this.processFile(file);
        });
    }

    processFile(file) {
        // Validate file
        const validation = this.validateFile(file);
        if (!validation.valid) {
            this.showError(validation.message);
            return;
        }

        // Show preview if enabled
        if (this.options.showPreview) {
            this.showPreview(file);
        }

        // Show success
        this.showSuccess();
        this.emit('file:uploaded', { file });
    }

    validateFile(file) {
        // Check file size
        if (file.size > this.options.maxSize) {
            return {
                valid: false,
                message: `File size must not exceed ${this.formatFileSize(this.options.maxSize)}`
            };
        }

        // Check file type
        if (this.options.allowedTypes.length > 0 && 
            !this.options.allowedTypes.includes(file.type)) {
            return {
                valid: false,
                message: `File type ${file.type} is not allowed`
            };
        }

        return { valid: true };
    }

    showPreview(file) {
        if (!this.preview) return;

        this.preview.innerHTML = '';

        if (file.type.startsWith('image/')) {
            const img = document.createElement('img');
            img.src = URL.createObjectURL(file);
            img.alt = file.name;
            img.className = 'file-upload-preview-image';
            this.preview.appendChild(img);
        } else {
            const div = document.createElement('div');
            div.className = 'file-upload-preview-file';
            div.innerHTML = `
                <div class="file-icon">📄</div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
            `;
            this.preview.appendChild(div);
        }
    }

    showProgress(percent) {
        if (!this.progress || !this.options.showProgress) return;

        const progressBar = this.progress.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${percent}%`;
        }

        const progressText = this.progress.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${Math.round(percent)}%`;
        }
    }

    showError(message) {
        this.removeClass(this.options.successClass);
        this.addClass(this.options.errorClass);
        
        if (this.errorMessage) {
            this.errorMessage.textContent = message;
            this.errorMessage.style.display = 'block';
        }

        this.emit('file:error', { message });
    }

    showSuccess() {
        this.removeClass(this.options.errorClass);
        this.addClass(this.options.successClass);
        
        if (this.errorMessage) {
            this.errorMessage.style.display = 'none';
        }

        this.emit('file:success');
    }

    clear() {
        this.input.value = '';
        this.removeClass(this.options.errorClass);
        this.removeClass(this.options.successClass);
        
        if (this.preview) {
            this.preview.innerHTML = '';
        }

        if (this.progress) {
            const progressBar = this.progress.querySelector('.progress-bar');
            if (progressBar) {
                progressBar.style.width = '0%';
            }
        }

        if (this.errorMessage) {
            this.errorMessage.style.display = 'none';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Public API methods
    getFiles() {
        return Array.from(this.input.files);
    }

    setFiles(files) {
        const dataTransfer = new DataTransfer();
        files.forEach(file => dataTransfer.items.add(file));
        this.input.files = dataTransfer.files;
    }

    upload(url, options = {}) {
        const files = this.getFiles();
        if (files.length === 0) return Promise.reject('No files selected');

        const formData = new FormData();
        files.forEach(file => {
            formData.append('file', file);
        });

        return fetch(url, {
            method: 'POST',
            body: formData,
            ...options
        }).then(response => {
            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }
            return response.json();
        });
    }
}

// Auto-initialize file uploads
document.addEventListener('DOMContentLoaded', () => {
    const fileUploads = document.querySelectorAll('.file-upload');
    fileUploads.forEach(upload => new FileUpload(upload));
});

// Export for use in other modules
window.FileUpload = FileUpload;
