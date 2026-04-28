-- ============================================================
-- schema.sql  –  Phonebook Database Schema (Practice 9 / TSIS1)
-- ============================================================

-- Groups / categories
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Seed default groups
INSERT INTO groups (name) VALUES
    ('Family'),
    ('Work'),
    ('Friend'),
    ('Other')
ON CONFLICT (name) DO NOTHING;

-- Contacts (base table – assumed to exist from Practice 7/8)
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Extended columns (safe to run on a fresh or existing DB)
ALTER TABLE contacts
    ADD COLUMN IF NOT EXISTS email    VARCHAR(100),
    ADD COLUMN IF NOT EXISTS birthday DATE,
    ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id);

-- Phones (1-to-many)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    phone      VARCHAR(20) NOT NULL,
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
);

-- Indexes for fast search
CREATE INDEX IF NOT EXISTS idx_contacts_name     ON contacts (name);
CREATE INDEX IF NOT EXISTS idx_contacts_email    ON contacts (email);
CREATE INDEX IF NOT EXISTS idx_phones_contact_id ON phones   (contact_id);