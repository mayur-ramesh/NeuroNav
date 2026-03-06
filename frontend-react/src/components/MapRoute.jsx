import { useEffect, useState, useCallback, Fragment } from 'react';
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
            width: 22px; height: 22px; 
            background: ${color}; 
            border: 3px solid white;
            border-radius: 50%; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [22, 22],
        iconAnchor: [11, 11],
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
            if (route.path && route.path.length > 0) {
                route.path.forEach(c => bounds.extend([c.lat, c.lng]));
            }
        });
        if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [60, 60], animate: true, maxZoom: 15 });
        }
    }, [allRoutes, map]);
    return null;
}

// Overlay circles component — subtle, location-aware indicators
function OverlayLayer({ signalData, type, visible }) {
    if (!visible || !signalData || signalData.length === 0) return null;

    const getStyle = (val) => {
        if (type === 'noise') {
            return {
                fillColor: `rgba(239, 68, 68, ${0.08 + val * 0.22})`,  // red tones
                radius: 500 + val * 800,
            };
        }
        if (type === 'crowd') {
            return {
                fillColor: `rgba(147, 51, 234, ${0.08 + val * 0.20})`,  // purple tones
                radius: 500 + val * 700,
            };
        }
        if (type === 'nature') {
            return {
                fillColor: `rgba(34, 197, 94, ${0.10 + val * 0.25})`,  // green tones
                radius: 600 + val * 600,
            };
        }
        return { fillColor: 'rgba(100,100,100,0.05)', radius: 400 };
    };

    return (
        <>
            {signalData.map((pt, i) => {
                const val = pt[type];
                if (val < 0.1) return null; // Only render meaningful signals
                const style = getStyle(val);
                return (
                    <Circle
                        key={`${type}-${i}`}
                        center={[pt.lat, pt.lng]}
                        radius={style.radius}
                        pathOptions={{
                            color: 'transparent',
                            fillColor: style.fillColor,
                            fillOpacity: 1,
                            stroke: false,
                        }}
                    />
                );
            })}
        </>
    );
}

export default function MapRoute({ selectedRoute, allRoutes = [], overlays = {} }) {
    const singaporeCenter = [1.3521, 103.8198];
    const defaultZoom = 12;
    const [signalData, setSignalData] = useState([]);

    const anyOverlayActive = overlays.crowd || overlays.noise || overlays.green;

    const fetchSignals = useCallback(async () => {
        if (!anyOverlayActive) return;
        if (signalData.length > 0) return;
        try {
            // Use resolution=18 for finer detail but signals are mostly 0 so it's sparse
            const res = await fetch(`${CONFIG.API_BASE_URL}/api/signals?resolution=18&min_lat=1.26&max_lat=1.42&min_lng=103.68&max_lng=104.00`);
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

    // Sort routes so the selected one renders last (on top)
    const sortedRoutes = allRoutes.slice().sort((a, b) => {
        if (a.id === selectedRoute?.id) return 1;
        if (b.id === selectedRoute?.id) return -1;
        return 0;
    });

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

            {/* Route Polylines — use Fragment, NOT div (div breaks Leaflet SVG layer) */}
            {sortedRoutes.map((route) => {
                if (!route.path || route.path.length === 0) return null;

                const coords = route.path.map(c => [c.lat, c.lng]);
                const isSelected = selectedRoute?.id === route.id;
                const isPreferred = route.role === 'preferred';
                const baseColor = isPreferred ? '#1d4ed8' : '#dc2626';

                return (
                    <Fragment key={route.id}>
                        {/* Shadow outline for depth */}
                        <Polyline
                            positions={coords}
                            pathOptions={{
                                color: '#000000',
                                weight: isSelected ? 10 : 5,
                                opacity: 0.12,
                                lineCap: 'round',
                                lineJoin: 'round',
                            }}
                        />
                        {/* Main colored route */}
                        <Polyline
                            positions={coords}
                            pathOptions={{
                                color: baseColor,
                                weight: isSelected ? 6 : 3,
                                opacity: isSelected ? 1.0 : 0.5,
                                lineCap: 'round',
                                lineJoin: 'round',
                            }}
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
                    </Fragment>
                );
            })}

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
