"""
WSGI entry point for Render deployment
"""

import os
from pathlib import Path
from app import app, initialize_en_writer

# Create necessary directories
Path("en_files").mkdir(exist_ok=True)
Path("backups").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)

# Initialize EN Writer
initialize_en_writer()

# This is the WSGI application that Render will use
application = app

if __name__ == "__main__":
    # Get port from environment variable (for Render)
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=False, host='0.0.0.0', port=port)
