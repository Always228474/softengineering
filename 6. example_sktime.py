from flask import Flask, request, jsonify
from datetime import datetime
import numpy as np
import joblib
import pandas as pd
from sktime.forecasting.ets import AutoETS
from sktime.forecasting.base import ForecastingHorizon
from sktime.performance_metrics.forecasting import mean_absolute_percentage_error

# Load your forecasting model and encoder (if necessary)
model = joblib.load("bike_availability_model.joblib")
encoder = joblib.load("station_encoder.joblib")

# Assuming you have historical data (for example, using pandas)
# This should be your historical bike availability data
# For demonstration, let's create a dummy dataframe
df = pd.DataFrame({
    'timestamp': pd.date_range(start="", periods=, freq=''),  # Daily frequency for example
    'available_bikes': np.random.randint(, , size=)  # Replace with your actual data
})

df.set_index('timestamp', inplace=True)

# Initialize Flask app
app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    try:
        # Get date, time, and station_id from the request
        date = request.args.get("date")
        time = request.args.get("time")
        station_id = request.args.get("station_id")  # Station ID as an input parameter

        if not date or not time or not station_id:
            return jsonify({"error": "Missing date, time, or station_id parameter"}), 400

        # Convert the station_id to integer
        station_id = int(station_id)

        # Combine the date and time to create a datetime object
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day_of_week = dt.weekday()

        # Assuming you have a forecasting model set up (like AutoETS)
        # Split historical data into train and test (for simplicity, let's just use all data)
        y_train = df['available_bikes']
        forecaster = AutoETS(auto=True, sp=365, n_jobs=-1)  # Adjust `sp` based on your data (daily -> yearly)
        forecaster.fit(y_train)

        # Generate a forecast for the next period (e.g., next day or hour)
        fh = ForecastingHorizon([pd.Timestamp(dt)], is_relative=False)
        y_pred = forecaster.predict(fh)

        # You can apply any additional logic here if needed (e.g., use encoder, other data)

        # Convert the prediction to an integer (if needed)
        predicted_bikes = int(round(y_pred[0]))

        # Return the predicted bike availability as a JSON response
        return jsonify({"predicted_available_bikes": predicted_bikes})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
