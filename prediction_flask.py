from flask import Flask, request, jsonify
from datetime import datetime
import numpy as np

import joblib
model = joblib.load("bike_availability_model.joblib")
encoder = joblib.load("station_encoder.joblib")

def fetch_openweather_forecast(date):
    # Stub: Replace with code to fetch weather forecast from OpenWeather
    return {
        "station_id": 32,
        "temperature": 20,
        "humidity": 60,
    }

# Initialize Flask app
app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    try:
        # Get date and time from request
        date = request.args.get("date")
        time = request.args.get("time")
        station_id = request.args.get("station_id")  # station_id as an input parameter
        
        if not date or not time or not station_id:
            return jsonify({"error": "Missing date, time, or station_id parameter"}), 400

        # Convert station_id to integer (it is usually a string by default)
        station_id = int(station_id)

        openweather_data = fetch_openweather_forecast(date)

        # Combine date and time into a single datetime object
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day_of_week = dt.weekday()

        # Combine data into input features
        input_features = [
            station_id,
            openweather_data["temperature"],
            openweather_data["humidity"],
            hour,
            day_of_week,
        ]

        # Apply the encoder to the station_id (assuming it needs encoding)
        station_id_encoded = encoder.transform([[station_id]])  # assuming encoder is a fitted encoder
        
        # Debugging: print the shape of the encoded station_id
        print("Encoded station_id features shape:", station_id_encoded.shape)

        # Concatenate the encoded station_id with the other features
        input_features_encoded = np.concatenate([
            station_id_encoded.flatten(),  # Flatten the encoded station_id
            input_features[1:],            # Other features (temperature, humidity, etc.)
        ])

        # Debugging: print the shape of the final input features
        print("Input features shape after concatenation:", input_features_encoded.shape)

        # Check the final number of features
        if input_features_encoded.shape[0] != 119:
            return jsonify({"error": f"Expected 119 features, but got {input_features_encoded.shape[0]}"}), 400

        # Reshape the input array to match the expected shape (1, 119 features)
        input_array = input_features_encoded.reshape(1, -1)

        # Make a prediction
        prediction = model.predict(input_array)
        
        # Apply round and int to ensure we get an integer
        predicted_bikes = int(round(prediction[0]))  # Round the prediction first, then cast to int

        # Return the result as an integer (make sure the prediction is an integer)
        return jsonify({"predicted_available_bikes": predicted_bikes})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
