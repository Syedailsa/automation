@extends('layouts.app')

@section('title', ($notebook->title ?? 'Notebook') . ' - NotebookLM Portal')

@section('content')
<div style="display: flex; gap: 2rem;">
    <!-- Sidebar -->
    <aside style="width: 250px; flex-shrink: 0;">
        @include('components.sidebar')
    </aside>

    <!-- Main Content -->
    <div style="flex: 1;">
        <!-- Breadcrumb -->
        <nav style="font-size: 0.875rem; color: #64748b; margin-bottom: 1rem;">
            <a href="/dashboard" style="color: #2563eb; text-decoration: none;">Dashboard</a>
            <span> / </span>
            <span>{{ $notebook->title ?? 'Notebook' }}</span>
        </nav>

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <h1 style="font-size: 1.5rem; font-weight: 700;">{{ $notebook->title ?? 'Untitled Notebook' }}</h1>
            <div style="display: flex; gap: 0.5rem;">
                <button onclick="deleteNotebook()" style="background: #ef4444; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: pointer;">Delete</button>
            </div>
        </div>

        <!-- Sources Section -->
        <section style="margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h2 style="font-size: 1.125rem; font-weight: 600;">Sources</h2>
                <button onclick="openAddSourceModal()" style="background: #10b981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: pointer;">+ Add Source</button>
            </div>
            @include('components.source-list', ['sources' => $notebook->sources ?? []])
        </section>

        <!-- Outputs Section -->
        <section style="margin-bottom: 2rem;">
            <h2 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem;">Outputs</h2>
            @include('components.output-grid', ['outputs' => $notebook->outputs ?? []])
        </section>

        <!-- Agent Input -->
        <section>
            <h2 style="font-size: 1.125rem; font-weight: 600; margin-bottom: 1rem;">AI Agent</h2>
            @include('components.agent-input')
        </section>
    </div>
</div>

@include('components.add-source-modal')
@endsection
