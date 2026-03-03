import { useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Approximate center of Singapore
const DEFAULT_CENTER = [1.3521, 103.8198];

function MapUpdater({ selectedRoute }) {
    const map = useMap();

    useEffect(() => {
        if (selectedRoute && selectedRoute.path && selectedRoute.path.length > 0) {
            const bounds = selectedRoute.path.map(p => [p.lat, p.lng]);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [selectedRoute, map]);

    return null;
}

export default function MapRoute({ selectedRoute }) {
    const polylinePositions = selectedRoute?.path?.map(p => [p.lat, p.lng]) || [];

    // Determine color based on the sensory score
    const getRouteColor = (score) => {
        if (score < 3.0) return '#22c55e'; // Green (Low sensory impact)
        if (score < 6.0) return '#f59e0b'; // Amber/Yellow (Medium impact)
        return '#ef4444'; // Red (High impact)
    };

    const routeColor = selectedRoute ? getRouteColor(selectedRoute.total_sensory_score) : '#4f46e5';

    return (
        <div className="h-full w-full relative z-0">
            <MapContainer
                center={DEFAULT_CENTER}
                zoom={12}
                style={{ height: '100%', width: '100%' }}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {polylinePositions.length > 0 && (
                    <Polyline
                        positions={polylinePositions}
                        pathOptions={{
                            color: routeColor,
                            weight: 8,
                            opacity: 0.9,
                            lineCap: 'round',
                            lineJoin: 'round'
                        }}
                    />
                )}

                <MapUpdater selectedRoute={selectedRoute} />
            </MapContainer>
        </div>
    );
}
