# iot_simulator.py
import time
import requests
import random

# URL of your Flask app running locally
SERVER_URL = "http://127.0.0.1:5000/iot-data"

def generate_sensor_data():
    return {
        "N": round(random.uniform(10, 150), 2),
        "P": round(random.uniform(5, 100), 2),
        "K": round(random.uniform(10, 120), 2),
        "temperature": round(random.uniform(15, 40), 2),
        "humidity": round(random.uniform(40, 90), 2),
        "ph": round(random.uniform(4.5, 8.5), 2),
        "rainfall": round(random.uniform(50, 250), 2)
    }

while True:
    data = generate_sensor_data()
    try:
        response = requests.post(SERVER_URL, json=data)
        print(f"[Sent] {data} → [Response] {response.text}")
    except Exception as e:
        print(f"[Error] Could not send data: {e}")
    
    time.sleep(5)  # Wait 5 seconds before sending next set
