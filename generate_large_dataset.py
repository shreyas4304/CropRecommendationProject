import pandas as pd
import numpy as np
import random
from datetime import datetime
import os

# Define the base data structure
regions = ['North', 'East', 'South', 'West', 'Central', 'Northeast']
states = {
    'North': ['Punjab', 'Haryana', 'Himachal Pradesh'],
    'East': ['West Bengal', 'Odisha', 'Jharkhand', 'Bihar'],
    'South': ['Karnataka', 'Kerala', 'Tamil Nadu', 'Andhra Pradesh'],
    'West': ['Maharashtra', 'Gujarat', 'Rajasthan', 'Goa'],
    'Central': ['Madhya Pradesh', 'Chhattisgarh', 'Uttar Pradesh', 'Uttarakhand'],
    'Northeast': ['Assam', 'Manipur', 'Nagaland', 'Arunachal Pradesh']
}

crops = {
    'Rice': {'N': (85, 95), 'P': (38, 45), 'K': (40, 45), 'temp': (25, 32), 'humidity': (75, 85), 'ph': (6.0, 7.0), 'rainfall': (200, 300)},
    'Wheat': {'N': (80, 90), 'P': (45, 60), 'K': (40, 45), 'temp': (20, 28), 'humidity': (60, 70), 'ph': (6.5, 7.5), 'rainfall': (100, 200)},
    'Maize': {'N': (70, 80), 'P': (35, 45), 'K': (30, 40), 'temp': (25, 35), 'humidity': (65, 75), 'ph': (6.5, 7.5), 'rainfall': (150, 250)},
    'Sugarcane': {'N': (80, 100), 'P': (40, 50), 'K': (45, 55), 'temp': (25, 35), 'humidity': (70, 80), 'ph': (6.5, 7.5), 'rainfall': (150, 250)},
    'Cotton': {'N': (75, 85), 'P': (40, 45), 'K': (35, 45), 'temp': (30, 38), 'humidity': (60, 70), 'ph': (6.5, 7.5), 'rainfall': (80, 150)},
    'Vegetables': {'N': (70, 80), 'P': (35, 45), 'K': (35, 45), 'temp': (20, 30), 'humidity': (65, 80), 'ph': (6.0, 7.0), 'rainfall': (150, 250)}
}

soil_types = ['Clay', 'Loamy', 'Alluvial', 'Black', 'Red', 'Sandy', 'Coastal', 'Hilly', 'Laterite']
seasons = ['Kharif', 'Rabi', 'Year-round', 'Summer']
irrigation_types = ['Drip', 'Flood', 'Sprinkler']
fertilizers = ['NPK', 'DAP', 'Urea']
harvest_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def generate_random_value(min_val, max_val):
    return round(random.uniform(min_val, max_val), 1)

def generate_crop_data(num_rows):
    data = []
    for _ in range(num_rows):
        region = random.choice(regions)
        state = random.choice(states[region])
        crop = random.choice(list(crops.keys()))
        crop_params = crops[crop]
        
        row = {
            'region': region,
            'state': state,
            'district': f"District_{random.randint(1, 50)}",
            'crop': crop,
            'N': generate_random_value(*crop_params['N']),
            'P': generate_random_value(*crop_params['P']),
            'K': generate_random_value(*crop_params['K']),
            'temperature': generate_random_value(*crop_params['temp']),
            'humidity': generate_random_value(*crop_params['humidity']),
            'ph': generate_random_value(*crop_params['ph']),
            'rainfall': generate_random_value(*crop_params['rainfall']),
            'soil_type': random.choice(soil_types),
            'season': random.choice(seasons),
            'yield_tonnes': round(random.uniform(1.5, 5.0), 1),
            'irrigation_type': random.choice(irrigation_types),
            'farm_size_hectares': round(random.uniform(0.5, 5.0), 1),
            'fertilizer_used': random.choice(fertilizers),
            'harvest_month': random.choice(harvest_months),
            'market_price_per_kg': round(random.uniform(20, 100), 1)
        }
        data.append(row)
    return pd.DataFrame(data)

def main():
    # Calculate number of rows needed for 1GB
    # Each row is approximately 200 bytes
    # 1GB = 1,073,741,824 bytes
    rows_needed = 1_073_741_824 // 200
    
    print(f"Generating {rows_needed:,} rows of data...")
    
    # Generate data in chunks to manage memory
    chunk_size = 1_000_000  # 1 million rows per chunk
    num_chunks = rows_needed // chunk_size
    
    for i in range(num_chunks):
        print(f"Generating chunk {i+1}/{num_chunks}...")
        df = generate_crop_data(chunk_size)
        
        # Save to CSV, appending if not first chunk
        mode = 'w' if i == 0 else 'a'
        header = i == 0
        
        df.to_csv('large_crop_data_india.csv', mode=mode, header=header, index=False)
        
        # Free up memory
        del df
    
    print("Dataset generation complete!")

if __name__ == "__main__":
    main() 