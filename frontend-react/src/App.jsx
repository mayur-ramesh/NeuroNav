import { useState } from 'react'
import MapRoute from './components/MapRoute'
import SensoryForm from './components/SensoryForm'

function App() {
    const [routes, setRoutes] = useState([])
    const [selectedRoute, setSelectedRoute] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleRouteSearch = async (requestData) => {
        setLoading(true)
        setError(null)
        setRoutes([])
        setSelectedRoute(null)

        try {
            const response = await fetch('http://localhost:8000/api/route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })

            if (!response.ok) {
                let errorMessage = 'Failed to fetch routes. Backend might be down.';
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
                    }
                } catch (e) {
                    // Ignore JSON parse errors
                }
                throw new Error(errorMessage);
            }

            const data = await response.json()
            setRoutes(data.routes)
            if (data.routes.length > 0) {
                setSelectedRoute(data.routes[0])
            }
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex h-screen w-full bg-slate-50 text-slate-800 overflow-hidden">
            {/* Sidebar for Form and Route list */}
            <div className="w-[380px] min-w-[320px] bg-white shadow-xl z-50 flex flex-col h-full border-r border-slate-200 overflow-y-auto">
                <div className="p-6 border-b border-slate-200 shrink-0">
                    <div className="flex items-center space-x-2 mb-6">
                        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex justify-center items-center">
                            <span className="text-white font-bold text-sm">NN</span>
                        </div>
                        <h1 className="text-2xl font-bold tracking-tight text-indigo-900">NeuroNav</h1>
                    </div>

                    <SensoryForm onSearch={handleRouteSearch} loading={loading} />

                    {error && (
                        <div className="p-4 mt-4 text-sm text-red-700 bg-red-50 rounded-lg border border-red-100">
                            {error}
                        </div>
                    )}
                </div>

                {/* Route List */}
                <div className="flex-1 p-4 space-y-3 bg-slate-50">
                    {routes.length === 0 && !loading && !error && (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400 p-8 text-center space-y-4">
                            <svg className="w-12 h-12 stroke-current opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            <p className="text-sm">Enter origin, destination, and your sensory profile to find the calmest routes.</p>
                        </div>
                    )}
                    {routes.map((route, idx) => (
                        <div
                            key={route.id}
                            onClick={() => setSelectedRoute(route)}
                            className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${selectedRoute?.id === route.id
                                ? 'border-indigo-500 bg-indigo-50 shadow-md transform -translate-y-0.5'
                                : 'border-white bg-white shadow-sm hover:border-indigo-200 hover:shadow-md'
                                }`}
                        >
                            <div className="flex justify-between items-center mb-3">
                                <span className={`font-bold ${idx === 0 ? 'text-indigo-700' : 'text-slate-700'}`}>
                                    {route.category}
                                </span>
                                <span className="flex items-center space-x-1 bg-white px-2 py-1 rounded-md shadow-sm border border-slate-100 text-xs font-semibold text-slate-700">
                                    <span className={`w-2 h-2 rounded-full ${route.total_sensory_score < 3.0 ? 'bg-green-500' :
                                        route.total_sensory_score < 6.0 ? 'bg-amber-500' :
                                            'bg-red-500'
                                        }`}></span>
                                    <span>Cost: {route.total_sensory_score.toFixed(1)}</span>
                                </span>
                            </div>
                            <div className="text-sm text-slate-500 flex justify-between font-medium">
                                <span className="flex items-center space-x-1.5">
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                                    <span>{(route.total_distance / 1000).toFixed(1)} km</span>
                                </span>
                                <span className="flex items-center space-x-1.5">
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                                    <span>{Math.round(route.total_duration / 60)} min</span>
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Map Area */}
            <div className="flex-1 h-full bg-slate-100">
                <MapRoute selectedRoute={selectedRoute} />
            </div>
        </div>
    )
}

export default App
