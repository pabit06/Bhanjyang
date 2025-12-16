// Bulk Download Functionality
function updateSelection() {
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');
    const count = checkboxes.length;
    const countElement = document.getElementById('selected-count');
    const downloadBtn = document.getElementById('bulk-download-btn');

    countElement.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
    downloadBtn.disabled = count === 0;

    if (count > 0) {
        downloadBtn.classList.remove('disabled:bg-gray-300', 'disabled:cursor-not-allowed');
        downloadBtn.classList.add('bg-deuraligreen', 'hover:bg-bhanjyangred');
    } else {
        downloadBtn.classList.add('disabled:bg-gray-300', 'disabled:cursor-not-allowed');
        downloadBtn.classList.remove('bg-deuraligreen', 'hover:bg-bhanjyangred');
    }
}

function selectAllFiles() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    updateSelection();
}

function clearSelection() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    updateSelection();
}

function downloadSelected() {
    const checkboxes = document.querySelectorAll('.file-checkbox:checked');
    const fileIds = Array.from(checkboxes).map(checkbox => checkbox.getAttribute('data-file-id'));

    if (fileIds.length === 0) {
        alert('Please select at least one file to download.');
        return;
    }

    if (fileIds.length > 10) {
        if (!confirm(`You are about to download ${fileIds.length} files. This may take a while. Continue?`)) {
            return;
        }
    }

    // Create form and submit
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/downloads/bulk/'; // Reused path assuming logic, but best to use rendered URL. But extracted JS shouldn't contain django tags.
    // The original code used {% url "downloads:bulk_download" %}
    // I should pass this URL via data attribute or a global variable.
    // For now I will assume the template will provide it in a data attribute on the body or button.

    // Actually, looking at the template, there is no easy place to put it without modifying the template significantly.
    // I will modify the template to add data-bulk-download-url to the body or a container.
    // Wait, I can't use {% url %} in .js file.
    // I'll grab it from the download button's data attribute which I will add.

    // Let's assume I will add `data-url` to the bulk download button or similar.
    // Or I can keep the logic in the template if it's too coupled, but the goal is to extract.
    // I'll update the function to get the URL from a data attribute on the container.

    const container = document.getElementById('downloadable-files');
    const bulkUrl = container ? container.dataset.bulkUrl : '/downloads/bulk/';

    form.action = bulkUrl;

    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken.value;
        form.appendChild(csrfInput);
    }

    // Add file IDs
    fileIds.forEach(fileId => {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'file_ids';
        input.value = fileId;
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
}

// Initialize selection count on page load
document.addEventListener('DOMContentLoaded', function () {
    updateSelection();
});

function showMoreFiles(categoryCode) {
    // Get current URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('show_all', 'true');

    // Redirect to show all files
    window.location.href = '?' + urlParams.toString();
}

// Add smooth scroll animation for better UX
document.addEventListener('DOMContentLoaded', function () {
    // Add fade-in animation to category sections
    const categorySections = document.querySelectorAll('[id^="category-"]');
    categorySections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';

        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
});
