#!/usr/bin/env python3
"""
Simple backup script for Notebooker
Creates a backup and pushes to GitHub
"""

import subprocess
import sys
from datetime import datetime

def run_command(command):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_backup():
    """Create a backup commit and push to GitHub"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Creating backup at {timestamp}")
    
    # Add all changes
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"Error adding files: {stderr}")
        return False
    
    # Commit changes
    commit_message = f"Backup: {timestamp}"
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        if "nothing to commit" in stderr:
            print("No changes to backup")
            return True
        print(f"Error committing: {stderr}")
        return False
    
    # Push to GitHub
    success, stdout, stderr = run_command("git push origin main")
    if not success:
        print(f"Error pushing to GitHub: {stderr}")
        return False
    
    print("✓ Backup completed successfully")
    return True

def main():
    """Main backup function"""
    print("Notebooker Backup Script")
    print("=" * 30)
    
    success = create_backup()
    
    if success:
        print("Backup completed successfully!")
    else:
        print("Backup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
