<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'NotebookLM Portal')</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', system-ui, sans-serif; background: #f8fafc; color: #1e293b; }
        .container { max-width: 1280px; margin: 0 auto; padding: 0 1rem; }
    </style>
</head>
<body>
    @include('components.header')
    <main class="container" style="padding-top: 1rem;">
        @if(session('success'))
            @include('components.toast', ['type' => 'success', 'message' => session('success')])
        @endif
        @if(session('error'))
            @include('components.toast', ['type' => 'error', 'message' => session('error')])
        @endif
        @yield('content')
    </main>
    @yield('scripts')
</body>
</html>
