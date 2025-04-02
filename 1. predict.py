import pandas as pd
import joblib

# Load the saved model and encoder
model = joblib.load("bike_availability_model.joblib")
encoder = joblib.load("station_encoder.joblib")

# Define new input data for prediction (with renamed columns)
new_data = pd.DataFrame({
    'station_id': [32],  # raw station_id value
    'temp': [20],  # Renamed from 'temp'
    'humidity': [60],
    'hour': [9],
    'day': [2]   # Example: 0 = Monday, 1 = Tuesday, etc.
})

# One-hot encode the station_id for new data (matching training transformation)
station_encoded_new = encoder.transform(new_data[['station_id']])
station_encoded_new_df = pd.DataFrame(station_encoded_new, columns=encoder.get_feature_names_out(['station_id']))

# Drop the 'station_id' column and concatenate the encoded columns
new_data = pd.concat([new_data.drop(columns=['station_id']), station_encoded_new_df], axis=1)

# Get the model's expected feature names
model_feature_names = model.feature_names_in_

# Check for missing columns in new data
missing_columns = set(model_feature_names) - set(new_data.columns)
extra_columns = set(new_data.columns) - set(model_feature_names)

# Remove missing columns (this ensures no missing columns are in the input data)
if missing_columns:
    print(f"Missing columns from input data: {missing_columns}")
    # Handle missing columns here (e.g., set them to 0 or another default value)
    # Example: Add columns with NaN or 0 values to ensure the correct input shape
    for col in missing_columns:
        new_data[col] = 0  # You can choose how to handle missing columns (e.g., 0 or NaN)

# Rename extra columns to match the training columns (in case they are renamed versions of the original columns)
if extra_columns:
    print(f"Extra columns present: {extra_columns}")
    # If extra columns are renamed columns, we will simply drop them
    new_data = new_data.drop(columns=extra_columns)

# Ensure columns are in the correct order as per the model's feature names
new_data = new_data[model_feature_names]

# Make prediction
prediction = model.predict(new_data)

# Output prediction
print(f"Predicted value: {prediction[0]}")
