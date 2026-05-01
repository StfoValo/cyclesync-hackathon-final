document.addEventListener('DOMContentLoaded', () => {

    // 1. Enter Dashboard Logic
    const enterButton = document.getElementById('btn-enter');
    if (enterButton) {
        enterButton.addEventListener('click', () => {
            // Fade to black effect
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s ease';

            setTimeout(() => {
                // Route to the new /dashboard endpoint we created in main.py
                window.location.href = '/dashboard';
            }, 500);
        });
    }

    // 2. Scroll Animation Observer (The Fade-in Cards)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const fadeElements = document.querySelectorAll('.fade-in-section');
    fadeElements.forEach(el => observer.observe(el));
});