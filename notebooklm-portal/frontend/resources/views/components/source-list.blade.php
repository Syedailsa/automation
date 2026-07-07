@if(!empty($sources) && count($sources) > 0)
    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
        @foreach($sources as $source)
            @include('components.source-item', ['source' => $source])
        @endforeach
    </div>
@else
    <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 0.5rem; padding: 1.5rem; text-align: center;">
        <p style="color: #64748b;">No sources added yet</p>
    </div>
@endif
