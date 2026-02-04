# Quick Deployment Reference

## 🎯 Step-by-Step Deployment

### 1️⃣ Push to GitHub (DONE ✓)
Your code is ready with all deployment configs!

### 2️⃣ Deploy Backend on Render

**A. Create Database**
- Go to: https://dashboard.render.com
- Click: New + → PostgreSQL
- Name: `community-feed-db`
- Copy the **Internal Database URL**

**B. Create Web Service**
- Click: New + → Web Service
- Connect your GitHub repo
- Settings:
  ```
  Name: community-feed-backend
  Root Directory: backend
  Build Command: ./build.sh
  Start Command: gunicorn config.wsgi:application
  ```

**C. Environment Variables**
```
SECRET_KEY → Click "Generate"
DEBUG → False
PYTHON_VERSION → 3.11.0
DATABASE_URL → [Paste from step A]
ALLOWED_HOSTS → your-service-name.onrender.com
CORS_ALLOWED_ORIGINS → https://your-app.vercel.app (update later)
```

**D. Deploy & Copy URL**
- Click "Create Web Service"
- Wait ~5-10 min
- Copy URL: `https://your-service-name.onrender.com`

### 3️⃣ Deploy Frontend on Vercel

**A. Import Project**
- Go to: https://vercel.com/dashboard
- Click: Add New → Project
- Import your GitHub repo

**B. Configure**
```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build (auto)
Output Directory: dist (auto)
```

**C. Environment Variable**
```
VITE_API_URL → https://your-service-name.onrender.com/api
```
(Use the URL from step 2D, add `/api` at the end)

**D. Deploy & Copy URL**
- Click "Deploy"
- Wait ~2-3 min
- Copy URL: `https://your-app.vercel.app`

### 4️⃣ Update Backend CORS

- Go back to Render → Your service → Environment
- Update `CORS_ALLOWED_ORIGINS` to your Vercel URL
- Click "Save Changes" (auto redeploys)

### 5️⃣ Test! 🎉

Visit your Vercel URL and enjoy your deployed app!

---

## 🔧 Environment Variables Reference

### Backend (Render)
| Variable | Value |
|----------|-------|
| SECRET_KEY | Generate in Render |
| DEBUG | False |
| PYTHON_VERSION | 3.11.0 |
| DATABASE_URL | From Render PostgreSQL |
| ALLOWED_HOSTS | your-app.onrender.com |
| CORS_ALLOWED_ORIGINS | https://your-app.vercel.app |

### Frontend (Vercel)
| Variable | Value |
|----------|-------|
| VITE_API_URL | https://your-app.onrender.com/api |

---

## ⚡ Common Issues

### "Permission denied: build.sh"
Already fixed! The file is executable.

### CORS errors
Make sure `CORS_ALLOWED_ORIGINS` has:
- `https://` prefix
- Your actual Vercel URL
- No trailing slash

### API not connecting
Check `VITE_API_URL` has `/api` at the end

### Database errors
Verify `DATABASE_URL` is the **Internal** database URL from Render

---

## 🚀 After Deployment

**Seed Data (Optional)**
- Go to Render → Your service → Shell
- Run: `python manage.py seed_data`

**Auto-Deploy**
- Push to GitHub → Both services auto-deploy!
- Monitor: Check logs in Render/Vercel dashboards

**Custom Domains**
- Render: Settings → Custom Domain
- Vercel: Project Settings → Domains

---

## 📱 Your Deployed URLs

```
Backend:  https://_____________.onrender.com
Frontend: https://_____________.vercel.app
Database: [Render PostgreSQL Dashboard]
```

Fill these in after deployment!
