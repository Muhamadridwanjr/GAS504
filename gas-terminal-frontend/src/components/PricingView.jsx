import React, { useState, useEffect } from 'react';
import {
    Zap, Check, Star, Shield, Trophy,
    ChevronRight, ArrowUpRight, Crown,
    Clock, Flame, ShoppingCart
} from 'lucide-react';
import { fetchTiers, fetchBillingStatus, subscribeTier, buyBooster } from '../services/api';
import { useAuth } from '../context/AuthContext';

const PricingView = () => {
    const { user } = useAuth();
    const [tiers, setTiers] = useState({});
    const [billing, setBilling] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isAnnual, setIsAnnual] = useState(false);
    const [processing, setProcessing] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            const [tiersData, billingData] = await Promise.all([
                fetchTiers(),
                user ? fetchBillingStatus(user.id) : null
            ]);
            setTiers(tiersData);
            setBilling(billingData);
            setLoading(false);
        };
        loadData();
    }, [user]);

    const handleSubscribe = async (tierId) => {
        if (!user) return;
        setProcessing(tierId);
        const res = await subscribeTier(user.id, tierId, isAnnual ? 'annual' : 'monthly');
        if (res.status === 'success') {
            const updatedBilling = await fetchBillingStatus(user.id);
            setBilling(updatedBilling);
        }
        setProcessing(null);
    };

    const handleBuyBooster = async (packId) => {
        if (!user) return;
        setProcessing(packId);
        const res = await buyBooster(user.id, packId);
        if (res.status === 'success') {
            const updatedBilling = await fetchBillingStatus(user.id);
            setBilling(updatedBilling);
        }
        setProcessing(null);
    };

    if (loading) return (
        <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-yellow-400"></div>
        </div>
    );

    const levelProgress = billing ? (billing.level_score % 100) : 0; // Simplified progress UI

    return (
        <div className="p-4 md:p-8 space-y-12 pb-24 max-w-7xl mx-auto">
            {/* Header / XP Section */}
            <div className="flex flex-col md:flex-row gap-8 items-start justify-between">
                <div className="space-y-2">
                    <h1 className="text-4xl font-black tracking-tight font-display">
                        GAS <span className="text-yellow-400">MONETIZATION</span>
                    </h1>
                    <p className="text-sm text-[var(--text-dim)] uppercase tracking-widest font-bold">
                        LEVEL UP YOUR TRADING WITH AI POWER
                    </p>
                </div>

                {billing && (
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6 w-full md:w-96 shadow-2xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-3">
                            <Trophy className="text-yellow-400/20 group-hover:text-yellow-400/40 transition-colors" size={48} />
                        </div>
                        <div className="relative z-10 flex items-center gap-4 mb-4">
                            <div className="w-12 h-12 bg-yellow-400 rounded-xl flex items-center justify-center text-black font-black text-xl">
                                {billing.level}
                            </div>
                            <div>
                                <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">Level Progress</p>
                                <p className="text-lg font-bold">{billing.level_score} XP <span className="text-sm font-normal text-[var(--text-dim)]">/ Next Level</span></p>
                            </div>
                        </div>
                        <div className="h-2 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-yellow-400 to-yellow-600 transition-all duration-1000"
                                style={{ width: `${levelProgress}%` }}
                            />
                        </div>
                        <div className="mt-4 flex justify-between text-[10px] font-bold text-[var(--text-dim)] uppercase tracking-tight">
                            <span>Current: {billing.tier}</span>
                            <span>{billing.quota} Monthly · {billing.boost} Boosters</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Pricing Toggle */}
            <div className="flex flex-col items-center gap-6">
                <div className="flex items-center gap-4 bg-[var(--bg-card)] border border-[var(--border-color)] p-1 rounded-full">
                    <button
                        onClick={() => setIsAnnual(false)}
                        className={`px-6 py-2 rounded-full text-xs font-bold transition-all ${!isAnnual ? 'bg-yellow-400 text-black shadow-lg' : 'text-[var(--text-dim)] hover:text-white'}`}
                    >
                        Bulanan
                    </button>
                    <button
                        onClick={() => setIsAnnual(true)}
                        className={`px-6 py-2 rounded-full text-xs font-bold transition-all ${isAnnual ? 'bg-yellow-400 text-black shadow-lg' : 'text-[var(--text-dim)] hover:text-white'}`}
                    >
                        Tahunan <span className="ml-1 text-[10px] opacity-75">(Save 10%)</span>
                    </button>
                </div>
            </div>

            {/* Pricing Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                {Object.entries(tiers).map(([id, tier]) => (
                    <div key={id} className={`bg-[var(--bg-card)] border-2 rounded-3xl p-8 flex flex-col gap-6 transition-all hover:scale-[1.02] hover:shadow-2xl relative overflow-hidden ${billing?.tier === id ? 'border-yellow-400' : 'border-[var(--border-color)]'}`}>
                        {id === 'premium' && (
                            <div className="absolute top-4 right-4 bg-yellow-400 text-black text-[10px] font-black px-2 py-1 rounded italic">BEST VALUE</div>
                        )}
                        <div className="space-y-1">
                            <p className="text-[10px] text-yellow-400 font-black uppercase tracking-[0.2em]">{tier.name}</p>
                            <div className="flex items-baseline gap-1">
                                <span className="text-4xl font-black">${isAnnual ? tier.annual_price : tier.monthly_price}</span>
                                <span className="text-[var(--text-dim)] text-xs font-bold">/{isAnnual ? 'yr' : 'mo'}</span>
                            </div>
                        </div>

                        <div className="space-y-4 flex-1">
                            <div className="flex items-center gap-2 text-xs font-bold bg-[var(--bg-panel)] p-2 rounded-lg border border-[var(--border-color)]">
                                <Zap size={14} className="text-yellow-400" />
                                <span>{tier.monthly_quota} Analyses / month</span>
                            </div>
                            <div className="flex items-center gap-2 text-xs font-bold bg-[var(--bg-panel)] p-2 rounded-lg border border-[var(--border-color)]">
                                <Clock size={14} className="text-yellow-400" />
                                <span>{tier.daily_limit} Daily Limit</span>
                            </div>

                            <div className="pt-4 space-y-3">
                                <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">Included Models:</p>
                                {tier.models.map(m => (
                                    <div key={m} className="flex items-center gap-2 text-[11px] font-medium text-[var(--text-primary)]">
                                        <Check size={12} className="text-green-500 shrink-0" />
                                        <span>{m}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <button
                            disabled={processing === id || billing?.tier === id}
                            onClick={() => handleSubscribe(id)}
                            className={`w-full py-4 rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-2 ${billing?.tier === id ? 'bg-[var(--bg-panel)] text-[var(--text-dim)] cursor-default' : 'bg-primary text-secondary hover:bg-yellow-300 active:scale-95 shadow-[0_10px_20px_rgba(250,204,21,0.2)]'}`}
                        >
                            {processing === id ? (
                                <div className="h-4 w-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                            ) : (
                                <>
                                    {billing?.tier === id ? 'PLAN ANDA' : 'PILIH PLAN'}
                                    <ChevronRight size={16} />
                                </>
                            )}
                        </button>
                    </div>
                ))}
            </div>

            {/* Booster Section */}
            <div className="space-y-8">
                <div className="text-center space-y-2">
                    <h2 className="text-3xl font-black font-display">BOOSTER <span className="text-yellow-400">ANALYSIS</span></h2>
                    <p className="text-sm text-[var(--text-dim)] font-bold uppercase tracking-widest">Beli analisa tambahan tanpa kedaluwarsa</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                        { id: 'single', name: '1 Booster', count: 10, price: 0.99, icon: <Flame /> },
                        { id: 'multipack_10', name: '10 Booster', count: 100, price: 8.99, discount: '10% HEMAN', icon: <Star /> },
                        { id: 'multipack_50', name: '50 Booster', count: 500, price: 39.99, discount: '20% HEMAT', icon: <Crown /> }
                    ].map(pack => (
                        <div key={pack.id} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-3xl p-6 flex items-center justify-between group hover:border-yellow-400 transition-all">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-2xl bg-[var(--bg-panel)] border border-[var(--border-color)] flex items-center justify-center text-yellow-400 group-hover:scale-110 transition-transform">
                                    {pack.icon}
                                </div>
                                <div>
                                    <p className="font-black text-lg">{pack.name}</p>
                                    <p className="text-xs text-[var(--text-dim)] font-bold">{pack.count} Analisa</p>
                                    {pack.discount && <span className="text-[9px] bg-green-500/10 text-green-500 font-bold px-1.5 py-0.5 rounded">{pack.discount}</span>}
                                </div>
                            </div>
                            <div className="text-right space-y-2">
                                <p className="text-2xl font-black">${pack.price}</p>
                                <button
                                    disabled={processing === pack.id}
                                    onClick={() => handleBuyBooster(pack.id)}
                                    className="bg-yellow-400 text-black px-4 py-2 rounded-xl text-[10px] font-black hover:bg-yellow-300 transition-all flex items-center gap-2"
                                >
                                    {processing === pack.id ? <div className="h-2 w-2 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : <ShoppingCart size={12} />}
                                    BELI
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Perks/Leveling Details */}
            <div className="bg-gradient-to-br from-[var(--bg-card)] to-[var(--bg-main)] border border-[var(--border-color)] rounded-[3rem] p-12 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-yellow-400/5 blur-[120px] -z-0" />
                <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    <div className="space-y-6">
                        <div className="inline-flex items-center gap-2 bg-yellow-400/10 text-yellow-400 px-4 py-2 rounded-full border border-yellow-400/20">
                            <Shield size={16} />
                            <span className="text-[10px] font-black uppercase tracking-widest">Loyalty Program</span>
                        </div>
                        <h2 className="text-4xl font-black font-display leading-tight">Makin Aktif Trading,<br /><span className="text-yellow-400">Makin Banyak Keuntungan</span></h2>
                        <p className="text-[var(--text-dim)] text-sm leading-relaxed">Sistem leveling kami memberikan reward atas setiap aktivitas Anda di platform. Dapatkan daily analysis tambahan dan diskon booster hingga 20% tanpa biaya tambahan.</p>

                        <div className="grid grid-cols-2 gap-4">
                            {[
                                { l: 'Level 6+', d: '+1 Daily Analysis', s: '5% Off Booster' },
                                { l: 'Level 16+', d: 'Priority Queue', s: '15% Off Booster' }
                            ].map((p, i) => (
                                <div key={i} className="bg-[var(--bg-panel)] p-4 rounded-2xl border border-[var(--border-color)] space-y-1">
                                    <p className="text-xs font-black text-yellow-400">{p.l}</p>
                                    <p className="text-[11px] font-bold">{p.d}</p>
                                    <p className="text-[10px] text-[var(--text-dim)]">{p.s}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-4">
                        <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-[0.3em] mb-8">Cara Mendapatkan XP</p>
                        {[
                            { label: 'Analisa Market', xp: '+1 XP', sub: 'Per satu kali analisa' },
                            { label: 'Signal Profit', xp: '+5 XP', sub: 'Saat signal GAS menyentuh TP' },
                            { label: 'Referral', xp: '+10 XP', sub: 'Undang teman Anda' },
                            { label: 'Daily Login', xp: '+1 XP', sub: 'Bonus harian masuk platform' }
                        ].map((item, i) => (
                            <div key={i} className="flex items-center justify-between p-4 bg-[var(--bg-panel)]/50 border border-[var(--border-color)] rounded-2xl hover:bg-[var(--bg-panel)] transition-colors">
                                <div>
                                    <p className="text-sm font-bold">{item.label}</p>
                                    <p className="text-[10px] text-[var(--text-dim)]">{item.sub}</p>
                                </div>
                                <span className="bg-yellow-400 text-black text-[10px] font-black px-3 py-1 rounded-lg">{item.xp}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PricingView;
