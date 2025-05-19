# Crop Recommendation System

A Flask-based web application that provides crop recommendations based on various parameters like soil conditions, weather, and market demand.

## Features

- User authentication and authorization
- Dynamic crop recommendations based on multiple parameters
- Weather integration
- Premium report generation
- Consultation booking system
- IoT data integration
- Testimonials system

## Deployment Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd CropRecommendationProject
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with:
```
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key
OPENWEATHER_API_KEY=your-api-key
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
gunicorn app:app
```

## Development

For development, run:
```bash
flask run
```

## Required Files

- `app.py`: Main application file
- `crop_model.pkl`: Trained ML model
- `encoder.pkl`: Label encoder
- `crops_info.json`: Crop information
- `indian_regions.py`: Regional data
- `requirements.txt`: Python dependencies

## Environment Variables

- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key
- `OPENWEATHER_API_KEY`: OpenWeather API key

## Dependencies

See `requirements.txt` for complete list of dependencies.

## License

This project is licensed under the MIT License. 