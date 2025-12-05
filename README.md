# Invoice QC Service

This project extracts invoices from PDFs, validates them against a designed schema, and exposes a CLI and HTTP API for extraction and quality-control (QC).

## Schema & Validation Design

### Fields (invoice-level):
- `invoice_number`: Identifier for the invoice (string).
- `external_reference`: Optional external reference (string).
- `seller_name`: Seller / supplier name (string).
- `seller_tax_id`: Seller VAT / tax id (string, optional).
- `seller_address`: Seller address (string, optional).
- `buyer_name`: Buyer / customer name (string).
- `buyer_tax_id`: Buyer VAT / tax id (string, optional).
- `buyer_address`: Buyer address (string, optional).
- `invoice_date`: Invoice date (ISO 8601 string, e.g. `2024-01-10`).
- `due_date`: Due date / payment deadline (ISO 8601 string, optional).
- `currency`: Currency code (3-letter, e.g. `EUR`, `USD`, `INR`).
- `net_total`: Net amount before tax (number).
- `tax_amount`: Tax amount (number).
- `gross_total`: Total amount including tax (number).
- `payment_terms`: Optional text about payment terms (string).
- `line_items`: List of items (see below).

### Line item structure (if present):
- `description` (string)
- `quantity` (number, optional)
- `unit_price` (number, optional)
- `line_total` (number)

### Validation rules (QC):

**Completeness / Format rules:**
- `invoice_number` and `invoice_date` must be present and non-empty.  (Core identifiers.)
- `seller_name` and `buyer_name` must be present.  (Parties must be known.)
- `currency` must be a known 3-letter currency (one of: `EUR, USD, GBP, INR`).  (Avoid unknown currencies.)

**Business rules:**
- `net_total + tax_amount` ≈ `gross_total` (tolerance: 0.5 currency units).  (Totals should match.)
- Sum of `line_items[].line_total` ≈ `net_total` (tolerance: 1.0) when line items are present.  (Line items reconcile.)
- `due_date` must be on or after `invoice_date` (if present).  (Payment deadlines shouldn't be before invoice date.)

**Anomaly / Duplicate rules:**
- No duplicate invoices in the same batch: duplicate key is (`invoice_number`, `seller_name`, `invoice_date`).  (Catches re-submitted invoices.)
- Totals must not be negative.  (Reject nonsense amounts.)

**Rationale:** These rules are lightweight but practical for a QC step: they ensure minimal completeness, numerical consistency, and basic fraud/duplication detection.

## Usage

### CLI

Extract invoices from PDFs:
```bash
python -m invoice_qc.cli extract --pdf-dir pdfs/ --output extracted.json
```

Validate extracted invoices:
```bash
python -m invoice_qc.cli validate --input extracted.json --report validation_report.json
```

Full pipeline (extract + validate):
```bash
python -m invoice_qc.cli full-run --pdf-dir pdfs/ --report validation_report.json
```

### HTTP API

Start the FastAPI server:
```bash
python -m uvicorn invoice_qc.api:app --host 0.0.0.0 --port 8000
```

Then visit http://localhost:8000 to use the interactive web console.

**API Endpoints:**
- `GET /` – Serve the QC console UI.
- `GET /health` – Health check.
- `POST /validate-json` – Validate a list of invoice JSON objects.
- `POST /extract-and-validate-pdfs` – Upload PDFs, extract, and validate in one step.

## How this could integrate into a larger system

This service is designed to fit into a larger document-processing pipeline:

1. **Data Source**: PDFs or JSON invoices come from upstream services (e.g., document scanners, OCR, or accounting software).

2. **Queue Integration**: The service can be deployed to process invoices from a message queue (e.g., RabbitMQ, AWS SQS):
   - A consumer listens for invoice documents.
   - Sends them to the `/extract-and-validate-pdfs` endpoint.
   - Stores results in a database or publishes to a downstream queue.

3. **API Integration**: Other services can call `/validate-json` to validate their own extracted invoice data before committing to a database.

4. **Dashboard Integration**: The interactive console at `/` can be embedded or linked from an internal tool dashboard for staff review of flagged invoices.

5. **Workflow Orchestration**: Tools like Airflow, Prefect, or Temporal can orchestrate:
   - PDF → Extraction → Validation → Database → Notification

6. **Containerization**: Deploy as Docker container:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "-m", "uvicorn", "invoice_qc.api:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

7. **Error Handling**: Invalid invoices can be:
   - Flagged for manual review in the console.
   - Sent to a remediation workflow (e.g., operator fixes missing fields).
   - Stored in a quarantine bucket for later analysis.

8. **Audit Trail**: Store validation results (extracted data + validation report) for compliance and debugging.

This architecture allows the QC service to scale horizontally and integrate with both synchronous (API) and asynchronous (queue-based) workflows in enterprise systems.

## Project Structure

```
invoice-qc-service/
├── invoice_qc/
│   ├── api.py                  # FastAPI app with REST endpoints
│   ├── cli.py                  # CLI commands (extract, validate, full-run)
│   ├── extractor.py            # PDF extraction & parsing logic
│   ├── validator.py            # Validation rules & reporting
│   ├── models.py               # Data classes (Invoice, LineItem)
│   ├── config.py               # Configuration & constants
│   └── utils/
│       ├── parsing.py          # Helper functions
│       └── summaries.py        # Report generation
├── static/
│   └── index.html              # Web console UI
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
└── README.md                   # This file
```

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run CLI:**
   ```bash
   python -m invoice_qc.cli extract --pdf-dir sample_pdfs --output extracted.json
   ```

3. **Run API server:**
   ```bash
   python -m uvicorn invoice_qc.api:app --host 0.0.0.0 --port 8000
   ```

4. **Run tests:**
   ```bash
   python tests/test_basic.py
   ```

## Key Features

- **PDF Extraction**: Uses `pdfplumber` and `PyPDF2` to extract text from invoices.
- **Smart Parsing**: Heuristics-based text parsing to find invoice numbers, dates, amounts, seller/buyer names (supports German and English formats).
- **Comprehensive Validation**: Checks completeness, format, business rules, and anomalies.
- **Multiple Interfaces**: CLI for batch processing, HTTP API for integration, web console for manual review.
- **Flexible Output**: JSON reports with per-invoice errors and summary statistics.
- **Production-Ready**: Properly structured, error handling, and ready to containerize.

## Technical

- **Architecture**: Small, modular Python service with three main layers — extraction (`invoice_qc/extractor.py`), validation (`invoice_qc/validator.py`), and interfaces (CLI `invoice_qc/cli.py`, HTTP API `invoice_qc/api.py`, and web UI `static/index.html`). The service is stateless and designed to be run as a container for easy scaling.
- **Data model**: Invoices follow a consistent JSON shape defined in `invoice_qc/models.py` (invoice-level fields + `line_items`). This makes results predictable and easy to store in a database.
- **Extraction & validation**: Extraction uses `pdfplumber` (with `PyPDF2` fallback) and regex/heuristic parsing for multilingual labels and variable number formats. Validation enforces completeness, totals reconciliation (configurable tolerances in `invoice_qc/config.py`), date sanity, and duplicate/anomaly checks.
- **Interfaces**: Use the CLI for batch processing, the FastAPI HTTP endpoints for synchronous integration (`/validate-json`, `/extract-and-validate-pdfs`), or the web console for manual review. Multipart uploads require `python-multipart` (listed in `requirements.txt`).
- **Deployment**: Docker support included (`Dockerfile`, `docker-compose.yml`) — run via `docker-compose up --build`. For production, run behind a reverse proxy and use process managers (Gunicorn + Uvicorn workers) and object storage for large volumes.
- **Extensibility & config**: Extraction patterns and tolerances are configurable; add vendor-specific patterns or tune thresholds in `invoice_qc/config.py` or move patterns to external JSON/YAML for live updates.
- **Docs & walkthrough**: A non-technical, step-by-step web-console walkthrough is available at `docs/web_console_walkthrough.html` (open in a browser) for onboarding non-technical users.

---

## Author & Submission Notes

Author: **[Pulkit Sharma]**

This repository contains work primarily completed by me. I used targeted AI assistance only for non-core tasks such as documentation drafting and debugging suggestions. All implementation decisions, parsing heuristics, validation logic, and code were written and reviewed by me.

If you are preparing this repository for a job application, include the files listed in the project root (source, requirements, README, sample data). Do NOT include any secrets. See `SUBMISSION.md` for a short submission checklist and suggested commit message.

---

## AI Usage Disclosure

I used limited, targeted AI assistance for the following (transparent and minimal):
- Drafting and polishing `README.md`
- Suggestions for debugging and improving error handling in the web console.

No AI-generated code was copied into the project without review and modification. The codebase and architecture are my own work.


## Submission Checklist (quick)

- [ ] All source code under `invoice_qc/` is included and tested
- [ ] `requirements.txt` present and accurate
- [ ] `README.md` updated (this file)


