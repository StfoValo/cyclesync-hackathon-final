// ==========================================
// INTERNATIONALIZATION (i18n) ENGINE
// ==========================================

const translations = {
    en: {
        "hero-title": "The Sustainability <br /> <span class='text-brand-400 glow-text'>Digital Twin.</span>",
        "hero-subtitle": "Bridging the gap between a vehicle's birth, life, and second life. Moving the automotive industry beyond 'replace-by-default'.",
        "btn-enterprise": "Enterprise Portal",
        "btn-driver": "Driver Hub"
    },
    it: {
        "hero-title": "Il <span class='text-brand-400 glow-text'>Digital Twin</span> <br /> della Sostenibilità.",
        "hero-subtitle": "Colmiamo il divario tra la nascita, la vita e la seconda vita di un veicolo. Oltre il concetto di 'sostituzione di default'.",
        "btn-enterprise": "Portale Enterprise",
        "btn-driver": "App Guidatore"
    }
};

// Make function available globally so the HTML buttons can trigger it
window.setLanguage = function (lang) {
    // 1. Save preference
    localStorage.setItem('cyclesync_lang', lang);

    // 2. Update UI Toggle styling
    const btnEn = document.getElementById('lang-en');
    const btnIt = document.getElementById('lang-it');

    if (lang === 'en') {
        btnEn.className = "px-3 py-1.5 rounded-full text-xs font-bold transition-all bg-brand-500 text-slate-900 shadow-[0_0_10px_rgba(0,229,255,0.4)]";
        btnIt.className = "px-3 py-1.5 rounded-full text-xs font-bold transition-all text-slate-400 hover:text-white bg-transparent shadow-none";
    } else {
        btnIt.className = "px-3 py-1.5 rounded-full text-xs font-bold transition-all bg-brand-500 text-slate-900 shadow-[0_0_10px_rgba(0,229,255,0.4)]";
        btnEn.className = "px-3 py-1.5 rounded-full text-xs font-bold transition-all text-slate-400 hover:text-white bg-transparent shadow-none";
    }

    // 3. Swap the text using the dictionary
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang][key]) {
            element.innerHTML = translations[lang][key];
        }
    });
};

// Check memory on load (run this inside DOMContentLoaded or just at the bottom)
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('cyclesync_lang') || 'en';
    setLanguage(savedLang);
});