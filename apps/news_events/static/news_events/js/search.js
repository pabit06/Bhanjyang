document.addEventListener('DOMContentLoaded', function () {
    // Apply category colors from data attributes
    function hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    document.querySelectorAll('[data-category-color]').forEach(function (element) {
        const color = element.getAttribute('data-category-color');
        if (color) {
            if (element.classList.contains('category-icon-bg')) {
                const rgb = hexToRgb(color);
                if (rgb) {
                    element.style.backgroundColor = `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.2)`;
                }
            } else if (element.classList.contains('category-icon')) {
                element.style.color = color;
            }
        }
    });
});
