// Navigation handling for both desktop and mobile layouts
document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('navToggle');
    const siteNav = document.getElementById('siteNav');

    const setIconState = (isOpen) => {
        if (!navToggle) return;
        const icon = navToggle.querySelector('i');
        navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        if (icon) {
            icon.classList.toggle('fa-bars', !isOpen);
            icon.classList.toggle('fa-times', isOpen);
        }
    };

    const closeMenu = () => {
        if (!siteNav) return;
        siteNav.classList.remove('is-open');
        setIconState(false);
    };

    if (navToggle && siteNav) {
        navToggle.addEventListener('click', () => {
            const isOpen = !siteNav.classList.contains('is-open');
            siteNav.classList.toggle('is-open', isOpen);
            setIconState(isOpen);
        });

        siteNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                closeMenu();
            });
        });

        document.addEventListener('click', (event) => {
            const isClickOutside = !siteNav.contains(event.target) && !navToggle.contains(event.target);
            if (isClickOutside) {
                closeMenu();
            }
        });
    }

    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href') || '';
        const normalizedHref = href.split('/').pop();
        if (normalizedHref === currentPage) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
});
