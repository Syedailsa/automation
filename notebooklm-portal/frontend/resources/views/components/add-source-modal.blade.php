<div id="add-source-modal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 50; align-items: center; justify-content: center;">
    <div style="background: white; border-radius: 0.5rem; padding: 1.5rem; width: 90%; max-width: 500px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="font-size: 1.125rem; font-weight: 600;">Add Source</h3>
            <button onclick="closeAddSourceModal()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">&times;</button>
        </div>
        
        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
            <button onclick="selectSourceType('url')" style="text-align: left; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; cursor: pointer; background: white;">
                🔗 Website URL
            </button>
            <button onclick="selectSourceType('text')" style="text-align: left; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; cursor: pointer; background: white;">
                📝 Paste Text
            </button>
            <button onclick="selectSourceType('youtube')" style="text-align: left; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; cursor: pointer; background: white;">
                📺 YouTube Video
            </button>
            <button onclick="selectSourceType('file')" style="text-align: left; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 0.375rem; cursor: pointer; background: white;">
                📁 Upload File
            </button>
        </div>
    </div>
</div>

<script>
function openAddSourceModal() {
    document.getElementById('add-source-modal').style.display = 'flex';
}
function closeAddSourceModal() {
    document.getElementById('add-source-modal').style.display = 'none';
}
function selectSourceType(type) {
    closeAddSourceModal();
    // Handle source type selection
}
</script>
