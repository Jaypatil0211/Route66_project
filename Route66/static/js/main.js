// Route66 — Main JS

// Mobile menu toggle
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
        mobileMenu.classList.toggle('open');
    });
}

// ── Toast notifications ───────────────────────────────────────────────────────
function dismissToast(toast) {
    toast.classList.add('hiding');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
}

document.querySelectorAll('.toast').forEach(toast => {
    // Auto-dismiss after 5 s (matches CSS progress bar)
    const timer = setTimeout(() => dismissToast(toast), 5000);

    // Manual close button
    const btn = toast.querySelector('.toast-close');
    if (btn) {
        btn.addEventListener('click', () => {
            clearTimeout(timer);
            dismissToast(toast);
        });
    }
});

// Product card hover effect - stagger on load
document.querySelectorAll('.product-card').forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    setTimeout(() => {
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    }, i * 60);
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Confirm remove from cart
document.querySelectorAll('.cart-remove').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (!confirm('Remove this item from your cart?')) {
            e.preventDefault();
        }
    });
});
