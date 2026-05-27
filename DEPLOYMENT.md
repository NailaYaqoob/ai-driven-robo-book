# Deployment Guide

Complete guide for deploying the Physical AI & Humanoid Robotics Interactive Textbook.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
3. [Backend Deployment (Railway)](#backend-deployment-railway)
4. [Connecting Frontend and Backend](#connecting-frontend-and-backend)
5. [Troubleshooting](#troubleshooting)
6. [Post-Deployment Checklist](#post-deployment-checklist)

---

## Architecture Overview

| Layer | Technology | Host | URL |
| --- | --- | --- | --- |
| Frontend | Docusaurus (static site) | **Vercel** | https://ai-driven-robo-book.vercel.app |
| Backend | FastAPI | **Railway** | https://ai-driven-robo-book-production.up.railway.app |

The frontend is a static Docusaurus build. The browser calls the backend
directly using the build-time variable `REACT_APP_API_URL`. The backend allows
the frontend origin via CORS (`ALLOWED_ORIGINS`). Wiring these two values
correctly is what "connects" the two halves — see
[Connecting Frontend and Backend](#connecting-frontend-and-backend).

---

## Frontend Deployment (Vercel)

### Prerequisites

- GitHub repository with code pushed to `main`
- A Vercel account linked to the GitHub repo
- Node.js 18+ installed locally for testing

### Setup Steps

#### 1. Import the Project into Vercel

1. Go to https://vercel.com/new
2. Select **Import Git Repository** and pick `ai-driven-robo-book`
3. In the project configuration:
   - **Root Directory**: `website`
   - **Framework Preset**: Docusaurus (auto-detected)
   - **Build Command**: `npm run build` (from `website/vercel.json`)
   - **Output Directory**: `build`
   - **Install Command**: `npm ci`

> The `website/vercel.json` file already pins these build settings, so the
> only manual step in the UI is setting **Root Directory** to `website`.

#### 2. Add Environment Variables

In Vercel → Project → **Settings → Environment Variables**, add the backend URL
for the **Production** (and Preview) environments:

```bash
REACT_APP_API_URL=https://ai-driven-robo-book-production.up.railway.app
```

> This variable is injected into the browser bundle at build time
> (see `website/docusaurus.config.js`). Without it, the site falls back to
> `http://localhost:8000` and the chatbot/auth/personalization features break
> in production.

#### 3. Test Locally Before Deploying

```bash
cd website
npm install

# Build against the live backend exactly like Vercel does
REACT_APP_API_URL=https://ai-driven-robo-book-production.up.railway.app npm run build

# Serve the production build locally
npm run serve
```

Visit `http://localhost:3000` to test the production build.

#### 4. Deploy

**Automatic (recommended):** Vercel deploys every push to `main` to production
and every other branch/PR to a preview URL:

```bash
git add .
git commit -m "feat: update content for deployment"
git push origin main
```

**Manual:** From the Vercel dashboard, open the project and click
**Deployments → Redeploy**, or run `vercel --prod` with the Vercel CLI from the
`website/` directory.

#### 5. Access Your Deployed Site




```
https://ai-driven-robo-book.vercel.app
```

### Custom Domain (Optional)

1. In Vercel → Project → **Settings → Domains**, add your domain
   (e.g. `textbook.example.com`).
2. Add the DNS record Vercel shows you at your registrar (usually a `CNAME`
   pointing to `cname.vercel-dns.com`).
3. Vercel provisions HTTPS automatically.
4. **Important:** also add the new domain to the backend `ALLOWED_ORIGINS`
   (see [Connecting Frontend and Backend](#connecting-frontend-and-backend)).

---

## Backend Deployment (Railway)

### Prerequisites

- Railway account (https://railway.app)
- Railway CLI installed
- Environment variables ready (API keys, database URLs)

### Setup Steps

#### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

#### 2. Login to Railway

```bash
railway login
```

#### 3. Create New Project

**Option A: Railway Dashboard**
1. Go to https://railway.app/dashboard
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Authorize Railway to access your repository
5. Select `learn-humanoid-robotics` repository

**Option B: Railway CLI**
```bash
cd backend
railway init
```

#### 4. Configure Environment Variables

In Railway dashboard (Project → Variables):

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
NEON_DATABASE_URL=postgresql://user:pass@host/dbname
QDRANT_URL=https://xxxxx.qdrant.cloud
QDRANT_API_KEY=xxxxxxxxxxxxx
BETTER_AUTH_SECRET=xxxxxxxxxxxxx  # Generate with: openssl rand -hex 32
JWT_SECRET_KEY=xxxxxxxxxxxxx      # Generate with: openssl rand -hex 32
PYTHON_VERSION=3.11
PORT=8000

# CORS — allow the frontend origin(s) to call this API.
# Comma-separated. Must include your Vercel production domain.
ALLOWED_ORIGINS=https://ai-driven-robo-book.vercel.app,http://localhost:3000
```

> Vercel preview deployments (`*.vercel.app`) are matched automatically by a
> regex in `backend/app/main.py`, so you only need to list your production
> domain (and `localhost:3000` for local dev) here.

#### 5. Set Build Configuration

Railway should auto-detect FastAPI. If needed, set:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 6. Deploy

**Option A: Automatic Deployment**
Railway auto-deploys on git push to `main`:

```bash
git push origin main
```

**Option B: Manual Deployment**
```bash
railway up
```

#### 7. Run Database Migrations

After first deployment:

```bash
railway run alembic upgrade head
```

#### 8. Access Backend API

This project's backend is deployed at:
```
https://ai-driven-robo-book-production.up.railway.app
```

API documentation available at:
```
https://ai-driven-robo-book-production.up.railway.app/docs
```

Health check:
```
https://ai-driven-robo-book-production.up.railway.app/health
```

---

## Connecting Frontend and Backend

The two halves connect through exactly two values that must agree:

| Value | Where it lives | Set it to |
| --- | --- | --- |
| `REACT_APP_API_URL` | Vercel env var (frontend build) | `https://ai-driven-robo-book-production.up.railway.app` |
| `ALLOWED_ORIGINS` | Railway env var (backend CORS) | `https://ai-driven-robo-book.vercel.app,http://localhost:3000` |

**How it works**

1. At build time, `website/docusaurus.config.js` injects `REACT_APP_API_URL`
   into the browser bundle via webpack `DefinePlugin`. All frontend API clients
   (`RAGChatbot.tsx`, `lib/auth-client.ts`, `context/PersonalizationContext.tsx`)
   read this single variable. If unset, they fall back to `http://localhost:8000`.
2. The browser calls `${REACT_APP_API_URL}/api/...` directly.
3. The backend's CORS middleware (`backend/app/main.py`) allows the request only
   if the request `Origin` is in `ALLOWED_ORIGINS` or matches the `*.vercel.app`
   regex (which covers preview deployments).

**Checklist to wire them up**

- [ ] Set `REACT_APP_API_URL` in Vercel → Settings → Environment Variables, then
      **redeploy** the frontend (env vars only apply to new builds).
- [ ] Set `ALLOWED_ORIGINS` in Railway → Variables to include the Vercel domain.
- [ ] Verify end-to-end:
      ```bash
      # CORS preflight should echo back the allowed origin
      curl -i -X OPTIONS \
        -H "Origin: https://ai-driven-robo-book.vercel.app" \
        -H "Access-Control-Request-Method: POST" \
        https://ai-driven-robo-book-production.up.railway.app/api/rag/query
      ```
      Look for `access-control-allow-origin: https://ai-driven-robo-book.vercel.app`.

---

## Troubleshooting

### Frontend Issues

#### Build Fails with "Module not found"

**Solution:**
```bash
cd website
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Broken Links Warning

**Solution:**
1. Run build locally to see specific broken links:
   ```bash
   npm run build 2>&1 | grep "Broken link"
   ```

2. Fix links in MDX files:
   - Remove `.mdx` extensions from internal links
   - Use absolute paths like `/docs/introduction/` instead of `./`
   - Ensure document IDs match actual file structure

#### 404 / Broken Routing on Vercel

**Causes:**
- Wrong `baseUrl` in `docusaurus.config.js` (must be `/` for a root domain)
- Vercel **Root Directory** not set to `website`

**Solution:**
1. Check `website/docusaurus.config.js`:
   ```javascript
   url: 'https://ai-driven-robo-book.vercel.app',
   baseUrl: '/',
   ```
2. Verify Vercel → Settings → General → **Root Directory** = `website`.

#### Chatbot / Auth / Personalization Fails in Production

**Symptom:** Network tab shows requests going to `http://localhost:8000`, or
CORS errors in the console.

**Cause:** `REACT_APP_API_URL` was not set at build time, or `ALLOWED_ORIGINS`
on the backend doesn't include the Vercel domain.

**Solution:** See
[Connecting Frontend and Backend](#connecting-frontend-and-backend). Remember to
**redeploy** the frontend after changing the Vercel env var.

### Backend Issues

#### Database Connection Fails

**Solution:**
1. Verify `NEON_DATABASE_URL` format:
   ```
   postgresql://user:password@host.neon.tech/dbname?sslmode=require
   ```

2. Test connection locally:
   ```bash
   cd backend
   python -c "from app.core.database import engine; print('✓ Connected')"
   ```

#### OpenAI API Rate Limit

**Solution:**
1. Check API key tier (free tier has strict limits)
2. Implement rate limiting in backend
3. Use caching for frequently asked questions

#### Railway Build Fails

**Common Causes:**
- Missing `requirements.txt`
- Incompatible Python version
- Missing environment variables

**Solution:**
1. Verify `requirements.txt` exists in `backend/`
2. Set `PYTHON_VERSION=3.11` in Railway environment
3. Check Railway build logs for specific errors

---

## Post-Deployment Checklist

### Frontend Verification

- [ ] Site loads at https://ai-driven-robo-book.vercel.app
- [ ] All pages accessible via navigation
- [ ] Search functionality works
- [ ] Images and diagrams render correctly
- [ ] Mobile responsive design works
- [ ] No console errors in browser DevTools
- [ ] Lighthouse scores:
  - Performance: >90
  - Accessibility: >95
  - Best Practices: >90
  - SEO: >90

**Run Lighthouse Audit:**
```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run audit
lighthouse https://ai-driven-robo-book.vercel.app --view
```

### Backend Verification

- [ ] API documentation accessible at `/docs`
- [ ] Health check endpoint returns 200
- [ ] Database migrations applied successfully
- [ ] Vector database (Qdrant) connected
- [ ] OpenAI API calls working
- [ ] CORS configured for frontend domain
- [ ] Environment variables set correctly
- [ ] No sensitive data in logs

**Test Backend Health:**
```bash
curl https://ai-driven-robo-book-production.up.railway.app/health
# Expected: {"status": "healthy"} (or "degraded" if Qdrant/DB not yet seeded)
```

### Integration Testing

- [ ] Frontend can connect to backend API
- [ ] Chatbot sends queries and receives responses
- [ ] User authentication flow works
- [ ] Personalization settings persist
- [ ] Link between frontend and backend CORS configured

### Monitoring Setup

1. **Vercel**: Monitor frontend builds and deployments
   - Vercel dashboard → Project → Deployments / Analytics

2. **Railway Metrics**: Monitor backend performance
   - Railway dashboard → Metrics tab

3. **Error Tracking** (Optional):
   - Sentry for backend errors
   - Vercel Web Analytics for frontend analytics

---

## Rollback Procedure

### Frontend Rollback

**Option 1: Revert Git Commit**
```bash
git revert HEAD
git push origin main
```

**Option 2: Promote a Previous Vercel Deployment**
1. Vercel dashboard → Project → **Deployments**
2. Find a previous successful deployment
3. Open the **⋯** menu → **Promote to Production**

### Backend Rollback

**Option 1: Railway Dashboard**
1. Go to Deployments tab
2. Find previous successful deployment
3. Click "Redeploy"

**Option 2: Railway CLI**
```bash
railway rollback
```

---

## Continuous Integration / Continuous Deployment

Deployment is fully managed by the hosting platforms — no GitHub Actions
workflow is required:

- **Frontend (Vercel)**: every push to `main` triggers a production build and
  deploy; every branch/PR gets a preview URL. Vercel runs `npm ci` and
  `npm run build` (a failed build blocks the deploy).
- **Backend (Railway)**: every push to `main` rebuilds and redeploys the
  FastAPI service.

---

## Support

- **Issues**: https://github.com/NailaYaqoob/ai-driven-robo-book/issues
- **Discussions**: https://github.com/NailaYaqoob/ai-driven-robo-book/discussions
- **Documentation**: See README.md and specs/ directory

---

**Last Updated**: 2026-05-27
**Version**: 1.1.0
