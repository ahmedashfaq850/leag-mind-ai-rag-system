# LegalMind Chat Frontend

React + TypeScript + Tailwind CSS chat interface for the LegalMind RAG API.

## Setup

```bash
npm install
```

## Development

1. Start the backend: `uvicorn backend.api.main:app --reload`
2. Start the frontend: `npm run dev`

The frontend runs at http://localhost:5173 and proxies `/api/*` to the backend at http://localhost:8000.

## Build

```bash
npm run build
```

Output is in `dist/`. Serve with any static file server, and configure your server to proxy `/api/query` to the backend.
