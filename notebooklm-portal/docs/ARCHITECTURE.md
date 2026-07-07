# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User's Browser                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                          │
│                    Reverse Proxy                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
┌───────────────────┐       ┌───────────────────┐
│   Laravel Frontend│       │  FastAPI Backend   │
│     (Port 80)     │       │    (Port 8000)     │
│                   │       │                    │
│  - Blade Views    │       │  - REST API        │
│  - Auth Flow      │◄─────►│  - WebSocket       │
│  - Dashboard      │  API  │  - AI Agent        │
└───────────────────┘       └────────┬───────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌───────────────────┐           ┌───────────────────┐
        │   PostgreSQL      │           │    Playwright      │
        │   (Port 5432)     │           │   Browser Automation│
        │                   │           │                    │
        │  - Users          │           │  - Google Login    │
        │  - Notebooks      │           │  - NotebookLM Ops  │
        │  - Sources        │           │  - File Downloads  │
        │  - Outputs        │           │                    │
        └───────────────────┘           └───────────────────┘
```

## Backend Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (Routes)                       │
│  Handles HTTP requests, validation, authentication         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Service Layer (Business Logic)            │
│  Implements business rules, orchestrates operations         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Data Layer (Models + Database)              │
│  SQLAlchemy models, database operations                     │
└─────────────────────────────────────────────────────────────┘
```

### Component Overview

#### API Layer (`app/api/`)
- **auth.py**: Google OAuth flow, JWT generation
- **users.py**: Profile and settings management
- **notebooks.py**: Notebook CRUD operations
- **sources.py**: Source management within notebooks
- **outputs.py**: Generated output handling
- **agent.py**: AI agent interaction endpoints
- **ws.py**: WebSocket real-time updates

#### Service Layer (`app/services/`)
- **auth_service.py**: OAuth token exchange, user creation
- **user_service.py**: User CRUD operations
- **notebook_service.py**: Notebook business logic
- **source_service.py**: Source management logic
- **output_service.py**: Output handling
- **storage_service.py**: File system operations

#### Core Layer (`app/core/`)
- **security.py**: JWT creation/verification, password hashing
- **deps.py**: FastAPI dependency injection (get_current_user)
- **exceptions.py**: Custom HTTP exceptions

#### Schema Layer (`app/schemas/`)
Pydantic models for request/response validation

#### Model Layer (`app/models/`)
SQLAlchemy ORM models mapping to database tables

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      users      │     │    notebooks    │     │     sources     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │────<│ user_id (FK)    │     │ id (PK)         │
│ email           │     │ id (PK)         │────<│ notebook_id(FK) │
│ name            │     │ title           │     │ title           │
│ google_id       │     │ description     │     │ source_type     │
│ avatar_url      │     │ notebooklm_id   │     │ url             │
│ access_token    │     │ status          │     │ file_path       │
│ refresh_token   │     │ source_count    │     │ content         │
│ token_expiry    │     │ created_at      │     │ status          │
│ notebooklm_     │     │ updated_at      │     │ metadata (JSONB)│
│   connected     │     └─────────────────┘     │ created_at      │
│ preferred_llm   │                             └─────────────────┘
│ llm_api_key     │
│ created_at      │     ┌─────────────────┐     ┌─────────────────┐
│ last_login      │     │     outputs     │     │ execution_logs  │
└─────────────────┘     ├─────────────────┤     ├─────────────────┤
                        │ id (PK)         │     │ id (PK)         │
                        │ user_id (FK)    │     │ user_id (FK)    │
                        │ notebook_id(FK) │     │ original_input  │
                        │ output_type     │     │ detected_       │
                        │ file_path       │     │   language      │
                        │ file_size       │     │ refined_input   │
                        │ mime_type       │     │ actions (JSONB) │
                        │ metadata (JSONB)│     │ result (JSONB)  │
                        │ created_at      │     │ status          │
                        └─────────────────┘     │ error_message   │
                                                │ duration_ms     │
                                                │ created_at      │
                                                │ completed_at    │
                                                └─────────────────┘
```

## Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Frontend │     │ Backend  │     │ Google   │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │  1. Click Login│                │                │
     │───────────────>│                │                │
     │                │ 2. Get OAuth URL               │
     │                │───────────────>│                │
     │                │                │ 3. Redirect    │
     │                │                │───────────────>│
     │                │                │                │
     │  4. Login with Google           │                │
     │────────────────────────────────────────────────>│
     │                │                │                │
     │                │ 5. Auth Code   │                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ 6. Exchange Code                │
     │                │───────────────>│ 7. Token       │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │ 8. User Info   │
     │                │                │<───────────────│
     │                │                │                │
     │                │ 9. JWT Token   │                │
     │                │<───────────────│                │
     │  10. Logged In │                │                │
     │<───────────────│                │                │
```

## AI Agent Flow (P3)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Backend  │     │   LLM    │     │Playwright│
│  Input   │     │  Agent   │     │ Provider │     │ Browser  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │ 1. Raw Input   │                │                │
     │───────────────>│                │                │
     │                │ 2. Refine      │                │
     │                │───────────────>│                │
     │                │ 3. Refined     │                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ 4. Plan Actions│                │
     │                │───────────────>│                │
     │                │ 5. Action Plan │                │
     │                │<───────────────│                │
     │                │                │                │
     │                │ 6. Execute     │                │
     │                │───────────────────────────────>│
     │                │ 7. Result      │                │
     │                │<───────────────────────────────│
     │                │                │                │
     │ 8. Output      │                │                │
     │<───────────────│                │                │
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Production Setup                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Nginx     │    │   Uvicorn   │    │  PostgreSQL  │     │
│  │   (80/443)  │───>│   (8000)    │───>│   (5432)    │     │
│  │   SSL/TLS   │    │   Workers   │    │   Persistent │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│                     ┌──────┴──────┐                         │
│                     │    Redis    │                         │
│                     │   (Cache)   │                         │
│                     └─────────────┘                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Async SQLAlchemy**: Using async/await for database operations to handle concurrent requests efficiently
2. **Pydantic V2**: For fast data validation and serialization
3. **JWT Authentication**: Stateless auth for scalability
4. **Service Layer Pattern**: Separates business logic from HTTP concerns
5. **UUID Primary Keys**: For better security and distributed system support
6. **JSONB Columns**: For flexible metadata storage (source metadata, execution results)
7. **WebSocket Support**: For real-time updates during long-running operations
