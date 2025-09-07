# 🚀 Render Deployment Setup

## 📋 **Quick Setup Steps**

### **Step 1: Create PostgreSQL Database**
1. Go to [render.com](https://render.com) and sign up
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `notebooker-db`
   - **Database**: `notebooker`
   - **User**: `notebooker_user`
   - **Plan**: **Free** (1GB storage)
4. Click **"Create Database"**
5. **Copy the External Database URL** (you'll need this)

### **Step 2: Deploy Web Service**
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `idkwhatitshouldbeman/Notebooker`
3. Configure:
   - **Name**: `notebooker`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:application`
   - **Plan**: **Free**

### **Step 3: Add Environment Variables**
In your web service settings, add:
```
DATABASE_URL=<your_postgresql_url_from_step_1>
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

### **Step 4: Deploy**
Click **"Create Web Service"** and wait for deployment!

## 🎯 **What You Get**

### **Free Tier Limits:**
- ✅ **1GB PostgreSQL database** (thousands of users)
- ✅ **750 hours/month** web service
- ✅ **Automatic SSL** certificate
- ✅ **Custom domain** support

### **User Data Persistence:**
- 🔄 **Page refresh** → Data stays
- 💻 **Different devices** → Data follows you
- ⏰ **Days/weeks later** → Data persists
- 🔐 **Secure login** → Only you see your data

## 📊 **Storage Breakdown**

### **1GB Database Can Store:**
- **~10,000 users** (basic info)
- **~50,000 EN files** (average 20KB each)
- **~100,000 planning sections**
- **~1,000,000 LLM interactions**

### **If You Need More Space:**
- **Supabase**: +500MB free
- **Railway**: +1GB free
- **PlanetScale**: +1GB free
- **Total**: **3.5GB free** across services!

## 🔧 **Database URL Format**
Render provides a URL like:
```
postgresql://username:password@hostname:port/database
```

## 🚀 **Deployment Commands**

### **Deploy to GitHub:**
```powershell
python deploy.py
```

### **Render automatically:**
1. Pulls from GitHub
2. Installs dependencies
3. Connects to PostgreSQL
4. Starts your app
5. Handles SSL

## 🌐 **Your Live URLs**

After deployment:
- **Website**: `https://notebooker.onrender.com`
- **Database**: Managed by Render
- **GitHub**: `https://github.com/idkwhatitshouldbeman/Notebooker.git`

## 💡 **Pro Tips**

1. **Free Tier**: App spins down after 15 minutes of inactivity (first load takes ~30 seconds)
2. **Database Backups**: Render automatically backs up your PostgreSQL
3. **Custom Domain**: Add your own domain later
4. **Scaling**: Easy to upgrade to paid plans

## 🆘 **Troubleshooting**

### **Database Connection Issues:**
- Check `DATABASE_URL` environment variable
- Ensure PostgreSQL service is running
- Verify connection string format

### **Build Failures:**
- Check `requirements.txt` for all dependencies
- Ensure Python version compatibility
- Check build logs in Render dashboard

### **App Not Starting:**
- Verify `wsgi.py` exists
- Check start command: `gunicorn wsgi:application`
- Review application logs

## 🎉 **Result**

Your Notebooker will be a **real web application** with:
- ✅ **Persistent user data**
- ✅ **Professional hosting**
- ✅ **Automatic backups**
- ✅ **SSL security**
- ✅ **Custom domain ready**

**Total cost: $0/month** (free tier) 🎉
