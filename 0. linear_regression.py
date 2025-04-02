import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import joblib
import ast

# Load the dataset
data = pd.read_csv("final_merged_data.csv")
#print(data.columns)
# Rename columns to match the model's expected input
data.rename(columns={
    'max_air_temperature_celsius': 'temp',
    'max_relative_humidity_percent': 'humidity',
}, inplace=True)
# Check for missing values and drop rows with any missing values
data.dropna(inplace=True)
# Check for duplicate rows and drop them
data.drop_duplicates(inplace=True)
# Ensure 'station_id' is treated as a categorical variable
data['station_id'] = data['station_id'].astype('category')
# Convert categorical variables to category type
for col in data.select_dtypes(include=['object']).columns:
    if col != 'station_id':  # Skip 'station_id' as it's already handled
        data[col] = data[col].astype('category')
# Convert 'day' to categorical type
data['day'] = data['day'].astype('category')
# Check for any remaining non-numeric columns
non_numeric_columns = data.select_dtypes(exclude=['number']).columns.tolist()
if non_numeric_columns:
    print(f"Warning: Non-numeric columns detected: {non_numeric_columns}")
    # Optionally, drop or convert these columns as needed

# Convert 'day' to numeric (0-6) if it's not already
if 'day' in data.columns:
    data['day'] = pd.to_numeric(data['day'], errors='coerce')  # Convert safely
    data.dropna(subset=['day'], inplace=True)  # Drop rows with NaN in 'day'
# Convert 'hour' to numeric (0-23) if it's not already
if 'hour' in data.columns:
    data['hour'] = pd.to_numeric(data['hour'], errors='coerce')  # Convert safely
    data.dropna(subset=['hour'], inplace=True)  # Drop rows with NaN in 'hour'




# Ensure the 'weather' column is properly parsed (if it's in JSON format)
if 'weather' in data.columns:
    data['weather'] = data['weather'].apply(ast.literal_eval)  # Convert safely using literal_eval
    data["weather_main"] = data["weather"].apply(lambda x: x[0]["main"] if isinstance(x, list) and x else None)
    data["weather_desc"] = data["weather"].apply(lambda x: x[0]["description"] if isinstance(x, list) and x else None)
    data.drop(columns=["weather"], inplace=True)

# Convert timestamp to datetime format safely
if 'dt' in data.columns:
    data["dt"] = pd.to_datetime(data["dt"], errors='coerce')  # Convert safely
    data["hour"] = data["dt"].dt.hour
    data["day_of_week"] = data["dt"].dt.dayofweek
    data.drop(columns=["dt"], inplace=True)  # Drop raw date-time column

# Drop any extra or irrelevant columns that the model doesn't need
# These columns should match the features you trained the model with: ['station_id', 'temp', 'humidity', 'hour', 'day']
columns_to_keep = ['station_id', 'temp', 'humidity', 'hour', 'day', 'num_bikes_available']
data = data[columns_to_keep]

# Ensure no missing values in station_id before encoding
data.dropna(subset=['station_id'], inplace=True)

# Define features and target for bike availability prediction
features = ["station_id", "temp", "humidity", "hour", "day"]
target = "num_bikes_available"

# Ensure selected features exist in the dataset
available_features = [col for col in features if col in data.columns]

# Drop rows with missing values
data.dropna(subset=available_features + [target], inplace=True)

# One-hot encode 'station_id'
encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
station_encoded = encoder.fit_transform(data[['station_id']])
station_encoded_df = pd.DataFrame(station_encoded, columns=encoder.get_feature_names_out(['station_id']))
data = pd.concat([data.drop(columns=['station_id']), station_encoded_df], axis=1)


# Scale numerical features
scaler = StandardScaler()
data[['temp', 'humidity']] = scaler.fit_transform(data[['temp', 'humidity']])

# Ensure all columns are numeric before training
non_numeric_columns = data.select_dtypes(exclude=['number']).columns.tolist()
if non_numeric_columns:
    print(f"Warning: Dropping non-numeric columns: {non_numeric_columns}")
    data = data.drop(columns=non_numeric_columns)

# Define X (features) and y (target)
X = data.drop(columns=[target])
y = data[target]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean Absolute Error: {mae}")
print(f"R² Score: {r2}")

# Save the model, encoder, and scaler
joblib.dump(model, "bike_availability_model.joblib")
joblib.dump(encoder, "station_encoder.joblib")
joblib.dump(scaler, "scaler.joblib")
print("Model, encoder, and scaler saved.")