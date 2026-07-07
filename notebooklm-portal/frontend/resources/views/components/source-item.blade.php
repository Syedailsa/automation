<div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 0.75rem; display: flex; justify-content: space-between; align-items: center;">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span style="font-size: 1.25rem;">{{ $source->type === 'url' ? '🔗' : ($source->type === 'text' ? '📝' : ($source->type === 'youtube' ? '📺' : '📄')) }}</span>
        <div>
            <div style="font-weight: 500;">{{ $source->title ?? 'Untitled' }}</div>
            <div style="font-size: 0.75rem; color: #64748b;">{{ $source->type }}</div>
        </div>
    </div>
    <div style="display: flex; gap: 0.5rem;">
        <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background: {{ $source->status === 'ready' ? '#dcfce7' : '#fef3c7' }}; color: {{ $source->status === 'ready' ? '#166534' : '#92400e' }};">
            {{ $source->status ?? 'processing' }}
        </span>
    </div>
</div>
