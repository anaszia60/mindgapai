import React from 'react';
import { Brain, LayoutDashboard, Upload, Home } from 'lucide-react';

const Navbar = ({ activeTab, setActiveTab }) => {
    const tabs = [
        { id: 'home', icon: Home, label: 'Home' },
        { id: 'upload', icon: Upload, label: 'Upload' },
        { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    ];

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between glass rounded-2xl px-6 py-3">
                <div className="flex items-center gap-2">
                    <div className="bg-blue-600 p-2 rounded-lg">
                        <Brain className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-xl font-bold tracking-tight">MindGap <span className="text-blue-500">AI</span></span>
                </div>

                <div className="flex items-center gap-4">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all ${activeTab === tab.id
                                    ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <tab.icon className="w-4 h-4" />
                            <span className="text-sm font-medium">{tab.label}</span>
                        </button>
                    ))}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
