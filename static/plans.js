let chart = null;

function loadCurrentWeather() {
    fetch("/api/weather")
        .then(res => res.json())
        .then(data => {
            document.getElementById("temp").textContent = data.temp.toFixed(1);
            document.getElementById("feels_like").textContent = data.feels_like.toFixed(1);
            document.getElementById("wind_speed").textContent = data.wind_speed.toFixed(1);
            document.getElementById("weather_main").textContent = data.weather_main;
            document.getElementById("weather_desc").textContent = data.weather_desc;
            document.getElementById("weather_icon").src = getWeatherIcon(data.weather_main);
            updateRecommendation(data);
        })
        .catch(err => {
            console.error("Failed to load weather:", err);
        });
}

function getWeatherIcon(main) {
    const icons = {
        Clear: "https://openweathermap.org/img/wn/01d.png",
        Clouds: "https://openweathermap.org/img/wn/03d.png",
        Rain: "https://openweathermap.org/img/wn/09d.png",
        Drizzle: "https://openweathermap.org/img/wn/10d.png",
        Thunderstorm: "https://openweathermap.org/img/wn/11d.png",
        Snow: "https://openweathermap.org/img/wn/13d.png",
        Mist: "https://openweathermap.org/img/wn/50d.png"
    };
    return icons[main] || icons["Clear"];
}

function updateRecommendation(data) {
    const wind = data.wind_speed;
    const condition = data.weather_main.toLowerCase();
    let text = "We recommend the <strong>Daily Plan</strong> for flexible, short rides.";

    if (wind > 6 || condition.includes("rain") || condition.includes("storm")) {
        text = "⚠️ The weather looks rough. Consider a <strong>Weekly or Monthly Plan</strong> to avoid frequent exposure.";
    } else if (data.temp < 5) {
        text = "🥶 It's cold today. A <strong>Weekly Plan</strong> might suit commuters better.";
    } else if (data.temp > 20) {
        text = "😎 Great riding weather! Try a <strong>Daily Plan</strong> and enjoy the breeze.";
    }

    document.getElementById("recommend-text").innerHTML = text;
}

function loadForecast() {
    fetch("/api/future_weather")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("forecast-preview");
            container.innerHTML = "";
            data.forEach(day => {
                const div = document.createElement("div");
                div.className = "forecast-card";
                div.innerHTML = `
                    <strong>${formatDate(day.date)}</strong>
                    <p>🌡️ ${day.temp_min.toFixed(0)}°C ~ ${day.temp_max.toFixed(0)}°C</p>
                    <p>${day.weather_main}</p>
                `;
                container.appendChild(div);
            });
        });
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" });
}

function loadHourlyChart() {
    fetch("/api/weather/hourly")
        .then(res => res.json())
        .then(data => {
            const labels = data.map(d => d.time);
            const temp = data.map(d => d.temp);
            const feels = data.map(d => d.feels_like);

            const ctx = document.getElementById("weatherChart").getContext("2d");
            if (chart) chart.destroy();

            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: "Temp (°C)",
                            data: temp,
                            borderColor: "#f39c12",
                            backgroundColor: "rgba(243, 156, 18, 0.1)",
                            fill: true
                        },
                        {
                            label: "Feels Like (°C)",
                            data: feels,
                            borderColor: "#3498db",
                            backgroundColor: "rgba(52, 152, 219, 0.1)",
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            title: { display: true, text: "Hour" }
                        },
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: "Temperature (°C)" }
                        }
                    }
                }
            });
        })
        .catch(err => {
            console.error("❌ Error loading hourly weather data:", err);
        });
}

// 初始化
window.addEventListener("DOMContentLoaded", () => {
    loadCurrentWeather();
    loadForecast();
    loadHourlyChart();
});


