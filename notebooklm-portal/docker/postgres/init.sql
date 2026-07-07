-- Initial seed data for development
-- This runs when the PostgreSQL container starts for the first time

INSERT INTO users (id, email, name, google_id, preferred_llm, created_at, last_login)
VALUES
  ('550e8400-e29b-41d4-a716-446655440001', 'admin@notebooklm.local', 'Admin User', 'google-admin-001', 'openai', NOW(), NOW()),
  ('550e8400-e29b-41d4-a716-446655440002', 'dev@notebooklm.local', 'Developer', 'google-dev-002', 'anthropic', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO notebooks (id, user_id, title, description, status, created_at, updated_at)
VALUES
  ('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'Research Notes', 'Collection of research papers and summaries', 'active', NOW(), NOW()),
  ('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', 'Meeting Notes', 'Weekly team meeting summaries', 'active', NOW(), NOW()),
  ('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440002', 'Project Ideas', 'Brainstorming and project concepts', 'active', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO sources (id, notebook_id, title, source_type, url, status, created_at)
VALUES
  ('770e8400-e29b-41d4-a716-446655440001', '660e8400-e29b-41d4-a716-446655440001', 'AI Research Paper', 'url', 'https://arxiv.org/abs/2301.00001', 'ready', NOW()),
  ('770e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440001', 'ML Survey', 'url', 'https://arxiv.org/abs/2301.00002', 'processing', NOW()),
  ('770e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440002', 'Meeting Transcript', 'text', NULL, 'ready', NOW())
ON CONFLICT (id) DO NOTHING;

SELECT 'Seed data inserted successfully' AS status;
