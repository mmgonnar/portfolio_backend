# Portfolio Backend

FastAPI service behind [mmgonnar.com](https://www.mmgonnar.com). It is the only backend the
portfolio frontend talks to, and it does three things:

1. Serves the portfolio project list, localized to Spanish or English.
2. Accepts the short contact form, stores it, and emails a notification.
3. Accepts the multi step design brief with file attachments, stores it, builds a PDF in memory,
   and emails the PDF plus the uploaded files.

The frontend is a separate Next.js app deployed on Vercel. This service is deployed on Render at
`https://portfolio-backend-tarb.onrender.com`. Persistence and the REST layer are Supabase
(hosted PostgreSQL). Transactional email is Resend.

There is no authentication anywhere in this service. Every endpoint is public. The protections
that exist are CORS origin pinning and a honeypot field on the contact form.

---

## Stack

| Concern | Choice |
|---|---|
| Language | Python 3.12.10 (pinned in `.python-version`) |
| Web framework | FastAPI 0.142.2 |
| Validation | Pydantic v2 models in `app/models/` |
| Database | Supabase (PostgreSQL), accessed through `supabase-py` 2.32.0 |
| Email | Resend 2.49.1 |
| PDF | fpdf2 2.8.9 |
| Local server | Uvicorn 0.54.0 |
| Production server | Gunicorn 26.2.0 with Uvicorn workers |
| Form parsing | python-multipart (required for the multipart brief endpoint) |

Exact versions live in `requirements.txt` and are all pinned.

---

## Folder structure

```
app/
  main.py                      FastAPI app, CORS, and the /, /health, /contact, /projects routes
  db/
    supabase_client.py         Module level Supabase client, built at import time from env vars
  models/
    schemas.py                 ContactMessage (request) and ProjectResponse (response)
    brief.py                   BriefSubmission model, its enums, and its coercion validators
  features/
    contact/
      service.py               Honeypot check, ticket id, save, then best effort Resend email
      data.py                  Insert into public.portfolio_contact
    projects/
      service.py               Picks the language specific columns and shapes ProjectResponse
      data.py                  Select from public.projects, newest first
    briefs/
      router.py                POST /api/v1/send-brief, the multipart endpoint
      service.py               Builds the PDF, composes the HTML email, sends through Resend
      labels.py                Maps frontend keys to readable Spanish labels
  utils/
    pdf_generator.py           Builds the brief PDF in memory and returns bytes
assets/mmgonnar.png            Logo stamped into the PDF footer
supabase_migration.sql         Adds design_briefs.currency
supabase_migration_brief_restructure.sql
                               Adds the design and scope columns to design_briefs
.github/workflows/keep_alive.yml
                               Daily cron that pings Supabase so the free project is not paused
Procfile                       Render start command
BACKEND_FIELDS.md              Field by field contract for the brief form
PROJECT_SUMMARY.md             Older working notes, superseded by this file
test_file_upload.py            Ad hoc manual script against a local server, not a test suite
```

The layout convention is one folder per feature under `app/features/`, split into `router` (HTTP),
`service` (business logic), and `data` (Supabase access). Contact and projects predate the router
split and are wired directly in `app/main.py`; only briefs has its own `APIRouter`.

---

## Endpoints

Base URL locally is `http://127.0.0.1:8000`. Interactive docs are at `/docs` and the OpenAPI
schema at `/openapi.json`, both served by FastAPI with no configuration.

No endpoint requires auth, an API key, or a session.

### `GET /`

Liveness only. Touches nothing.

Response `200`:

```json
{ "message": "API ready" }
```

### `GET /health` and `HEAD /health`

Readiness. Runs `select id from projects limit 1` against Supabase, so it fails when the database
is unreachable or paused.

Response `200`:

```json
{ "status": "ok" }
```

Response `503` when the Supabase call raises. The exception is logged server side, never returned:

```json
{ "status": "degraded" }
```

Declared with `@app.api_route(..., methods=["GET", "HEAD"])` so uptime checkers that send `HEAD`
do not get a 405.

### `GET /projects`

Returns every row of `public.projects`, newest first, flattened to one language.

| Query param | Type | Default | Notes |
|---|---|---|---|
| `lang` | string | `es` | Selects the `*_es` or `*_en` columns. Only `es` and `en` exist in the table. |

Response `200`, a JSON array of:

```json
[
  {
    "id": "uuid-or-text",
    "title": "Project title",
    "description": "Short description",
    "architecture": "Architecture notes",
    "technical_details": "Technical notes",
    "image_url": "https://...",
    "logo_url": "https://...",
    "repository_url": "https://github.com/...",
    "live_url": "https://...",
    "technologies": ["FastAPI", "Supabase"],
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

`logo_url`, `repository_url`, and `live_url` are nullable. Every other field is required, so a row
missing one of them makes the whole request fail.

Response `500` with `{"detail": "Error getting projects"}` on any failure, including an unknown
`lang`, which makes the column lookup fail.

### `POST /contact`

Content type `application/json`. Body is the `ContactMessage` model:

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | |
| `email` | string | yes | Validated as an email by `EmailStr` |
| `message` | string | yes | |
| `phone_extension` | string or null | no | Honeypot. Real users never see this field. |

If `phone_extension` has any value the request is treated as a bot: nothing is stored, no email is
sent, and the endpoint returns a success shaped response so the bot learns nothing.

```json
{ "status": "success", "message": "Processed" }
```

Otherwise the row is inserted into `public.portfolio_contact` (with `phone_extension` stripped), a
reference id is generated, and a notification email is attempted. Email failures are logged and
swallowed, so the submission still succeeds.

Response `200`:

```json
{
  "status": "success",
  "data": [{ "id": 123, "name": "John Doe", "email": "john@example.com", "message": "..." }],
  "ticket_id": "REF-1A2B3C4D"
}
```

`data` is whatever Supabase returns from the insert. `ticket_id` is a fresh `REF-` prefixed
8 character slice of a UUID, generated per request and not persisted.

Response `422` on validation failure (Pydantic), `500` with a generic message if the insert fails.

### `POST /api/v1/send-brief`

Content type `multipart/form-data`. This is the design brief form. Every field is a form field,
not JSON. The full field by field contract, including what each key means and how budget bands map
to currency, is in `BACKEND_FIELDS.md`.

Required form fields: `name`, `email`, `projectType`, `projectDescription`, `features`, `budget`,
`timeline`.

| Field | Type | Default | Notes |
|---|---|---|---|
| `name` | string | required | |
| `email` | string | required | Not email validated at this endpoint, unlike `/contact` |
| `phone` | string | `""` | |
| `company` | string | `""` | |
| `projectName` | string | `""` | Falls back to `company`, then `name`, when empty |
| `projectType` | string | required | `website`, `landing`, `web_app`, `dashboard`, `redesign`, `other`. Empty becomes `website`. |
| `projectDescription` | string | required | |
| `hasExistingSite` | bool | `false` | |
| `existingSiteUrl` | string | `""` | |
| `features` | repeated string | required | Repeat the key once per selection. A JSON array or comma separated string is not supported. |
| `featuresDetail` | string | `""` | |
| `targetAudience` | string | `""` | |
| `competitors` | string | `""` | |
| `visualStyle` | string | `""` | |
| `visualReferences` | string | `""` | |
| `brandColors` | string | `""` | |
| `brandAssetsReady` | string | `"false"` | Parsed as `true` only for the literal string `true`, case insensitive |
| `designStatus` | string | `""` | `ready`, `brand_kit`, `none` |
| `designLink` | string | `""` | |
| `wantsDesignQuote` | string | `"false"` | Same string to bool parsing |
| `scopeLevel` | string | `""` | `basic`, `medium`, `advanced`. Computed by the frontend. |
| `scopeWeight` | string | `""` | Non negative integer, as a string. Computed by the frontend. |
| `budget` | string | required | `r1`, `r2`, `r3`, `r4`. Empty becomes `not_defined`. |
| `timeline` | string | required | `asap`, `one_month`, `one_3_months`, `two_three_months`, `flexible`. Empty becomes `flexible`. |
| `flexibleBudget` | string | `"false"` | Same string to bool parsing |
| `currency` | string | `"USD"` | `USD` or `MXN`. Decides which band label `budget` renders as. |
| `additionalNotes` | string | `""` | |
| `locale` | string | `"en"` | Language the client filled the form in |
| `referenceLinks` | string | `""` | |
| `attachments` | file list | none | Uploaded files. Never stored, only emailed. |

Scope is deliberately not recomputed here. The frontend owns the weight table in
`features/brief/utils/scope.ts`; this endpoint validates the shape only. An unknown `scopeLevel`
or a non integer `scopeWeight` is logged and stored empty rather than rejecting the brief, because
a usable brief matters more than an estimate.

What happens on a successful request:

1. Request shape is logged. Content is never logged, because names, emails, and descriptions are
   personal data and Render retains logs.
2. `budget` and `timeline` keys are turned into display strings. Budget bands depend on `currency`.
3. A row is inserted into `public.design_briefs`, with the full normalized payload in the
   `full_data` JSON column.
4. If that insert raises, a fallback insert writes only `client_name`, `client_email`,
   `project_type`, and `full_data`. This is logged as a warning because the row is then incomplete.
5. Attachment file names are collected and added to the PDF payload.
6. A PDF is generated in memory (never written to disk) and emailed through Resend along with the
   uploaded files. The email and PDF are always in Spanish regardless of `locale`, because they are
   for the site owner, not the client.

Response `200`:

```json
{
  "status": "success",
  "message": "Brief recibido. Te contactaré pronto.",
  "id": "uuid-of-the-design_briefs-row"
}
```

Response `422` when a required form field is missing. Response `500` with
`{"detail": "No se pudo guardar el brief. Por favor intenta mas tarde"}` when both inserts fail,
or `{"detail": "Error interno del servidor. Por favor intenta mas tarde"}` for anything else.
Exception detail is never returned to the client, because it can leak Supabase table and column
names.

Note that email sending is not best effort here, unlike `/contact`: if Resend fails after the row
was saved, the request returns 500 even though the brief is safely in the database.

---

## Local setup

```bash
git clone git@github.com:mmgonnar/portfolio_backend.git
cd portfolio_backend

python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # then fill in the values
```

Run the server:

```bash
uvicorn app.main:app --reload
```

The API is then on `http://127.0.0.1:8000`, with docs on `http://127.0.0.1:8000/docs`.

`app/db/supabase_client.py` builds the Supabase client at import time and raises if the
credentials are missing, so the app will not start without a valid `.env`. There is no offline or
mock mode.

To mirror production locally, use the Procfile command instead:

```bash
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app
```

---

## Running the tests

Test dependencies live in `requirements-dev.txt` (which pulls in `requirements.txt`); they are
kept out of `requirements.txt` because Render installs that one.

```bash
pip install -r requirements-dev.txt
pytest
```

The suite under `tests/` needs no `.env` and no running server: it sets dummy values for the
required environment variables before importing the app, replaces the Supabase client with a fake
and captures `resend.Emails.send`, so no test can touch the database or send an email even when
real credentials are present in the environment.

Tests marked `xfail` document known bugs (the 0.9 issues list) and the pending 7.2 upload limits
as tests of the correct behavior. They count as expected failures today; once the fix lands, the
test starts passing, strict mode flags it, and the marker comes off.

---

## Environment variables

Names are taken from the code. Copy `.env.example` to `.env` and fill it in. Never commit `.env`;
it is gitignored.

| Variable | Required | Read in | Purpose |
|---|---|---|---|
| `SUPABASE_URL` | yes | `app/db/supabase_client.py` | Supabase project REST URL |
| `SUPABASE_KEY` | yes | same file | Supabase API key. Use the anon key. |
| `RESEND_API_KEY` | no | `app/features/briefs/service.py`, `app/features/contact/service.py` | Resend API key. When absent, both endpoints log a warning and skip the email instead of failing. |
| `LOG_LEVEL` | no | `app/main.py` | Root log level, default `INFO`. Without the `logging.basicConfig` call in `main.py` the app loggers emit nothing, because the root logger defaults to `WARNING`. |

On `SUPABASE_KEY`: the keep alive workflow comment states that the anon key is the only acceptable
value there, since the repository and its Actions logs are public. The same reasoning applies to
the service role key in general, so prefer the anon key for this service and rely on RLS.

GitHub Actions needs `SUPABASE_URL` and `SUPABASE_KEY` as repository secrets for the keep alive
workflow. Render needs `SUPABASE_URL`, `SUPABASE_KEY`, and `RESEND_API_KEY`.

---

## Supabase

Three tables in the `public` schema. There is no migration tool and no schema under version
control beyond the two ad hoc `.sql` files, so the authoritative schema is whatever is in the
Supabase project.

### `projects`

Read by `GET /projects` and by `GET /health`. Queried with `select("*").order("created_at", desc=True)`.
Columns the code requires:

- `id`, `created_at`
- `image_url`, `technologies` (array)
- `logo_url`, `repository_url`, `live_url` (nullable)
- `title_es` / `title_en`
- `description_es` / `description_en`
- `architecture_es` / `architecture_en`
- `technical_details_es` / `technical_details_en`

The language suffix is built from the `lang` query param, so adding a language means adding four
columns, not changing code.

### `portfolio_contact`

Written by `POST /contact`. Columns: `name`, `email`, `message`, plus whatever Supabase manages
(`id`, `created_at`). The honeypot `phone_extension` is stripped before the insert and never
stored.

### `design_briefs`

Written by `POST /api/v1/send-brief`. Columns the code writes:

`client_name`, `client_email`, `client_phone`, `company`, `project_name`, `project_type`,
`project_description`, `has_existing_site`, `existing_site_url`, `features` (array),
`target_audience`, `budget`, `timeline`, `flexible_budget`, `currency`, `locale`,
`additional_notes`, `design_status`, `design_link`, `wants_design_quote`, `scope_level`,
`scope_weight`, `full_data` (JSON).

`id` and `created_at` are Supabase managed; `id` is read back and returned in the response. `None`
values are filtered out before the insert, so a column only receives a value when one was given.
`full_data` always holds the complete normalized payload, which is what the PDF is built from, so
nothing is lost even when individual columns are missing.

The two migration files add columns to this table and are run by hand in the Supabase SQL editor:

```bash
# supabase_migration.sql                        -> currency
# supabase_migration_brief_restructure.sql      -> design_status, design_link,
#                                                  wants_design_quote, scope_level, scope_weight
```

Run `supabase_migration_brief_restructure.sql` before deploying a version that sends the design
and scope fields, otherwise every insert falls back to the 4 column path and briefs land
incomplete.

### Row level security

RLS is configured in the Supabase dashboard and is not visible in this repository. The one signal
in the code is the comment in `.github/workflows/keep_alive.yml`, which describes `public.projects`
as the only table the anon role can read once RLS is enabled. That implies the intended policy
shape is: anon can `select` on `projects`, anon can `insert` into `portfolio_contact` and
`design_briefs`, and anon can read neither of those two back. Confirm the actual policies in the
dashboard before relying on this.

### Keep alive

A free Supabase project is paused after a week of inactivity, which would take the whole API down.
`.github/workflows/keep_alive.yml` runs daily at 00:00 UTC and `curl`s the Supabase REST endpoint
for `projects?select=id&limit=1` with `-f` so a non 200 fails the job. It can also be triggered
manually with `workflow_dispatch`. It pings Supabase directly, not this API, so it does nothing
about Render spinning the web service down.

---

## CORS

Configured in `app/main.py` with `allow_credentials=True`, `allow_methods=["*"]`, and
`allow_headers=["*"]`.

Explicit allowed origins:

- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `https://www.mmgonnar.com`
- `https://mmgonnar.com`
- `https://portfolio-backend-tarb.onrender.com`

Vercel preview deployments get a different host on every commit, so they cannot be listed. They
are matched by regex instead:

```
^https://portfolio-[a-z0-9-]+-mmgonnars-projects\.vercel\.app$
```

This covers both forms Vercel generates for this project,
`portfolio-<hash>-mmgonnars-projects.vercel.app` and
`portfolio-git-<branch>-mmgonnars-projects.vercel.app`. The pattern requires the project name as a
prefix and the team scope as a suffix, so a project named `portfolio-*` under someone else's Vercel
account does not match. Both ends are anchored and the middle segment rejects dots, so
`portfolio-x.vercel.app.another-domain.com` does not match either. Production stays on the explicit
list.

If the frontend moves to a different Vercel team or the project is renamed, this regex has to
change or every preview deployment breaks with a CORS error.

---

## Deploy on Render

The service runs as a Render web service from this repository's `main` branch.

- Runtime: Python. The version comes from `.python-version` (3.12.10). An earlier `runtime.txt` was
  removed because Render does not read it.
- Build command: `pip install -r requirements.txt`
- Start command: the `Procfile`, which Render reads automatically:

  ```
  web: gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app
  ```

  Two workers, not four. A free Render instance has little memory and four Uvicorn workers is
  more than it can hold.
- Render injects `PORT`; Gunicorn with the Uvicorn worker class picks it up without configuration.
- Environment variables to set in the Render dashboard: `SUPABASE_URL`, `SUPABASE_KEY`,
  `RESEND_API_KEY`, and optionally `LOG_LEVEL`.
- Health check path: `/health`. It returns 503 when Supabase is unreachable, which is what you
  want a health check to catch, unlike `/` which always returns 200.

On the free tier the instance spins down when idle, so the first request after a quiet period
takes tens of seconds. The PDF is generated in memory and the uploaded files are only forwarded to
Resend, so no writable disk is needed and nothing has to survive a restart.

There is no `render.yaml`; the service is configured in the dashboard.
