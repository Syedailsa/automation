@if(session('success'))
<div style="background: #dcfce7; border: 1px solid #bbf7d0; color: #166534; padding: 0.75rem 1rem; border-radius: 0.375rem; margin-bottom: 1rem;">
    {{ session('success') }}
</div>
@endif

@if(session('error'))
<div style="background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; padding: 0.75rem 1rem; border-radius: 0.375rem; margin-bottom: 1rem;">
    {{ session('error') }}
</div>
@endif
