import pandas as pd
import pickle

# Load trained model and encoder
model = pickle.load(open("crop_model.pkl", "rb"))
encoder = pickle.load(open("encoder.pkl", "rb"))

# Function to recommend crop
def recommend_crop(N, P, K, temperature, humidity, ph, rainfall):
    input_data = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], 
                              columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
    predicted_label = model.predict(input_data)[0]
    return encoder.inverse_transform([predicted_label])[0]

# Example input values (You can modify these)
N = 90
P = 42
K = 43
temperature = 20.8
humidity = 82.0
ph = 6.5
rainfall = 202.0

# Get prediction
predicted_crop = recommend_crop(N, P, K, temperature, humidity, ph, rainfall)
print(f"Recommended Crop: {predicted_crop}")
