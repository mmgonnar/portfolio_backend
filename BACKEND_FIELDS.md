# Brief Form Backend Fields

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| name | string | User's full name |
| email | string | User's email address |
| projectType | string | Type of project: 'website', 'web_app', 'landing', 'redesign', 'dashboard', 'other', or '' |
| projectName | string | Name of the project |
| projectDescription | string | Description of the project |
| features | string[] | Array of selected feature keys: 'auth', 'admin_dashboard', 'forms_emails', 'database', 'integrations', 'seo', 'multi_language', 'deployment' |
| designStatus | string | What the client has for the design: 'ready', 'brand_kit', 'none', or '' |
| budget | string | Budget range key: 'r1', 'r2', 'r3', 'r4', or '' |
| timeline | string | Timeline key: 'asap', 'one_month', 'two_three_months', 'flexible', or '' |
| locale | string | Language code |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| phone | string | Phone number |
| company | string | Company or project name |
| existingSiteUrl | string | URL of existing website |
| featuresDetail | string | Additional details about features |
| competitors | string | Competitor information |
| visualStyle | string | Visual style preference key |
| visualReferences | string | Reference URLs (comma-separated) |
| brandColors | string | Brand colors (e.g., "blue, red, yellow") |
| brandAssetsReady | boolean | Whether brand assets are ready |
| flexibleBudget | boolean | Whether budget is flexible |
| additionalNotes | string | Any additional notes |
| hasExistingSite | boolean | Whether user has existing site |
| targetAudience | string | Description of target audience, the step is skippable |
| designLink | string | Where the finished design lives, sent when designStatus is 'ready' |
| wantsDesignQuote | boolean | Client asked for a UI/UX design quote, an additional service |
| scopeLevel | string | Computed scope: 'basic', 'medium' or 'advanced' |
| scopeWeight | integer | Computed scope weight, a non negative integer |

## Files

| Field | Type | Description |
|-------|------|-------------|
| files | File[] | Array of uploaded files (brand assets, references) |

## Notes

- **features** is sent as multiple entries with key `features` (e.g., `features: 'auth'`, `features: 'database'`)
- **budget** values map to ranges:
  - r1: under $1,200 (USD) / under $15,000 MXN
  - r2: $1,200 - $3,000 (USD) / $15,000 - $40,000 MXN
  - r3: $3,000 - $6,000 (USD) / $40,000 - $80,000 MXN
  - r4: $6,000+ (USD) / $80,000+ MXN
- Currency is determined by user's timezone (Mexico = MXN, else = USD)
- **timeline**, **projectType**, **features**, **designStatus** and **scopeLevel** are keys. They are
  turned into readable Spanish labels in `app/features/briefs/labels.py`, which the PDF, the email
  and the router all share. Every lookup falls back to the value it was given, so briefs saved
  before this change, which stored translated titles such as "Gestión de Contenidos", still print
  correctly, and retired keys (`cms`, `payments`, `analytics`, `mobile`, `wordpress`) stay in the
  tables on purpose.
- **scopeLevel** and **scopeWeight** are computed by the frontend in
  `features/brief/utils/scope.ts`, which owns the weights and the prices. The backend validates the
  shape only, a known level and a non negative integer, and never recomputes them: a second copy of
  that table in Python would drift. An invalid value is logged and stored empty rather than
  rejecting the brief.

## Database

The five columns this adds to `public.design_briefs` are in
`supabase_migration_brief_restructure.sql`: `design_status`, `design_link`, `wants_design_quote`,
`scope_level` and `scope_weight`. Run it before deploying this version.