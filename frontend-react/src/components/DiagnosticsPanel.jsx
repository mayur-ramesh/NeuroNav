export default function DiagnosticsPanel({ routes, mode }) {
    if (!routes || routes.length === 0) return null;

    const prefRoute = routes[0];
    const longRoute = routes.length > 1 ? routes[1] : null;
    const hasDiag = prefRoute.debug || (longRoute && longRoute.debug);

    if (!hasDiag) return null;

    return (
        <details className="mt-2 group">
            <summary className="cursor-pointer text-sm font-bold text-slate-500 hover:text-slate-700 py-2 flex items-center gap-2">
                <span className="text-xs bg-slate-100 px-2 py-0.5 rounded-md">🔧</span>
                <span>Developer Diagnostics</span>
            </summary>
            <div className="bg-slate-900 text-slate-300 p-4 rounded-xl text-xs font-mono space-y-2 mt-1">
                <div className="flex justify-between items-center mb-2 border-b border-slate-700 pb-2">
                    <span className="font-bold text-white text-sm">Route Analysis</span>
                    <span className="bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded uppercase text-[10px]">{mode}</span>
                </div>

                {prefRoute.debug && (
                    <div className="space-y-1">
                        <p><span className="text-slate-500">Provider:</span> {prefRoute.debug.provider || 'simulated'}</p>
                        <p><span className="text-slate-500">Candidates:</span> {prefRoute.debug.candidate_count || 'N/A'}</p>
                        <p><span className="text-slate-500">Preferred:</span> {prefRoute.debug.selection_reason}</p>
                    </div>
                )}

                {longRoute && longRoute.debug && (
                    <div className="pt-2 mt-2 border-t border-slate-700/50 space-y-1">
                        <p><span className="text-slate-500">Longest:</span> {longRoute.debug.selection_reason}</p>
                        <p><span className="text-slate-500">Overlap:</span> {longRoute.debug.overlap != null ? (longRoute.debug.overlap * 100).toFixed(1) + '%' : 'N/A'}</p>
                        {longRoute.debug.max_allowed && (
                            <p><span className="text-slate-500">Max Dist:</span> {(longRoute.debug.max_allowed / 1000).toFixed(2)} km</p>
                        )}
                    </div>
                )}
            </div>
        </details>
    );
}
