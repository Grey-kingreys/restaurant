// static/js/navbar-mobile.js - VERSION SIMPLE

// Attendre que tout soit prêt
function initMobileMenu() {

    const btn = document.getElementById('mobile-menu-button');
    const sidebar = document.getElementById('sidebar');
    const mobileMenu = document.getElementById('mobile-menu');


    if (!btn) {
        console.error('Button not found!');
        return;
    }

    btn.addEventListener('click', function () {

        // Afficher/masquer la sidebar
        if (sidebar) {
            sidebar.classList.toggle('hidden');
        }

        // Afficher/masquer le menu mobile
        if (mobileMenu) {
            mobileMenu.classList.toggle('hidden');
        }

        // Changer l'icône
        const icon = btn.querySelector('svg');
        if (icon) {
            const isOpen = sidebar && !sidebar.classList.contains('hidden');

            if (isOpen) {
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>';
            } else {
                icon.innerHTML = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>';
            }
        }
    });
}

// Différentes façons d'attendre que le DOM soit prêt
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileMenu);
} else {
    initMobileMenu();
}
