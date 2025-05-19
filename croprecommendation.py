import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("Crop_recommendation.csv")

# Encode categorical labels (crop names)
encoder = LabelEncoder()
df['label'] = encoder.fit_transform(df['label'])

# Features (X) - All columns except 'label'
X = df.drop(columns=['label'])

# Target (y) - The 'label' column
y = df['label']

# Split dataset into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize models
models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
    "Support Vector Machine": SVC(kernel='linear'),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
}

# Train and evaluate models
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{name} Accuracy: {accuracy:.2f}")
    print(f"Classification Report for {name}:\n{classification_report(y_test, y_pred)}\n")

# Save the best-performing model (Random Forest in this case)
best_model = models["Random Forest"]
pickle.dump(best_model, open("crop_model.pkl", "wb"))

# Save the label encoder
pickle.dump(encoder, open("encoder.pkl", "wb"))

print("Model and encoder saved successfully!")

# Function to predict crop recommendation based on input features
def recommend_crop(N, P, K, temperature, humidity, ph, rainfall, model=best_model):
    input_data = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]], columns=X.columns)
    predicted_label = model.predict(input_data)[0]
    return encoder.inverse_transform([predicted_label])[0]

# Example prediction
example_crop = recommend_crop(90, 42, 43, 20.8, 82.0, 6.5, 202.0)
print(f"Recommended Crop: {example_crop}")
