import { useState } from 'react';
import SOSButton from './components/SOSButton';
import DiagnosticsPanel from './components/DiagnosticsPanel';
import SensoryForm from './components/SensoryForm';
import MapRoute from './components/MapRoute';
import { CONFIG } from './config';

function App() {
    const [routes, setRoutes] = useState([]);
    const [selectedRoute, setSelectedRoute] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [uxMode, setUxMode] = useState(true);
    const [overlays, setOverlays] = useState({ crowd: false, noise: false, green: false });
    const [currentMode, setCurrentMode] = useState('walking');

    const handleRouteSearch = async (requestData) => {
        setLoading(true);
        setError(null);
        setRoutes([]);
        setSelectedRoute(null);
        setOverlays(requestData.overlays || overlays);
        setCurrentMode(requestData.mode);

        const payload = {
            origin: requestData.origin,
            destination: requestData.destination,
            mode: requestData.mode,
            profile: requestData.profile
        };

        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/api/route`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Diagnostics': 'true'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                let errorMessage = 'Failed to fetch routes. Backend might be down.';
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
                    }
                } catch (e) { }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            setRoutes(data.routes);
            if (data.routes && data.routes.length > 0) {
                setSelectedRoute(data.routes[0]);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleOverlayToggle = (key) => {
        setOverlays(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const baseTextClass = uxMode ? "text-base" : "text-sm";
    const headingClass = uxMode ? "text-2xl" : "text-xl";

    // Generate smart explanations based on route data
    const getExplanations = (route) => {
        if (!route) return [];
        const explanations = [];
        const isPreferred = route.role === 'preferred';

        if (isPreferred) {
            explanations.push({ icon: '🛡️', text: 'Lowest overall sensory impact' });
            if (route.total_sensory_score < 3) {
                explanations.push({ icon: '🌿', text: 'Passes through quieter green areas' });
            }
            explanations.push({ icon: '🔇', text: 'Avoids busy intersections where possible' });
            explanations.push({ icon: '🏘️', text: 'Prefers quieter residential streets' });
        } else {
            explanations.push({ icon: '📏', text: 'Maximum diverse alternative path' });
            explanations.push({ icon: '🔀', text: 'Explores different corridors and streets' });
            if (route.distance_m > 3000) {
                explanations.push({ icon: '🚶', text: 'Longer route with more variety' });
            }
        }
        return explanations;
    };

    return (
        <div className={`flex h-screen w-full text-slate-800 overflow-hidden ${uxMode ? 'bg-slate-100' : 'bg-slate-50'}`}>

            {/* Left Panel */}
            <div className="w-[420px] min-w-[380px] max-w-[450px] bg-white shadow-2xl z-[1000] flex flex-col h-full border-r border-slate-200/80">
                {/* Header */}
                <div className="px-6 pt-5 pb-4 border-b border-slate-100 shrink-0 bg-gradient-to-b from-indigo-50/50 to-white">
                    <div className="flex justify-between items-center mb-5">
                        <div className="flex items-center space-x-3">
                            <img src="/logo.png" alt="NeuroNav" className="w-10 h-10 rounded-xl shadow-lg shadow-indigo-200 object-cover" />
                            <div>
                                <h1 className={`${headingClass} font-extrabold tracking-tight text-indigo-900 leading-none`}>NeuroNav</h1>
                                <p className="text-[11px] text-indigo-400 font-medium">Calm Navigation for Singapore</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setUxMode(!uxMode)}
                            className={`px-3 py-1.5 rounded-full text-[11px] font-bold border-2 whitespace-nowrap ${uxMode
                                ? 'bg-indigo-100 border-indigo-200 text-indigo-700'
                                : 'bg-slate-100 border-slate-200 text-slate-500 hover:bg-slate-200'
                                }`}
                            title="Toggle Autism-Friendly Mode"
                        >
                            {uxMode ? '🧠 Calm UI' : 'Calm UI: OFF'}
                        </button>
                    </div>
                </div>

                {/* Scrollable Content */}
                <div className="flex-1 overflow-y-auto">
                    <div className="px-6 py-5">
                        <SensoryForm
                            onSearch={handleRouteSearch}
                            loading={loading}
                            uxMode={uxMode}
                            overlays={overlays}
                            onOverlayToggle={handleOverlayToggle}
                        />

                        {error && (
                            <div className={`p-4 mt-5 text-red-800 bg-red-50 rounded-xl border-2 border-red-200 font-medium ${baseTextClass}`}>
                                <span className="mr-2">⚠️</span>{error}
                            </div>
                        )}
                    </div>

                    {/* Route Results */}
                    <div className="px-6 pb-6 space-y-4">
                        {routes.length === 0 && !loading && !error && (
                            <div className="flex flex-col items-center justify-center text-slate-400 py-10 text-center bg-gradient-to-b from-slate-50 to-white rounded-2xl border-2 border-dashed border-slate-200">
                                <div className="mb-4 p-4 bg-white rounded-2xl shadow-sm">
                                    <svg className="w-10 h-10 stroke-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                                    </svg>
                                </div>
                                <p className={`${baseTextClass} font-semibold text-slate-500`}>Choose locations and tap<br />"Find Calm Route"</p>
                            </div>
                        )}

                        {loading && (
                            <div className="flex flex-col items-center justify-center py-12 space-y-3">
                                <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
                                <span className="text-indigo-600 font-bold text-sm">Analyzing calm paths...</span>
                            </div>
                        )}

                        {!loading && routes.length > 0 && (
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <h3 className="font-extrabold text-slate-800 text-lg">Route Comparison</h3>
                                    <span className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded-md font-semibold">{routes.length} routes</span>
                                </div>

                                {routes.map((route) => {
                                    const isPreferred = route.role === 'preferred';
                                    const isSelected = selectedRoute?.id === route.id;
                                    const explanations = getExplanations(route);
                                    const accentColor = isPreferred ? 'indigo' : 'red';

                                    return (
                                        <div
                                            key={route.id}
                                            onClick={() => setSelectedRoute(route)}
                                            className={`rounded-2xl border-2 cursor-pointer overflow-hidden transition-all duration-150 ${isSelected
                                                ? `border-${accentColor}-500 shadow-lg shadow-${accentColor}-100 ring-2 ring-${accentColor}-200`
                                                : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-md'
                                                }`}
                                        >
                                            {/* Card Header */}
                                            <div className={`p-4 ${isSelected ? (isPreferred ? 'bg-indigo-50' : 'bg-red-50') : 'bg-white'}`}>
                                                <div className="flex justify-between items-start">
                                                    <div className="flex items-center gap-2">
                                                        <div className={`w-3 h-3 rounded-full ${isPreferred ? 'bg-indigo-600' : 'bg-red-600'}`}></div>
                                                        <h4 className={`font-bold ${uxMode ? 'text-lg' : 'text-base'} ${isPreferred ? 'text-indigo-800' : 'text-red-800'}`}>
                                                            {route.name}
                                                        </h4>
                                                    </div>
                                                    <div className={`px-2.5 py-1 rounded-lg text-xs font-bold ${route.total_sensory_score < 4
                                                        ? 'bg-green-100 text-green-700'
                                                        : route.total_sensory_score < 8
                                                            ? 'bg-amber-100 text-amber-700'
                                                            : 'bg-red-100 text-red-700'
                                                        }`}>
                                                        Score: {route.total_sensory_score.toFixed(1)}
                                                    </div>
                                                </div>

                                                <div className="flex gap-6 mt-3">
                                                    <div>
                                                        <div className="text-2xl font-black text-slate-800">{Math.round(route.duration_s / 60)}<span className="text-sm font-semibold text-slate-500 ml-1">min</span></div>
                                                    </div>
                                                    <div>
                                                        <div className="text-2xl font-black text-slate-800">{(route.distance_m / 1000).toFixed(1)}<span className="text-sm font-semibold text-slate-500 ml-1">km</span></div>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Card Explanation */}
                                            <div className="px-4 py-3 bg-slate-50/80 border-t border-slate-100">
                                                <ul className="space-y-1.5">
                                                    {explanations.map((exp, i) => (
                                                        <li key={i} className="flex items-center gap-2 text-sm text-slate-600">
                                                            <span className="text-base">{exp.icon}</span>
                                                            <span>{exp.text}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}

                        <SOSButton />

                        {routes.length > 0 && (
                            <DiagnosticsPanel routes={routes} mode={currentMode} />
                        )}
                    </div>
                </div>
            </div>

            {/* Right Panel - Map */}
            <div className="flex-1 h-full relative" style={{ minHeight: '100vh' }}>
                <MapRoute selectedRoute={selectedRoute} allRoutes={routes} overlays={overlays} />
            </div>
        </div>
    );
}

export default App;
