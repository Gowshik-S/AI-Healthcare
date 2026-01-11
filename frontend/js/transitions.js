/**
 * Healthcare AI - Smooth Transitions Module
 * Shared transition effects for all pages
 */

(function () {
    'use strict';

    // Wait for DOM
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        initPageLoad();
        initNavbarScroll();
        initScrollAnimations();
        initButtonEffects();
    }

    /**
     * Page load fade-in animation
     */
    function initPageLoad() {
        document.body.style.opacity = '0';
        document.body.style.transition = 'opacity 0.4s ease';

        requestAnimationFrame(() => {
            document.body.style.opacity = '1';
        });
    }

    /**
     * Navbar shadow on scroll
     */
    function initNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        let ticking = false;

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    const scrolled = window.pageYOffset > 50;
                    navbar.style.boxShadow = scrolled
                        ? '0 2px 10px rgba(0, 0, 0, 0.08)'
                        : 'none';
                    navbar.style.background = scrolled
                        ? 'rgba(255, 255, 255, 0.98)'
                        : '';
                    ticking = false;
                });
                ticking = true;
            }
        });
    }

    /**
     * Scroll-triggered fade-in animations
     */
    function initScrollAnimations() {
        const animatedElements = document.querySelectorAll(
            '.card, .action-card, .stat-card, .service-card, .step, ' +
            '.consultation-card, .prescription-card, .activity-item, .trust-item'
        );

        if (!animatedElements.length) return;

        // Set initial state
        animatedElements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            el.style.transitionDelay = `${Math.min(index * 0.05, 0.3)}s`;
        });

        // Intersection Observer
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, {
            root: null,
            rootMargin: '0px 0px -50px 0px',
            threshold: 0.1
        });

        animatedElements.forEach(el => observer.observe(el));
    }

    /**
     * Button hover lift effect
     */
    function initButtonEffects() {
        const buttons = document.querySelectorAll('.btn, .action-card');

        buttons.forEach(btn => {
            btn.style.transition = btn.style.transition
                ? btn.style.transition + ', transform 0.2s ease'
                : 'transform 0.2s ease';

            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-2px)';
            });

            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0)';
            });
        });
    }

    // Expose for manual triggering if needed
    window.HealthcareTransitions = {
        init,
        initScrollAnimations,
        initButtonEffects
    };
})();
