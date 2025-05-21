import os
import shutil
import subprocess
import sys

def create_deployment_package():
    """Create a deployment package with necessary files."""
    # Files to include
    required_files = [
        'app.py',
        'wsgi.py',
        'requirements.txt',
        'crop_model.pkl',
        'encoder.pkl',
        'crops_info.json',
        'indian_regions.py',
        'Procfile',
        'runtime.txt',
        '.env'
    ]
    
    # Create deployment directory
    if os.path.exists('deployment'):
        shutil.rmtree('deployment')
    os.makedirs('deployment')
    
    # Copy required files
    for file in required_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join('deployment', file))
    
    # Copy templates and static directories
    if os.path.exists('templates'):
        shutil.copytree('templates', os.path.join('deployment', 'templates'))
    if os.path.exists('static'):
        shutil.copytree('static', os.path.join('deployment', 'static'))
    
    print("Deployment package created successfully!")

def setup_virtual_environment():
    """Set up virtual environment and install dependencies."""
    try:
        # Create virtual environment
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Activate virtual environment and install requirements
        if os.name == 'nt':  # Windows
            pip_path = os.path.join('venv', 'Scripts', 'pip')
        else:  # Unix/Linux
            pip_path = os.path.join('venv', 'bin', 'pip')
        
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        
        print("Virtual environment set up successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up virtual environment: {e}")
        sys.exit(1)

def main():
    """Main deployment function."""
    print("Starting deployment process...")
    
    # Create deployment package
    create_deployment_package()
    
    # Set up virtual environment
    setup_virtual_environment()
    
    print("\nDeployment package is ready!")
    print("\nNext steps:")
    print("1. Upload the contents of the 'deployment' directory to your hosting platform")
    print("2. Set up the environment variables on your hosting platform")
    print("3. Configure the WSGI application to use wsgi.py")
    print("4. Start the application")

if __name__ == '__main__':
    main() 