# Brief Form Backend Fields

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| name | string | User's full name |
| email | string | User's email address |
| projectType | string | Type of project: 'website', 'webapp', 'wordpress', 'landing', 'redesign', 'other', or '' |
| projectName | string | Name of the project |
| projectDescription | string | Description of the project |
| features | string[] | Array of selected feature keys: 'cms', 'auth', 'payments', 'analytics', 'seo', 'multi_language', 'integrations', 'mobile' |
| targetAudience | string | Description of target audience |
| budget | string | Budget range key: 'r1', 'r2', 'r3', 'r4', 'r5', or '' |
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

## Files

| Field | Type | Description |
|-------|------|-------------|
| files | File[] | Array of uploaded files (brand assets, references) |

## Notes

- **features** is sent as multiple entries with key `features` (e.g., `features: 'cms'`, `features: 'payments'`)
- **budget** values map to ranges:
  - r1: $1K - $3K (USD) / $10K - $15K MXN
  - r2: $3K - $5K (USD) / $15K - $20K MXN
  - r3: $5K - $10K (USD) / $20K - $25K MXN
  - r4: $10K - $25K (USD) / $25K - $30K MXN
  - r5: $25K+ (USD) / $30K+ MXN
- Currency is determined by user's timezone (Mexico = MXN, else = USD)
- **timeline** values map to:
  - asap: ASAP
  - one_month: 1 Month
  - two_three_months: 2-3 Months
  - flexible: Flexible