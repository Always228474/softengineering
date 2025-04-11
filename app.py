from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text


app = Flask(__name__)
app.secret_key = '1234'
API_KEY = app.config['API_KEY']
CONTRACT_NAME = "dublin"
API_URL = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"

Weather_KEY = app.config['Weather_KEY']
LAT, LON = 53.3498, -6.2603  
Weather_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,hourly,daily,alerts&appid={Weather_KEY}&units=metric"

bikes_engine = create_engine(f"mysql+pymysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['BIKES_DB']}")
weather_engine = create_engine(f"mysql+pymysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['WEATHER_DB']}")
future_engine = create_engine(f"mysql+pymysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['FUTURE_DB']}")
user_engine = create_engine(f"mysql+pymysql://{DB_CONFIG['USER']}:{DB_CONFIG['PASSWORD']}@{DB_CONFIG['HOST']}:{DB_CONFIG['PORT']}/{DB_CONFIG['LOGIN_DB']}")


@app.route('/')
@app.route('/')
def index():
    return render_template("index.html", google_maps_api_key=app.config['GOOGLE_MAPS_API_KEY'])


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


@app.route('/api/station/<int:number>/history', methods=['GET'])
def get_station_history(number):
    try:
        # 默认今天
        date = "2025-04-05"  # 固定历史数据日期
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
        # 默认今天
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
        with future_engine.connect() as conn:
            result = conn.execute(text("""
                SELECT dt, temp_max, temp_min, weather_main
                FROM daily_weather
                ORDER BY dt ASC
                LIMIT 5
            """))
            future_data = [
                {
                    "date": row[0].strftime("%Y-%m-%d"),
                    "temp_max": float(row[1]),
                    "temp_min": float(row[2]),
                    "weather_main": row[3]
                }
                for row in result
            ]
        return jsonify(future_data)
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


if __name__ == "__main__":
    app.run(debug=True)
