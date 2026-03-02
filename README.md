## Portfolio Backend API

This repository contains a small FastAPI backend used for a personal portfolio site.

Frontend: [mmgonnar.com](https://www.mmgonnar.com/)

It exposes endpoints to:

- **Health check**: confirm the API is running.
- **Projects**: fetch portfolio projects stored in Supabase.
- **Contact**: submit contact messages, persisted to Supabase, and optionally emailed via Resend.

---

## Tech Stack

- **Python** (FastAPI)
- **Supabase** (PostgreSQL + REST)
- **Pydantic** for request/response models
- **Uvicorn / Gunicorn** for ASGI serving

---

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd portfolio_backend
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment variables

Create a `.env` file in the project root with your Supabase credentials:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_service_role_or_anon_key

# Optional (enables email notifications on contact submit)
RESEND_API_KEY=your_resend_api_key
```

The app will raise an error at startup if these variables are missing.

---

## Running the Server

### Local development

Run with `uvicorn`:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Production (example)

This repo includes a `Procfile` for process managers like Heroku:

```bash
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

You can adapt this to your hosting provider (Render, Fly.io, etc.).

---

## API Overview

Base URL examples:

- Local: `http://127.0.0.1:8000`
- Frontend CORS origins allowed:
  - `http://localhost:3000`
  - `http://localhost:5173`
  - `http://127.0.0.1:3000`
  - `https://www.mmgonnar.com`
  - `https://portfolio-backend-tarb.onrender.com`

### `GET /`

- **Description**: Health check.
- **Response**:

```json
{ "message": "API ready" }
```

### `GET /projects`

- **Description**: Returns all portfolio projects, ordered by `id` descending.
- **Backed by**: Supabase table `portfolio_projects`.

Example project shape (from `Projects` schema):

```json
{
  "id": 1,
  "title": "My Project",
  "description": "Short description",
  "image_url": "https://...",
  "tech_stack": ["FastAPI", "Supabase"],
  "github_url": "https://github.com/...",
  "demo_url": "https://..."
}
```

### `POST /contact`

- **Description**: Submit a contact message.
- **Backed by**: Supabase table `portfolio_contact`.
- **Extra behavior**:
  - If `RESEND_API_KEY` is configured, an email notification is sent via Resend (best-effort; failures are logged but do not fail the request).
  - A honeypot field `phone_extension` is accepted to detect bots; if it is present, the API short-circuits and returns success without storing/sending.
  - A `ticket_id` like `REF-XXXXXXXX` is generated and returned on successful processing.
- **Request body** (`ContactMessage`):

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "Hi, I love your work!",
  "phone_extension": null
}
```

Example success response:

```json
{
  "status": "success",
  "data": [{ "id": 123, "name": "John Doe", "email": "john@example.com", "message": "..." }],
  "ticket_id": "REF-1A2B3C4D"
}
```

---

## Supabase Schema (reference)

You should have at least the following tables in your Supabase project:

- **`portfolio_projects`**: stores portfolio projects (fields matching the `Projects` model in `app/models/schemas.py`).
- **`portfolio_contact`**: stores contact form submissions (fields matching `ContactMessage`).

Adjust column names and types to match your models.

---

## Deployment Notes

- Ensure `SUPABASE_URL` and `SUPABASE_KEY` are configured as environment variables in your hosting provider.
- Use the `Procfile` command for production-ready ASGI serving with Gunicorn + Uvicorn workers.
- Optionally add logging and error monitoring in production environments.

---

## License

Add your preferred license here (e.g., MIT) if you want to open source this project.

