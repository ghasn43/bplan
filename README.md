# Business Plan Studio

A professional, investor-grade web application for capturing **all the
assumptions** required to build a complete financial projection for a business
plan. This first phase delivers the full input workflow, validation system,
data model, and save/load structure — the foundation that the projection engine
(P&L, Cash Flow, Balance Sheet) is built on next.

> Designed to feel like a premium SaaS planning tool (LivePlan / Causal /
> Fathom), suitable for investors, consultants, banks, and accelerators.

---

## Tech stack

| Layer    | Stack                                                            |
| -------- | ---------------------------------------------------------------- |
| Backend  | Python · FastAPI · Pydantic v2 · JSON file storage (Postgres-ready) |
| Frontend | React · TypeScript · Vite · React Router · TanStack Query · React Hook Form · Zod |

---

## Project structure

```
business-plan-app/
├── backend/
│   └── app/
│       ├── main.py          # FastAPI app + router wiring + seed-on-startup
│       ├── config.py        # env-driven settings
│       ├── models/          # Pydantic domain models (one file per topic)
│       ├── schemas/         # request-only schemas
│       ├── routes/          # project routes + generated section routers
│       ├── services/        # registry, completion/review, seed, project service
│       ├── storage/         # StorageBackend interface + JSONStorage
│       └── utils/
├── frontend/
│   └── src/
│       ├── api/             # fetch client + React Query hooks
│       ├── components/      # ui primitives, form engine, page templates
│       ├── layouts/         # AppLayout, Sidebar, TopBar, ProjectContext
│       ├── pages/           # 14 workflow pages + projects list / new
│       ├── routes/          # router + navigation model
│       ├── types/           # TS mirror of backend models
│       ├── utils/           # formatting, option lists
│       └── styles/          # design tokens + global stylesheet
└── README.md
```

---

## Quick start

Run the backend and frontend in two terminals.

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000/api`
- Docs: `http://127.0.0.1:8000/docs`
- A demo project (**Acme SaaS — Demo Plan**) is seeded on first run.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` (the dev server proxies `/api` to the backend).

---

## The 14-page input workflow

| #  | Page                  | Captures                                              |
| -- | --------------------- | ----------------------------------------------------- |
| 1  | Project Setup         | Identity, currency, projection period & frequency     |
| 2  | Products & Services   | What the company sells (multiple, typed by revenue)   |
| 3  | Revenue Assumptions   | Volume, growth, churn, contracts, payment terms       |
| 4  | Direct Costs / COGS   | Per-unit & % costs, live gross-margin preview         |
| 5  | Staffing Plan         | Roles, headcount, salaries, benefits, payroll summary |
| 6  | Operating Expenses    | Recurring costs with frequency & escalation           |
| 7  | Startup Costs         | Pre-opening costs, capitalised vs expensed            |
| 8  | Capital Expenditure   | Fixed assets & depreciation assumptions               |
| 9  | Working Capital       | Cash conversion cycle (DSO/DIO/DPO) preview           |
| 10 | Financing             | Equity, multiple loans, grants, total funding         |
| 11 | Tax & Regulatory      | Corporate tax, VAT, duties, payroll compliance        |
| 12 | Scenarios             | Base / Conservative / Optimistic adjustment sliders   |
| 13 | KPIs & Targets        | Margins, break-even, CAC/LTV, investor metrics        |
| 14 | Review & Completion   | Full summary, checklist, validation, JSON export      |

Each page provides a title + subtitle, professional card sections, grouped
fields, inline validation, tooltips on financial terms, a sticky save bar, and
Previous / Next navigation. A live completion percentage is shown in the top bar
and the sidebar.

---

## Key design decisions

- **Single source of truth for sections.** The backend `services/registry.py`
  declares every section once; the section CRUD routers, completion engine, and
  export ordering are all generated from it. Adding a section is a one-liner.
- **Schema-driven forms.** Frontend pages declare a `FormConfig`; inputs, Zod
  validation, and API wiring are derived automatically via reusable page
  templates (`SingletonFormPage`, `CollectionPage`, `PerProductPage`).
- **Storage abstraction.** Persistence sits behind a `StorageBackend` interface
  with a JSON implementation today and a clean PostgreSQL upgrade path.
- **Projection-ready data model.** Period/frequency are first-class so the model
  already supports 3, 5, or 10-year monthly/quarterly/yearly projections.

---

## API overview

```
GET/POST           /api/projects
GET/PUT/DELETE      /api/projects/{id}
GET                 /api/projects/{id}/completion
GET                 /api/projects/{id}/review
GET                 /api/projects/{id}/export-json

# Singleton sections (GET/PUT):   setup, working-capital, financing, tax, kpis
# Collection sections (CRUD):     products, revenue, direct-costs, staffing,
#                                 operating-expenses, startup-costs,
#                                 fixed-assets, scenarios
```

See `backend/README.md` and the Swagger docs for full details.

---

## Next development phase

The captured assumptions are the input to a projection engine. Recommended order:

1. **Calculation engine** — turn assumptions into monthly time series
   (revenue build-up, COGS, payroll, opex, depreciation, loan amortisation,
   working-capital timing, tax).
2. **Financial statements** — Profit & Loss, Cash Flow, Balance Sheet.
3. **Break-even analysis** and KPI/target tracking against actuals.
4. **Scenario comparison charts** (Base vs Conservative vs Optimistic).
5. **Exports** — investor report, Word/PDF, Excel.
6. **Persistence upgrade** — implement `PostgresStorage` behind the existing
   `StorageBackend` interface; add auth & multi-user workspaces.
