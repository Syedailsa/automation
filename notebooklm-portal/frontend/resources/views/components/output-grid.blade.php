@if(!empty($outputs) && count($outputs) > 0)
    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;">
        @foreach($outputs as $output)
            @include('components.output-card', ['output' => $output])
        @endforeach
    </div>
@else
    <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 0.5rem; padding: 1.5rem; text-align: center;">
        <p style="color: #64748b;">No outputs generated yet</p>
    </div>
@endif
