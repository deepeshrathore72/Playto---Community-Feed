# Deployment Checklist

## Pre-Deployment Tasks

### 1. Code Preparation
- [ ] All changes committed to git
- [ ] Code pushed to GitHub repository
- [ ] Latest changes merged to main branch

### 2. Environment Files Ready
- [ ] Backend: Review `.env.example` for required variables
- [ ] Frontend: Review `.env.example` for required variables

## Backend Deployment (Render)

### 1. Create PostgreSQL Database
- [ ] Sign up/login to [Render](https://render.com)
- [ ] Create new PostgreSQL database
- [ ] Name: `community-feed-db`
- [ ] Save the Internal Database URL

### 2. Deploy Web Service
- [ ] Create new Web Service
- [ ] Connect GitHub repository
- [ ] Root Directory: `backend`
- [ ] Build Command: `./build.sh`
- [ ] Start Command: `gunicorn config.wsgi:application`

### 3. Configure Environment Variables
- [ ] SECRET_KEY (generate new)
- [ ] DEBUG=False
- [ ] PYTHON_VERSION=3.11.0
- [ ] DATABASE_URL (from PostgreSQL service)
- [ ] ALLOWED_HOSTS (will be: your-app-name.onrender.com)
- [ ] CORS_ALLOWED_ORIGINS (update after frontend deployment)

### 4. Verify Backend
- [ ] Build completes successfully
- [ ] Service is live at https://your-app-name.onrender.com
- [ ] Test API endpoint: https://your-app-name.onrender.com/api/users/

### 5. Seed Data (Optional)
- [ ] Run: `python manage.py seed_data` in Render Shell

## Frontend Deployment (Vercel)

### 1. Deploy to Vercel
- [ ] Sign up/login to [Vercel](https://vercel.com)
- [ ] Import GitHub repository
- [ ] Root Directory: `frontend`
- [ ] Framework: Vite (auto-detected)

### 2. Configure Environment Variables
- [ ] VITE_API_URL=https://your-app-name.onrender.com/api

### 3. Deploy
- [ ] Click Deploy and wait
- [ ] Note your Vercel URL: https://your-project.vercel.app

## Post-Deployment

### 1. Update Backend CORS
- [ ] Go back to Render service
- [ ] Update CORS_ALLOWED_ORIGINS with Vercel URL
- [ ] Save and redeploy

### 2. Test Full Stack
- [ ] Visit Vercel frontend URL
- [ ] Create a test user
- [ ] Create a test post
- [ ] Add a comment
- [ ] Toggle likes
- [ ] Check leaderboard

### 3. Monitor
- [ ] Check Render logs for errors
- [ ] Check Vercel deployment logs
- [ ] Monitor performance

## URLs to Save

- Backend URL: `https://_____.onrender.com`
- Frontend URL: `https://_____.vercel.app`
- Database: (Render PostgreSQL dashboard)

## Quick Commands

### Update deployment after code changes:
```bash
git add .
git commit -m "Your commit message"
git push
```
Both Render and Vercel will auto-deploy!

### Run migrations on Render:
```bash
# In Render Shell
python manage.py migrate
```

### View logs:
- Render: Service Dashboard → Logs tab
- Vercel: Project → Deployments → Click deployment → Logs

## Troubleshooting Quick Fixes

### Backend not connecting:
1. Check DATABASE_URL is correct
2. Verify all environment variables are set
3. Check Render logs for errors

### CORS errors:
1. Verify CORS_ALLOWED_ORIGINS includes Vercel URL (with https://)
2. No trailing slashes in URLs
3. Redeploy after updating

### Frontend not loading:
1. Check VITE_API_URL is correct
2. Verify it includes `/api` at the end
3. Check browser console for errors

### 404 errors on frontend routes:
- Should be fixed by vercel.json (already created)
- Redeploy if needed
