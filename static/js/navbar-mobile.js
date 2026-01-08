// static/js/navbar-mobile.js

/**
 * Gestion du menu mobile responsive
 * Contrôle l'ouverture/fermeture du menu hamburger
 */

document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    // Vérifier que les éléments existent
    if (!mobileMenuButton || !mobileMenu) {
        return;
    }

    // SVG icons
    const hamburgerIcon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>';
    const closeIcon = '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>';

    /**
     * Toggle le menu mobile et change l'icône
     */
    function toggleMobileMenu() {
        mobileMenu.classList.toggle('hidden');
        const icon = mobileMenuButton.querySelector('svg');

        if (mobileMenu.classList.contains('hidden')) {
            icon.innerHTML = hamburgerIcon;
        } else {
            icon.innerHTML = closeIcon;
        }
    }

    /**
     * Ferme le menu mobile
     */
    function closeMobileMenu() {
        mobileMenu.classList.add('hidden');
        const icon = mobileMenuButton.querySelector('svg');
        icon.innerHTML = hamburgerIcon;
    }

    // Toggle du menu mobile au clic sur le bouton
    mobileMenuButton.addEventListener('click', toggleMobileMenu);

    // Fermer le menu mobile quand on clique sur un lien
    const mobileLinks = mobileMenu.querySelectorAll('a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });

    // Fermer le menu mobile si on redimensionne vers desktop
    let resizeTimer;
    window.addEventListener('resize', () => {
        // Debounce pour éviter trop d'appels
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (window.innerWidth >= 1024) { // lg breakpoint de Tailwind
                closeMobileMenu();
            }
        }, 250);
    });

    // Fermer le menu si on clique en dehors (optionnel mais recommandé)
    document.addEventListener('click', (event) => {
        const isClickInside = mobileMenu.contains(event.target) ||
            mobileMenuButton.contains(event.target);

        if (!isClickInside && !mobileMenu.classList.contains('hidden')) {
            closeMobileMenu();
        }
    });
});