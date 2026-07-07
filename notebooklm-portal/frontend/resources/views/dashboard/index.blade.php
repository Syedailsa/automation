@extends('layouts.app')

@section('title', 'Dashboard - NotebookLM Portal')

@section('content')
<div style="display: flex; gap: 2rem;">
    <!-- Sidebar -->
    <aside style="width: 250px; flex-shrink: 0;">
        @include('components.sidebar')
    </aside>

    <!-- Main Content -->
    <div style="flex: 1;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h1 style="font-size: 1.5rem; font-weight: 700;">My Notebooks</h1>
            <a href="/notebooks/create" style="background: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.375rem; text-decoration: none;">
                + New Notebook
            </a>
        </div>

        <!-- Notebooks Grid -->
        <div id="notebooks-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">
            @forelse($notebooks ?? [] as $notebook)
                @include('components.notebook-card', ['notebook' => $notebook])
            @empty
                @include('components.empty-state')
            @endforelse
        </div>
    </div>
</div>
@endsection
