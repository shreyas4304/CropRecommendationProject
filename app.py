from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)

# Load the trained model and encoder
model = pickle.load(open("crop_model.pkl", "rb"))
encoder = pickle.load(open("encoder.pkl", "rb"))

# Route for homepage
@app.route('/')
def home():
    return render_template("index.html")

# Route for prediction
@app.route('/predict', methods=["POST"])
def predict():
    try:
        # Get form data
        N = float(request.form["N"])
        P = float(request.form["P"])
        K = float(request.form["K"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        ph = float(request.form["ph"])
        rainfall = float(request.form["rainfall"])

        # Prepare input data
        input_data = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]],
                                  columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

        # Predict crop
        predicted_label = model.predict(input_data)[0]
        crop_name = encoder.inverse_transform([predicted_label])[0]

        return render_template("index.html", prediction=f"Recommended Crop: {crop_name}")

    except Exception as e:
        return render_template("index.html", prediction=f"Error: {e}")

if __name__ == "__main__":
    app.run(debug=True)
