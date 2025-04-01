import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import pickle
import json

# Load JSON file correctly
with open("dublin_weather.json", "r") as file:
    weather_data = json.load(file)

# Convert only the 'hourly' section into a DataFrame
data = pd.DataFrame(weather_data["hourly"])

# Extract relevant weather features
data["weather_main"] = data["weather"].apply(lambda x: x[0]["main"])
data["weather_desc"] = data["weather"].apply(lambda x: x[0]["description"])

# Drop the original 'weather' column
data = data.drop(columns=["weather"])

# Convert timestamp to readable format
data["dt"] = pd.to_datetime(data["dt"], unit="s")

# Extract additional time-based features
data["hour"] = data["dt"].dt.hour
data["day_of_week"] = data["dt"].dt.dayofweek

# Display the cleaned data
print(data.head())

# Define features and target based on available columns
features = ["temp", "humidity", "wind_speed", "pop", "hour", "day_of_week"]  # Adjusted for actual column names
target = "temp"  # Change this if predicting something else

# Ensure no missing values
data.dropna(inplace=True)

# Define X (features) and y (target)
X = data[features]
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

# Display model coefficients
print("\nModel Coefficients:")
for feature, coef in zip(features, model.coef_):
    print(f"{feature}: {coef}")
print(f"Intercept: {model.intercept_}")

# Save the model to a file
model_filename = "bike_availability_model.joblib"
joblib.dump(model, model_filename)
print(f"Model saved to {model_filename}")

# Save the model to a .pkl file
model_filename = "bike_availability_model.pkl"
with open(model_filename, "wb") as file:
    pickle.dump(model, file)
print(f"Model saved to {model_filename}")