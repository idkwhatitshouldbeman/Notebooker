#!/usr/bin/env python3
"""
Render-optimized startup script for Notebooker
"""

import os
import sys
from pathlib import Path

def setup_directories():
    """Create necessary directories"""
    directories = ['en_files', 'images', 'backups', 'static', 'templates']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_environment():
    """Check if running on Render"""
    if os.environ.get('RENDER'):
        print("🚀 Running on Render platform")
        return True
    else:
        print("💻 Running locally")
        return False

def main():
    """Main startup function"""
    print("Notebooker - Agentic Engineering Notebook Writer")
    print("=" * 50)
    
    # Check environment
    is_render = check_environment()
    
    # Setup directories
    print("\nSetting up directories...")
    setup_directories()
    
    # Import and run the app
    try:
        from app import app, initialize_en_writer
        
        # Initialize EN Writer
        print("\nInitializing EN Writer...")
        initialize_en_writer()
        
        # Get port from environment
        port = int(os.environ.get('PORT', 5000))
        
        print(f"\n🌐 Starting server on port {port}")
        print("=" * 50)
        
        # Run the app
        app.run(debug=False, host='0.0.0.0', port=port)
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
