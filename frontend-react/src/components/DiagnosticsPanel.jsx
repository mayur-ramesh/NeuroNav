export default function DiagnosticsPanel({ routes, mode }) {
    if (!routes || routes.length === 0 || !routes[0].debug) return null;

    const prefRoute = routes[0];
    const longRoute = routes.length > 1 ? routes[1] : null;

    return (
        <div className="mt-4 bg-slate-800 text-slate-300 p-4 rounded-xl text-xs font-mono space-y-2">
            <div className="flex justify-between items-center mb-2 border-b border-slate-700 pb-2">
                <span className="font-bold text-white">Diagnostics (Dev)</span>
                <span className="bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded uppercase">{mode}</span>
            </div>

            <div className="space-y-1">
                <p><span className="text-slate-500">Routing Provider:</span> {prefRoute.debug.provider || 'simulated'}</p>
                <p><span className="text-slate-500">Candidates Generated:</span> {prefRoute.debug.candidate_count || 'N/A'}</p>
                <p><span className="text-slate-500">Selection (Opt 1):</span> {prefRoute.debug.selection_reason}</p>

                {longRoute && longRoute.debug && (
                    <div className="pt-2 mt-2 border-t border-slate-700 border-dashed">
                        <p><span className="text-slate-500">Selection (Opt 2):</span> {longRoute.debug.selection_reason}</p>
                        <p><span className="text-slate-500">Overlap Ratio:</span> {longRoute.debug.overlap ? (longRoute.debug.overlap * 100).toFixed(1) + '%' : 'N/A'}</p>
                        {longRoute.debug.max_allowed && (
                            <p><span className="text-slate-500">Dist Bound limit:</span> {(longRoute.debug.max_allowed / 1000).toFixed(2)}km</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
