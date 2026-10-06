-- Brief restructure: design answers and computed scope.
-- Run in the Supabase SQL Editor.

alter table public.design_briefs
  add column if not exists design_status text,
  add column if not exists design_link text,
  add column if not exists wants_design_quote boolean not null default false,
  add column if not exists scope_level text,
  add column if not exists scope_weight integer;

-- Rollback
-- alter table public.design_briefs
--   drop column if exists design_status,
--   drop column if exists design_link,
--   drop column if exists wants_design_quote,
--   drop column if exists scope_level,
--   drop column if exists scope_weight;
