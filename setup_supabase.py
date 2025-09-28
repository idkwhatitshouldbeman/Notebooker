#!/usr/bin/env py
"""
Supabase Setup Script for Notebooker
This script helps you configure Supabase connection
"""

import os
import sys
from pathlib import Path

def main():
    print("🚀 Notebooker Supabase Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Please run this script from the Notebooker root directory")
        sys.exit(1)
    
    print("\n📋 Step 1: Get Your Supabase Credentials")
    print("-" * 40)
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to Settings → General")
    print("4. Copy your 'Reference ID'")
    print("5. Go to Settings → API")
    print("6. Copy your 'service_role' key (NOT the anon key)")
    
    print("\n🔧 Step 2: Update Environment Variables")
    print("-" * 40)
    
    # Get user input
    supabase_url = input("\nEnter your Supabase URL (https://[project-ref].supabase.co): ").strip()
    supabase_key = input("Enter your Supabase Service Role Key: ").strip()
    
    if not supabase_url or not supabase_key:
        print("❌ Both URL and Key are required!")
        sys.exit(1)
    
    # Create .env file
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# API Configuration
API_KEY=notebooker-api-key-2024
SECRET_KEY=your-secret-key-change-in-production

# AI Service Configuration
AI_SERVICE_URL=https://your-ai-service.onrender.com

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
PORT=5002
"""
    
    # Write to backend/.env
    backend_env_path = Path("backend/.env")
    with open(backend_env_path, "w") as f:
        f.write(env_content)
    
    print(f"\n✅ Environment file created: {backend_env_path}")
    
    print("\n🚀 Step 3: Deploy to Render")
    print("-" * 40)
    print("1. Go to: https://dashboard.render.com")
    print("2. Find your service: ntbk-ai-flask-api")
    print("3. Go to Environment tab")
    print("4. Update these variables:")
    print(f"   SUPABASE_URL = {supabase_url}")
    print(f"   SUPABASE_KEY = {supabase_key}")
    print("5. Click 'Save Changes'")
    print("6. Redeploy the service")
    
    print("\n🧪 Step 4: Test Connection")
    print("-" * 40)
    print("1. Check Render logs for: 'Supabase PostgreSQL connection successful'")
    print("2. If you see errors, double-check your credentials")
    
    print("\n✨ Setup Complete!")
    print("Your Notebooker backend will now use Supabase as the database.")

if __name__ == "__main__":
    main()
