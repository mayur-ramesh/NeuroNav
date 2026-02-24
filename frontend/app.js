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

    // Show loading state (Simplified for now)
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span>Calculating...</span> <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline ml-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
    btn.disabled = true;

    // Simulate API Call to Backend
    setTimeout(() => {
        // Reset Button
        btn.innerHTML = originalText;
        btn.disabled = false;

        // Show Results Panel
        document.getElementById('route-results').classList.remove('hidden');

        // Draw a simulated route on map (Clementi to Orchard approximation)
        const latlngs = [
            [1.3151, 103.7652], // Clementi MRT
            [1.3120, 103.7800], // Quiet Path
            [1.3050, 103.8300], // Near Orchard
            [1.3038, 103.8322]  // Destination
        ];

        // Clear existing layers if any (basic implementation)
        map.eachLayer((layer) => {
            if (layer instanceof L.Polyline || layer instanceof L.Marker) {
                map.removeLayer(layer);
            }
        });

        const polyline = L.polyline(latlngs, {color: '#4f46e5', weight: 5, opacity: 0.8}).addTo(map);
        
        // Add markers
        const startIcon = L.divIcon({ className: 'bg-white border-2 border-primary rounded-full w-4 h-4', iconSize: [16,16]});
        const endIcon = L.divIcon({ className: 'bg-primary border-2 border-white rounded-full w-4 h-4', iconSize: [16,16]});
        
        L.marker(latlngs[0], {icon: startIcon}).addTo(map);
        L.marker(latlngs[latlngs.length - 1], {icon: endIcon}).addTo(map);

        // Zoom map to polyline
        map.fitBounds(polyline.getBounds(), {padding: [50, 50]});

    }, 800);
});
