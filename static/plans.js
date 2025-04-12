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

function setupPredictionForm() {
    const form = document.getElementById("predict-form");
    const resultCard = document.getElementById("prediction-result");

    if (!form) return;

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const stationId = document.getElementById("station_id").value;
        const date = document.getElementById("date").value;
        const time = document.getElementById("time").value;

        fetch(`/predict?station_id=${stationId}&date=${date}&time=${time}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert("❌ Prediction failed: " + data.error);
                    resultCard.style.display = "none";
                } else {
                    document.getElementById("result_station_id").innerText = data.station_id;
                    document.getElementById("result_datetime").innerText = data.datetime;
                    document.getElementById("result_bikes").innerText = data.predicted_bikes;
                    document.getElementById("result_docks").innerText = data.predicted_docks;
                    document.getElementById("result_wind").innerText = data.wind_speed;
                    resultCard.style.display = "block";

                    // 动态获取历史平均值
                    fetch(`/api/station/${stationId}/history`)
                        .then(res => res.json())
                        .then(history => {
                            const avgBikes = history.reduce((sum, h) => sum + h.available_bikes, 0) / history.length;
                            const avgDocks = history.reduce((sum, h) => sum + h.available_stands, 0) / history.length;

                            const predBikes = data.predicted_bikes;
                            const predDocks = data.predicted_docks;

                            const bikesColor = predBikes < 5 ? "#e74c3c" : "#3498db";
                            const docksColor = predDocks < 5 ? "#e74c3c" : "#2ecc71";

                            const ctx = document.getElementById("predictChart").getContext("2d");
                            if (window.predictChartInstance) {
                                window.predictChartInstance.destroy();
                            }

                            window.predictChartInstance = new Chart(ctx, {
                                type: "bar",
                                data: {
                                    labels: ["Available Bikes", "Available Docks"],
                                    datasets: [
                                        {
                                            label: "Prediction",
                                            data: [predBikes, predDocks],
                                            backgroundColor: [bikesColor, docksColor],
                                        },
                                        {
                                            label: "Historical Average",
                                            data: [avgBikes, avgDocks],
                                            backgroundColor: ["#95a5a6", "#95a5a6"],
                                        },
                                    ],
                                },
                                options: {
                                    responsive: true,
                                    plugins: {
                                        title: {
                                            display: true,
                                            text: "Prediction vs. Historical Average",
                                        },
                                    },
                                    scales: {
                                        y: {
                                            beginAtZero: true,
                                            title: { display: true, text: "Count" },
                                        },
                                    },
                                },
                            });
                        });
                }
            })
            .catch(err => {
                alert("🚨 Something went wrong.");
                console.error(err);
            });
    });
}



// 在页面加载完成后初始化预测表单功能
window.addEventListener("DOMContentLoaded", () => {
    loadCurrentWeather();
    loadForecast();
    loadHourlyChart();
    setupPredictionForm(); // 👈 加上这个！
});

// 初始化
window.addEventListener("DOMContentLoaded", () => {
    loadCurrentWeather();
    loadForecast();
    loadHourlyChart();
});


