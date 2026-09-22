# Contextual RAG — Frontend

React + TypeScript frontend for the Contextual RAG application (Anthropic's Contextual
Retrieval technique). **Phase 1** delivered the application shell; **Phase 2** added full
document management backed by the FastAPI document API. Chat streaming, retrieval
visualization, and authentication are intentionally not implemented yet.

## Stack

- React 19 + TypeScript + Vite
- Tailwind CSS **3.4** (pinned below 4.x)
- shadcn/ui components
- Zustand (client state) + TanStack Query (server state)
- React Router 7
- react-markdown

## Getting started

```bash
npm install
npm run dev                  # http://localhost:5173
```

The Vite dev server proxies `/api/*` to `http://localhost:8000` (backend), so the browser
stays same-origin and no CORS is needed. Copy `.env.example` to `.env.local` only if the
frontend must point at a different backend.

## Scripts

| Command            | Description                                |
| ------------------ | ------------------------------------------ |
| `npm run dev`      | Start the Vite dev server                  |
| `npm run build`    | Typecheck (`tsc -b`) and production build  |
| `npm run preview`  | Preview the production build               |
| `npm run lint`     | ESLint                                     |

## Configuration

| Variable          | Description                                   | Default              |
| ----------------- | --------------------------------------------- | -------------------- |
| `VITE_API_URL`    | Base URL of the FastAPI backend (no trailing `/`). Leave unset during local dev — Vite proxies `/api` to `http://localhost:8000`. | *(unset → proxy)* |

## Structure

```
src/
  api/             Typed API client (client, documents, chat, types, query keys)
  components/
    documents/     DocumentUploader, DocumentCard, DocumentList, UploadProgress,
                   ProcessingStatus, EmptyDocumentsState, DeleteDocumentDialog
    layout/        AppLayout, Sidebar, Header, mobile drawer
    ui/            shadcn/ui primitives (button, card, input, alert-dialog, …)
    markdown.tsx   react-markdown wrapper
    theme-provider.tsx
  hooks/           TanStack Query hooks (useDocuments, useUploadDocument, …)
  lib/utils.ts     cn() helper
  lib/format.ts    bytes/date/file-type formatters
  pages/           Overview, Chat, Documents, Settings
  stores/          Zustand stores: ui, document selection, active conversation
  router.tsx       Route table (all routes inside AppLayout)
```

## Phase 1 (application shell)

- Responsive shell with sidebar navigation (Chat · Documents · Settings), header, and dark mode.
- Zustand stores for UI state, the selected document, and the active conversation.
- API client abstraction wired to `VITE_API_URL` with typed request/response helpers.
- TanStack Query wired up and exercised by the Settings backend-health check.

## Phase 2 (document management)

- Upload via drag-and-drop or file picker with per-file XHR progress bars and multi-file support.
- The upload mutation injects the returned document into the cache immediately, then the list
  stays in sync via TanStack Query. The list polls at 2.5s intervals while any document is
  `uploaded`/`processing`, so statuses update when backend processing completes.
- Document cards show file type, size, uploaded date, and a live `ProcessingStatus`
  (uploaded / processing / processed / failed) with actions to select and delete.
- Delete flows through a confirmation `AlertDialog`; documents are removed from the cache and,
  if the deleted document was selected, the selection is cleared.
- Meaningful errors: network failures, rejected uploads (e.g. unsupported file type), and
  fetch failures each surface with actionable copy and retry controls.
- API layer matches the backend exactly: `GET/POST /api/documents`, `GET/DELETE
  /api/documents/{id}`, `GET /api/documents/{id}/chunks`, `GET /api/health`.

Deliberately deferred to later phases: chat/streaming, retrieval visualization, comparison
views, and authentication.