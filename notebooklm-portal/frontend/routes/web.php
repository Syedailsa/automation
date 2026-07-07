<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Http;

// Auth routes
Route::get('/login', function () {
    return view('auth.login');
})->name('login');

Route::get('/auth/google/redirect', function () {
    $params = [
        'client_id' => config('services.google.client_id'),
        'redirect_uri' => config('services.google.redirect_uri'),
        'response_type' => 'code',
        'scope' => 'openid email profile',
        'access_type' => 'offline',
    ];
    return redirect('https://accounts.google.com/o/oauth2/v2/auth?' . http_build_query($params));
})->name('auth.google.redirect');

Route::get('/auth/callback', function () {
    $code = request('code');
    if (!$code) {
        return redirect('/login')->withErrors(['error' => 'No code provided']);
    }
    
    try {
        $response = Http::post(config('app.backend_url') . '/api/auth/google/callback', [
            'code' => $code,
        ]);
        
        if ($response->successful()) {
            session(['token' => $response->json('access_token')]);
            session(['user' => $response->json('user')]);
            return redirect('/dashboard');
        }
        
        return redirect('/login')->withErrors(['error' => 'Authentication failed']);
    } catch (\Exception $e) {
        return redirect('/login')->withErrors(['error' => 'Connection failed']);
    }
})->name('auth.callback');

Route::post('/logout', function () {
    session()->forget('token');
    session()->forget('user');
    return redirect('/');
})->name('logout');

// Protected routes
Route::middleware(['auth'])->group(function () {
    Route::get('/dashboard', function () {
        $token = session('token');
        $notebooks = [];
        
        try {
            $response = Http::withToken($token)->get(config('app.backend_url') . '/api/notebooks');
            if ($response->successful()) {
                $notebooks = $response->json('data', []);
            }
        } catch (\Exception $e) {}
        
        return view('dashboard.index', ['notebooks' => $notebooks]);
    })->name('dashboard');

    Route::get('/notebooks/{id}', function ($id) {
        $token = session('token');
        $notebook = null;
        
        try {
            $response = Http::withToken($token)->get(config('app.backend_url') . '/api/notebooks/' . $id);
            if ($response->successful()) {
                $notebook = $response->json('data');
            }
        } catch (\Exception $e) {}
        
        return view('dashboard.notebook', ['notebook' => $notebook]);
    })->name('notebooks.show');

    Route::get('/settings', function () {
        return view('settings.index');
    })->name('settings');

    Route::get('/settings/notebooklm', function () {
        $token = session('token');
        $connected = false;
        
        try {
            $response = Http::withToken($token)->get(config('app.backend_url') . '/api/users/notebooklm-status');
            if ($response->successful()) {
                $connected = $response->json('connected', false);
            }
        } catch (\Exception $e) {}
        
        return view('settings.notebooklm', ['connected' => $connected]);
    })->name('settings.notebooklm');
});

// API proxy routes
Route::middleware(['auth'])->prefix('api')->group(function () {
    Route::post('/agent/execute', function () {
        $token = session('token');
        $response = Http::withToken($token)->post(config('app.backend_url') . '/api/agent/execute', request()->all());
        return $response->json();
    });
    
    Route::get('/notebooks/{id}/sources', function ($id) {
        $token = session('token');
        $response = Http::withToken($token)->get(config('app.backend_url') . '/api/notebooks/' . $id . '/sources');
        return $response->json();
    });
});
