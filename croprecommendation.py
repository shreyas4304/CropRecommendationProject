import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("Crop_recommendation.csv")

# Display basic information
print(df.info())  # Data types and missing values
print(df.head())  # First 5 rows
print(df.describe())  # Statistical summary

# Check for missing values
print("Missing values in dataset:")
print(df.isnull().sum())

# Encode categorical labels (crop names)
encoder = LabelEncoder()
df['label'] = encoder.fit_transform(df['label'])

# Features (X) - All columns except 'label'
X = df.drop(columns=['label'])

# Target (y) - The 'label' column
y = df['label']

# Split dataset into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

# Classification report
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Save the trained model
pickle.dump(model, open("crop_model.pkl", "wb"))

# Save the label encoder
pickle.dump(encoder, open("encoder.pkl", "wb"))

print("Model and encoder saved successfully!")

# Function to predict crop recommendation based on input features
def recommend_crop(N, P, K, temperature, humidity, ph, rainfall):
    input_data = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], 
                              columns=X.columns)
    predicted_label = model.predict(input_data)[0]
    return encoder.inverse_transform([predicted_label])[0]

# Example prediction
example_crop = recommend_crop(90, 42, 43, 20.8, 82.0, 6.5, 202.0)
print(f"Recommended Crop: {example_crop}")
