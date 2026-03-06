import { useState } from 'react';
import {
    Footprints,
    CarFront,
    Bike,
    Bus,
    TrainFront,
    Map as MapIcon,
    Layers
} from 'lucide-react';

const LOCATIONS = [
    { name: 'Orchard Road', lat: 1.3048, lng: 103.8318 },
    { name: 'Marina Bay Sands', lat: 1.2834, lng: 103.8607 },
    { name: 'Jurong East', lat: 1.3331, lng: 103.7422 },
    { name: 'Tampines', lat: 1.3533, lng: 103.9452 },
    { name: 'Woodlands', lat: 1.4368, lng: 103.7862 },
    { name: 'Changi Airport', lat: 1.3644, lng: 103.9915 },
    { name: 'NUS', lat: 1.2966, lng: 103.7764 },
    { name: 'NTU', lat: 1.3483, lng: 103.6831 },
    { name: 'SUTD', lat: 1.3404, lng: 103.9610 },
    { name: 'SMU', lat: 1.2963, lng: 103.8502 }
];

const MODES = [
    { id: 'walking', icon: Footprints, label: 'Walking' },
    { id: 'cycling', icon: Bike, label: 'Cycling' },
    { id: 'driving', icon: CarFront, label: 'Driving' },
    { id: 'bus', icon: Bus, label: 'Bus' },
    { id: 'mrt', icon: TrainFront, label: 'MRT' }
];

export default function SensoryForm({ onSearch, loading, uxMode, overlays, onOverlayToggle }) {
    const [originIdx, setOriginIdx] = useState(0);
    const [destIdx, setDestIdx] = useState(1);
    const [mode, setMode] = useState('walking');

    const [noiseSens, setNoiseSens] = useState(0.8);
    const [crowdSens, setCrowdSens] = useState(0.8);
    const [predictSens, setPredictSens] = useState(0.8);
    const [natureSens, setNatureSens] = useState(0.5);
    const [shelterSens, setShelterSens] = useState(0.8);

    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch({
            origin: LOCATIONS[originIdx],
            destination: LOCATIONS[destIdx],
            mode: mode,
            profile: {
                noise_sensitivity: parseFloat(noiseSens),
                crowd_sensitivity: parseFloat(crowdSens),
                predictability_preference: parseFloat(predictSens),
                nature_preference: parseFloat(natureSens),
                shelter_preference: parseFloat(shelterSens)
            },
            overlays
        });
    };

    const textClass = uxMode ? "text-base font-bold" : "text-sm font-medium";
    const bgClass = uxMode ? "bg-slate-100" : "bg-white";

    return (
        <form onSubmit={handleSubmit} className="space-y-6">

            {/* Travel Mode Icon Selector */}
            <div className="space-y-2">
                <label className={`block text-slate-800 ${textClass}`}>Travel Mode</label>
                <div className="flex space-x-2 bg-slate-50 p-1.5 rounded-xl border-2 border-slate-200">
                    {MODES.map((m) => {
                        const Icon = m.icon;
                        const isSelected = mode === m.id;
                        return (
                            <button
                                key={m.id}
                                type="button"
                                onClick={() => setMode(m.id)}
                                className={`flex-1 flex flex-col items-center justify-center py-2 px-1 rounded-lg transition-all ${isSelected
                                    ? 'bg-indigo-600 text-white shadow-md'
                                    : 'text-slate-500 hover:bg-indigo-50 hover:text-indigo-700'
                                    }`}
                                title={m.label}
                                aria-label={m.label}
                            >
                                <Icon className={`w-6 h-6 pointer-events-none ${isSelected ? 'stroke-[2.5px]' : 'stroke-2'}`} />
                                <span className={`text-[10px] sm:text-xs mt-1 font-bold pointer-events-none ${isSelected ? 'opacity-100' : 'opacity-75'}`}>
                                    {m.label}
                                </span>
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Locations */}
            <div className="space-y-4">
                <div className="relative">
                    <label className={`block text-slate-800 mb-1 ${textClass}`}>Starting Point</label>
                    <div className="absolute left-3 top-8 sm:top-9 flex items-center h-5 w-5 text-indigo-400">
                        <MapIcon className="w-4 h-4" />
                    </div>
                    <select
                        className={`w-full rounded-xl border-2 border-slate-300 pl-10 pr-4 py-2 drop-shadow-sm focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 font-medium text-slate-700 ${bgClass}`}
                        value={originIdx}
                        onChange={e => setOriginIdx(Number(e.target.value))}
                    >
                        {LOCATIONS.map((loc, idx) => (
                            <option key={`org-${idx}`} value={idx} disabled={idx === destIdx}>{loc.name}</option>
                        ))}
                    </select>
                </div>

                <div className="relative">
                    <label className={`block text-slate-800 mb-1 ${textClass}`}>Destination</label>
                    <div className="absolute left-3 top-8 sm:top-9 flex items-center h-5 w-5 text-red-400">
                        <MapIcon className="w-4 h-4" />
                    </div>
                    <select
                        className={`w-full rounded-xl border-2 border-slate-300 pl-10 pr-4 py-2 drop-shadow-sm focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 font-medium text-slate-700 ${bgClass}`}
                        value={destIdx}
                        onChange={e => setDestIdx(Number(e.target.value))}
                    >
                        {LOCATIONS.map((loc, idx) => (
                            <option key={`dst-${idx}`} value={idx} disabled={idx === originIdx}>{loc.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Sensitivities */}
            <div className="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4 space-y-4 shadow-inner">
                <h3 className={`font-bold text-slate-800 flex items-center space-x-2 border-b-2 border-slate-200 pb-2 ${uxMode ? 'text-lg' : 'text-base'}`}>
                    <span>Sensory Preferences</span>
                </h3>

                <SliderRow label="Noise Sensitivity" val={noiseSens} setVal={setNoiseSens} color="accent-indigo-600" uxMode={uxMode} />
                <SliderRow label="Crowd Avoidance" val={crowdSens} setVal={setCrowdSens} color="accent-indigo-600" uxMode={uxMode} />
                <SliderRow label="Route Predictability" val={predictSens} setVal={setPredictSens} color="accent-indigo-600" desc="Higher avoids complex turns" uxMode={uxMode} />
                <SliderRow label="Nature Preference" val={natureSens} setVal={setNatureSens} color="accent-green-600" desc="Prioritize parks & greenery" uxMode={uxMode} />
                <SliderRow label="Sheltered Paths" val={shelterSens} setVal={setShelterSens} color="accent-sky-600" desc="Prioritize covered walkways" uxMode={uxMode} />
            </div>

            {/* Overlays Toggle */}
            <div className="space-y-2">
                <h3 className={`font-bold text-slate-800 flex items-center space-x-2 ${uxMode ? 'text-lg' : 'text-base'}`}>
                    <Layers className="w-5 h-5 text-slate-500" />
                    <span>Map Overlays</span>
                </h3>
                <div className="flex gap-2 flex-wrap">
                    <ToggleBtn
                        label="🔊 Noise" active={overlays.noise}
                        onClick={() => onOverlayToggle('noise')}
                    />
                    <ToggleBtn
                        label="👥 Crowds" active={overlays.crowd}
                        onClick={() => onOverlayToggle('crowd')}
                    />
                    <ToggleBtn
                        label="🌿 Greenery" active={overlays.green}
                        onClick={() => onOverlayToggle('green')}
                    />
                </div>
            </div>

            {/* Primary Action */}
            <button
                type="submit"
                disabled={loading}
                className={`w-full mt-6 bg-indigo-600 text-white font-extrabold py-4 px-4 rounded-xl shadow-[0_4px_0_0_#3730a3] active:shadow-none active:translate-y-1 hover:bg-indigo-500 focus:outline-none focus:ring-4 focus:ring-indigo-500/40 transition-all disabled:opacity-50 disabled:cursor-not-allowed ${uxMode ? 'text-xl' : 'text-lg'}`}
            >
                {loading ? 'Finding Calm Path...' : 'Find Calm Route'}
            </button>
        </form>
    );
}

function SliderRow({ label, val, setVal, color, desc, uxMode }) {
    return (
        <div>
            <div className="flex justify-between items-center mb-1">
                <label className={`font-bold text-slate-700 ${uxMode ? 'text-sm' : 'text-xs'}`}>{label}</label>
                <span className={`text-slate-500 font-mono ${uxMode ? 'text-sm' : 'text-xs'}`}>{(val * 10).toFixed(0)}/10</span>
            </div>
            <input
                type="range"
                min="0" max="1" step="0.1"
                value={val}
                onChange={e => setVal(e.target.value)}
                className={`w-full h-2 bg-slate-300 rounded-lg appearance-none cursor-pointer ${color}`}
            />
            {desc && !uxMode && <p className="text-[10px] text-slate-400 mt-1">{desc}</p>}
        </div>
    );
}

function ToggleBtn({ label, active, onClick }) {
    return (
        <button
            type="button"
            onClick={onClick}
            className={`px-3 py-1.5 rounded-full text-xs font-bold border-2 transition-colors ${active ? 'bg-indigo-100 border-indigo-300 text-indigo-800 shadow-inner' : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'
                }`}
        >
            {label}
        </button>
    );
}
