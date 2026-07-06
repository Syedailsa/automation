# API Documentation

Base URL: `http://localhost:8000`

Interactive docs available at: http://localhost:8000/docs

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <token>
```

---

## Auth Endpoints

### Get Google OAuth URL

```
GET /api/auth/google/redirect
```

**Response:**
```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### Exchange Code for Token

```
POST /api/auth/google/callback
```

**Request:**
```json
{
  "code": "google-auth-code",
  "state": "optional-state"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user_id": "uuid"
}
```

### Get Current User

```
GET /api/auth/me
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "avatar_url": "https://...",
  "notebooklm_connected": false,
  "preferred_llm": "openai"
}
```

### Logout

```
POST /api/auth/logout
```

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

## User Endpoints

### Get Profile

```
GET /api/users/profile
```

**Response:** Full user profile object

### Update Profile

```
PUT /api/users/profile
```

**Request:**
```json
{
  "name": "New Name",
  "avatar_url": "https://new-url.com/avatar.jpg"
}
```

### Get Settings

```
GET /api/users/settings
```

**Response:**
```json
{
  "preferred_llm": "openai",
  "notebooklm_connected": false
}
```

### Update Settings

```
PUT /api/users/settings
```

**Request:**
```json
{
  "preferred_llm": "anthropic"
}
```

### Store LLM API Key

```
POST /api/users/llm-key
```

**Request:**
```json
{
  "llm_api_key": "sk-your-api-key"
}
```

### Get NotebookLM Status

```
GET /api/users/notebooklm-status
```

**Response:**
```json
{
  "notebooklm_connected": true,
  "last_login": "2024-01-15T10:30:00"
}
```

---

## Notebook Endpoints

### List Notebooks

```
GET /api/notebooks?skip=0&limit=50
```

**Query Parameters:**
- `skip` (int): Offset for pagination (default: 0)
- `limit` (int): Max items per page (default: 50, max: 100)

**Response:**
```json
{
  "notebooks": [...],
  "total": 10
}
```

### Create Notebook

```
POST /api/notebooks
```

**Request:**
```json
{
  "title": "My Notebook",
  "description": "Research notes"
}
```

**Response:** Notebook object (201 Created)

### Get Notebook

```
GET /api/notebooks/{notebook_id}
```

### Update Notebook

```
PUT /api/notebooks/{notebook_id}
```

**Request:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "status": "archived"
}
```

### Delete Notebook

```
DELETE /api/notebooks/{notebook_id}
```

**Response:**
```json
{
  "message": "Notebook deleted successfully"
}
```

### List Notebook Sources

```
GET /api/notebooks/{notebook_id}/sources?skip=0&limit=50
```

### List Notebook Outputs

```
GET /api/notebooks/{notebook_id}/outputs?skip=0&limit=50
```

---

## Source Endpoints

### Add URL Source

```
POST /api/notebooks/{notebook_id}/sources/url
```

**Request:**
```json
{
  "title": "Article Title",
  "source_type": "url",
  "url": "https://example.com/article"
}
```

### Add Text Source

```
POST /api/notebooks/{notebook_id}/sources/text
```

**Request:**
```json
{
  "title": "My Notes",
  "source_type": "text",
  "content": "Full text content here..."
}
```

### Get Source Content

```
GET /api/notebooks/{notebook_id}/sources/{source_id}/content
```

### Delete Source

```
DELETE /api/notebooks/{notebook_id}/sources/{source_id}
```

---

## Output Endpoints

### Delete Output

```
DELETE /api/outputs/{output_id}
```

---

## Agent Endpoints (P3)

### Refine Input

```
POST /api/agent/refine
```

### Execute Workflow

```
POST /api/agent/execute
```

---

## WebSocket Endpoints (P4)

### Agent Execution Updates

```
WS /ws/agent/{execution_id}
```

### Source Processing Status

```
WS /ws/notebooks/{notebook_id}/sources
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**HTTP Status Codes:**
- `400` - Bad Request
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
