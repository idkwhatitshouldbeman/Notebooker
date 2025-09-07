#!/usr/bin/env python3
"""
Notebooker Deployment Script
Automatically commits and pushes all changes to GitHub
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting Notebooker Deployment...")
    print("=" * 50)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Please run this from the project root.")
        return False
    
    # Get current timestamp for commit message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Step 1: Add all changes
    if not run_command("git add .", "Adding all changes"):
        return False
    
    # Step 2: Check if there are changes to commit
    result = subprocess.run("git diff --cached --quiet", shell=True, capture_output=True)
    if result.returncode == 0:
        print("ℹ️  No changes to commit. Repository is up to date.")
        return True
    
    # Step 3: Commit changes
    commit_message = f"Update Notebooker - {timestamp}"
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        return False
    
    # Step 4: Push to GitHub
    if not run_command("git push origin main", "Pushing to GitHub"):
        return False
    
    print("=" * 50)
    print("🎉 Deployment completed successfully!")
    print("📁 Repository: https://github.com/idkwhatitshouldbeman/Notebooker.git")
    print("🌐 Local server: http://localhost:5000")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
