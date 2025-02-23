import requests
import json


API_KEY = "5d666bca7461699abf87b1cc5fba8d0c"
LAT, LON = 53.3498, -6.2603  
API_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=current,alerts&appid={API_KEY}&units=metric"

