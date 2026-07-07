<header style="background: white; border-bottom: 1px solid #e2e8f0; padding: 0.75rem 1rem;">
    <div class="container" style="display: flex; justify-content: space-between; align-items: center;">
        <a href="/" style="font-size: 1.25rem; font-weight: 700; color: #2563eb; text-decoration: none;">
            NotebookLM Portal
        </a>
        <nav style="display: flex; gap: 1rem; align-items: center;">
            @auth
                <a href="/dashboard" style="color: #64748b; text-decoration: none;">Dashboard</a>
                <a href="/settings" style="color: #64748b; text-decoration: none;">Settings</a>
                <span style="color: #64748b;">{{ auth()->user()->email ?? 'User' }}</span>
                <form method="POST" action="{{ route('logout') }}" style="display:inline;">
                    @csrf
                    <button type="submit" style="background: #ef4444; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.375rem; cursor: pointer;">Logout</button>
                </form>
            @else
                <a href="{{ route('login') }}" style="background: #2563eb; color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 0.375rem;">Login</a>
            @endauth
        </nav>
    </div>
</header>
