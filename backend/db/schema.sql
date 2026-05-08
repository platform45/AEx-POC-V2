-- AEx RAG – database schema
-- Run against the aex_rag database inside the pgvector container.

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS case_contexts (
    id          UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    title       VARCHAR(255) NOT NULL,
    description TEXT         NOT NULL,
    -- 1024-dimensional embedding produced by Voyage AI (voyage-4)
    embedding   VECTOR(1024),
    -- Flexible diagnostic payload: inputs, actions, results, outcome
    raw_context JSONB        NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Approximate nearest-neighbour index for L2 similarity search.
-- lists = 100 is a reasonable default; tune upward as row count grows.
CREATE INDEX IF NOT EXISTS idx_case_contexts_embedding
    ON case_contexts USING ivfflat (embedding vector_l2_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_case_contexts_created_at
    ON case_contexts (created_at DESC);

-- GIN index allows efficient querying inside raw_context JSON.
CREATE INDEX IF NOT EXISTS idx_case_contexts_raw_context
    ON case_contexts USING gin (raw_context);
