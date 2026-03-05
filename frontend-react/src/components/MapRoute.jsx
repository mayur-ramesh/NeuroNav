import { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, Circle, useMap, ZoomControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { CONFIG } from '../config';

// Fix default marker icon
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom colored marker
function createIcon(color) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            width: 24px; height: 24px; 
            background: ${color}; 
            border: 3px solid white;
            border-radius: 50%; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
    });
}

const originIcon = createIcon('#4f46e5');
const destIcon = createIcon('#dc2626');

// Auto-fit bounds when routes load
function RouteBounds({ allRoutes }) {
    const map = useMap();
    useEffect(() => {
        if (!allRoutes || allRoutes.length === 0) return;
        const bounds = L.latLngBounds();
        allRoutes.forEach(route => {
            if (route.path) {
                route.path.forEach(c => bounds.extend([c.lat, c.lng]));
            }
        });
        if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [60, 60], animate: true, maxZoom: 15 });
        }
    }, [allRoutes, map]);
    return null;
}

// Overlay circles component
function OverlayLayer({ signalData, type, visible }) {
    if (!visible || !signalData || signalData.length === 0) return null;

    const getColor = (val) => {
        if (type === 'nature') {
            // Green shades
            const g = Math.round(100 + val * 155);
            return `rgba(22, ${g}, 66, ${0.15 + val * 0.35})`;
        }
        if (type === 'noise') {
            // Orange-red shades
            const r = Math.round(200 + val * 55);
            return `rgba(${r}, ${Math.round(100 - val * 60)}, 20, ${0.15 + val * 0.4})`;
        }
        if (type === 'crowd') {
            // Purple shades
            const b = Math.round(130 + val * 125);
            return `rgba(${Math.round(100 + val * 80)}, 40, ${b}, ${0.12 + val * 0.35})`;
        }
        return 'rgba(100,100,100,0.1)';
    };

    return (
        <>
            {signalData.map((pt, i) => {
                const val = pt[type];
                if (val < 0.15) return null; // Skip very low signals
                return (
                    <Circle
                        key={`${type}-${i}`}
                        center={[pt.lat, pt.lng]}
                        radius={800 + val * 600}
                        pathOptions={{
                            color: 'transparent',
                            fillColor: getColor(val),
                            fillOpacity: 1,
                        }}
                    >
                        <Popup>
                            <div className="text-xs">
                                <strong className="capitalize">{type}</strong>: {(val * 100).toFixed(0)}%
                            </div>
                        </Popup>
                    </Circle>
                );
            })}
        </>
    );
}

export default function MapRoute({ selectedRoute, allRoutes = [], overlays = {} }) {
    const singaporeCenter = [1.3521, 103.8198];
    const defaultZoom = 12;
    const [signalData, setSignalData] = useState([]);

    // Fetch signal data for overlays when any overlay is toggled on
    const anyOverlayActive = overlays.crowd || overlays.noise || overlays.green;

    const fetchSignals = useCallback(async () => {
        if (!anyOverlayActive) return;
        if (signalData.length > 0) return; // Already fetched
        try {
            const res = await fetch(`${CONFIG.API_BASE_URL}/api/signals?resolution=14`);
            if (res.ok) {
                const data = await res.json();
                setSignalData(data.points);
            }
        } catch (e) {
            console.warn('Failed to fetch signal data:', e);
        }
    }, [anyOverlayActive, signalData.length]);

    useEffect(() => {
        fetchSignals();
    }, [fetchSignals]);

    return (
        <MapContainer
            center={singaporeCenter}
            zoom={defaultZoom}
            className="w-full h-full"
            zoomControl={false}
            style={{ height: '100%', width: '100%' }}
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            />
            <ZoomControl position="bottomright" />
            <RouteBounds allRoutes={allRoutes} />

            {/* Environmental Overlays */}
            <OverlayLayer signalData={signalData} type="noise" visible={overlays.noise} />
            <OverlayLayer signalData={signalData} type="crowd" visible={overlays.crowd} />
            <OverlayLayer signalData={signalData} type="nature" visible={overlays.green} />

            {/* Route Polylines — render non-selected first (below), then selected (on top) */}
            {allRoutes
                .slice()
                .sort((a, b) => (a.id === selectedRoute?.id ? 1 : -1))
                .map((route) => {
                    if (!route.path || route.path.length === 0) return null;

                    const coords = route.path.map(c => [c.lat, c.lng]);
                    const isSelected = selectedRoute?.id === route.id;
                    const isPreferred = route.role === 'preferred';
                    const baseColor = isPreferred ? '#1d4ed8' : '#dc2626';

                    return (
                        <div key={route.id}>
                            {/* Shadow line for depth */}
                            <Polyline
                                positions={coords}
                                color="rgba(0,0,0,0.15)"
                                weight={isSelected ? 12 : 6}
                                opacity={1}
                                lineCap="round"
                                lineJoin="round"
                            />
                            {/* Main colored line */}
                            <Polyline
                                positions={coords}
                                color={baseColor}
                                weight={isSelected ? 7 : 4}
                                opacity={isSelected ? 1.0 : 0.45}
                                lineCap="round"
                                lineJoin="round"
                            >
                                <Popup>
                                    <div style={{ minWidth: 140 }}>
                                        <div style={{ fontWeight: 700, fontSize: 14, color: baseColor, marginBottom: 4 }}>
                                            {route.name}
                                        </div>
                                        <div style={{ fontSize: 12, color: '#64748b' }}>
                                            {(route.distance_m / 1000).toFixed(2)} km · {Math.round(route.duration_s / 60)} min
                                        </div>
                                        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
                                            Sensory Cost: {route.total_sensory_score.toFixed(1)}
                                        </div>
                                    </div>
                                </Popup>
                            </Polyline>
                        </div>
                    );
                })
            }

            {/* Origin & Destination Markers */}
            {allRoutes.length > 0 && allRoutes[0].path && allRoutes[0].path.length > 0 && (
                <>
                    <Marker position={[allRoutes[0].path[0].lat, allRoutes[0].path[0].lng]} icon={originIcon}>
                        <Popup><strong>Origin</strong></Popup>
                    </Marker>
                    <Marker
                        position={[
                            allRoutes[0].path[allRoutes[0].path.length - 1].lat,
                            allRoutes[0].path[allRoutes[0].path.length - 1].lng
                        ]}
                        icon={destIcon}
                    >
                        <Popup><strong>Destination</strong></Popup>
                    </Marker>
                </>
            )}
        </MapContainer>
    );
}
