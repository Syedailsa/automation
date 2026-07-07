@extends('layouts.app')

@section('title', 'NotebookLM Status - NotebookLM Portal')

@section('content')
<div style="display: flex; gap: 2rem;">
    <aside style="width: 250px; flex-shrink: 0;">
        @include('components.sidebar')
    </aside>
    
    <div style="flex: 1;">
        <h1 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem;">NotebookLM Connection</h1>
        
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
                <div style="width: 1rem; height: 1rem; border-radius: 50%; background: {{ $connected ? '#10b981' : '#ef4444' }}"></div>
                <span style="font-weight: 500;">{{ $connected ? 'Connected' : 'Not Connected' }}</span>
            </div>
            
            @if(!$connected)
                <p style="color: #64748b; margin-bottom: 1rem;">Connect your NotebookLM account to enable automation features.</p>
                <a href="/api/auth/notebooklm/login" style="display: inline-block; background: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.375rem; text-decoration: none;">Connect NotebookLM</a>
            @else
                <p style="color: #64748b; margin-bottom: 1rem;">Your NotebookLM account is connected and ready to use.</p>
                <form method="POST" action="/api/auth/notebooklm/disconnect" style="display:inline;">
                    @csrf
                    <button type="submit" style="background: #ef4444; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: pointer;">Disconnect</button>
                </form>
            @endif
        </div>
    </div>
</div>
@endsection
