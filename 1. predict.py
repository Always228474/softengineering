import pandas as pd
import pickle

# Load the saved model
with open("bike_availability_model.pkl", "rb") as file:
    model = pickle.load(file)

# Define new input data for prediction (matching trained features)
new_data = pd.DataFrame({
    'temp': [20],        # Match 'temperature' -> 'temp'
    'humidity': [60],
    'wind_speed': [10],
    'pop': [0],          # Match 'precipitation' -> 'pop'
    'hour': [9],
    'day_of_week': [2]   # Example: 0 = Monday, 1 = Tuesday, etc.
})

# Make prediction
prediction = model.predict(new_data)

# Output prediction
print(f"Predicted value: {prediction[0]}")
