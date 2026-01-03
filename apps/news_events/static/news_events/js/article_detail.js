function shareOnFacebook() {
    const url = encodeURIComponent(window.location.href);
    const title = document.title ? encodeURIComponent(document.title) : '';
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}&t=${title}`, '_blank', 'width=600,height=400');
}

function shareOnTwitter() {
    const url = encodeURIComponent(window.location.href);
    const text = document.title ? encodeURIComponent(document.title) : '';
    window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank', 'width=600,height=400');
}

function shareOnLinkedIn() {
    const url = encodeURIComponent(window.location.href);
    const title = document.title ? encodeURIComponent(document.title) : '';
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}&title=${title}`, '_blank', 'width=600,height=400');
}

function copyLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        const message = window.newsEventsMessages?.linkCopied || 'Link copied to clipboard!';
        alert(message);
    });
}
