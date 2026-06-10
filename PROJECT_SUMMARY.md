# Portfolio Backend - Project Summary

## Overview
Backend for portfolio website with contact form and brief submission form. Handles project inquiries, generates PDF briefs, and sends emails with attachments.

## Quick Status (May 2026)
- ✅ Contact form: Working
- ✅ Brief form: Working (with file uploads)
- ✅ Email notifications: Working with Resend
- ⚠️ Files: Attached directly to email (not stored in Supabase due to Free Tier limitations)
- ⚠️ Frontend pointing to localhost instead of deployed backend (needs fix)

---

## Form Endpoints

### Contact Form
- **URL**: `POST /contact`
- **Content-Type**: JSON
- **Fields**:
  - `name`: string (required)
  - `email`: string (required)  
  - `message`: string (required)

### Brief Form
- **URL**: `POST /api/v1/send-brief`
- **Content-Type**: multipart/form-data
- **Fields**:
  - `name`: string (required)
  - `email`: string (required)
  - `company`: string
  - `projectName`: string
  - `projectType`: string (required)
  - `projectDescription`: string (required)
  - `hasExistingSite`: bool/string
  - `existingSiteUrl`: string
  - `features`: string or JSON array
  - `featuresDetail`: string
  - `targetAudience`: string
  - `competitors`: string
  - `visualStyle`: string
  - `visualReferences`: string
  - `brandColors`: string
  - `brandAssetsReady`: bool/string
  - `budget`: string (required) - keys: r1, r2, r3, r4, r5
  - `currency`: string - "USD" or "MXN" (defaults to "USD")
  - `timeline`: string (required) - "asap", "one_month", "two_three_months", "flexible"
  - `flexibleBudget`: bool/string
  - `additionalNotes`: string
  - `locale`: string ("en" or "es")
  - `referenceLinks`: string
  - `attachments`: File[] (optional)

---

## Features Implemented

### 1. Contact Form
- Simple validation with Pydantic
- Sends email via Resend

### 2. Brief Form
- Multi-step form processing
- Budget range display based on currency:
  - USD: $1K-$3K, $3K-$5K, $5K-$10K, $10K-$25K, $25K+
  - MXN: $10K-$15K, $15K-$20K, $20K-$25K, $25K-$30K, $30K+
- Timeline display:
  - "asap" → "ASAP"
  - "one_month" → "1 Mes"
  - "two_three_months" → "2-3 Meses"
  - "flexible" → "Flexible"
- Field validators for handling string/bool conversions:
  - `files`: converts None/empty string/JSON string to array
  - `hasExistingSite`, `brandAssetsReady`, `flexibleBudget`: converts string "true"/"false" to bool
- PDF generation with all form data
- File attachments sent directly via email (not stored)

### 3. Email Notifications
- HTML email with brief summary
- PDF attachment (auto-generated)
- Uploaded files attached to email

---

## Supabase Database

### Table: design_briefs
Columns:
- `id`: UUID (primary key)
- `created_at`: timestamp
- `client_name`: text
- `client_email`: text
- `client_phone`: text
- `company`: text
- `project_name`: text
- `project_type`: text
- `project_description`: text
- `has_existing_site`: boolean
- `existing_site_url`: text
- `features`: text[]
- `target_audience`: text
- `budget`: text
- `timeline`: text
- `locale`: text
- `flexible_budget`: boolean
- `additional_notes`: text
- `currency`: text (needs migration)
- `files`: text[] (optional)
- `full_data`: jsonb (complete submission)
- `status`: text

### Migration SQL (run in Supabase SQL Editor):
```sql
ALTER TABLE design_briefs 
ADD COLUMN IF NOT EXISTS client_phone TEXT,
ADD COLUMN IF NOT EXISTS company TEXT,
ADD COLUMN IF NOT EXISTS project_name TEXT,
ADD COLUMN IF NOT EXISTS project_description TEXT,
ADD COLUMN IF NOT EXISTS has_existing_site BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS existing_site_url TEXT,
ADD COLUMN IF NOT EXISTS features TEXT[],
ADD COLUMN IF NOT EXISTS target_audience TEXT,
ADD COLUMN IF NOT EXISTS flexible_budget BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS additional_notes TEXT,
ADD COLUMN IF NOT EXISTS currency TEXT,
ADD COLUMN IF NOT EXISTS files TEXT[];
```

---

## Known Issues / todo

### Fixed Issues
- ✅ Files field validation (None/empty string → [])
- ✅ Bool field parsing ("true"/"false" strings)
- ✅ Currency column added to backend model

### Outstanding Issues
- ⚠️ Frontend API URL hardcoded to localhost - NEEDS FIX: Point to `https://portfolio-backend-tarb.onrender.com`
- ⚠️ Frontend sends data with `name` as URL in some cases (check frontend field mapping)

---

## Environment Variables (Render)
Required:
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase anon key
- `RESEND_API_KEY`: Resend API key for emails

---

## Key Files

### Backend:
- `app/main.py` - FastAPI app setup
- `app/models/brief.py` - BriefSubmission model
- `app/models/schemas.py` - ContactMessage model  
- `app/features/briefs/router.py` - Brief form endpoint
- `app/features/briefs/service.py` - Email/PDF generation
- `app/utils/pdf_generator.py` - PDF generation

### Frontend (separate repo):
- Check for .env or API config - needs to point to deployed backend URL