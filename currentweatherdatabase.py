import requests
import time
from datetime import datetime
from sqlalchemy import create_engine, text

LAT, LON = 53.3498, -6.2603  
API_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=minutely,hourly,daily,alerts&appid={API_KEY}&units=metric"

USER = "root"
PASSWORD = "228474"
HOST = "127.0.0.1"
PORT = "3306"
DB = "dublinweather"

connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
engine = create_engine(connection_string, echo=True)

def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def weather_to_db(data):
    if not data or "current" not in data:
        print("No valid data to insert into database!")
        return

    weather_insert = text("""
    INSERT INTO current_weather (dt, sunrise, sunset, temp, feels_like, pressure, humidity, dew_point, uvi, clouds, visibility, wind_speed, wind_deg, weather_id, weather_main, weather_desc, weather_icon) 
    VALUES (:dt, :sunrise, :sunset, :temp, :feels_like, :pressure, :humidity, :dew_point, :uvi, :clouds, :visibility, :wind_speed, :wind_deg, :weather_id, :weather_main, :weather_desc, :weather_icon)
    ON DUPLICATE KEY UPDATE 
    temp=VALUES(temp), feels_like=VALUES(feels_like), pressure=VALUES(pressure), humidity=VALUES(humidity), 
    dew_point=VALUES(dew_point), uvi=VALUES(uvi), clouds=VALUES(clouds), visibility=VALUES(visibility), 
    wind_speed=VALUES(wind_speed), wind_deg=VALUES(wind_deg), weather_id=VALUES(weather_id), 
    weather_main=VALUES(weather_main), weather_desc=VALUES(weather_desc), weather_icon=VALUES(weather_icon);
    """)

    try:
        with engine.connect() as conn:
            with conn.begin():
                current = data["current"]

                weather_vals = {
                    "dt": datetime.utcfromtimestamp(current["dt"]),
                    "sunrise": datetime.utcfromtimestamp(current["sunrise"]),
                    "sunset": datetime.utcfromtimestamp(current["sunset"]),
                    "temp": current["temp"],
                    "feels_like": current["feels_like"],
                    "pressure": current["pressure"],
                    "humidity": current["humidity"],
                    "dew_point": current.get("dew_point", None),
                    "uvi": current.get("uvi", None),
                    "clouds": current["clouds"],
                    "visibility": current.get("visibility", None),
                    "wind_speed": current["wind_speed"],
                    "wind_deg": current["wind_deg"],
                    "weather_id": current["weather"][0]["id"],
                    "weather_main": current["weather"][0]["main"],
                    "weather_desc": current["weather"][0]["description"],
                    "weather_icon": current["weather"][0]["icon"],
                }

                conn.execute(weather_insert, weather_vals)

        print("Data inserted successfully!")
    except Exception as e:
        print(f"Database insert failed: {e}")


def main():
    while True:
        data = fetch_data()
        if data:
            weather_to_db(data)
        time.sleep(60 * 60)  

if __name__ == "__main__":
    main()


