# TruthTag

TruthTag is a portfolio/demo application for investigating product identifiers against a fictional sample registry. It combines a static HTML/CSS/JavaScript frontend with a FastAPI API and SQLite database.

**This is not a production product-authentication service.** A matching record only means that an identifier matched a record in this demo database. It does not verify a manufacturer, prove a physical item's authenticity, or establish that its identifier has not been copied. All included brands, registry records, pricing data, and warning cases are fictional.

## Current capabilities

- Look up identifiers against the sample registry and return match, warning, or inconclusive results with evidence fields and a heuristic risk score.
- Record API lookups in SQLite and recent results in browser `localStorage`.
- Browse fictional product records and view sample retailer listings and historical price observations.
- Submit incident reports to the API and retrieve reports associated with an authenticated user.
- Register standard user accounts and issue signed bearer tokens. Public registration cannot assign administrator or brand-representative roles.
- Provide role-protected product, batch, bulk-import, incident-triage, and anomaly-telemetry endpoints for accounts provisioned outside public registration.
- Validate image upload size, format, and integrity. **Visual product matching is unavailable** because verified reference-image baselines are not configured.
- Preview a camera stream in supported browsers. QR/barcode decoding is not implemented.
- Create sample product records in the browser-only Registration Studio. These records are not submitted to the API or verified by a brand.

Pricing is sample data, not live retailer availability or current market pricing. Repeated-query signals are based on stored demo lookups; they are not cross-region clone detection or an external threat feed.

## Requirements

- Python 3.10 or newer
- Dependencies listed in [`requirements.txt`](./requirements.txt)

The frontend is served directly by FastAPI. There is no Node-based build step.

## Local development

From the repository root, create and activate a virtual environment, then install the pinned dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set the required settings in PowerShell and start the API:

```powershell
$env:TRUTHTAG_ENV = "development"
$env:TRUTHTAG_JWT_SECRET = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:TRUTHTAG_DB_PATH = Join-Path $PWD "truthtag-local.db"
$env:TRUTHTAG_SEED_DEMO_DATA = "true"
python -m uvicorn backend.main:app --reload
```

Open <http://127.0.0.1:8000/>. The API health endpoint is <http://127.0.0.1:8000/api/health>, and the interactive API documentation is at <http://127.0.0.1:8000/docs>.

The application does not load `.env` files automatically; export the variables in the process environment as above or use a deployment platform's environment configuration. The checked-in [`.env.example`](./.env.example) is a reference template only. Never use its placeholder secret in a deployed environment.

Demo seeding is opt-in and allowed only when `TRUTHTAG_ENV` is `development`, `test`, or `testing`. Development seeding creates fictional catalog/pricing data but no login accounts. Test-only sample accounts are created by the test fixture and must not be used as deployment credentials.

## Tests

The tests configure their own test environment, signing secret, and temporary SQLite database:

```powershell
python -m pytest -q
```

## Security and deployment status

The API refuses to start without `TRUTHTAG_JWT_SECRET` containing at least 32 characters. Configure `TRUTHTAG_CORS_ORIGINS` as a comma-separated allowlist only when a frontend is hosted on a different origin. The API does not enable credentialed CORS.

The project is **not ready for production deployment**. Before exposing it to real users, provision administrator and brand roles through a controlled process, use managed secret storage and HTTPS, define database backup/migration and incident-retention procedures, add appropriate rate limiting and operational monitoring, and replace fictional data and simulated features with verified data sources. The SQLite database and all local environment files are excluded by `.gitignore`; removing a file from the current Git index does not erase it from earlier commits. Review or clean repository history before making a repository containing previously committed sensitive data public.

## Configuration reference

| Variable | Purpose | Default |
| --- | --- | --- |
| `TRUTHTAG_ENV` | Environment gate for demo seeding | `production` |
| `TRUTHTAG_JWT_SECRET` | HS256 signing key; required, minimum 32 characters | None; startup fails |
| `TRUTHTAG_DB_PATH` | SQLite database location | `truthtag-local.db` at repository root |
| `TRUTHTAG_SEED_DEMO_DATA` | Seed fictional records when exactly `true` | `false` |
| `TRUTHTAG_CORS_ORIGINS` | Comma-separated allowed browser origins | Empty |
