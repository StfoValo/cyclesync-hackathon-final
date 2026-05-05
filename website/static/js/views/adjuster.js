export function initAdjuster() {
    const selector = document.getElementById('claim-selector');
    const scenarios = document.querySelectorAll('.scenario-container');

    if (selector) {
        selector.addEventListener('change', (e) => {
            const selectedVal = e.target.value;

            // Hide all scenarios
            scenarios.forEach(sec => {
                sec.classList.add('hidden');
                sec.classList.remove('fade-in');
            });

            // Show the selected scenario
            const activeScenario = document.getElementById('scenario-' + selectedVal);
            if (activeScenario) {
                activeScenario.classList.remove('hidden');
                // Trigger a quick reflow to restart the CSS fade-in animation
                void activeScenario.offsetWidth;
                activeScenario.classList.add('fade-in');
            }
        });
    }
}