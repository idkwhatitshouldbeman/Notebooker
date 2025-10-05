#!/usr/bin/env python3
"""
Deployment script to apply CORS fixes and test the API
"""

import os
import sys
import subprocess
import time

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_cors
        print("✅ Flask and Flask-CORS are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_server():
    """Start the Flask development server"""
    print("🚀 Starting Flask development server...")
    
    # Set environment variables
    env = os.environ.copy()
    env['FLASK_APP'] = 'app.py'
    env['FLASK_ENV'] = 'development'
    env['DEBUG'] = 'True'
    env['PORT'] = '5002'
    
    try:
        # Start the server in the background
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("⏳ Waiting for server to start...")
        time.sleep(3)  # Give server time to start
        
        # Check if server is running
        import requests
        try:
            response = requests.get("http://localhost:5002/", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                return process
            else:
                print(f"⚠️  Server responded with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return None

def run_tests():
    """Run the CORS test script"""
    print("\n🧪 Running CORS tests...")
    try:
        result = subprocess.run([sys.executable, 'test_cors_fix.py'], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🔧 Notebooker CORS Fix Deployment")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start server")
        sys.exit(1)
    
    try:
        # Run tests
        tests_passed = run_tests()
        
        if tests_passed:
            print("\n🎉 Deployment successful! CORS issues should be fixed.")
            print("\n📋 Next steps:")
            print("1. Deploy the updated code to Render")
            print("2. Update environment variables in Render dashboard")
            print("3. Test the live deployment")
        else:
            print("\n⚠️  Some tests failed. Check the logs above.")
            
    finally:
        # Clean up
        if server_process:
            print("\n🛑 Stopping development server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
