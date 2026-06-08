# 🚀 CareSync - Deployment Guide

## Option 1: Deploy on Render.com (FREE - Recommended, No Credit Card)

### Step 1: Install Git
1. Download Git from https://git-scm.com/download/win
2. Install with default settings
3. Restart VS Code / Terminal after installation

### Step 2: Create a GitHub Account
1. Go to https://github.com and Sign Up (free)
2. Verify your email

### Step 3: Push Project to GitHub
Open PowerShell in your project folder and run:

```powershell
# Initialize git repo
git init
git add .
git commit -m "Initial commit - CareSync Hospital Management System"

# Create new GitHub repository first at https://github.com/new
# Then run (replace YOUR_USERNAME):
git remote add origin https://github.com/YOUR_USERNAME/caresync-hospital.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy on Render.com
1. Go to https://render.com and Sign Up (free)
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"** → Select your GitHub repo
4. Fill in settings:
   - **Name**: `caresync-hospital`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click **"Create Web Service"**
6. ✅ Your app will be live at: `https://caresync-hospital.onrender.com`

> ⚠️ **Free tier note**: App may sleep after 15 min inactivity. First load takes ~30 seconds.

---

## Option 2: Deploy on PythonAnywhere (EASIEST - No Git Required)

### Step 1: Create Account
1. Go to https://www.pythonanywhere.com and Sign Up (free)
2. Verify email

### Step 2: Upload Project Files
1. Go to **Files** tab
2. Create folder: `/home/yourusername/caresync/`
3. Upload all project files:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - Folder: `templates/` (with `index.html`)

### Step 3: Install Dependencies
1. Go to **Consoles** tab → **Bash**
2. Run:
```bash
cd ~/caresync
pip3.10 install --user -r requirements.txt
```

### Step 4: Create Web App
1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose: **Flask** → **Python 3.10**
4. Set Source code: `/home/yourusername/caresync`
5. Set WSGI file path → Edit it to:
```python
import sys
sys.path.insert(0, '/home/yourusername/caresync')
from app import app as application
```
6. Click **Reload**
7. ✅ Your app is live at: `yourusername.pythonanywhere.com`

---

## Option 3: Share Locally via ngrok (Instant - No Deployment)

### For testing with others on same network or internet temporarily:

1. Download ngrok: https://ngrok.com/download
2. Sign up at https://ngrok.com (free)
3. Get your auth token from dashboard
4. Open PowerShell and run:
```powershell
# Authenticate ngrok
ngrok authtoken YOUR_AUTH_TOKEN

# Start tunnel (while your app is running on port 5000)
ngrok http 5000
```
5. ✅ Share the `https://xxxxx.ngrok.io` URL - works from any device on internet!

---

## 🔑 Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Doctor | `sarah.jenkins@hospital.com` | `doctor123` |
| Patient | `john.doe@email.com` | `patient123` |
| Patient | OP Number: `OP-2026-0001` | `patient123` |

---

## 📋 What's Already Ready for Deployment

- ✅ `Procfile` - Gunicorn production server config
- ✅ `render.yaml` - Render.com auto-config
- ✅ `requirements.txt` - All dependencies listed
- ✅ `.gitignore` - Sensitive files excluded
- ✅ SQLite database (auto-created on first run)
- ✅ Sample data auto-loaded on startup
- ✅ Environment variable support (`SECRET_KEY`, `DATABASE_URL`)
