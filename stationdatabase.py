import requests
import time
from datetime import datetime
from sqlalchemy import create_engine, text

CONTRACT_NAME = "dublin"
API_URL = f"https://api.jcdecaux.com/vls/v1/stations?contract={CONTRACT_NAME}&apiKey={API_KEY}"

USER = "root"
PASSWORD = "228474"
HOST = "127.0.0.1"
PORT = "3306"
DB = "dublinbikes"

connection_string = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
engine = create_engine(connection_string, echo=True)

def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def stations_to_db(data):
    if not data:
        print("No data to insert into database!")
        return

    station_insert = text("""
    INSERT INTO station (address, banking, bike_stands, name, number, position_lat, position_lng, bonus) 
    VALUES (:address, :banking, :bikestands, :name, :number, :position_lat, :position_lng, :bonus)
    ON DUPLICATE KEY UPDATE 
    banking=VALUES(banking), bike_stands=VALUES(bike_stands), bonus=VALUES(bonus);
    """)


    availability_insert = text("""
    INSERT INTO availability (number, last_update, available_bikes, available_bike_stands, status)
    VALUES (:number, :last_update, :available_bikes, :available_bike_stands, :status)
    ON DUPLICATE KEY UPDATE 
    available_bikes=VALUES(available_bikes), available_bike_stands=VALUES(available_bike_stands), status=VALUES(status), last_update=VALUES(last_update);
    """)

    try:
        with engine.connect() as conn:
            with conn.begin():
                for station in data:
                    position = station.get("position", {"lat": 0.0, "lng": 0.0})

                    station_vals = {
                        "address": station.get("address", "Unknown"),
                        "banking": 1 if station.get("banking", False) else 0,  
                        "bikestands": int(station.get("bike_stands", 0)),
                        "bonus": 1 if station.get("bonus", False) else 0,  
                        "name": station.get("name", "Unnamed"),
                        "number": station.get("number", 0),
                        "position_lat": position.get("lat", 0.0),
                        "position_lng": position.get("lng", 0.0),
                    }

                    conn.execute(station_insert, station_vals)

                    availability_vals = {
                        "number": station.get("number", 0),
                        "last_update": datetime.utcfromtimestamp(station["last_update"] / 1000),
                        "available_bikes": station.get("available_bikes", 0),
                        "available_bike_stands": station.get("available_bike_stands", 0),
                        "status": station.get("status", "UNKNOWN"),
                    }
                    conn.execute(availability_insert, availability_vals)

        print("Data inserted successfully!")
    except Exception as e:
        print(f"Database insert failed: {e}")

def main():
    while True:
        data = fetch_data()
        if data:
            stations_to_db(data)
        time.sleep(5 * 60)

if __name__ == "__main__":
    main()


