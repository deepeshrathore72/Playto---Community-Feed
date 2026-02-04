# Deployment Guide

This guide will help you deploy the Community Feed application with the backend on Render and the frontend on Vercel.

## Prerequisites

- GitHub account
- Render account (sign up at [render.com](https://render.com))
- Vercel account (sign up at [vercel.com](https://vercel.com))
- Your code pushed to a GitHub repository

## Part 1: Deploy Backend to Render

### Step 1: Create a PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **PostgreSQL**
3. Configure the database:
   - **Name**: `community-feed-db`
   - **Database**: `community_feed`
   - **User**: `community_feed_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free tier is fine for testing
4. Click **Create Database**
5. Wait for the database to be created (takes ~1-2 minutes)
6. **Save the Internal Database URL** (you'll need this)

### Step 2: Deploy Django Backend

1. From Render Dashboard, click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure the web service:
   - **Name**: `community-feed-backend`
   - **Region**: Same as your database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`
   - **Plan**: Free tier is fine for testing

4. Add Environment Variables (click **Advanced** → **Add Environment Variable**):
   ```
   SECRET_KEY = [Click "Generate" to auto-generate]
   DEBUG = False
   PYTHON_VERSION = 3.11.0
   DATABASE_URL = [Paste the Internal Database URL from Step 1]
   ALLOWED_HOSTS = your-app-name.onrender.com
   CORS_ALLOWED_ORIGINS = https://your-vercel-app.vercel.app
   ```
   
   **Note**: You'll update `CORS_ALLOWED_ORIGINS` after deploying the frontend.

5. Click **Create Web Service**

6. Wait for deployment to complete (5-10 minutes for first deployment)

7. Once deployed, your backend will be available at: `https://your-app-name.onrender.com`

### Step 3: Seed Initial Data (Optional)

After the backend is deployed, you can seed initial data:

1. From your Render service page, go to **Shell** tab
2. Run the seed command:
   ```bash
   python manage.py seed_data
   ```

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Environment Variable File

1. In your frontend directory, create `.env.production` file:
   ```
   VITE_API_URL=https://your-app-name.onrender.com/api
   ```
   Replace `your-app-name` with your actual Render service name.

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

3. Login to Vercel:
   ```bash
   vercel login
   ```

4. Deploy:
   ```bash
   vercel
   ```
   - Select your scope (team/personal)
   - Link to existing project or create new
   - Confirm the settings
   - Wait for deployment

5. For production deployment:
   ```bash
   vercel --prod
   ```

#### Option B: Using Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

5. Add Environment Variables:
   ```
   VITE_API_URL = https://your-app-name.onrender.com/api
   ```

6. Click **Deploy**

7. Wait for deployment to complete (~2-3 minutes)

8. Your frontend will be available at: `https://your-project.vercel.app`

### Step 3: Update Backend CORS Settings

1. Go back to your Render service
2. Update the `CORS_ALLOWED_ORIGINS` environment variable:
   ```
   https://your-project.vercel.app
   ```

3. Click **Save Changes**
4. The service will automatically redeploy

## Verification

1. Visit your Vercel frontend URL
2. The app should load and connect to the backend
3. Try creating a user, post, and comment to verify everything works

## Common Issues and Solutions

### Backend Issues

**Issue**: Build fails with "Permission denied: './build.sh'"
- **Solution**: Make the build script executable:
  ```bash
  git update-index --chmod=+x backend/build.sh
  git commit -m "Make build.sh executable"
  git push
  ```

**Issue**: Static files not loading
- **Solution**: Ensure `whitenoise` is in requirements.txt and `STATIC_ROOT` is configured

**Issue**: Database connection errors
- **Solution**: Verify `DATABASE_URL` is correctly set and database is running

### Frontend Issues

**Issue**: API calls fail with CORS errors
- **Solution**: 
  - Verify `CORS_ALLOWED_ORIGINS` includes your Vercel URL
  - Check that `VITE_API_URL` is correctly set
  - Ensure no trailing slashes in URLs

**Issue**: Environment variables not working
- **Solution**: 
  - In Vercel, environment variables must be prefixed with `VITE_`
  - Redeploy after adding environment variables
  - Check browser console for the actual API URL being used

**Issue**: 404 on refresh
- **Solution**: The `vercel.json` file handles this by rewriting all routes to index.html

## Environment Variables Summary

### Backend (Render)
```
SECRET_KEY=[Generated]
DEBUG=False
PYTHON_VERSION=3.11.0
DATABASE_URL=[From Render PostgreSQL]
ALLOWED_HOSTS=your-app-name.onrender.com
CORS_ALLOWED_ORIGINS=https://your-project.vercel.app
```

### Frontend (Vercel)
```
VITE_API_URL=https://your-app-name.onrender.com/api
```

## Post-Deployment

### Monitor Your Application

- **Render**: Check logs in the service's Logs tab
- **Vercel**: Check deployment logs and runtime logs in the Deployments tab

### Enable Auto-Deploy

Both platforms automatically deploy when you push to your repository:
- **Render**: Auto-deploys on push to configured branch
- **Vercel**: Auto-deploys on push to any branch (production on main)

### Custom Domains (Optional)

Both Render and Vercel support custom domains:
- **Render**: Go to Settings → Custom Domain
- **Vercel**: Go to Project Settings → Domains

## Database Migrations

When you make model changes:

1. Update your models locally
2. Create migrations: `python manage.py makemigrations`
3. Commit and push to GitHub
4. Render will automatically run migrations during deployment (via build.sh)

Alternatively, run migrations manually in Render Shell:
```bash
python manage.py migrate
```

## Scaling

### Free Tier Limitations
- **Render**: Spins down after 15 minutes of inactivity (first request may be slow)
- **Vercel**: Generous free tier for hobby projects

### Upgrading
- Consider upgrading Render plans for always-on services
- Vercel's free tier is usually sufficient for most projects

## Support

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/

## Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` generated
- ✅ Database credentials secured
- ✅ CORS properly configured
- ✅ ALLOWED_HOSTS restricted
- ✅ HTTPS enabled (automatic on both platforms)
- ✅ Environment variables not committed to git
