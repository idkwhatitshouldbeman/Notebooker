# 🚀 Supabase Setup for Notebooker

## 🔐 **Secure Configuration**

### **Step 1: Create Environment File**
1. Copy `env_template.txt` to `.env`
2. Fill in your Supabase credentials:

```bash
# Copy the template
cp env_template.txt .env

# Edit .env with your actual values
SUPABASE_URL=https://kqwwwmhuczwksraysvpp.supabase.co
SUPABASE_KEY=snJrAKpW4jqAuzUa
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
OPENROUTER_API_KEY=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
```

### **Step 2: Test Supabase Connection**
```powershell
python supabase_config.py
```

## 🎯 **What You Get**

### **Supabase Free Tier:**
- ✅ **500MB PostgreSQL database**
- ✅ **50,000 monthly active users**
- ✅ **Automatic backups**
- ✅ **Real-time subscriptions**
- ✅ **Built-in authentication**

### **Storage Capacity:**
- **500MB = ~25,000 users + 100,000 EN files**
- **Perfect for text-based content**
- **Will last a very long time**

## 🔒 **Security Features**

### **Environment Variables:**
- ✅ **Keys stored securely** in `.env` file
- ✅ **Never committed to git**
- ✅ **Different keys for dev/prod**

### **Database Security:**
- ✅ **SSL encrypted connections**
- ✅ **Row-level security** (if needed)
- ✅ **Automatic backups**

## 🚀 **Deployment**

### **Local Development:**
```powershell
# Set up environment
cp env_template.txt .env
# Edit .env with your keys

# Start the app
python app.py
```

### **Cloud Deployment (Render):**
1. Add environment variables in Render dashboard:
   ```
   SUPABASE_URL=https://kqwwwmhuczwksraysvpp.supabase.co
   SUPABASE_KEY=snJrAKpW4jqAuzUa
   SECRET_KEY=your_secret_key_here
   FLASK_ENV=production
   OPENROUTER_API_KEY=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
   ```

2. Deploy to GitHub:
   ```powershell
   python deploy.py
   ```

## 📊 **Database Schema**

### **Tables Created:**
- **`users`** - User accounts and preferences
- **`en_files`** - Engineering notebook files
- **`planning_sheets`** - Planning sections and decisions
- **`images`** - Image metadata and captions
- **`llm_interactions`** - AI interaction logs

### **Data Types:**
- **Text content** - Stored efficiently
- **JSON fields** - For tags, preferences, metadata
- **Timestamps** - Automatic creation/update tracking

## 🔧 **Features**

### **User Management:**
- ✅ **Secure password hashing**
- ✅ **Session management**
- ✅ **User preferences**

### **Data Persistence:**
- 🔄 **Page refresh** → Data stays
- 💻 **Different devices** → Data follows you
- ⏰ **Days/weeks later** → Data persists
- 🔐 **Secure login** → Only you see your data

### **LLM Integration:**
- ✅ **OpenRouter API** with 6 free models
- ✅ **Interaction logging**
- ✅ **Cost tracking**

## 🆘 **Troubleshooting**

### **Connection Issues:**
- Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Ensure Supabase project is active
- Verify network connectivity

### **Authentication Errors:**
- Check API key permissions
- Verify project URL format
- Ensure database is accessible

### **Table Creation Issues:**
- Check database permissions
- Verify PostgreSQL connection
- Review error logs

## 🎉 **Result**

Your Notebooker now has:
- ✅ **Secure Supabase database**
- ✅ **Persistent user data**
- ✅ **Professional hosting ready**
- ✅ **500MB free storage**
- ✅ **Automatic backups**

**Total cost: $0/month** (free tier) 🎉
