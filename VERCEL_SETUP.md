# Vercel Environment Variable Setup

## Required Environment Variables

Your Vercel deployment needs to know where to find the backend API.

### Steps to Configure:

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click your project**: playto-community-feed-bice
3. **Go to Settings** → **Environment Variables**
4. **Add this variable**:

   **Key**: `VITE_API_URL`
   **Value**: `https://playto-community-feed-1z8f.onrender.com/api`
   
   **Environments**: Check all three boxes:
   - ✅ Production
   - ✅ Preview  
   - ✅ Development

5. **Click "Save"**

6. **Redeploy**:
   - Go to **Deployments** tab
   - Click the **...** menu on the latest deployment
   - Click **"Redeploy"**
   - Check **"Use existing build cache"** (optional)
   - Click **"Redeploy"**

---

## Render CORS Configuration

Your backend also needs to allow requests from Vercel.

### Steps:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click your service**: playto-community-feed-1z8f
3. **Go to Environment** tab
4. **Find or add** `CORS_ALLOWED_ORIGINS`
5. **Set value to**:
   ```
   https://playto-community-feed-bice.vercel.app
   ```
   (Remove the trailing slash if present)

6. **Also ensure** `DATABASE_URL` is set to:
   ```
   postgresql://neondb_owner:npg_E3stYzOh8PWx@ep-orange-frost-aiqf8f3g-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

7. **Click "Save Changes"** - Render will auto-redeploy

---

## Test After Both Redeploy (wait 3-5 minutes)

1. Visit: https://playto-community-feed-bice.vercel.app
2. Click the **Login** button
3. You should see 5 users: alice, bob, charlie, diana, eve

**If it still doesn't work, check:**
- Browser console for errors (F12 → Console tab)
- Network tab to see what URLs are being called
- Render logs for backend errors
