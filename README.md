# 🚲 Find My Bicycle Dublin

**Find My Bicycle Dublin** is a ✨ smart, responsive web application ✨ designed to help users explore real-time bike availability across Dublin, plan journeys, check current and forecasted weather, and even predict future station capacity. Whether you're a daily commuter, visitor, or a data enthusiast, this project has something for you! 🎉

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 Getting Started](#-getting-started)
  - [🔧 Installation](#-installation)
  - [⚙️ Configuration](#️-configuration)
- [💻 Usage](#-usage)
- [🧬 Testing](#-testing)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [📧 Contact](#-contact)

---

## ✨ Features

- **📍 Interactive Station Map**: Visualize all bike stations in Dublin with real-time data, and explore historical trends via Chart.js.  
- **🌤️ Weather Dashboard**: View current weather, 5-day forecast, and hourly trends using OpenWeather API.  
- **🔮 Ride Prediction**: Predict future availability of bikes and docks using per-station machine learning models.  

---

## 🚀 Getting Started

### 🔧 Installation

To get started with **Find My Bicycle Dublin**, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/Always228474/find-my-bicycle.git
   ```

2. Navigate to the project directory:

   ```bash
   cd find-my-bicycle
   ```

3. Install the Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

> 📦 Dependencies include: `Flask`, `SQLAlchemy`, `pandas`, `requests`, `joblib`, `PyMySQL`

---

### ⚙️ Configuration

To configure the project, create a `config.py` file or edit the existing one. Example:

```python
DB_CONFIG = {
    "USER": "your_mysql_user",
    "PASSWORD": "your_password",
    "HOST": "localhost",
    "PORT": "3306",
    "BIKES_DB": "dublinbikes",
    "WEATHER_DB": "dublinweather",
    "FUTURE_DB": "futureweather",
    "LOGIN_DB": "login",
    "GOOGLE_MAPS_KEY": "your_google_maps_key",
    "API_KEY": "your_jcdecaux_api_key",
    "Weather_KEY": "your_openweather_key"
}
```

---

## 💻 Usage

To run the Flask server:

```bash
python app.py
```

Open your browser and visit:

```
http://localhost:5000
```

Key Pages:

- `/` – Homepage with plans and intro
- `/stations` – Interactive station map + route planner
- `/plans` – Weather forecast + prediction tools
- `/login` – Basic user login page

---

## 🧬 Testing

Basic functionality can be tested manually via:

```bash
curl http://localhost:5000/api/stations
curl http://localhost:5000/api/weather
curl http://localhost:5000/predict?station_id=42&date=2025-04-10&time=10:30
```

Future improvements include automated test cases using `pytest`.

---

## 🤝 Contributing

We welcome contributions! 🎉 To contribute:

1. Fork the repo.
2. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add your awesome feature"
   ```

4. Push to your branch:

   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a Pull Request 🚀

---

## 📝 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details. 📄

---

## 📧 Contact

If you have any questions or feedback, feel free to reach out:

- **Email**: info@findmybike.ie 📩
- **GitHub Issues**: [Open an Issue](https://github.com/Always228474/find-my-bicycle/issues) 🐛

---

Made with ❤️ by [Always228474](https://github.com/Always228474). Happy cycling! 🚴‍♀️🚴‍♂️
