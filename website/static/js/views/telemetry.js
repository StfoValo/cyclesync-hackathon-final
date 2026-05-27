import { initRegistry } from './registry.js?v=8';
import { initVehiclePassport } from './vehicle_passport.js?v=10';

export function initTelemetry() {
    const mapFrame = document.getElementById('map-frame');
    if (mapFrame) {
        mapFrame.src = '/api/fleet/map?view=fleet';
    }

    const btnViewFleet = document.getElementById('btn-view-fleet');
    const btnViewRegistry = document.getElementById('btn-view-registry');
    const btnViewSuppliers = document.getElementById('btn-view-suppliers');

    const mapPanel = document.getElementById('map-view-panel');
    const registryPanel = document.getElementById('registry-view-panel');
    const passportPanel = document.getElementById('vehicle-passport-panel');

    const allBtns = [btnViewFleet, btnViewRegistry, btnViewSuppliers].filter(Boolean);

    function activateBtn(btn) {
        allBtns.forEach(b => {
            b.classList.remove('bg-brand-600', 'text-white', 'shadow-lg');
            b.classList.add('text-slate-400', 'hover:text-white');
        });
        btn.classList.add('bg-brand-600', 'text-white', 'shadow-lg');
        btn.classList.remove('text-slate-400', 'hover:text-white');
    }

    function showPanel(panel) {
        [mapPanel, registryPanel, passportPanel].forEach(p => { if (p) p.classList.add('hidden'); });
        if (panel) panel.classList.remove('hidden');
    }

    if (btnViewFleet) {
        btnViewFleet.addEventListener('click', () => {
            activateBtn(btnViewFleet);
            showPanel(mapPanel);
            if (mapFrame) mapFrame.src = '/api/fleet/map?view=fleet';
        });
    }

    if (btnViewRegistry) {
        btnViewRegistry.addEventListener('click', () => {
            activateBtn(btnViewRegistry);
            showPanel(registryPanel);
        });
    }

    if (btnViewSuppliers) {
        btnViewSuppliers.addEventListener('click', () => {
            activateBtn(btnViewSuppliers);
            showPanel(mapPanel);
            if (mapFrame) mapFrame.src = '/api/fleet/map?view=suppliers';
        });
    }

    // Initialize the registry module (loads data, wires event listeners)
    initRegistry();
    initVehiclePassport();
}
