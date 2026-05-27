# Quick Deploy Guide

**5-Minute Setup — Frontend on Vercel, Backend on Railway**

| Layer | Host | URL |
| --- | --- | --- |
| Frontend (Docusaurus) | Vercel | https://ai-driven-robo-book.vercel.app |
| Backend (FastAPI) | Railway | https://ai-driven-robo-book-production.up.railway.app |

> Full reference: [DEPLOYMENT.md](DEPLOYMENT.md)

## Prerequisites ✓

- [x] Code pushed to GitHub repository
- [x] Build passes locally (`npm run build` succeeds)
- [x] Vercel account linked to the GitHub repo
- [x] Railway service running the backend

## Steps to Deploy the Frontend (Vercel)

### 1. Import the Project (one-time)

1. Go to https://vercel.com/new and import `ai-driven-robo-book`
2. Set **Root Directory** to `website`
3. Framework preset (Docusaurus) and build settings come from
   `website/vercel.json` — no other changes needed

### 2. Add the Backend URL (one-time, required)

Vercel → Project → **Settings → Environment Variables**:

```bash
REACT_APP_API_URL=https://ai-driven-robo-book-production.up.railway.app
```

> Without this, the chatbot/auth/personalization features call
> `http://localhost:8000` and fail in production. Env var changes only apply to
> **new builds**, so redeploy after adding it.

### 3. Push to Main Branch

```bash
git add .
git commit -m "Deploy: frontend on Vercel"
git push origin main
```

Vercel deploys `main` to production automatically and every branch/PR to a
preview URL.

### 4. Access Your Site

🌐 **Your Live Site:**
```
https://ai-driven-robo-book.vercel.app
```

---

## Connect Frontend ↔ Backend

Two values must agree:

| Value | Where | Set to |
| --- | --- | --- |
| `REACT_APP_API_URL` | Vercel env var | `https://ai-driven-robo-book-production.up.railway.app` |
| `ALLOWED_ORIGINS` | Railway env var | `https://ai-driven-robo-book.vercel.app,http://localhost:3000` |

Verify CORS end-to-end:

```bash
curl -i -X OPTIONS \
  -H "Origin: https://ai-driven-robo-book.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  https://ai-driven-robo-book-production.up.railway.app/api/rag/query
# Look for: access-control-allow-origin: https://ai-driven-robo-book.vercel.app
```

---

## Verify Deployment

```bash
# Frontend loads
open https://ai-driven-robo-book.vercel.app

# Backend healthy
curl https://ai-driven-robo-book-production.up.railway.app/health
```

Expected:
- ✅ Site loads without errors
- ✅ Chatbot returns answers (no CORS / localhost errors in the console)
- ✅ Backend `/health` returns `healthy` or `degraded`

---

## Common Issues & Quick Fixes

### ❌ Chatbot/auth hit `localhost:8000` in production
`REACT_APP_API_URL` wasn't set at build time. Add it in Vercel and **redeploy**.

### ❌ CORS errors in the browser console
Add the Vercel domain to `ALLOWED_ORIGINS` in Railway and redeploy the backend.

### ❌ 404 / broken routing on Vercel
Confirm Vercel **Root Directory** = `website` and `baseUrl: '/'` in
`website/docusaurus.config.js`.

### ❌ Build fails on Vercel
Reproduce locally:
```bash
cd website
npm ci
REACT_APP_API_URL=https://ai-driven-robo-book-production.up.railway.app npm run build
```

---

## Update Content After Deployment

1. Edit MDX files in `website/docs/`
2. Test locally (`npm start`, then `npm run build`)
3. Push to GitHub — Vercel redeploys automatically:
   ```bash
   git add .
   git commit -m "Update: <description>"
   git push origin main
   ```

---

## Support

**Full Documentation:** See [DEPLOYMENT.md](DEPLOYMENT.md)

**Issues:** https://github.com/NailaYaqoob/ai-driven-robo-book/issues

---

**Ready to Deploy?** Push to `main` — Vercel (frontend) and Railway (backend)
handle the rest! 🚀
