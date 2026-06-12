# Business Plan Projection — Frontend

A premium, enterprise-grade React + TypeScript + Vite UI for capturing every
assumption behind a financial projection. Built with React Router, TanStack
Query, React Hook Form, and Zod.

## Requirements

- Node.js 18+ (20+ recommended)

## Setup & run

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api` to the FastAPI
backend at `http://127.0.0.1:8000`, so **start the backend first**.

To point at a different API origin, set `VITE_API_BASE` (e.g. in `.env.local`):

```
VITE_API_BASE=http://localhost:8000/api
```

## Scripts

| Command           | Description                          |
| ----------------- | ------------------------------------ |
| `npm run dev`     | Start the Vite dev server            |
| `npm run build`   | Type-check and build for production  |
| `npm run preview` | Preview the production build         |
| `npm run lint`    | Type-check only (`tsc --noEmit`)     |

## Architecture

```
src/
  api/         fetch client + React Query hooks
  components/
    ui/        primitives: Badge, Modal, Toast, Tooltip, Progress, EmptyState…
    form/      schema-driven form engine (field config → inputs + Zod)
    pages/     reusable page templates (Singleton, Collection, PerProduct)
    …          SectionCard, PageHeader, SaveBar, DataTable, SummaryCard…
  layouts/     AppLayout, Sidebar, TopBar, ProjectContext
  pages/       the 14 workflow pages + projects list / new
  routes/      router + central navigation model
  schemas/     (reserved for shared zod schemas)
  styles/      design tokens + global stylesheet
  types/       TypeScript mirror of the backend models
  utils/       formatting, option lists
```

### Schema-driven forms

Most pages declare a `FormConfig` (cards → fields). `SchemaFields` renders the
inputs, `buildZodSchema` derives validation, and the reusable
`SingletonFormPage` / `CollectionPage` / `PerProductPage` templates wire them to
the API. Adding a field is usually a one-line config change.

### Design system

Tokens live in `styles/theme.css` (slate neutrals; blue/emerald/amber accents).
Components use semantic classes from `styles/global.css` — white cards on a soft
background, subtle borders and shadows, tabular numerics, and accessible
tooltips for financial terms.

## Numeric & data conventions

- **Numbers** display with thousands separators but are stored as plain numbers.
- **Percentages** are entered/stored as whole percents (e.g. `9` = 9%).
- **Currency** is selected once in Project Setup and reused app-wide.
- **Dates** use native date inputs and are stored as ISO strings.
