document.addEventListener('DOMContentLoaded', function () {
    // Newsletter subscription
    const newsletterForm = document.getElementById('newsletter-form');
    const messageDiv = document.getElementById('newsletter-message');

    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const email = formData.get('email');

            if (!email) {
                const message = window.newsEventsMessages?.enterEmail || 'Please enter your email address.';
                showMessage(message, 'error');
                return;
            }

            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            const subscribingText = window.newsEventsMessages?.subscribing || 'Subscribing...';
            submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${subscribingText}`;
            submitBtn.disabled = true;

            // Get URL from form action or predefined variable if needed. 
            // In the original template it was '{% url "news_events:subscribe" %}'
            // We need to handle this. For now, assuming the form has an action or we use a data attribute.
            // But wait, the original code used inline Django template tag. 
            // Better approach: Use a data attribute on the form.
            const subscribeUrl = this.getAttribute('data-url') || '/news-events/subscribe/';

            fetch(subscribeUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showMessage(data.message, 'success');
                        this.reset();
                    } else {
                        showMessage(data.message, 'error');
                    }
                })
                .catch(error => {
                    const message = window.newsEventsMessages?.subscriptionFailed || 'Subscription failed. Please try again later.';
                    showMessage(message, 'error');
                })
                .finally(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                });
        });
    }

    function showMessage(message, type) {
        messageDiv.innerHTML = message;
        messageDiv.className = `mt-4 text-sm ${type === 'success' ? 'text-green-200' : 'text-red-200'}`;

        setTimeout(() => {
            messageDiv.innerHTML = '';
            messageDiv.className = 'mt-4';
        }, 5000);
    }
});
