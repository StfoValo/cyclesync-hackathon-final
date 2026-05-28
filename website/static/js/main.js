import { initTelemetry } from './views/telemetry.js?v=8';
import { initActuarial } from './views/actuarial.js?v=3';
import { initPredictiveAsset } from './views/predictive_asset.js?v=3';
import { initAIStrategy } from './views/ai_strategy.js?v=3';
import { initESG } from './views/esg.js?v=9';
import { initAdjuster } from './views/adjuster.js?v=13';

const viewModules = {
    'telemetry-view':  { path: '/static/partials/telemetry_tab.html',  init: initTelemetry },
    'executive-view':  { path: '/static/partials/executive_tab.html',  init: initActuarial },
    'ai-view':         { path: '/static/partials/ai_tab.html',         init: initAIStrategy },
    'esg-view':        { path: '/static/partials/esg_tab.html?v=7',        init: initESG },
    'adjuster-view':   { path: '/static/partials/adjuster_tab.html',   init: initAdjuster }
};

const loadedViews = new Set();

document.addEventListener('DOMContentLoaded', () => {
    const navItems = document.querySelectorAll('.nav-item');
    const viewSections = document.querySelectorAll('.view-section');

    async function loadView(targetId) {
        const section = document.getElementById(targetId);
        if (!section) return;

        // Hide all
        viewSections.forEach(sec => sec.classList.remove('active'));
        // Show target
        section.classList.add('active');

        if (!loadedViews.has(targetId)) {
            loadedViews.add(targetId); // Prevent race condition on rapid clicks
            try {
                const config = viewModules[targetId];
                if (!config) return;

                const cacheBuster = '?v=' + new Date().getTime();
                const response = await fetch(config.path + cacheBuster);
                if (!response.ok) throw new Error("Failed to load partial");
                const html = await response.text();
                section.innerHTML = html;

                // Instantly translate the newly injected HTML
                if (window.setLanguage) {
                    window.setLanguage(localStorage.getItem('veritwin_lang') || 'en');
                }

                if (config.init) {
                    config.init();
                }

                // Re-initialize Lucide icons after dynamic content injection
                if (window.lucide) setTimeout(() => lucide.createIcons(), 80);

            } catch (err) {
                loadedViews.delete(targetId); // Revert if failed
                console.error(`Error loading view ${targetId}:`, err);
            }
        }

        // Force resize explicitly to prevent window event overload
        setTimeout(() => {
            if (typeof window.Chart !== 'undefined') {
                for (let id in window.Chart.instances) {
                    window.Chart.instances[id].resize();
                }
            }
        }, 50);
    }

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            navItems.forEach(nav => nav.classList.remove('active'));
            e.currentTarget.classList.add('active');

            const targetId = e.currentTarget.getAttribute('data-target');
            loadView(targetId);
        });
    });

    // Load initial view
    const activeItem = document.querySelector('.nav-item.active');
    if (activeItem) {
        loadView(activeItem.getAttribute('data-target'));
    }

    console.log("VeriTwin Frontend Shell Initialized v3.");
});
