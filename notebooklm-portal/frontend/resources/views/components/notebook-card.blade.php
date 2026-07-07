<a href="/notebooks/{{ $notebook->id }}" style="display: block; background: white; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; text-decoration: none; color: inherit; transition: box-shadow 0.2s;">
    <h3 style="font-weight: 600; margin-bottom: 0.5rem;">{{ $notebook->title ?? 'Untitled' }}</h3>
    <p style="color: #64748b; font-size: 0.875rem; margin-bottom: 0.75rem;">{{ $notebook->sources_count ?? 0 }} sources</p>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.75rem; color: #94a3b8;">{{ $notebook->created_at?->diffForHumans() ?? '' }}</span>
        <span style="font-size: 0.75rem; color: #10b981;">{{ $notebook->status ?? 'active' }}</span>
    </div>
</a>
