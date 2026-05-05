-- Add columns to design_briefs table in Supabase
-- Run this in Supabase SQL Editor

ALTER TABLE design_briefs
ADD COLUMN IF NOT EXISTS client_phone TEXT,
ADD COLUMN IF NOT EXISTS company TEXT,
ADD COLUMN IF NOT EXISTS project_description TEXT,
ADD COLUMN IF NOT EXISTS has_existing_site BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS existing_site_url TEXT,
ADD COLUMN IF NOT EXISTS features TEXT[],
ADD COLUMN IF NOT EXISTS target_audience TEXT,
ADD COLUMN IF NOT EXISTS flexible_budget BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS additional_notes TEXT,
ADD COLUMN IF NOT EXISTS files TEXT[];

-- For storage, create bucket manually in Supabase Dashboard:
-- Go to Storage > New bucket
-- Name: brief-files
-- Public bucket: ON
-- File size limit: 10MB
-- Allowed mime types: image/png, image/jpeg, image/gif, image/webp, application/pdf