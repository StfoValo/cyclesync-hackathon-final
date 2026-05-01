import { initTelemetry } from './views/telemetry.js';
import { initActuarial } from './views/actuarial.js';
import { initPredictiveAsset } from './views/predictive_asset.js';
import { initAIStrategy } from './views/ai_strategy.js';
import { initESG } from './views/esg.js';

const viewModules = {
    'telemetry-view': { path: '/static/partials/telemetry_tab.html', init: initTelemetry },
    'executive-view': { path: '/static/partials/executive_tab.html', init: initActuarial },
    'asset-view': { path: '/static/partials/asset_tab.html', init: initPredictiveAsset },
    'ai-view': { path: '/static/partials/ai_tab.html', init: initAIStrategy },
    'esg-view': { path: '/static/partials/esg_tab.html', init: initESG }
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
                
                const response = await fetch(config.path);
                if (!response.ok) throw new Error("Failed to load partial");
                const html = await response.text();
                section.innerHTML = html;
                
                if (config.init) {
                    config.init();
                }
                
                
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
    
    console.log("CycleSync Frontend Shell Initialized.");
});
