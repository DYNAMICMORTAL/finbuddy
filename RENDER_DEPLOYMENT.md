# Deploy FinBuddy to Render.com

This guide will help you deploy your FinBuddy application to Render.com, which offers free hosting for web applications.

## 🌐 Why Render.com?

- **Free tier available** with good performance
- **Automatic deployments** from Git repositories
- **Built-in SSL/HTTPS** for all deployments
- **Environment variable management** through dashboard
- **Automatic builds** on every git push
- **Better than Heroku's free tier** (which was discontinued)

## 📋 Prerequisites

1. A GitHub account with your FinBuddy repository
2. A Render.com account (free signup at https://render.com)
3. Your API keys ready

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

1. **Ensure all files are committed to Git:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Your repository should have these files:**
   - ✅ `build.sh` - Build script for Render
   - ✅ `start.sh` - Start script for Render
   - ✅ `render.yaml` - Render configuration (optional)
   - ✅ `requirements.txt` - Python dependencies (with gunicorn)
   - ✅ `runtime.txt` - Python version specification
   - ✅ `Procfile` - Backup process configuration

### Step 2: Create New Web Service on Render

1. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Click "New +" → "Web Service"

2. **Connect Your Repository:**
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account if not already connected
   - Select your `finbuddy` repository

3. **Configure Web Service:**
   ```
   Name: finbuddy-app (or your preferred name)
   Environment: Python 3
   Build Command: chmod +x build.sh && ./build.sh
   Start Command: chmod +x start.sh && ./start.sh
   Plan: Free (or Starter if you need more resources)
   ```

### Step 3: Set Environment Variables

In the Render dashboard, add these environment variables:

**Required API Keys:**
```env
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
FINANCE_KEY=your_finance_api_key_here
```

**Flask Configuration:**
```env
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
PYTHONPATH=/opt/render/project/src
```

**Optional:**
```env
DATABASE_URL=your_database_url_here
FIREBASE_PROJECT_ID=your_firebase_project_id
```

### Step 4: Deploy

1. **Click "Create Web Service"**
2. **Render will automatically:**
   - Clone your repository
   - Run the build script (`build.sh`)
   - Install dependencies from `requirements.txt`
   - Start your application with the start script (`start.sh`)

3. **Monitor the deployment:**
   - Watch the build logs in real-time
   - First deployment takes 5-10 minutes
   - You'll get a live URL like `https://finbuddy-app.onrender.com`

## 🔧 Advanced Configuration

### Custom Domain (Paid Plans)
```yaml
# In render.yaml
services:
  - type: web
    name: finbuddy
    customDomains:
      - name: your-domain.com
        certificateId: your-cert-id
```

### Database Integration
For persistent data, consider adding a PostgreSQL database:

1. **Add PostgreSQL Service:**
   - In Render dashboard: "New +" → "PostgreSQL"
   - Get the database URL from the dashboard

2. **Update Environment Variables:**
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

3. **Update your Flask app configuration** to use the DATABASE_URL

### Auto-Deploy Setup
Render automatically deploys when you push to your main branch. To disable:
```yaml
# In render.yaml
services:
  - type: web
    autoDeploy: false
```

## 📊 Monitoring & Management

### Health Checks
Render automatically monitors your app health using the `/` endpoint.

### Logs
- View real-time logs in the Render dashboard
- Download logs for debugging

### Scaling (Paid Plans)
```yaml
# In render.yaml
services:
  - type: web
    scaling:
      minInstances: 1
      maxInstances: 3
```

## 🔍 Troubleshooting

### Common Issues:

1. **Build Fails:**
   ```bash
   # Check build.sh permissions
   chmod +x build.sh start.sh
   git add . && git commit -m "Fix permissions" && git push
   ```

2. **App Won't Start:**
   - Check environment variables are set correctly
   - Verify gunicorn is in requirements.txt
   - Check logs for error messages

3. **Database Errors:**
   - Ensure SQLite database files are created in writable directories
   - Consider upgrading to PostgreSQL for production

4. **API Timeout:**
   - Render free tier has 60-second request timeout
   - Optimize long-running API calls
   - Consider upgrading to paid plan for longer timeouts

### Debug Commands:
```bash
# Test locally with production settings
FLASK_ENV=production python app.py

# Test gunicorn locally
gunicorn --bind 0.0.0.0:8000 app:app
```

## 📝 Cost Considerations

### Free Tier Limits:
- 750 hours/month (enough for 1 always-on service)
- Services spin down after 15 minutes of inactivity
- Cold start time: ~30 seconds

### Paid Tier Benefits:
- No spin-down delays
- More memory and CPU
- Custom domains
- Priority support

## 🎯 Final Checklist

- ✅ Repository pushed to GitHub
- ✅ Environment variables configured in Render
- ✅ Build and start scripts are executable
- ✅ All API keys are valid and have sufficient quotas
- ✅ Database is properly initialized
- ✅ Health check endpoint (`/`) is working

## 🚀 Deploy Command Summary

```bash
# 1. Prepare and push your code
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. Go to Render dashboard and create web service
# 3. Connect repository and configure settings
# 4. Add environment variables
# 5. Deploy!
```

Your FinBuddy app will be live at: `https://your-service-name.onrender.com`

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [Render Python Guide](https://render.com/docs/deploy-flask)
- [Environment Variables on Render](https://render.com/docs/environment-variables)
- [Custom Domains on Render](https://render.com/docs/custom-domains)

---

**Note:** Remember to never commit your API keys to Git. Always use environment variables for sensitive configuration!
