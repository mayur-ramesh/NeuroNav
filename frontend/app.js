// Initialize Map centered on Singapore
const map = L.map('map').setView([1.3521, 103.8198], 12);

// Add clear, minimal map tiles (CartoDB Positron)
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
}).addTo(map);

// Form Submission Logic
document.getElementById('routing-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const origin = document.getElementById('origin-input').value;
    const dest = document.getElementById('dest-input').value;
    const noiseWeight = document.getElementById('noise-weight').value;
    const crowdWeight = document.getElementById('crowd-weight').value;

    if (!origin || !dest) {
        alert("Please enter both origin and destination.");
        return;
    }

    // Show loading state
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span>Calculating...</span> <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline ml-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
    btn.disabled = true;

    try {
        // 1. Geocode Origin and Destination
        const startCoords = await geocode(origin);
        const endCoords = await geocode(dest);

        if (!startCoords || !endCoords) {
            throw new Error("Could not find coordinates for the provided addresses.");
        }

        // 2. Fetch Route from OSRM (Walking profile to align with ASD sensory focus)
        const routeData = await getRoute(startCoords, endCoords);
        if (!routeData || !routeData.routes || routeData.routes.length === 0) {
            throw new Error("Could not calculate a walking route between these locations.");
        }

        const route = routeData.routes[0];
        const geometry = route.geometry; // GeoJSON LineString
        const durationSecs = route.duration;
        const distanceMeters = route.distance;

        // 3. Update the UI Metrics (if the elements exist)
        const calmDurationEl = document.getElementById('calm-duration');
        const calmDistanceEl = document.getElementById('calm-distance');
        if (calmDurationEl) calmDurationEl.innerHTML = `<svg class="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg> ${Math.round(durationSecs / 60)} min`;
        if (calmDistanceEl) calmDistanceEl.innerHTML = `<svg class="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg> ${(distanceMeters / 1000).toFixed(1)} km`;

        // 4. Update the Map
        // Clear existing layers safely (avoiding tile layer)
        map.eachLayer((layer) => {
            if (layer instanceof L.Polyline || layer instanceof L.Marker || layer instanceof L.GeoJSON) {
                map.removeLayer(layer);
            }
        });

        // Draw new route
        const routeLayer = L.geoJSON(geometry, {
            style: { color: '#4f46e5', weight: 6, opacity: 0.8 }
        }).addTo(map);

        // Add start and end markers
        const startIcon = L.divIcon({ className: 'bg-white border-[3px] border-primary rounded-full w-4 h-4 shadow-md', iconSize: [16, 16] });
        const endIcon = L.divIcon({ className: 'bg-primary border-[3px] border-white rounded-full w-4 h-4 shadow-md', iconSize: [16, 16] });

        // Leaflet expects [lat, lng], but our custom coords object is {lat, lon}
        L.marker([startCoords.lat, startCoords.lon], { icon: startIcon }).addTo(map);
        L.marker([endCoords.lat, endCoords.lon], { icon: endIcon }).addTo(map);

        // Zoom to fit route
        map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });

        // Show Results Panel
        document.getElementById('route-results').classList.remove('hidden');

    } catch (error) {
        console.error("Routing Error:", error);
        alert(error.message || "An error occurred while calculating the route.");
    } finally {
        // Reset Button
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// Helper: Geocode using OpenStreetMap Nominatim
async function geocode(query) {
    // Append Singapore context to help Nominatim
    const searchString = encodeURIComponent(query + ", Singapore");
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${searchString}&limit=1`);
    const data = await response.json();

    if (data && data.length > 0) {
        return {
            lat: parseFloat(data[0].lat),
            lon: parseFloat(data[0].lon)
        };
    }
    return null;
}

// Helper: Get route from OSRM (Walking profile)
async function getRoute(start, end) {
    // OSRM expects coordinates in lon,lat order!
    const coords = `${start.lon},${start.lat};${end.lon},${end.lat}`;
    // Using the public OSRM API for walking (foot)
    const url = `https://router.project-osrm.org/route/v1/foot/${coords}?overview=full&geometries=geojson`;

    const response = await fetch(url);
    if (!response.ok) {
        throw new Error("Failed to fetch route from OSRM.");
    }
    return await response.json();
}
