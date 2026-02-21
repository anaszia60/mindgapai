import React, { useEffect, useState } from 'react';
import { TrendingUp, AlertTriangle, History, Star } from 'lucide-react';
import axios from 'axios';

const Dashboard = () => {
    const [stats, setStats] = useState({ weak_topics: [], history: [] });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axios.get('http://localhost:5000/api/stats');
                setStats(response.data);
            } catch (error) {
                console.error('Error fetching stats:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (loading) return <div className="mt-20 text-center">Loading dashboard...</div>;

    return (
        <div className="mt-24 max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-2 gap-8 pb-20">
            {/* Weak Topics */}
            <div className="glass-card h-fit">
                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6 text-amber-500" />
                    Weak Topics (Knowledge Gaps)
                </h3>
                <div className="space-y-4">
                    {stats.weak_topics.length > 0 ? (
                        stats.weak_topics.map((item, idx) => (
                            <div key={idx} className="flex items-center justify-between p-4 rounded-xl bg-slate-900/50 border border-slate-700">
                                <span className="font-medium">{item.topic}</span>
                                <span className="text-xs font-bold px-2 py-1 bg-amber-500/10 text-amber-500 rounded-md">
                                    Failed {item.frequency} times
                                </span>
                            </div>
                        ))
                    ) : (
                        <p className="text-slate-500 text-center py-4">No knowledge gaps detected yet! Keep it up.</p>
                    )}
                </div>
            </div>

            {/* Performance History */}
            <div className="glass-card">
                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                    <History className="w-6 h-6 text-blue-500" />
                    Learning History
                </h3>
                <div className="space-y-4">
                    {stats.history.length > 0 ? (
                        stats.history.map((item, idx) => (
                            <div key={idx} className="p-4 rounded-xl bg-slate-900/50 border border-slate-700 hover:border-blue-500/30 transition-all cursor-default">
                                <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-bold">{item.topic}</h4>
                                    <span className={`text-xs font-bold px-2 py-1 rounded-md uppercase ${item.level === 'beginner' ? 'bg-green-500/10 text-green-500' :
                                            item.level === 'intermediate' ? 'bg-blue-500/10 text-blue-500' :
                                                'bg-purple-500/10 text-purple-500'
                                        }`}>
                                        {item.level}
                                    </span>
                                </div>
                                <div className="flex items-center justify-between text-sm text-slate-400">
                                    <span>{item.date.split(' ')[0]}</span>
                                    <div className="flex items-center gap-1">
                                        <Star className={`w-4 h-4 ${item.score / item.total >= 0.7 ? 'text-yellow-500' : 'text-slate-600'}`} />
                                        <span className="font-bold text-slate-200">{item.score}/{item.total}</span>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p className="text-slate-500 text-center py-4">No history available yet.</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
