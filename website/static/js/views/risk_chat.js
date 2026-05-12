document.addEventListener('click', async (e) => {
    // Dynamic suggested questions visibility
    const btnRegional = e.target.closest('#btn-view-regional');
    const btnDemo = e.target.closest('#btn-view-demographic');
    const btnAsset = e.target.closest('#btn-view-asset');
    
    if (btnRegional || btnDemo || btnAsset) {
        const qGroupRegional = document.getElementById('q-group-regional');
        const qGroupDemo = document.getElementById('q-group-demo');
        const qGroupAsset = document.getElementById('q-group-asset');
        
        if (qGroupRegional && qGroupDemo && qGroupAsset) {
            qGroupRegional.classList.add('hidden');
            qGroupDemo.classList.add('hidden');
            qGroupAsset.classList.add('hidden');
            
            if (btnRegional) qGroupRegional.classList.remove('hidden');
            if (btnDemo) qGroupDemo.classList.remove('hidden');
            if (btnAsset) qGroupAsset.classList.remove('hidden');
        }
    }

    // Listen for clicks on our predefined question buttons
    const btn = e.target.closest('.suggested-q');
    if (btn) {
        const questionId = btn.getAttribute('data-qid');
        const questionText = btn.querySelector('span').innerText;
        await handlePredefinedQuery(questionId, questionText);
    }
});

async function handlePredefinedQuery(questionId, questionText) {
    const chatHistory = document.getElementById('risk-chat-history');
    const currentLang = localStorage.getItem('veritwin_lang') || 'en';

    // 1. Append User Selection
    appendMessage(chatHistory, 'user', questionText);

    // 2. Create the AI Bubble that we will slowly fill with text
    const aiBubbleId = 'ai-msg-' + Date.now();
    const bubbleContent = appendEmptyAIMessage(chatHistory, aiBubbleId);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        // 3. Call the Backend
        const response = await fetch('/api/ai/ask-predefined', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: questionId,
                question_text: questionText,
                language: currentLang
            })
        });

        // 4. Read the Stream (The Typewriter Effect!)
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            // Decode the chunk and append it
            const chunk = decoder.decode(value);
            console.log("Stream chunk:", chunk);
            fullText += chunk;

            // Format markdown (lists, bold, breaks)
            let formattedText = fullText
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/(?:^|\n)(?:[*\+\-]\s+.*(?:\n|$))+/g, function(match) {
                    const items = match.trim().split(/\n/).map(line => {
                        return '<li>' + line.replace(/^[*\+\-]\s+/, '') + '</li>';
                    }).join('');
                    return '<ul class="list-disc ml-4 space-y-1 my-2">' + items + '</ul>';
                })
                .replace(/\n\n/g, '<br><br>')
                .replace(/\n/g, '<br>');

            bubbleContent.innerHTML = formattedText;
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

    } catch (error) {
        console.error("Chat Stream Error:", error);
        bubbleContent.innerHTML = '⚠️ Connection to VeriTwin AI Orchestrator lost. Please check network logs.';
    }
}

function appendMessage(container, sender, text) {
    const isUser = sender === 'user';
    const wrapper = document.createElement('div');
    wrapper.className = `flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`;

    wrapper.innerHTML = `
        <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 border ${isUser ? 'bg-slate-700 border-slate-600' : 'bg-brand-500/20 border-brand-500/50'}">
            <span class="text-xs">${isUser ? '👤' : 'AI'}</span>
        </div>
        <div class="text-sm p-3 rounded-2xl border ${isUser ? 'bg-brand-600 text-white rounded-tr-none border-brand-500 shadow-lg' : 'bg-slate-800 text-slate-200 rounded-tl-none border-white/5'}">
            ${text}
        </div>
    `;
    container.appendChild(wrapper);
}

function appendEmptyAIMessage(container, id) {
    const wrapper = document.createElement('div');
    wrapper.className = "flex gap-3";
    wrapper.innerHTML = `
        <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 border bg-brand-500/20 border-brand-500/50">
            <span class="text-xs">AI</span>
        </div>
        <div id="${id}" class="text-sm p-3 rounded-2xl border bg-slate-800 text-slate-200 rounded-tl-none border-white/5 w-full leading-relaxed">
            <span class="animate-pulse">...</span>
        </div>
    `;
    container.appendChild(wrapper);
    return wrapper.querySelector(`#${id}`);
}