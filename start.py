#!/usr/bin/env python3
"""
Notebooker Startup Script
Simple script to start the Notebooker system with proper setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'gpt4all', 'langchain', 'transformers', 
        'torch', 'pillow', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        'en_files',
        'images', 
        'backups',
        'static',
        'templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def start_backup_system():
    """Start the backup system in background"""
    try:
        import backup_system
        backup_manager = backup_system.BackupManager()
        
        # Create initial backup
        backup_path = backup_manager.create_backup("initial_backup")
        if backup_path:
            print(f"✓ Initial backup created: {backup_path}")
        
        return True
    except Exception as e:
        print(f"Warning: Could not start backup system: {e}")
        return False

def start_web_interface():
    """Start the Flask web interface"""
    try:
        print("\n" + "="*50)
        print("Starting Notebooker Web Interface")
        print("="*50)
        print("Open your browser to: http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\nShutting down Notebooker...")
        print("Thank you for using Notebooker!")
    except Exception as e:
        print(f"Error starting web interface: {e}")
        return False

def main():
    """Main startup function"""
    print("Notebooker - Agentic Engineering Notebook Writer")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and try again.")
        sys.exit(1)
    
    # Create directories
    print("\nSetting up directories...")
    create_directories()
    
    # Start backup system
    print("\nSetting up backup system...")
    start_backup_system()
    
    # Start web interface
    print("\nStarting web interface...")
    start_web_interface()

if __name__ == "__main__":
    main()
