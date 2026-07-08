<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

class FastApiClient
{
    private string $baseUrl;
    private string $token;

    public function __construct(?string $token = null)
    {
        $this->baseUrl = config('app.backend_url', 'http://backend:8000');
        $this->token = $token ?? session('token', '');
    }

    private function request(string $method, string $path, array $data = []): array
    {
        try {
            $http = Http::withToken($this->token)
                ->timeout(30)
                ->withoutVerifying();

            $response = match ($method) {
                'GET' => $http->get($this->baseUrl . $path),
                'POST' => $http->post($this->baseUrl . $path, $data),
                'PUT' => $http->put($this->baseUrl . $path, $data),
                'DELETE' => $http->delete($this->baseUrl . $path),
                default => throw new \InvalidArgumentException("Unsupported method: $method"),
            };

            if ($response->successful()) {
                return ['success' => true, 'data' => $response->json()];
            }

            return ['success' => false, 'error' => $response->json('detail', 'Request failed')];
        } catch (\Exception $e) {
            Log::error("FastAPI request failed: {$method} {$path}", ['error' => $e->getMessage()]);
            return ['success' => false, 'error' => 'Backend service unavailable'];
        }
    }

    // ── Auth ──

    public function exchangeGoogleCode(string $code): array
    {
        return $this->request('POST', '/api/auth/google/callback', ['code' => $code]);
    }

    public function getMe(): array
    {
        return $this->request('GET', '/api/auth/me');
    }

    // ── Notebooks ──

    public function getNotebooks(int $skip = 0, int $limit = 50): array
    {
        return $this->request('GET', "/api/notebooks?skip={$skip}&limit={$limit}");
    }

    public function getNotebook(string $id): array
    {
        return $this->request('GET', "/api/notebooks/{$id}");
    }

    public function createNotebook(string $title, ?string $description = null): array
    {
        return $this->request('POST', '/api/notebooks', [
            'title' => $title,
            'description' => $description,
        ]);
    }

    public function updateNotebook(string $id, array $data): array
    {
        return $this->request('PUT', "/api/notebooks/{$id}", $data);
    }

    public function deleteNotebook(string $id): array
    {
        return $this->request('DELETE', "/api/notebooks/{$id}");
    }

    // ── Sources ──

    public function getSources(string $notebookId, int $skip = 0, int $limit = 50): array
    {
        return $this->request('GET', "/api/notebooks/{$notebookId}/sources?skip={$skip}&limit={$limit}");
    }

    public function addUrlSource(string $notebookId, string $url, ?string $title = null): array
    {
        return $this->request('POST', "/api/notebooks/{$notebookId}/sources/url", [
            'title' => $title ?? $url,
            'source_type' => 'url',
            'url' => $url,
        ]);
    }

    public function addTextSource(string $notebookId, string $content, ?string $title = null): array
    {
        return $this->request('POST', "/api/notebooks/{$notebookId}/sources/text", [
            'title' => $title ?? 'Text Source',
            'source_type' => 'text',
            'content' => $content,
        ]);
    }

    public function deleteSource(string $notebookId, string $sourceId): array
    {
        return $this->request('DELETE', "/api/notebooks/{$notebookId}/sources/{$sourceId}");
    }

    // ── Outputs ──

    public function getOutputs(string $notebookId, int $skip = 0, int $limit = 50): array
    {
        return $this->request('GET', "/api/notebooks/{$notebookId}/outputs?skip={$skip}&limit={$limit}");
    }

    public function deleteOutput(string $outputId): array
    {
        return $this->request('DELETE', "/api/outputs/{$outputId}");
    }

    // ── Agent ──

    public function agentRefine(string $inputText, ?string $language = null): array
    {
        return $this->request('POST', '/api/agent/refine', [
            'input_text' => $inputText,
            'language' => $language,
        ]);
    }

    public function agentExecute(string $inputText, ?string $notebookId = null): array
    {
        return $this->request('POST', '/api/agent/execute', [
            'input_text' => $inputText,
            'notebook_id' => $notebookId,
        ]);
    }

    public function agentChat(array $messages, ?string $system = null): array
    {
        return $this->request('POST', '/api/agent/chat', [
            'messages' => $messages,
            'system' => $system,
        ]);
    }

    public function getAgentStatus(string $executionId): array
    {
        return $this->request('GET', "/api/agent/status/{$executionId}");
    }

    public function getAgentHistory(int $limit = 50, int $offset = 0): array
    {
        return $this->request('GET', "/api/agent/history?limit={$limit}&offset={$offset}");
    }

    // ── User Settings ──

    public function getProfile(): array
    {
        return $this->request('GET', '/api/users/profile');
    }

    public function updateProfile(array $data): array
    {
        return $this->request('PUT', '/api/users/profile', $data);
    }

    public function getSettings(): array
    {
        return $this->request('GET', '/api/users/settings');
    }

    public function updateSettings(array $data): array
    {
        return $this->request('PUT', '/api/users/settings', $data);
    }

    public function getNotebookLmStatus(): array
    {
        return $this->request('GET', '/api/users/notebooklm-status');
    }
}
