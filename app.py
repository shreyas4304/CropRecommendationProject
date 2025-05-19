from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import pickle
import os
from datetime import datetime
import json
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import time
from indian_regions import INDIAN_STATES, SOIL_TYPES, CLIMATE_ZONES, CROP_SUITABILITY, MARKET_DEMAND, GOVERNMENT_SCHEMES, SEASONAL_CALENDAR

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crop_recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Get API key from environment variable or use a default for development
app.config['OPENWEATHER_API_KEY'] = os.getenv('OPENWEATHER_API_KEY', '93b12c69b606a88b69162eb9e43e73f7')

# Add default weather values in case API fails
DEFAULT_WEATHER = {
    'temperature': 25.0,  # Default temperature in Celsius
    'humidity': 65.0,     # Default humidity percentage
    'rainfall': 0.0       # Default rainfall in mm
}

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    contact_no = db.Column(db.String(15), nullable=True)  # Optional contact number
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    predictions = db.relationship('Prediction', backref='user', lazy=True)
    testimonials = db.relationship('Testimonial', backref='user', lazy=True)

# Prediction Model
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    growing_season = db.Column(db.String(20), nullable=False)
    growing_area = db.Column(db.Float, nullable=False)
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    irrigation_type = db.Column(db.String(20), nullable=False)
    predicted_crop = db.Column(db.String(100), nullable=False)
    expected_yield = db.Column(db.String(100))
    growing_tips = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    premium_paid = db.Column(db.Boolean, default=False)  # New field for premium report payment

# IoT Data Model
class IoTData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    moisture = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Testimonial Model
class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)  # For government verification
    is_featured = db.Column(db.Boolean, default=False)  # For featured testimonials

# Consultation Booking Model
class ConsultationBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    preferred_datetime = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(200), nullable=True)
    paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Load crop information
with open('crops_info.json', 'r') as f:
    CROPS_INFO = json.load(f)

# Load the trained model and encoder
model = pickle.load(open("crop_model.pkl", "rb"))
encoder = pickle.load(open("encoder.pkl", "rb"))

# Define valid ranges for inputs
VALID_RANGES = {
    "N": (0, 200),  # Nitrogen
    "P": (0, 200),  # Phosphorus
    "K": (0, 200),  # Potassium
    "temperature": (0, 50),  # Temperature in Celsius
    "humidity": (0, 100),  # Humidity in percentage
    "ph": (0, 14),  # pH level
    "rainfall": (0, 1000)  # Rainfall in mm
}

# Default values for technical parameters by farming type
DEFAULT_TECHNICALS = {
    'traditional': {
        'N': 100,
        'P': 45,
        'K': 45,
        'temperature': 27,
        'humidity': 65,
        'ph': 6.7,
        'rainfall': 220
    },
    'vertical': {  # Default values for vertical farming
        'N': 85,
        'P': 40,
        'K': 40,
        'temperature': 23,
        'humidity': 75,
        'ph': 6.2,
        'rainfall': 0  # Controlled water supply
    }
}

# Vertical farming methods and their characteristics
VERTICAL_FARMING_METHODS = {
    'hydroponic': {
        'description': 'Growing plants in nutrient-rich water without soil',
        'suitable_for': ['lettuce', 'tomato', 'spinach', 'herbs', 'radish_microgreens', 'pea_shoots', 'sunflower_microgreens'],
        'advantages': [
            'Efficient water use',
            'Precise nutrient control',
            'Higher yield in less space',
            'Perfect for microgreens production'
        ]
    },
    'aeroponic': {
        'description': 'Growing plants in air by misting roots with nutrient solution',
        'suitable_for': ['lettuce', 'herbs', 'tomato', 'leafy_greens', 'radish_microgreens', 'pea_shoots'],
        'advantages': [
            'Maximum root aeration',
            'Fastest growth rate',
            'Minimal water usage',
            'Ideal for quick-growing crops'
        ]
    },
    'aquaponic': {
        'description': 'Combining fish farming with plant growing in a symbiotic system',
        'suitable_for': ['lettuce', 'herbs', 'tomato', 'spinach', 'microgreens'],
        'advantages': [
            'Sustainable ecosystem',
            'Dual output (fish + plants)',
            'Natural nutrient cycle',
            'Great for continuous harvesting'
        ]
    }
}

# Additional microgreens-specific growing tips
MICROGREENS_TIPS = {
    'setup': [
        "Use shallow trays with good drainage",
        "Stack growing levels vertically for maximum space efficiency",
        "Install proper LED lighting for each level",
        "Maintain good air circulation between levels"
    ],
    'management': [
        "Monitor humidity levels closely",
        "Keep growing medium consistently moist",
        "Maintain strict cleanliness protocols",
        "Plan successive plantings for continuous harvest"
    ]
}

# Define vertical farming crop categories and their suitability
VERTICAL_CROPS = {
    'leafy_greens': {
        'crops': ['lettuce', 'spinach', 'kale', 'arugula', 'swiss_chard'],
        'difficulty': 'easy',
        'space_efficiency': 'high',
        'growth_rate': 'fast'
    },
    'herbs': {
        'crops': ['basil', 'mint', 'cilantro', 'parsley', 'thyme'],
        'difficulty': 'easy',
        'space_efficiency': 'high',
        'growth_rate': 'medium'
    },
    'fruiting_vegetables': {
        'crops': ['tomato', 'pepper', 'cucumber', 'strawberry'],
        'difficulty': 'medium',
        'space_efficiency': 'medium',
        'growth_rate': 'medium'
    },
    'microgreens': {
        'crops': ['radish_microgreens', 'pea_shoots', 'sunflower_microgreens'],
        'difficulty': 'easy',
        'space_efficiency': 'very_high',
        'growth_rate': 'very_fast'
    }
}

# Create database tables
with app.app_context():
    db.create_all()  # Only create tables if they do not exist

    # Only add sample testimonials if there are no users
    if User.query.count() == 0:
        sample_testimonials = [
            # Featured
            {
                'fullname': 'Rajesh Kumar',
                'email': 'rajesh.kumar@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a farmer from Punjab. The crop recommendation system helped me increase my wheat yield by 25%. The soil analysis was very accurate. Feedback on 10 May 2025.',
                'rating': 5,
                'location': 'Punjab',
                'is_featured': True,
                'is_verified': True,
                'created_at': datetime(2025, 5, 10)
            },
            {
                'fullname': 'Priya Sharma',
                'email': 'priya.sharma@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a new farmer from Haryana. The system guided me perfectly for my first rice crop. Feedback on 10 May 2025.',
                'rating': 5,
                'location': 'Haryana',
                'is_featured': True,
                'is_verified': True,
                'created_at': datetime(2025, 5, 10)
            },
            # Recent (not featured)
            {
                'fullname': 'Mohammed Iqbal',
                'email': 'mohammed.iqbal@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a cotton farmer from Gujarat. The weather predictions were spot on. Saved my crop from unexpected rains. Feedback on 10 May 2025.',
                'rating': 4,
                'location': 'Gujarat',
                'is_featured': False,
                'is_verified': True,
                'created_at': datetime(2025, 5, 10)
            },
            {
                'fullname': 'Lakshmi Devi',
                'email': 'lakshmi.devi@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a vertical farmer from Karnataka. Good support for modern farming. Feedback on 9 May 2025.',
                'rating': 5,
                'location': 'Karnataka',
                'is_featured': False,
                'is_verified': True,
                'created_at': datetime(2025, 5, 9)
            },
            {
                'fullname': 'Suresh Patel',
                'email': 'suresh.patel@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a vegetable farmer from Maharashtra. The soil health recommendations were helpful. Feedback on 8 May 2025.',
                'rating': 3,
                'location': 'Maharashtra',
                'is_featured': False,
                'is_verified': True,
                'created_at': datetime(2025, 5, 8)
            },
            {
                'fullname': 'Anita Singh',
                'email': 'anita.singh@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a farmer from Uttar Pradesh. The app is easy to use, but I wish there were more tips for sugarcane. Feedback on 7 May 2025.',
                'rating': 4,
                'location': 'Uttar Pradesh',
                'is_featured': False,
                'is_verified': True,
                'created_at': datetime(2025, 5, 7)
            },
            {
                'fullname': 'Ravi Verma',
                'email': 'ravi.verma@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a maize farmer from Bihar. The recommendations were good, but the weather data was sometimes delayed. Feedback on 6 May 2025.',
                'rating': 3,
                'location': 'Bihar',
                'is_featured': False,
                'is_verified': True,
                'created_at': datetime(2025, 5, 6)
            },
            # Another featured
            {
                'fullname': 'Sunita Reddy',
                'email': 'sunita.reddy@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a tomato farmer from Andhra Pradesh. The government scheme info was very useful. Feedback on 5 May 2025.',
                'rating': 5,
                'location': 'Andhra Pradesh',
                'is_featured': True,
                'is_verified': True,
                'created_at': datetime(2025, 5, 5)
            },
            # Another recent
            {
                'fullname': 'Deepak Joshi',
                'email': 'deepak.joshi@example.com',
                'password': generate_password_hash('password123'),
                'content': 'I am a wheat farmer from Rajasthan. The app is good, but sometimes slow. Feedback on 4 May 2025.',
                'rating': 4,
                'location': 'Rajasthan',
                'is_featured': False,
                'is_verified': True,
                'created_at': datetime(2025, 5, 4)
            }
        ]
        for testimonial_data in sample_testimonials:
            user = User(
                fullname=testimonial_data['fullname'],
                email=testimonial_data['email'],
                password=testimonial_data['password']
            )
            db.session.add(user)
            db.session.flush()  # To get the user ID

            testimonial = Testimonial(
                user_id=user.id,
                content=testimonial_data['content'],
                rating=testimonial_data['rating'],
                location=testimonial_data['location'],
                is_featured=testimonial_data['is_featured'],
                is_verified=testimonial_data['is_verified'],
                created_at=testimonial_data['created_at']
            )
            db.session.add(testimonial)
        db.session.commit()

# Route for homepage
@app.route('/')
def home():
    return render_template('home.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        contact_no = request.form.get('contact_no')  # Optional

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            fullname=fullname,
            email=email,
            password=hashed_password,
            contact_no=contact_no
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.fullname
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access the dashboard', 'warning')
        return redirect(url_for('login'))
    
    # Get user's recent predictions
    predictions = Prediction.query.filter_by(user_id=session['user_id']).order_by(Prediction.created_at.desc()).limit(5).all()
    
    # Get IoT data for charts
    iot_data = IoTData.query.filter_by(user_id=session['user_id']).order_by(IoTData.timestamp.desc()).limit(24).all()
    
    # Prepare data for charts
    chart_data = {
        'labels': [data.timestamp.strftime('%H:%M') for data in reversed(iot_data)],
        'temperature': [data.temperature for data in reversed(iot_data)],
        'humidity': [data.humidity for data in reversed(iot_data)],
        'moisture': [data.moisture for data in reversed(iot_data)]
    }

    # Get all user's testimonials (including unverified)
    user_testimonials = Testimonial.query.filter_by(user_id=session['user_id']).order_by(Testimonial.created_at.desc()).all()
    
    return render_template('dashboard.html', predictions=predictions, chart_data=chart_data, user_testimonials=user_testimonials)

# Route for prediction
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return render_template('index.html', states=INDIAN_STATES.keys())

    if request.method == 'POST':
        try:
            # Get user-friendly form data
            state = request.form.get('state')
            district = request.form.get('district')

            # Validate required fields
            if not state:
                raise ValueError("Please select a state.")
            if not district:
                raise ValueError("Please select a district.")
            if district not in INDIAN_STATES.get(state, []):
                raise ValueError(f"Invalid district {district} for state {state}")

            # Get other form data
            farm_size = float(request.form.get('farm_size'))
            farming_type = request.form.get('farming_type')
            growing_season = request.form.get('growing_season')
            investment_range = request.form.get('investment_range')
            experience = int(request.form.get('experience'))

            # Use default technical values based on farming type
            tech = DEFAULT_TECHNICALS.get(farming_type, DEFAULT_TECHNICALS['traditional'])
            values = {k: v for k, v in tech.items()}

            # Fetch real-time weather data for the specific district
            weather_used = {}
            try:
                api_key = app.config['OPENWEATHER_API_KEY']
                location_query = f"{district},{state},IN"
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location_query}&appid={api_key}&units=metric"
                app.logger.info(f"Fetching weather for: {location_query}")

                response = requests.get(url)
                app.logger.info(f"Weather API response status: {response.status_code}")

                if response.status_code == 200:
                    weather_data = response.json()
                    values['temperature'] = weather_data['main']['temp']
                    values['humidity'] = weather_data['main']['humidity']

                    weather_used = {
                        'temperature': f"{values['temperature']}°C",
                        'humidity': f"{values['humidity']}%",
                        'rainfall': f"{values['rainfall']}mm"
                    }
                    app.logger.info(f"Successfully fetched weather data: {weather_used}")
                else:
                    app.logger.error(f"Weather API error: {response.text}")
                    raise Exception(f"Weather API returned status code {response.status_code}")

            except Exception as e:
                app.logger.error(f"Weather API error: {str(e)}")
                values['temperature'] = DEFAULT_WEATHER['temperature']
                values['humidity'] = DEFAULT_WEATHER['humidity']
                values['rainfall'] = DEFAULT_WEATHER['rainfall']

                weather_used = {
                    'temperature': f"{DEFAULT_WEATHER['temperature']}°C",
                    'humidity': f"{DEFAULT_WEATHER['humidity']}%",
                    'rainfall': f"{DEFAULT_WEATHER['rainfall']}mm"
                }
                app.logger.info(f"Using default weather values: {weather_used}")

            # Get region-specific information for the selected district
            soil_type = SOIL_TYPES.get(state, {}).get(district, 'Unknown')
            climate_zone = CLIMATE_ZONES.get(state, {}).get(district, 'Unknown')
            suitable_crops = CROP_SUITABILITY.get(soil_type, {}).get(climate_zone, [])

            # Initialize variables for prediction
            predicted_crop = None
            crop_info = {}

            if farming_type == 'vertical':
                # Vertical farming logic remains the same
                category_scores = {
                    'leafy_greens': 0,
                    'herbs': 0,
                    'fruiting_vegetables': 0,
                    'microgreens': 0
                }

                # Scoring logic remains the same
                if farm_size < 300:
                    category_scores['microgreens'] += 3
                    category_scores['herbs'] += 2
                elif farm_size < 600:
                    category_scores['herbs'] += 3
                    category_scores['leafy_greens'] += 2
                else:
                    category_scores['fruiting_vegetables'] += 3
                    category_scores['leafy_greens'] += 1

                if experience < 2:
                    category_scores['microgreens'] += 2
                    category_scores['leafy_greens'] += 1
                elif experience < 4:
                    category_scores['herbs'] += 2
                    category_scores['leafy_greens'] += 2
                else:
                    category_scores['fruiting_vegetables'] += 3

                investment_min = float(investment_range.split('-')[0].replace('₹', '').replace(',', ''))
                if investment_min < 50000:
                    category_scores['microgreens'] += 2
                    category_scores['leafy_greens'] += 1
                elif investment_min < 100000:
                    category_scores['herbs'] += 2
                    category_scores['leafy_greens'] += 2
                else:
                    category_scores['fruiting_vegetables'] += 3

                if values['temperature'] > 28:
                    category_scores['herbs'] += 2
                    category_scores['microgreens'] += 1
                elif values['temperature'] < 20:
                    category_scores['leafy_greens'] += 2
                    category_scores['microgreens'] += 1

                selected_category = max(category_scores.items(), key=lambda x: x[1])[0]
                possible_crops = VERTICAL_CROPS[selected_category]['crops']

                # Select specific crop based on conditions
                if selected_category == 'leafy_greens':
                    predicted_crop = 'spinach' if values['temperature'] > 25 else 'lettuce'
                elif selected_category == 'herbs':
                    predicted_crop = 'basil' if values['temperature'] > 25 else 'mint'
                elif selected_category == 'fruiting_vegetables':
                    predicted_crop = 'tomato' if values['temperature'] > 25 else 'pepper'
                elif selected_category == 'microgreens':
                    predicted_crop = 'radish_microgreens' if farm_size < 200 else 'pea_shoots' if farm_size < 400 else 'sunflower_microgreens'

            else:
                # Traditional farming - use ML model
                X = [[values['N'], values['P'], values['K'], values['temperature'],
                      values['humidity'], values['ph'], values['rainfall']]]
                predicted_crop = encoder.inverse_transform(model.predict(X))[0]

                # Check if predicted crop is suitable for the district
                if predicted_crop not in suitable_crops:
                    # Find the most suitable crop for the district
                    crop_scores = {}
                    for crop in suitable_crops:
                        score = 0
                        if crop in MARKET_DEMAND:
                            if MARKET_DEMAND[crop]['demand'] == 'High':
                                score += 3
                            elif MARKET_DEMAND[crop]['demand'] == 'Medium':
                                score += 2
                            else:
                                score += 1

                            if MARKET_DEMAND[crop]['price_trend'] == 'Increasing':
                                score += 2
                            elif MARKET_DEMAND[crop]['price_trend'] == 'Stable':
                                score += 1

                            if MARKET_DEMAND[crop]['export_potential'] == 'High':
                                score += 2
                            elif MARKET_DEMAND[crop]['export_potential'] == 'Medium':
                                score += 1

                        current_month = datetime.now().strftime('%B')
                        for season, data in SEASONAL_CALENDAR.items():
                            if current_month in data['months'] and crop in data['crops']:
                                score += 2

                        crop_scores[crop] = score

                    if crop_scores:
                        predicted_crop = max(crop_scores.items(), key=lambda x: x[1])[0]
                    elif suitable_crops:
                        predicted_crop = suitable_crops[0]

            # Get crop information
            crop_info = CROPS_INFO.get(predicted_crop, {})

            # Add more details to crop_info for frontend display
            crop_info['region_specific'] = {
                'soil_type': soil_type,
                'climate_zone': climate_zone,
                'suitable_crops': suitable_crops,
                'market_demand': MARKET_DEMAND.get(predicted_crop, {}),
                'applicable_schemes': {k: v for k, v in GOVERNMENT_SCHEMES.items()},
                'seasonal_timing': next((season for season, data in SEASONAL_CALENDAR.items()
                                      if predicted_crop in data['crops']), 'Year-round')
            }
            crop_info['input_parameters'] = {
                'state': state,
                'district': district,
                'farm_size': farm_size,
                'farming_type': farming_type,
                'growing_season': growing_season,
                'investment_range': investment_range,
                'experience': experience,
                'weather_used': weather_used,
            }
            # Add fallback for missing details
            crop_info.setdefault('growing_season', growing_season)
            crop_info.setdefault('expected_yield', '20-30 tons/ha' if predicted_crop == 'tomato' else 'Varies by crop and region')
            crop_info.setdefault('growing_duration', '60-90 days' if predicted_crop == 'tomato' else 'Varies by crop')
            crop_info.setdefault('water_requirements', 'Moderate (600-800 mm/season)' if predicted_crop == 'tomato' else 'Depends on crop')
            crop_info.setdefault('temperature_range', '20-30°C' if predicted_crop == 'tomato' else 'Depends on crop')
            crop_info.setdefault('growing_category', None)
            crop_info.setdefault('selection_factors', None)
            crop_info.setdefault('vertical_farming_methods', None)
            crop_info.setdefault('tips', [])

            # Fill missing market analysis with sensible defaults
            if 'region_specific' in crop_info:
                market = crop_info['region_specific'].get('market_demand', {})
                crop_info['region_specific']['market_demand'] = {
                    'demand': market.get('demand', 'Medium'),
                    'price_trend': market.get('price_trend', 'Stable'),
                    'export_potential': market.get('export_potential', 'Medium')
                }

            # Store prediction if user is logged in
            if 'user_id' in session:
                prediction = Prediction(
                    user_id=session['user_id'],
                    growing_season=growing_season,
                    growing_area=float(farm_size),
                    nitrogen=values['N'],
                    phosphorus=values['P'],
                    potassium=values['K'],
                    temperature=values['temperature'],
                    humidity=values['humidity'],
                    ph=values['ph'],
                    rainfall=values['rainfall'],
                    irrigation_type=farming_type,
                    predicted_crop=predicted_crop,
                    expected_yield=crop_info.get('yield', 'N/A'),
                    growing_tips='\n'.join(crop_info.get('tips', [])),
                    premium_paid=False
                )
                db.session.add(prediction)
                db.session.commit()

            return render_template("index.html",
                                prediction=f"Recommended Crop: {predicted_crop}",
                                crop_info=crop_info,
                                weather_used=weather_used,
                                error=None,
                                states=INDIAN_STATES.keys())

        except Exception as e:
            app.logger.error(f"Prediction error: {str(e)}")
            return render_template("index.html",
                                prediction=None,
                                error=f"Error: {str(e)}",
                                states=INDIAN_STATES.keys())

@app.route('/get_weather/<location>')
def get_weather(location):
    try:
        api_key = app.config['OPENWEATHER_API_KEY']
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            return {
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity']
            }
        return {'error': 'Weather data not available'}, 400
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/generate_pdf/<int:prediction_id>')
def generate_pdf(prediction_id):
    if 'user_id' not in session:
        flash('Please login to download reports', 'warning')
        return redirect(url_for('login'))

    prediction = Prediction.query.get_or_404(prediction_id)
    if prediction.user_id != session['user_id'] and not User.query.get(session['user_id']).is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))

    # Create PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add content to PDF
    p.drawString(100, 750, f"Crop Recommendation Report")
    p.drawString(100, 730, f"Date: {prediction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 710, f"Recommended Crop: {prediction.predicted_crop}")
    
    # Add input values
    y = 670
    for field in ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']:
        p.drawString(100, y, f"{field.title()}: {getattr(prediction, field)}")
        y -= 20

    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"crop_recommendation_{prediction_id}.pdf",
        mimetype='application/pdf'
    )

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        flash('Please login to access admin panel', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))

    predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    return render_template('admin.html', predictions=predictions)

@app.route('/get_districts/<state>')
def get_districts(state):
    districts = INDIAN_STATES.get(state, [])
    return jsonify(districts)

@app.route('/get_region_info/<state>/<district>')
def get_region_info(state, district):
    soil_type = SOIL_TYPES.get(state, {}).get(district, 'Unknown')
    climate_zone = CLIMATE_ZONES.get(state, {}).get(district, 'Unknown')
    suitable_crops = CROP_SUITABILITY.get(soil_type, {}).get(climate_zone, [])
    
    # Get market demand for suitable crops
    market_info = {}
    for crop in suitable_crops:
        if crop in MARKET_DEMAND:
            market_info[crop] = MARKET_DEMAND[crop]
    
    # Get applicable government schemes
    applicable_schemes = {}
    for scheme, details in GOVERNMENT_SCHEMES.items():
        applicable_schemes[scheme] = details
    
    # Get seasonal recommendations
    current_month = datetime.now().strftime('%B')
    seasonal_recommendations = []
    for season, data in SEASONAL_CALENDAR.items():
        if current_month in data['months']:
            seasonal_recommendations.extend(data['crops'])
    
    return jsonify({
        'soil_type': soil_type,
        'climate_zone': climate_zone,
        'suitable_crops': suitable_crops,
        'market_info': market_info,
        'applicable_schemes': applicable_schemes,
        'seasonal_recommendations': seasonal_recommendations
    })

# Add new routes for testimonials
@app.route('/testimonials')
def testimonials():
    featured_testimonials = Testimonial.query.filter_by(is_featured=True).order_by(Testimonial.created_at.desc()).all()
    # Only show recent testimonials that are NOT featured
    recent_testimonials = Testimonial.query.filter_by(is_featured=False, is_verified=True).order_by(Testimonial.created_at.desc()).limit(10).all()
    return render_template('testimonials.html', featured=featured_testimonials, recent=recent_testimonials)

@app.route('/add_testimonial', methods=['POST'])
def add_testimonial():
    if 'user_id' not in session:
        flash('Please login to add a testimonial', 'warning')
        return redirect(url_for('login'))

    # Only allow users who have at least one prediction
    user_predictions = Prediction.query.filter_by(user_id=session['user_id']).count()
    if user_predictions == 0:
        flash('You must use the crop recommendation system before submitting feedback.', 'danger')
        return redirect(request.referrer or url_for('dashboard'))

    rating = request.form.get('rating')
    location = request.form.get('location')
    content = request.form.get('content')

    if not rating or not location or not content:
        flash('All fields are required', 'danger')
        return redirect(request.referrer or url_for('dashboard'))

    try:
        rating = int(rating)
    except Exception:
        flash('Invalid rating value.', 'danger')
        return redirect(request.referrer or url_for('dashboard'))

    testimonial = Testimonial(
        user_id=session['user_id'],
        content=content,
        rating=rating,
        location=location
    )
    db.session.add(testimonial)
    db.session.commit()
    
    flash('Thank you for your feedback! It will be reviewed and verified.', 'success')
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/pay_premium/<int:prediction_id>', methods=['GET', 'POST'])
def pay_premium(prediction_id):
    if 'user_id' not in session:
        flash('Please login to access premium reports.', 'warning')
        return redirect(url_for('login'))
    prediction = Prediction.query.get_or_404(prediction_id)
    if prediction.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    if prediction.premium_paid:
        flash('You have already paid for this premium report.', 'info')
        return redirect(url_for('dashboard'))
    # Demo: Simulate payment
    if 'pay' in request.args:
        prediction.premium_paid = True
        db.session.commit()
        flash('Payment successful! You can now download your premium report.', 'success')
        return redirect(url_for('download_premium_pdf', prediction_id=prediction.id))
    return render_template('pay_premium.html', prediction=prediction)

@app.route('/download_premium_pdf/<int:prediction_id>')
def download_premium_pdf(prediction_id):
    if 'user_id' not in session:
        flash('Please login to download premium reports', 'warning')
        return redirect(url_for('login'))
    prediction = Prediction.query.get_or_404(prediction_id)
    if prediction.user_id != session['user_id']:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    if not prediction.premium_paid:
        flash('Please pay for the premium report first.', 'warning')
        return redirect(url_for('pay_premium', prediction_id=prediction.id))
    # Generate a more detailed PDF for premium users
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"Premium Crop Recommendation Report")
    p.drawString(100, 730, f"Date: {prediction.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    p.drawString(100, 710, f"Recommended Crop: {prediction.predicted_crop}")
    y = 670
    for field in ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']:
        p.drawString(100, y, f"{field.title()}: {getattr(prediction, field)}")
        y -= 20
    # Add extra analytics for premium
    p.drawString(100, y-10, "--- Advanced Analytics & Market Trends ---")
    p.drawString(100, y-30, "- Market Demand: High")
    p.drawString(100, y-50, "- Price Trend: Increasing")
    p.drawString(100, y-70, "- Export Potential: Medium")
    p.drawString(100, y-90, "- Extra Tips: Use certified seeds, monitor soil health, and check local market prices.")
    p.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"premium_crop_recommendation_{prediction_id}.pdf",
        mimetype='application/pdf'
    )

@app.route('/consultation', methods=['GET', 'POST'])
def consultation():
    if 'user_id' not in session:
        flash('Please login to book a consultation.', 'warning')
        return redirect(url_for('login'))
    topics = [
        'Crop Selection',
        'Pest Management',
        'Market Advice',
        'Government Schemes',
        'Soil Health',
        'Other'
    ]
    price = 19  # INR
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        preferred_datetime = request.form.get('preferred_datetime')
        topic = request.form.get('topic')
        
        if not name or not email or not phone or not preferred_datetime or not topic:
            flash('All fields are required.', 'danger')
            return redirect(url_for('consultation'))
            
        booking = ConsultationBooking(
            name=name,
            email=email,
            phone=phone,
            preferred_datetime=preferred_datetime,
            topic=topic
        )
        db.session.add(booking)
        db.session.commit()
        flash('Your consultation booking has been received! Please complete payment to confirm your slot.', 'success')
        return redirect(url_for('consultation_payment', booking_id=booking.id))
    return render_template('consultation.html', topics=topics, price=price)

@app.route('/consultation_payment/<int:booking_id>')
def consultation_payment(booking_id):
    booking = ConsultationBooking.query.get_or_404(booking_id)
    price = 19
    if 'pay' in request.args:
        booking.paid = True
        db.session.commit()
        flash('Payment successful! Your consultation is confirmed. We will contact you soon.', 'success')
        return redirect(url_for('consultation_payment', booking_id=booking.id))
    return render_template('consultation_payment.html', booking=booking, price=price)

if __name__ == "__main__":
    app.run(debug=True)
