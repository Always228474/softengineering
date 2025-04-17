from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import pandas as pd
import joblib
import os

app = Flask(__name__)
app.secret_key = '1234'

API_KEY = DB_CONFIG['API_KEY']
Weather_KEY = DB_CONFIG['Weather_KEY']
GOOGLE_MAPS_API_KEY = DB_CONFIG['GOOGLE_MAPS_KEY']

CONTRACT_NAME = "dublin"
API_URL = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"

LAT, LON = 53.3498, -6.2603  
Weather_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,hourly,daily,alerts&appid={Weather_KEY}&units=metric"

bikes_engine = create_engine(f"mysql+pymysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['BIKES_DB']}")
weather_engine = create_engine(f"mysql+pymysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['WEATHER_DB']}")
future_engine = create_engine(f"mysql+pymysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['FUTURE_DB']}")
user_engine = create_engine(f"mysql+pymysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['LOGIN_DB']}")


@app.route('/')
def index():
    return render_template("index.html", google_maps_api_key=GOOGLE_MAPS_API_KEY)


@app.route('/api/stations', methods=['GET'])
def get_stations():
    try:
        response = requests.get(API_URL)
        stations_data = response.json()

        stations = [
            {
                "id": s["number"],
                "name": s["name"],
                "lat": s["position"]["lat"],
                "lon": s["position"]["lng"],
                "available_bikes": s["available_bikes"],
                "available_docks": s["available_bike_stands"]
            }
            for s in stations_data
        ]

        return jsonify(stations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/station/<int:station_id>/latest", methods=["GET"])
def get_latest_station_status(station_id):
    try:
        response = requests.get(API_URL)
        stations_data = response.json()
        for s in stations_data:
            if s["number"] == station_id:
                station = {
                    "id": s["number"],
                    "name": s["name"],
                    "lat": s["position"]["lat"],
                    "lon": s["position"]["lng"],
                    "available_bikes": s["available_bikes"],
                    "available_docks": s["available_bike_stands"]
                }
                return jsonify(station)
        return jsonify({"error": "Station not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/station/<int:number>/history', methods=['GET'])
def get_station_history(number):
    try:
        date = "2025-04-05"  
        start_time = datetime.strptime(date, "%Y-%m-%d")
        end_time = start_time + timedelta(days=1)

        with bikes_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT last_update, available_bikes, available_bike_stands
                FROM availability_history
                WHERE number = :number AND last_update BETWEEN :start AND :end
                ORDER BY last_update ASC
            """), {
                "number": number,
                "start": start_time,
                "end": end_time
            })

            history = [
                {
                    "timestamp": row[0].strftime("%H:%M"),
                    "available_bikes": row[1],
                    "available_stands": row[2]
                }
                for row in result
            ]
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
   


@app.route('/api/weather', methods=['GET'])
def get_weather():
    try:
        response = requests.get(Weather_URL)
        response.raise_for_status()
        data = response.json()

        current = data["current"]

        weather_data = {
            "datetime": datetime.utcfromtimestamp(current["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
            "temp": current["temp"],
            "feels_like": current["feels_like"],
            "humidity": current["humidity"],
            "pressure": current["pressure"],
            "wind_speed": current["wind_speed"],
            "weather_main": current["weather"][0]["main"],
            "weather_desc": current["weather"][0]["description"]
        }

        return jsonify(weather_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/api/weather/hourly', methods=['GET'])
def get_hourly_weather():
    try:
        date = "2025-04-05"
        start = datetime.strptime(date, "%Y-%m-%d")
        end = start + timedelta(days=1)

        with future_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT dt, temp, feels_like, wind_speed
                FROM hourly_weather
                WHERE dt BETWEEN :start AND :end
                ORDER BY dt ASC
            """), {
                "start": start,
                "end": end
            })

            hourly_data = [
                {
                    "time": row[0].strftime("%H:%M"),
                    "temp": float(row[1]),
                    "feels_like": float(row[2]),
                    "wind_speed": float(row[3])
                }
                for row in result
            ]

        return jsonify(hourly_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/future_weather', methods=['GET'])
def get_future_weather():
    try:
        url = f'https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=current,minutely,hourly,alerts&appid={Weather_KEY}&units=metric'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        forecast = []
        for daily in data['daily'][:5]:  
            forecast.append({
                "date": datetime.utcfromtimestamp(daily["dt"]).strftime("%Y-%m-%d"),
                "temp_min": daily["temp"]["min"],
                "temp_max": daily["temp"]["max"],
                "humidity": daily["humidity"],
                "wind_speed": daily["wind_speed"],
                "pop": daily.get("pop", 0),
                "weather_main": daily["weather"][0]["main"],
                "weather_desc": daily["weather"][0]["description"],
                "weather_icon": daily["weather"][0]["icon"]
            })

        return jsonify(forecast)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/predict', methods=['GET'])
def predict_bike_availability():
    try:
        station_id = request.args.get('station_id', type=int)
        date_str = request.args.get('date')   
        time_str = request.args.get('time')   

        if not all([station_id, date_str, time_str]):
            return jsonify({"error": "Missing parameters"}), 400

        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        hour = dt.hour
        weekday = dt.weekday()
        is_weekend = 1 if weekday >= 5 else 0

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={Weather_KEY}&units=metric"
        response = requests.get(weather_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to get weather data"}), 500

        weather_data = response.json()
        wind_speed = weather_data['wind']['speed']

        input_data = pd.DataFrame([{
            'hour': hour,
            'weekday': weekday,
            'is_weekend': is_weekend,
        }])

        model_path = os.path.join('models', f'model_station_{station_id}.pkl')
        if not os.path.exists(model_path):
            return jsonify({"error": f"Model for station {station_id} not found"}), 404

        model = joblib.load(model_path)
        prediction = model.predict(input_data)[0]  

        return jsonify({
            'station_id': station_id,
            'datetime': dt.strftime("%Y-%m-%d %H:%M"),
            'predicted_bikes': int(prediction[0]),
            'predicted_docks': int(prediction[1]),
            'wind_speed': wind_speed,
            'hour': hour,
            'weekday': weekday
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            with user_engine.connect() as conn:
                result = conn.execute(text("SELECT password FROM users WHERE email = :email"), {"email": email})
                user = result.fetchone()

                if user and user[0] == password:
                    session["user_email"] = email
                    flash("Login successful!", "success")
                    return redirect(url_for("home"))
                else:
                    flash("Invalid email or password", "error")
        except Exception:
            flash("Invalid email or password", "error")  

    return render_template("login.html")


@app.route('/stations')
def stations_page():
    return render_template("stations.html")

@app.route('/plans')
def plans():
    return render_template("plans.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
