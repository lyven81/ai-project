// Bookshelf frontend — single ask-bar, streams progress + final brief.

const form = document.getElementById('ask-form');
const input = document.getElementById('question-input');
const askBtn = document.getElementById('ask-button');
const progressContainer = document.getElementById('progress-container');
const statusText = document.getElementById('status-text');
const briefContainer = document.getElementById('brief-container');
const briefContent = document.getElementById('brief-content');

let currentBrief = '';
let sessionId = null;

function setStep(id, state) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('active', 'done');
    if (state) el.classList.add(state);
}

document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
        input.value = chip.dataset.q;
        form.requestSubmit();
    });
});

document.getElementById('ask-another').addEventListener('click', () => {
    briefContainer.classList.add('hidden');
    progressContainer.classList.add('hidden');
    input.value = '';
    input.focus();
});

document.getElementById('copy-brief').addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(currentBrief);
        const btn = document.getElementById('copy-brief');
        const original = btn.textContent;
        btn.textContent = 'Copied ✓';
        setTimeout(() => { btn.textContent = original; }, 1500);
    } catch (e) {
        alert('Copy failed. Use Ctrl+A then Ctrl+C in the brief area.');
    }
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = input.value.trim();
    if (!message) return;

    askBtn.disabled = true;
    briefContainer.classList.add('hidden');
    progressContainer.classList.remove('hidden');
    statusText.textContent = 'Starting...';
    setStep('step-researcher', 'active');
    setStep('step-judge', null);
    setStep('step-builder', null);
    currentBrief = '';

    try {
        const resp = await fetch('/api/chat_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: sessionId }),
        });
        if (!resp.ok || !resp.body) {
            const errText = await resp.text();
            throw new Error(errText || 'Request failed');
        }

        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const evt = JSON.parse(line);
                    if (evt.type === 'progress') {
                        statusText.textContent = evt.text;
                        if (evt.text.includes('Researcher')) {
                            setStep('step-researcher', 'active');
                        } else if (evt.text.includes('Judge')) {
                            setStep('step-researcher', 'done');
                            setStep('step-judge', 'active');
                        } else if (evt.text.includes('Writing') || evt.text.includes('brief')) {
                            setStep('step-judge', 'done');
                            setStep('step-builder', 'active');
                        }
                    } else if (evt.type === 'result') {
                        currentBrief = evt.text || '(empty brief — check console for errors)';
                        setStep('step-builder', 'done');
                        progressContainer.classList.add('hidden');
                        briefContent.innerHTML = marked.parse(currentBrief);
                        briefContainer.classList.remove('hidden');
                    }
                } catch (err) {
                    console.warn('Bad event line:', line, err);
                }
            }
        }
    } catch (err) {
        statusText.textContent = `Error: ${err.message}`;
        console.error(err);
    } finally {
        askBtn.disabled = false;
    }
});
