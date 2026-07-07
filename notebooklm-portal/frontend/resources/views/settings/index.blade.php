@extends('layouts.app')

@section('title', 'Settings - NotebookLM Portal')

@section('content')
<div style="display: flex; gap: 2rem;">
    <aside style="width: 250px; flex-shrink: 0;">
        @include('components.sidebar')
    </aside>
    
    <div style="flex: 1;">
        <h1 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem;">Settings</h1>
        
        <form method="POST" action="/settings" style="background: white; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1.5rem;">
            @csrf
            @method('PUT')
            
            <h2 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem;">Profile Settings</h2>
            
            <div style="margin-bottom: 1rem;">
                <label style="display: block; font-weight: 500; margin-bottom: 0.25rem;">Email</label>
                <input type="email" name="email" value="{{ old('email', auth()->user()->email ?? '') }}" style="width: 100%; border: 1px solid #cbd5e1; border-radius: 0.375rem; padding: 0.5rem;" disabled>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <label style="display: block; font-weight: 500; margin-bottom: 0.25rem;">LLM API Key (optional)</label>
                <input type="password" name="llm_api_key" placeholder="sk-..." style="width: 100%; border: 1px solid #cbd5e1; border-radius: 0.375rem; padding: 0.5rem;">
                <p style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">For OpenAI, Anthropic, or other LLM providers</p>
            </div>
            
            <button type="submit" style="background: #2563eb; color: white; border: none; padding: 0.5rem 1.5rem; border-radius: 0.375rem; cursor: pointer;">Save Changes</button>
        </form>
    </div>
</div>
@endsection
