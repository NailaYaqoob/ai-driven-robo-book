---
id: 0001
title: Switch frontend deploy to Vercel and wire frontend↔backend
stage: general
date: 2026-05-27
surface: agent
model: claude-opus-4-7
feature: none
branch: main
user: NailaYaqoob
command: none
labels: ["deployment", "vercel", "railway", "cors", "docusaurus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - DEPLOYMENT.md
  - QUICKSTART-DEPLOY.md
  - README.md
  - .github/workflows/deploy.yml (deleted)
  - website/vercel.json (new)
  - website/docusaurus.config.js
  - website/src/lib/auth-client.ts
  - website/src/context/PersonalizationContext.tsx
  - backend/app/core/config.py
  - backend/app/main.py
tests:
  - "website: npm ci (clean) — 1441 packages, exit 0"
  - "website: REACT_APP_API_URL=<railway> npm run build — SUCCESS, exit 0"
  - "verified Railway URL baked into build/assets/js, localhost:8000 fallback NOT leaked"
  - "live backend CORS preflight from Vercel origin → 200 with access-control-allow-origin echoed"
---

## Prompt

https://github.com/NailaYaqoob/ai-driven-robo-book, https://ai-driven-robo-book.vercel.app/check my deployment issue in DEPLOYMENT.md it shows github pages for front end but I want vercel for front end fix this issue and connect frontend and bckend

(Follow-up message provided the backend URL: https://ai-driven-robo-book-production.up.railway.app/)

## Response

Diagnosed two problems: (1) all deployment docs + a GitHub Actions workflow
described GitHub Pages, not Vercel; (2) the frontend→backend wiring was broken —
`RAGChatbot.tsx` used `REACT_APP_API_URL`, `auth-client.ts` used the Next.js name
`NEXT_PUBLIC_API_URL`, and `PersonalizationContext.tsx` used bare relative
`/api/...` paths, and Docusaurus does not expose `process.env.*` to browser code
by default — so everything silently fell back to `http://localhost:8000`.

Changes:
- **Frontend env injection**: added an inline Docusaurus plugin in
  `docusaurus.config.js` that injects `REACT_APP_API_URL` via webpack
  `DefinePlugin` (fallback `http://localhost:8000`). Updated `url` to the Vercel
  domain.
- **Standardized API base URL**: `auth-client.ts` now reads `REACT_APP_API_URL`;
  `PersonalizationContext.tsx` now prefixes its two fetches with `API_URL`.
- **Backend CORS**: `config.py` `ALLOWED_ORIGINS` default now includes
  `https://ai-driven-robo-book.vercel.app`; `main.py` adds
  `allow_origin_regex=r"https://.*\.vercel\.app"` for preview deploys.
- **Vercel build config**: added `website/vercel.json`.
- **Docs**: rewrote the frontend deployment sections of `DEPLOYMENT.md`,
  `QUICKSTART-DEPLOY.md`, and `README.md` for Vercel; added a "Connecting
  Frontend and Backend" section. Removed the now-redundant
  `.github/workflows/deploy.yml` (GitHub Pages).

Verified: clean `npm ci` + production build succeed; the Railway URL is baked
into the JS bundle with no `localhost:8000` leak; the live Railway backend
already returns the correct CORS headers for the Vercel origin.

Remaining manual step for the user: set `REACT_APP_API_URL` in Vercel → Settings
→ Environment Variables and redeploy the frontend.
