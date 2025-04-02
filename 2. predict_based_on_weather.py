import pandas as pd
import joblib
from datetime import datetime

# Load the trained model, encoder, and scaler
model = joblib.load("bike_availability_model.joblib")
encoder = joblib.load("station_encoder.joblib")
scaler = joblib.load("scaler.joblib")

# Check the type of encoder and model
print(type(encoder))  # Should be <class 'sklearn.preprocessing._encoders.OneHotEncoder'>
print(type(model))    # Should be <class 'sklearn.linear_model._base.LinearRegression'>

def get_weather_forecast():
    """Stub function for weather forecast. Returns fixed weather data."""
    return {
        'temp': 20.0,
        'humidity': 60.0,
    }

def predict_bike_availability(station_id, time_str):
    """Predict the number of available bikes for a given time."""
    # Parse input time to extract the hour and the day of the week
    date_time = datetime.strptime(time_str, "%H:%M")
    hour = date_time.hour
    day = date_time.weekday()  # Get the day of the week (0=Monday, 6=Sunday)

    # Use the function for weather forecast
    weather_features = get_weather_forecast()

    # Prepare input data for the model
    input_data = pd.DataFrame([{
        'station_id': station_id,
        'temp': weather_features['temp'],
        'humidity': weather_features['humidity'],
        'hour': hour,
        'day': day
    }])

    # One-hot encode 'station_id' using the loaded encoder
    station_encoded = encoder.transform(input_data[['station_id']])
    station_encoded_df = pd.DataFrame(station_encoded, columns=encoder.get_feature_names_out(['station_id']))



    # Drop the original 'station_id' column and concatenate the encoded columns
    input_data = input_data.drop(columns=['station_id'])
    input_data = pd.concat([input_data, station_encoded_df], axis=1)

    # Apply the same scaling to 'temp' and 'humidity' that was done during training
    input_data[['temp', 'humidity']] = scaler.transform(input_data[['temp', 'humidity']])

    # Ensure the columns are in the correct order as they were during training:
    expected_columns = model.feature_names_in_  # This ensures the exact order used during training


    # Reorder the columns to match the training set
    input_data = input_data.reindex(columns=expected_columns)


    # Print columns to verify they match the training columns
    print(f"Input data columns: {input_data.columns.tolist()}")
    print(f"Expected columns: {expected_columns}")

    # Make prediction using the trained model
    prediction = model.predict(input_data)
    return prediction[0]

# Example usage
time_str = "09:00"
station_id = "station_id_35"  # Define the station_id here

predicted_bikes = predict_bike_availability(station_id, time_str)
print(f"Predicted number of available bikes at {time_str}: {predicted_bikes}")
