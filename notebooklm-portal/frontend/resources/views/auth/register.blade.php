<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register - NotebookLM Portal</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', system-ui, sans-serif; background: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .login-card { background: white; border-radius: 0.5rem; padding: 2rem; width: 90%; max-width: 400px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .login-card h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }
        .login-card .subtitle { color: #64748b; margin-bottom: 1.5rem; }
        .divider { display: flex; align-items: center; gap: 1rem; margin: 1.5rem 0; color: #94a3b8; font-size: 0.875rem; }
        .divider::before, .divider::after { content: ''; flex: 1; height: 1px; background: #e2e8f0; }
        .form-group { margin-bottom: 1rem; text-align: left; }
        .form-group label { display: block; font-size: 0.875rem; font-weight: 500; color: #374151; margin-bottom: 0.25rem; }
        .form-group input { width: 100%; padding: 0.625rem 0.75rem; border: 1px solid #d1d5db; border-radius: 0.375rem; font-size: 1rem; outline: none; }
        .form-group input:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.15); }
        .btn-primary { width: 100%; padding: 0.625rem; background: #2563eb; color: white; border: none; border-radius: 0.375rem; font-size: 1rem; font-weight: 500; cursor: pointer; margin-top: 0.5rem; }
        .btn-primary:hover { background: #1d4ed8; }
        .btn-primary:disabled { background: #93c5fd; cursor: not-allowed; }
        .google-btn { display: inline-flex; align-items: center; gap: 0.75rem; width: 100%; justify-content: center; background: white; border: 1px solid #d1d5db; border-radius: 0.375rem; padding: 0.625rem 1.5rem; cursor: pointer; font-size: 1rem; }
        .google-btn:hover { background: #f9fafb; }
        .error-msg { background: #fef2f2; color: #991b1b; padding: 0.75rem; border-radius: 0.375rem; margin-bottom: 1rem; font-size: 0.875rem; }
        .login-link { margin-top: 1.5rem; font-size: 0.875rem; color: #64748b; }
        .login-link a { color: #2563eb; text-decoration: none; font-weight: 500; }
        .login-link a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>NotebookLM Portal</h1>
        <p class="subtitle">Create your account</p>

        @if($errors->any())
            <div class="error-msg">{{ $errors->first() }}</div>
        @endif

        <form method="POST" action="{{ route('auth.register.store') }}">
            @csrf
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" id="name" name="name" value="{{ old('name') }}" required autofocus placeholder="Your name">
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" value="{{ old('email') }}" required placeholder="you@example.com">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required minlength="6" placeholder="At least 6 characters">
            </div>
            <div class="form-group">
                <label for="password_confirmation">Confirm Password</label>
                <input type="password" id="password_confirmation" name="password_confirmation" required placeholder="Confirm your password">
            </div>
            <button type="submit" class="btn-primary">Create Account</button>
        </form>

        <div class="divider">or</div>

        <a href="{{ route('auth.google.redirect') }}" class="google-btn">
            <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
            Sign up with Google
        </a>

        <p class="login-link">
            Already have an account? <a href="{{ route('auth.login') }}">Sign in</a>
        </p>
    </div>
</body>
</html>
