-- Run in Supabase SQL editor
ALTER TABLE dpr
  DROP COLUMN IF EXISTS forging_qty,
  ADD COLUMN IF NOT EXISTS operator_name VARCHAR(150) DEFAULT '';

ALTER TABLE projects
  DROP COLUMN IF EXISTS has_forging;
