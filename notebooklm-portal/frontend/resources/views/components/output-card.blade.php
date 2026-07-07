<div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem;">
    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
        <span style="font-size: 1.5rem;">{{ $output->type === 'audio' ? '🔊' : ($output->type === 'video' ? '🎬' : ($output->type === 'quiz' ? '❓' : ($output->type === 'flashcards' ? '🗂️' : '📊'))) }}</span>
        <span style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 0.25rem; background: #dbeafe; color: #1e40af;">{{ $output->type }}</span>
    </div>
    <h4 style="font-weight: 500; margin-bottom: 0.25rem;">{{ $output->title ?? 'Untitled' }}</h4>
    <p style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.75rem;">{{ $output->created_at?->diffForHumans() ?? '' }}</p>
    @if($output->file_path)
        <a href="{{ $output->file_path }}" download style="display: block; text-align: center; background: #2563eb; color: white; padding: 0.5rem; border-radius: 0.375rem; text-decoration: none; font-size: 0.875rem;">Download</a>
    @endif
</div>
