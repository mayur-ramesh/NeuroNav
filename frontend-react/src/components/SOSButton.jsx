import { useState } from 'react';

export default function SOSButton() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="mt-4 border-t border-slate-200 pt-4">
            <button
                onClick={() => setIsOpen(true)}
                className="w-full bg-red-50 text-red-700 font-bold py-3 px-4 rounded-xl border-2 border-red-200 hover:bg-red-100 transition-colors flex items-center justify-center space-x-2"
            >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span>Emergency SOS</span>
            </button>

            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/50 p-4">
                    <div className="bg-white rounded-2xl w-full max-w-sm overflow-hidden shadow-2xl animate-in fade-in zoom-in duration-200">
                        <div className="bg-red-600 p-4 text-center">
                            <h2 className="text-xl font-bold text-white">Emergency Assistance</h2>
                        </div>
                        <div className="p-6 space-y-4">
                            <p className="text-slate-700 font-medium text-center">Do you need immediate medical help?</p>

                            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
                                <p className="text-xs text-slate-500 uppercase font-bold mb-1">Nearest Hospitals</p>
                                <ul className="text-sm space-y-1 text-slate-700">
                                    <li>• Singapore General Hospital (SGH)</li>
                                    <li>• Tan Tock Seng Hospital (TTSH)</li>
                                    <li>• National University Hospital (NUH)</li>
                                </ul>
                            </div>

                            <a href="tel:995" className="block w-full bg-red-600 text-white text-center font-bold py-4 rounded-xl text-lg hover:bg-red-700 shadow-lg">
                                Call 995 Now
                            </a>

                            <button
                                onClick={() => setIsOpen(false)}
                                className="w-full py-2 text-slate-500 font-medium hover:text-slate-800"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
