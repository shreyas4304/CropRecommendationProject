# Crop Recommendation System

A comprehensive web application that helps farmers make informed decisions about crop selection based on various parameters including soil conditions, weather data, and market trends.

## Features

- Crop recommendation based on soil parameters and weather conditions
- Real-time weather data integration
- Support for both traditional and vertical farming
- Market analysis and demand forecasting
- Government scheme recommendations
- Seasonal crop calendar
- User testimonials and feedback system
- Premium reports with detailed analytics
- Expert consultation booking system

## Technology Stack

- Python 3.x
- Flask (Web Framework)
- SQLAlchemy (Database ORM)
- SQLite (Database)
- HTML/CSS/JavaScript (Frontend)
- OpenWeather API (Weather Data)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crop-recommendation-system.git
cd crop-recommendation-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Create a `.env` file
- Add your OpenWeather API key:
```
OPENWEATHER_API_KEY=your_api_key_here
```

5. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
python app.py
```

## Usage

1. Register a new account or login
2. Enter your farm details and location
3. Get crop recommendations based on your inputs
4. View detailed analysis and market trends
5. Book consultations with experts if needed

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenWeather API for weather data
- Indian Agricultural Research Institute for crop data
- All contributors and users of the system 