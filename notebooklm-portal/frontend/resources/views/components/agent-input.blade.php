<div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;">
    <div style="display: flex; gap: 0.5rem;">
        <input type="text" id="agent-input" placeholder="Ask AI agent (e.g., 'Create a notebook about Python and add documentation...')" style="flex: 1; border: 1px solid #cbd5e1; border-radius: 0.375rem; padding: 0.75rem; font-size: 0.875rem;">
        <button onclick="executeAgent()" style="background: #8b5cf6; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 0.375rem; cursor: pointer; font-weight: 500;">Execute</button>
    </div>
    <div id="agent-status" style="margin-top: 0.5rem; font-size: 0.875rem; color: #64748b;"></div>
</div>

<script>
async function executeAgent() {
    const input = document.getElementById('agent-input').value;
    const status = document.getElementById('agent-status');
    if (!input.trim()) return;
    
    status.textContent = 'Processing...';
    try {
        const response = await fetch('/api/agent/execute', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({input: input, notebook_id: '{{ $notebook->id ?? null }}'})
        });
        const data = await response.json();
        status.textContent = data.message || 'Done!';
    } catch(e) {
        status.textContent = 'Error: ' + e.message;
    }
}
</script>
