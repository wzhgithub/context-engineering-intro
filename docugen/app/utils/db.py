"""Database utilities for PostgreSQL.

This module provides database connection pooling and initialization.
"""

import asyncpg
from typing import Optional

from app.config import settings


_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create database connection pool.

    Returns:
        asyncpg connection pool
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
        )
    return _pool


async def init_db() -> None:
    """Initialize database tables.

    Creates all required tables if they don't exist.
    """
    pool = await get_db_pool()

    async with pool.acquire() as conn:
        # Create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                hashed_password TEXT DEFAULT '',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Create templates table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id),
                name TEXT NOT NULL,
                description TEXT,
                sections JSONB DEFAULT '{}',
                formatting_rules JSONB DEFAULT '{}',
                required_fields TEXT[] DEFAULT '{}',
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Create knowledge_documents table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_documents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id),
                title TEXT NOT NULL,
                content TEXT,
                source TEXT,
                file_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Create knowledge_chunks table with PGVector
        await conn.execute("""
            CREATE EXTENSION IF NOT EXISTS vector;
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                document_id UUID REFERENCES knowledge_documents(id),
                content TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                embedding vector(1536),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Create vector index for better search performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding
            ON knowledge_chunks
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100)
        """)

        # Create tasks table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID REFERENCES users(id),
                thread_id UUID DEFAULT gen_random_uuid(),
                status TEXT DEFAULT 'pending',
                requirements TEXT NOT NULL,
                template_id UUID REFERENCES templates(id),
                knowledge_ids UUID[] DEFAULT '{}',
                workflow_state JSONB DEFAULT '{}',
                current_stage TEXT DEFAULT 'pending',
                revision_count INTEGER DEFAULT 0,
                max_revisions INTEGER DEFAULT 3,
                generated_document TEXT,
                review_feedback JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                error TEXT
            )
        """)

        # Create generated_documents table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS generated_documents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                task_id UUID REFERENCES tasks(id),
                user_id UUID REFERENCES users(id),
                title TEXT,
                content TEXT NOT NULL,
                template_id UUID REFERENCES templates(id),
                review_score FLOAT,
                review_feedback JSONB,
                status TEXT DEFAULT 'completed',
                error TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)


async def close_db_pool() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
