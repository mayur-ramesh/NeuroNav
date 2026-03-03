import { useState } from 'react';

// Mock Locations in Singapore
const LOCATIONS = [
    { name: 'Orchard Road', lat: 1.3048, lng: 103.8318 },
    { name: 'Marina Bay Sands', lat: 1.2834, lng: 103.8607 },
    { name: 'Clementi Mall', lat: 1.3150, lng: 103.7649 },
    { name: 'Changi Airport', lat: 1.3644, lng: 103.9915 },
    { name: 'Sentosa', lat: 1.2494, lng: 103.8303 }
];

export default function SensoryForm({ onSearch, loading }) {
    const [originIdx, setOriginIdx] = useState(0);
    const [destIdx, setDestIdx] = useState(1);
    const [mode, setMode] = useState('foot');
    const [noiseSens, setNoiseSens] = useState(0.5);
    const [crowdSens, setCrowdSens] = useState(0.5);
    const [predictSens, setPredictSens] = useState(0.5);
    const [natureSens, setNatureSens] = useState(0.5);

    const handleSubmit = (e) => {
        e.preventDefault();

        const requestData = {
            origin: { lat: LOCATIONS[originIdx].lat, lng: LOCATIONS[originIdx].lng },
            destination: { lat: LOCATIONS[destIdx].lat, lng: LOCATIONS[destIdx].lng },
            mode: mode,
            profile: {
                noise_sensitivity: parseFloat(noiseSens),
                crowd_sensitivity: parseFloat(crowdSens),
                predictability_preference: parseFloat(predictSens),
                nature_preference: parseFloat(natureSens)
            }
        };

        onSearch(requestData);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Travel Mode</label>
                    <select
                        className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        value={mode}
                        onChange={e => setMode(e.target.value)}
                    >
                        <option value="foot">Walking</option>
                        <option value="bike">Cycling</option>
                        <option value="driving">Driving</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Origin</label>
                    <select
                        className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        value={originIdx}
                        onChange={e => setOriginIdx(Number(e.target.value))}
                    >
                        {LOCATIONS.map((loc, idx) => (
                            <option key={`org-${idx}`} value={idx}>{loc.name}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">Destination</label>
                    <select
                        className="w-full rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        value={destIdx}
                        onChange={e => setDestIdx(Number(e.target.value))}
                    >
                        {LOCATIONS.map((loc, idx) => (
                            <option key={`dst-${idx}`} value={idx}>{loc.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="space-y-3 pt-2 border-t border-slate-100">
                <div>
                    <div className="flex justify-between text-xs mb-1">
                        <label className="font-medium text-slate-700">Noise Sensitivity</label>
                        <span className="text-slate-500">{(noiseSens * 10).toFixed(0)}/10</span>
                    </div>
                    <input
                        type="range"
                        min="0" max="1" step="0.1"
                        value={noiseSens}
                        onChange={e => setNoiseSens(e.target.value)}
                        className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                </div>

                <div>
                    <div className="flex justify-between text-xs mb-1">
                        <label className="font-medium text-slate-700">Crowd Avoidance</label>
                        <span className="text-slate-500">{(crowdSens * 10).toFixed(0)}/10</span>
                    </div>
                    <input
                        type="range"
                        min="0" max="1" step="0.1"
                        value={crowdSens}
                        onChange={e => setCrowdSens(e.target.value)}
                        className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                </div>

                <div>
                    <div className="flex justify-between text-xs mb-1">
                        <label className="font-medium text-slate-700">Route Predictability</label>
                        <span className="text-slate-500">{(predictSens * 10).toFixed(0)}/10</span>
                    </div>
                    <input
                        type="range"
                        min="0" max="1" step="0.1"
                        value={predictSens}
                        onChange={e => setPredictSens(e.target.value)}
                        className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                    <p className="text-[10px] text-slate-400 mt-0.5">Higher score avoids complex turns/intersections.</p>
                </div>

                <div>
                    <div className="flex justify-between text-xs mb-1">
                        <label className="font-medium text-green-700">Nature Preference</label>
                        <span className="text-slate-500">{(natureSens * 10).toFixed(0)}/10</span>
                    </div>
                    <input
                        type="range"
                        min="0" max="1" step="0.1"
                        value={natureSens}
                        onChange={e => setNatureSens(e.target.value)}
                        className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-green-600"
                    />
                    <p className="text-[10px] text-slate-400 mt-0.5">Higher score routes through parks and green zones.</p>
                </div>
            </div>

            <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 bg-indigo-600 text-white font-medium py-2.5 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors disabled:opacity-70 disabled:cursor-not-allowed text-sm"
            >
                {loading ? 'Finding Calm Path...' : 'Find Calm Route'}
            </button>
        </form>
    );
}
