#!/usr/bin/env python3
"""
Script to install dependencies and run the server
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install project dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("Warning: .env file not found!")
        print("Please create a .env file with:")
        print("GROQ_API_KEY=your_groq_api_key_here")
        print("GOOGLE_API_KEY=your_google_api_key_here")
        return False
    return True

def run_server():
    """Run the FastAPI server"""
    print("Starting server...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running server: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped by user")

def main():
    """Main function"""
    print("Developer Guidance System - Server Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Check environment file
    check_env_file()
    
    # Run server
    run_server()

if __name__ == "__main__":
    main()
