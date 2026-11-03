-- Add currency column to Supabase
-- Run this in Supabase SQL Editor

ALTER TABLE design_briefs ADD COLUMN IF NOT EXISTS currency TEXT;