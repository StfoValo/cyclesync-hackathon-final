export function initTelemetry() {
    const mapFrame = document.getElementById('map-frame');
    if (mapFrame) {
        mapFrame.src = '/api/fleet/map?view=fleet';
    }

    const btnViewFleet = document.getElementById('btn-view-fleet');
    const btnViewSuppliers = document.getElementById('btn-view-suppliers');

    if (btnViewFleet && btnViewSuppliers && mapFrame) {
        btnViewFleet.addEventListener('click', () => {
            btnViewFleet.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewFleet.classList.remove('text-slate-400', 'hover:text-white');
            
            btnViewSuppliers.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewSuppliers.classList.add('text-slate-400', 'hover:text-white');
            
            mapFrame.src = '/api/fleet/map?view=fleet';
        });

        btnViewSuppliers.addEventListener('click', () => {
            btnViewSuppliers.classList.add('bg-brand-600', 'text-white', 'shadow');
            btnViewSuppliers.classList.remove('text-slate-400', 'hover:text-white');
            
            btnViewFleet.classList.remove('bg-brand-600', 'text-white', 'shadow');
            btnViewFleet.classList.add('text-slate-400', 'hover:text-white');
            
            mapFrame.src = '/api/fleet/map?view=suppliers';
        });
    }
}
