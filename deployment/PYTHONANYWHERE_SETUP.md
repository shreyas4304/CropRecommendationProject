# PythonAnywhere Deployment Guide

## 1. Initial Setup

1. Go to https://www.pythonanywhere.com/ and sign up for a free account
2. Once logged in, go to the "Files" tab
3. Create a new directory called `crop_recommendation`
4. Upload all files from the deployment folder to this directory

## 2. Web App Setup

1. Go to the "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.9
5. Note your web app URL (it will be something like `yourusername.pythonanywhere.com`)

## 3. Virtual Environment Setup

1. Go to the "Consoles" tab
2. Start a new Bash console
3. Run these commands:
```bash
cd crop_recommendation
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. WSGI Configuration

1. Go back to the "Web" tab
2. Click on the WSGI configuration file link
3. Replace the contents with:
```python
import sys
import os

# Add the project directory to Python path
path = '/home/yourusername/crop_recommendation'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['OPENWEATHER_API_KEY'] = '93b12c69b606a88b69162eb9e43e73f7'

# Import the Flask app
from app import app as application
```

## 5. Environment Variables

1. Go to the "Web" tab
2. Find the "Environment variables" section
3. Add these variables:
```
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
OPENWEATHER_API_KEY=93b12c69b606a88b69162eb9e43e73f7
```

## 6. Database Setup

1. Go to the "Consoles" tab
2. Start a new Bash console
3. Run these commands:
```bash
cd crop_recommendation
source venv/bin/activate
python3.9
```
4. In the Python console:
```python
from app import db
db.create_all()
exit()
```

## 7. Final Steps

1. Go back to the "Web" tab
2. Click the "Reload" button for your web app
3. Your application should now be live at your PythonAnywhere URL

## Troubleshooting

If you encounter any issues:

1. Check the error logs in the "Web" tab
2. Verify all files are uploaded correctly
3. Make sure the virtual environment is activated
4. Confirm all environment variables are set
5. Check the WSGI configuration file path

## Support

If you need help:
1. Check the PythonAnywhere documentation
2. Look at the error logs in the "Web" tab
3. Contact PythonAnywhere support 