export function initAIStrategy() {
    const btnAnalyze = document.getElementById('btn-analyze');
    const regionSelector = document.getElementById('region-selector');
    const aiTerminal = document.getElementById('ai-terminal');

    if (btnAnalyze && regionSelector && aiTerminal) {
        btnAnalyze.addEventListener('click', async () => {
            const region = regionSelector.value;
            btnAnalyze.disabled = true;
            btnAnalyze.innerHTML = "Orchestrating Network...";
            
            aiTerminal.innerHTML = `⚠️ Fetching live telemetry for <b>${region}</b>...\n\n`;

            // Reset KPIs
            document.getElementById('ai-kpi-targeted').innerText = "---";
            document.getElementById('ai-kpi-opened').innerText = "---";
            document.getElementById('ai-kpi-booked').innerText = "---";
            document.getElementById('ai-kpi-roi').innerText = "---";

            try {
                const response = await fetch(`/api/ai/orchestrate/${region}`);
                const reader = response.body.getReader();
                const decoder = new TextDecoder("utf-8");

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    const cleanChunk = chunk.replace(/###/g, '').replace(/\*\*/g, '');
                    aiTerminal.innerHTML += cleanChunk;
                    aiTerminal.scrollTop = aiTerminal.scrollHeight;
                }
                
                // Simulate analytics arriving 1.5s later
                setTimeout(() => {
                    const targeted = Math.floor(Math.random() * (15000 - 8000 + 1)) + 8000;
                    const opened = Math.floor(targeted * (Math.random() * (0.45 - 0.35) + 0.35));
                    const booked = Math.floor(opened * (Math.random() * (0.12 - 0.08) + 0.08));
                    const roi = booked * (Math.random() * (4500 - 2500) + 2500);
                    
                    document.getElementById('ai-kpi-targeted').innerText = targeted.toLocaleString();
                    document.getElementById('ai-kpi-opened').innerText = Math.floor((opened / targeted) * 100) + "%";
                    document.getElementById('ai-kpi-booked').innerText = booked.toLocaleString();
                    document.getElementById('ai-kpi-roi').innerText = '€' + roi.toLocaleString(undefined, {maximumFractionDigits: 0});
                }, 1500);
                
            } catch (error) {
                aiTerminal.innerHTML += `\n\n<b style='color: #FF5A5A;'>[ERROR]</b> ${error.message}`;
            } finally {
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = `<svg class="w-5 h-5 inline-block mr-2 -mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>Generate Intervention Strategy`;
            }
        });
    }
}
