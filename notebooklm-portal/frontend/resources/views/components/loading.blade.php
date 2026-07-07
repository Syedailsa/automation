<div style="display: flex; align-items: center; gap: 0.5rem; color: #64748b;">
    <div style="width: 1rem; height: 1rem; border: 2px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
    <span>{{ $message ?? 'Loading...' }}</span>
</div>

<style>
@keyframes spin {
    to { transform: rotate(360deg); }
}
</style>
