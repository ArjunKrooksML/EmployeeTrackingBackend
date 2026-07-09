-- DPR remodel: replace description with size columns
-- Run this against the Supabase PostgreSQL database

ALTER TABLE dpr
  DROP COLUMN IF EXISTS description,
  ADD COLUMN IF NOT EXISTS mm16       INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS mm20       INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS mm25       INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS mm32       INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS forging_qty INTEGER DEFAULT 0;

-- Add forging flag to projects
ALTER TABLE projects
  ADD COLUMN IF NOT EXISTS has_forging BOOLEAN NOT NULL DEFAULT FALSE;
