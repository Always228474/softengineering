let map;
let markers = [];
let infoWindows = [];
let charts = {};
let directionsService;
let directionsRenderer;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 53.3498, lng: -6.2603 },
    zoom: 13,
  });

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer({ map: map });

  loadStations();
}
window.onload = initMap

function loadStations() {
  fetch("/api/stations")
    .then((res) => res.json())
    .then((stations) => {
      stations.forEach((station) => {
        const marker = new google.maps.Marker({
          position: { lat: station.lat, lng: station.lon },
          map: map,
          title: station.name,
          icon: {
            url: "/static/marker.png",
            scaledSize: new google.maps.Size(32, 32),
          },
        });

        const infoWindow = new google.maps.InfoWindow();

        marker.addListener("click", () => {
          infoWindows.forEach((w) => w.close());
          fetchAndShowHistory(station, marker, infoWindow);
        });

        markers.push({
          id: station.id,
          name: station.name.toLowerCase(),
          marker,
          infoWindow,
        });

        infoWindows.push(infoWindow);
      });
    });
}

function fetchAndShowHistory(station, marker, infoWindow) {
  fetch(`/api/station/${station.id}/history`)
    .then((res) => res.json())
    .then((history) => {
      const labels = history.map((h) => h.timestamp);
      const bikes = history.map((h) => h.available_bikes);
      const docks = history.map((h) => h.available_stands);

      const content = document.createElement("div");
      content.innerHTML = `
        <div style="font-family:Arial,sans-serif; max-width:350px;">
          <strong>${station.name}</strong> (ID: ${station.id})<br>
          🚲 <strong>Available Bikes:</strong> ${station.available_bikes}<br>
          🅿️ <strong>Available Docks:</strong> ${station.available_docks}<br>
          <canvas id="chart-${station.id}" width="300" height="200"></canvas>
        </div>
      `;

      infoWindow.setContent(content);
      infoWindow.open(map, marker);

      setTimeout(() => {
        const ctx = document.getElementById(`chart-${station.id}`)?.getContext("2d");
        if (!ctx) return;

        if (charts[station.id]) charts[station.id].destroy();

        charts[station.id] = new Chart(ctx, {
          type: "line",
          data: {
            labels: labels,
            datasets: [
              {
                label: "Available Bikes",
                data: bikes,
                borderColor: "blue",
                backgroundColor: "rgba(0,0,255,0.1)",
                fill: true,
              },
              {
                label: "Available Docks",
                data: docks,
                borderColor: "green",
                backgroundColor: "rgba(0,255,0,0.1)",
                fill: true,
              },
            ],
          },
          options: {
            responsive: false,
            scales: {
              x: {
                title: { display: true, text: "Time" },
              },
              y: {
                beginAtZero: true,
                title: { display: true, text: "Count" },
              },
            },
          },
        });
      }, 300);
    })
    .catch((error) => {
      console.error("❌ Error loading history:", error);
    });
}

function searchStation() {
  const keyword = document.getElementById("searchInput").value.trim().toLowerCase();
  if (!keyword) return;

  const match = markers.find(
    (s) => s.name.includes(keyword) || String(s.id) === keyword
  );

  if (match) {
    fetch(`/api/station/${match.id}/latest`)
      .then((res) => res.json())
      .then((station) => {
        map.setCenter(match.marker.getPosition());
        map.setZoom(16);
        infoWindows.forEach((w) => w.close());
        fetchAndShowHistory(station, match.marker, match.infoWindow);
      });
  } else {
    alert("❌ No matching station found.");
  }
}



function planJourney() {
  const start = document.getElementById("start").value;
  const end = document.getElementById("end").value;

  if (!start || !end) {
    alert("Please enter both start and end locations.");
    return;
  }

  const request = {
    origin: start,
    destination: end,
    travelMode: google.maps.TravelMode.BICYCLING,
  };

  directionsService.route(request, (result, status) => {
    if (status === "OK") {
      directionsRenderer.setDirections(result);
    } else {
      alert("Unable to find route: " + status);
    }
  });
}

window.initMap = initMap;


