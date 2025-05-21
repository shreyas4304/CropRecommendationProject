import os
import shutil

def create_package():
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
        'runtime.txt'
    ]
    
    # Create deployment directory
    if os.path.exists('deployment'):
        shutil.rmtree('deployment')
    os.makedirs('deployment')
    
    # Copy required files
    for file in required_files:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join('deployment', file))
            print(f"Copied {file}")
    
    # Copy templates and static directories
    if os.path.exists('templates'):
        shutil.copytree('templates', os.path.join('deployment', 'templates'))
        print("Copied templates directory")
    if os.path.exists('static'):
        shutil.copytree('static', os.path.join('deployment', 'static'))
        print("Copied static directory")
    
    print("\nDeployment package created successfully!")
    print("\nNext steps:")
    print("1. Go to https://www.pythonanywhere.com/ and create a free account")
    print("2. Upload the contents of the 'deployment' directory to your PythonAnywhere account")
    print("3. In PythonAnywhere dashboard:")
    print("   - Go to Web tab")
    print("   - Click 'Add a new web app'")
    print("   - Choose 'Manual configuration'")
    print("   - Choose Python 3.9")
    print("   - Set the path to your virtual environment")
    print("   - Set the WSGI configuration file to wsgi.py")
    print("4. Set up environment variables in PythonAnywhere:")
    print("   - FLASK_APP=app.py")
    print("   - FLASK_ENV=production")
    print("   - SECRET_KEY=your-secret-key")
    print("   - OPENWEATHER_API_KEY=your-api-key")
    print("5. Reload your web app")

if __name__ == '__main__':
    create_package() 