import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Zap, Check, X, Star, Shield, Trophy, Crown, Flame, ShoppingCart,
  Brain, Layers, Newspaper, Plus, CreditCard, Rocket, Medal,
  ChevronRight, ChevronDown, ChevronUp, Bot, BarChart2,
  Copy, Clock, CheckCircle, AlertCircle, ExternalLink, RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

/* ─────────────────────────────────────────────────────────
   DATA
───────────────────────────────────────────────────────── */
const PLANS = [
  {
    id: 'essential',
    emoji: '⚡',
    name: 'Essential',
    badge: null,
    monthlyPrice: 2.99,
    annualPrice: 26.88,
    credits: 100,
    rollover: null,
    models: [
      { name: 'DeepSeek V3.2', mult: '0.8×' },
      { name: 'GPT-5 Mini', mult: '1.0×' },
      { name: 'Grok 4.1 Fast', mult: '1.5×' },
      { name: 'Gemini 2.5 Pro', mult: '5.0×' },
    ],
    brokers: ['MT5 Signal', 'Crypto Signal', 'IDX Daily TF'],
    brokersNo: ['No Equity Sync'],
    ctaLabel: 'Start Essential',
    color: 'var(--text-dim)',
    accentClass: 'border-[var(--border-color)]',
    glowClass: '',
    planMultiplier: '1×',
  },
  {
    id: 'plus',
    emoji: '🚀',
    name: 'Plus',
    badge: null,
    monthlyPrice: 5.99,
    annualPrice: 53.88,
    credits: 200,
    rollover: null,
    models: [
      { name: 'Qwen3.5-35B', mult: '0.5×' },
      { name: 'Gemini 3 Flash', mult: '1.0×' },
      { name: 'Kimi K2.5', mult: '1.5×' },
      { name: 'Gemini 3 Pro', mult: '4.0×' },
    ],
    brokers: ['MT5 Signal', 'Crypto Signal', 'IDX Signal', 'Binance Balance (basic)'],
    brokersNo: [],
    ctaLabel: 'Start Plus',
    color: '#60a5fa',
    accentClass: 'border-blue-500/40',
    glowClass: '',
    planMultiplier: '1.5×',
  },
  {
    id: 'premium',
    emoji: '⭐',
    name: 'Premium',
    badge: 'Most Popular',
    monthlyPrice: 11.99,
    annualPrice: 107.88,
    credits: 400,
    rollover: '1×',
    models: [
      { name: 'Gemini 3.1 Flash Lite', mult: '0.7×' },
      { name: 'Claude Haiku 4.5', mult: '1.0×' },
      { name: 'Gemini 3.1 Pro', mult: '3.0×' },
      { name: 'Claude Opus 4.5', mult: '5.0×' },
    ],
    brokers: ['MT5 Equity', 'Binance Full', 'IDX Real-time', 'Portfolio View'],
    brokersNo: [],
    ctaLabel: 'Start Premium',
    color: 'var(--accent)',
    accentClass: 'border-yellow-400/60',
    glowClass: 'shadow-[0_0_40px_rgba(250,204,21,0.18)]',
    planMultiplier: '2×',
  },
  {
    id: 'ultimate',
    emoji: '👑',
    name: 'Ultimate',
    badge: '👑 Ultimate',
    monthlyPrice: 19.99,
    annualPrice: 179.88,
    credits: 700,
    rollover: '1.5×',
    models: [
      { name: 'Z.ai GLM 5', mult: '0.8×' },
      { name: 'Claude Sonnet 4.6', mult: '1.0×' },
      { name: 'GPT-5.4', mult: '2.0×' },
      { name: 'Claude Opus 4.6', mult: '3.5×' },
    ],
    brokers: ['MT5 Equity', 'Binance Full', '1 Crypto Extra', 'Unified Portfolio', 'EA Signal Trigger', 'REST API Access'],
    brokersNo: [],
    ctaLabel: 'Start Ultimate 👑',
    color: '#a855f7',
    accentClass: 'border-purple-500/50',
    glowClass: 'shadow-[0_0_40px_rgba(168,85,247,0.18)]',
    planMultiplier: '3×',
  },
  {
    id: 'ultra',
    emoji: '🤖',
    name: 'Ultra Ultimate',
    badge: '🤖 Ultra Ultimate',
    monthlyPrice: 39.99,
    annualPrice: 359.88,
    credits: 1500,
    rollover: '2×',
    models: [
      { name: 'Claude Sonnet 4.6', mult: '1.0×' },
      { name: 'GPT-5.4', mult: '1.0×' },
      { name: 'Gemini Pro 3.1', mult: '1.0×' },
      { name: 'Grok 4.2', mult: '1.0×' },
    ],
    brokers: ['All 20 AI Features', '4 AI Agent Slots', 'Polymarket Signal AI (#20)', 'Auto-Trading EA', 'Full API Access', 'Agent Marketplace'],
    brokersNo: [],
    ctaLabel: '🤖 Start Ultra Ultimate',
    color: '#f43f5e',
    accentClass: 'border-rose-500/60',
    glowClass: 'shadow-[0_0_60px_rgba(244,63,94,0.25)]',
    planMultiplier: '5×',
  },
];

const FEATURE_GROUPS = [
  {
    label: 'Core Features',
    features: [
      { name: 'Technical Analysis AI', cr: 3, essential: true, plus: true, premium: true, ultimate: true, ultra: true },
      { name: 'Signal System AI', cr: 3, essential: true, plus: true, premium: true, ultimate: true, ultra: true },
      { name: 'Smart Alert', cr: 1, essential: true, plus: true, premium: true, ultimate: true, ultra: true },
      { name: 'Session Optimizer', cr: 1, essential: true, plus: true, premium: true, ultimate: true, ultra: true },
    ],
  },
  {
    label: 'Market Intelligence',
    features: [
      { name: 'Fundamental Analysis AI', cr: 5, essential: false, plus: true, premium: true, ultimate: true, ultra: true },
      { name: 'Economic Calendar AI', cr: 4, essential: false, plus: true, premium: true, ultimate: true, ultra: true },
      { name: 'Sentiment Market AI', cr: 5, essential: false, plus: true, premium: true, ultimate: true, ultra: true },
      { name: 'Correlation Tracker', cr: 3, essential: false, plus: true, premium: true, ultimate: true, ultra: true },
      { name: 'AI Risk Manager', cr: 3, essential: false, plus: true, premium: true, ultimate: true, ultra: true },
    ],
  },
  {
    label: 'Advanced AI Tools',
    features: [
      { name: 'AI Market Briefing', cr: 10, essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'Hybrid System AI', cr: 8, essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'Drawdown Recovery', cr: 5, essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'Prop Firm Assistant', cr: 8, essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'AI Trade Journal', cr: 8, essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'AI Psychology Coach', cr: 5, essential: false, plus: false, premium: true, ultimate: true, ultra: true },
    ],
  },
  {
    label: 'Ultimate Exclusive',
    features: [
      { name: 'AI Backtesting Engine', cr: 20, essential: false, plus: false, premium: false, ultimate: true, ultra: true },
      { name: 'AI Mentor Mode', cr: 10, essential: false, plus: false, premium: false, ultimate: true, ultra: true },
      { name: 'Multi-Symbol Scanner', cr: 15, essential: false, plus: false, premium: false, ultimate: true, ultra: true },
    ],
  },
  {
    label: '🤖 AI Agent System (Feature #19)',
    features: [
      { name: 'AI Agent Execute (1 Agent)', cr: 5,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Agent Lab Competition', cr: 10, essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Multi-Model (4 Models)', cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Agent Performance Tracker', cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Auto-Disable (Safety)', cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'YAML Agent Config', cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'EA Auto-Trading Integration', cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
    ],
  },
  {
    label: '🔮 Polymarket Signal AI (Feature #20)',
    features: [
      { name: 'Prediction Feed (all markets)', cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Signal AI Prediction (YES/NO)', cr: 5,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'AI Agent Prediction (4 models)', cr: 5, essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Consensus Engine',              cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Category Filter (8 categories)',cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Analytics & History',           cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
      { name: 'Live Probability Updates',      cr: 0,  essential: false, plus: false, premium: false, ultimate: false, ultra: true },
    ],
  },
  {
    label: '🎰 Memecoin Signal AI (Feature #21)',
    features: [
      { name: 'Dexscreener Live Feed',   cr: 0,  essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'Anti-Rug Detection',       cr: 0,  essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'AI Score (0-100)',         cr: 5,  essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: '4-Model AI Signal',        cr: 5,  essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'Multi-Chain (5 chains)',   cr: 0,  essential: false, plus: false, premium: true, ultimate: true, ultra: true },
      { name: 'Auto-Refresh Scanner',     cr: 0,  essential: false, plus: false, premium: true, ultimate: true, ultra: true },
    ],
  },
];

const BOOSTERS = [
  { id: 'bronze', emoji: '🥉', name: 'Bronze Boost', price: 1.99, days: 7,  credits: 50,  xp: 200,  badge: 'Bronze badge 7d',  color: '#cd7f32',         border: 'border-amber-700/50' },
  { id: 'silver', emoji: '🥈', name: 'Silver Boost', price: 4.99, days: 14, credits: 150, xp: 500,  badge: 'Silver badge 14d', color: '#94a3b8',         border: 'border-slate-400/50' },
  { id: 'gold',   emoji: '🥇', name: 'Gold Boost',   price: 9.99, days: 30, credits: 350, xp: 1000, badge: 'Gold badge 30d',   color: 'var(--accent)',   border: 'border-yellow-400/60' },
];

const ADDONS = [
  { id: 'extra_equity', name: 'Extra Equity Slot', price: 1.99, cycle: '/mo', desc: '+1 MT5 or crypto slot', eligible: 'Plus+', icon: Plus },
  { id: 'ctrader', name: 'cTrader Premium Connect', price: 2.99, cycle: '/mo', desc: 'cTrader Open API + FIX API', eligible: 'Premium+', icon: BarChart2 },
  { id: 'metaapi', name: 'MetaApi Cloud Bridge', price: 4.99, cycle: '/mo', desc: 'Any MT5 broker without EA', eligible: 'Premium+', icon: Bot },
  { id: 'idx_rt', name: 'IDX Real-time Upgrade', price: 1.99, cycle: '/mo', desc: 'GoAPI.io intraday IDX data', eligible: 'Plus+', icon: Zap },
  { id: 'ea_signal', name: 'EA Auto-Signal Trigger', price: 1.99, cycle: '/mo', desc: 'Signal push to MT5 chart', eligible: 'Premium+', icon: Rocket },
  { id: 'tv_webhook', name: 'TradingView Webhook Bridge', price: 2.99, cycle: '/mo', desc: 'Webhook + AI analysis trigger', eligible: 'Plus+', icon: ChevronRight },
  { id: 'agent_slot', name: '+1 AI Agent Slot', price: 7.99, cycle: '/mo', desc: 'Extra autonomous trading agent', eligible: 'Ultra+', icon: Bot, isNew: true },
  { id: 'pro_models', name: 'Pro Models Pack', price: 9.99, cycle: '/mo', desc: 'GPT-5.4 + Claude Opus priority access', eligible: 'Ultimate+', icon: Brain, isNew: true },
  { id: 'auto_ea', name: 'Auto Trading EA License', price: 14.99, cycle: '/mo', desc: 'Full auto-execution on MT5 via agent signal', eligible: 'Ultra+', icon: Rocket, isNew: true },
];

const TOPUPS = [
  { id: 'topup_50', credits: 50, price: 0.99 },
  { id: 'topup_150', credits: 150, price: 2.49 },
  { id: 'topup_500', credits: 500, price: 6.99 },
];

const LEVELS = [
  { level: 1,  xp: 0,     emoji: '🌱', label: 'Rookie' },
  { level: 2,  xp: 100,   emoji: '📊', label: 'Apprentice' },
  { level: 3,  xp: 250,   emoji: '⚡', label: 'Trader' },
  { level: 4,  xp: 500,   emoji: '📈', label: 'Analyst' },
  { level: 5,  xp: 850,   emoji: '🎯', label: 'Strategist' },
  { level: 6,  xp: 1300,  emoji: '🔥', label: 'Expert' },
  { level: 7,  xp: 1900,  emoji: '💎', label: 'Master' },
  { level: 8,  xp: 2700,  emoji: '🚀', label: 'Elite' },
  { level: 9,  xp: 3700,  emoji: '👑', label: 'Champion' },
  { level: 10, xp: 5000,  emoji: '🌟', label: 'Legend' },
  { level: 11, xp: 6700,  emoji: '🏆', label: 'Grand Master' },
  { level: 12, xp: 8700,  emoji: '⚔️', label: 'Warrior' },
  { level: 13, xp: 11000, emoji: '🦅', label: 'Eagle' },
  { level: 14, xp: 13700, emoji: '🌊', label: 'Wave Rider' },
  { level: 15, xp: 16800, emoji: '🌙', label: 'Night Hunter' },
  { level: 16, xp: 20300, emoji: '⭐', label: 'All-Star' },
  { level: 17, xp: 24200, emoji: '🎖️', label: 'Commander' },
  { level: 18, xp: 28500, emoji: '🔱', label: 'Admiral' },
  { level: 19, xp: 33200, emoji: '🏅', label: 'Titan' },
  { level: 20, xp: 38300, emoji: '🥇', label: 'GAS GOD 🔑' },
];

const PLAN_MULTIPLIERS = {
  essential: '1×',
  plus: '1.5×',
  premium: '2×',
  ultimate: '3×',
};

/* ─────────────────────────────────────────────────────────
   TABS CONFIG
───────────────────────────────────────────────────────── */
const TABS = [
  { id: 'plans', label: 'Plans', icon: Crown },
  { id: 'features', label: 'Features', icon: Star },
  { id: 'boosters', label: 'Boosters', icon: Flame },
  { id: 'addons', label: 'Add-ons', icon: Plus },
  { id: 'credits', label: 'Credits', icon: CreditCard },
  { id: 'leveling', label: 'Leveling', icon: Trophy },
];

/* ─────────────────────────────────────────────────────────
   HELPERS
───────────────────────────────────────────────────────── */
function CheckIcon() {
  return <Check size={14} className="text-[var(--success)] shrink-0" />;
}
function CrossIcon() {
  return <X size={14} className="text-[var(--text-dim)]/40 shrink-0" />;
}

function PlanBadge({ plan }) {
  if (plan.id === 'ultimate') {
    return (
      <span className="inline-flex items-center gap-1 bg-purple-500/20 text-purple-300 text-[9px] font-black px-2 py-0.5 rounded-full border border-purple-500/30 uppercase tracking-widest">
        <Crown size={9} /> Ultimate
      </span>
    );
  }
  if (plan.badge === 'Most Popular') {
    return (
      <span className="inline-flex items-center gap-1 bg-yellow-400/20 text-[var(--accent)] text-[9px] font-black px-2 py-0.5 rounded-full border border-yellow-400/30 uppercase tracking-widest">
        <Star size={9} /> Most Popular
      </span>
    );
  }
  return null;
}

/* ─────────────────────────────────────────────────────────
   ERC20 PAYMENT MODAL
───────────────────────────────────────────────────────── */
function ERC20PaymentModal({ invoice, onClose, onSuccess }) {
  const [copied, setCopied] = useState('');
  const [status, setStatus] = useState('pending'); // pending | confirmed | expired | error
  const [timeLeft, setTimeLeft] = useState(0);
  const [txHash, setTxHash] = useState('');
  const [manualHash, setManualHash] = useState('');
  const [verifying, setVerifying] = useState(false);
  const pollRef = useRef(null);

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(key);
      setTimeout(() => setCopied(''), 2000);
    });
  };

  // Countdown timer
  useEffect(() => {
    if (!invoice?.expires_unix) return;
    const update = () => {
      const left = Math.max(0, invoice.expires_unix - Math.floor(Date.now() / 1000));
      setTimeLeft(left);
      if (left === 0) setStatus('expired');
    };
    update();
    const iv = setInterval(update, 1000);
    return () => clearInterval(iv);
  }, [invoice?.expires_unix]);

  // Auto-poll payment status every 10s
  useEffect(() => {
    if (!invoice?.order_id) return;
    const poll = async () => {
      // Always read fresh token in case it was refreshed
      const token = localStorage.getItem('gas-token') || '';
      if (!token) return; // not logged in, skip
      try {
        const res = await axios.get(`/web/api/v1/payments/erc20/status/${invoice.order_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.data?.status === 'completed') {
          setStatus('confirmed');
          setTxHash(res.data.tx_hash || '');
          clearInterval(pollRef.current);
          setTimeout(() => { onSuccess && onSuccess(res.data); onClose(); }, 3000);
        } else if (res.data?.status === 'expired') {
          setStatus('expired');
          clearInterval(pollRef.current);
        }
      } catch (e) {
        // 401 = token expired, stop polling — user must re-login
        if (e?.response?.status === 401) {
          clearInterval(pollRef.current);
        }
        // other errors: silent, retry next interval
      }
    };
    pollRef.current = setInterval(poll, 10000);
    poll(); // immediate first check
    return () => clearInterval(pollRef.current);
  }, [invoice?.order_id]);

  const handleManualVerify = async () => {
    if (!manualHash.trim()) return;
    setVerifying(true);
    try {
      const token = localStorage.getItem('gas-token') || '';
      const res = await axios.post('/web/api/v1/payments/erc20/verify', {
        order_id: invoice.order_id,
        tx_hash: manualHash.trim(),
      }, { headers: { Authorization: `Bearer ${token}` } });
      if (res.data?.status === 'confirmed') {
        setStatus('confirmed');
        setTxHash(manualHash.trim());
        clearInterval(pollRef.current);
        setTimeout(() => { onSuccess && onSuccess(res.data); onClose(); }, 2500);
      }
    } catch (e) {
      const detail = e?.response?.data?.detail || 'TX tidak ditemukan atau jumlah tidak cocok';
      alert('Verifikasi gagal: ' + detail);
    } finally {
      setVerifying(false);
    }
  };

  const mins = String(Math.floor(timeLeft / 60)).padStart(2, '0');
  const secs = String(timeLeft % 60).padStart(2, '0');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-md bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-yellow-400/15 border border-yellow-400/30 flex items-center justify-center">
              <span className="text-base">₮</span>
            </div>
            <div>
              <p className="text-sm font-black text-[var(--text-primary)]">Bayar dengan USDT ERC-20</p>
              <p className="text-[10px] text-[var(--text-dim)] font-bold">{invoice?.package} · {invoice?.credits} Credits</p>
            </div>
          </div>
          <button onClick={onClose} className="w-7 h-7 rounded-lg bg-[var(--bg-hover)] flex items-center justify-center hover:bg-red-500/20 transition-colors">
            <X size={14} className="text-[var(--text-dim)]" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {status === 'confirmed' ? (
            <div className="text-center py-6 space-y-3">
              <div className="w-16 h-16 rounded-full bg-green-500/15 border border-green-500/30 flex items-center justify-center mx-auto">
                <CheckCircle size={32} className="text-green-400" />
              </div>
              <p className="text-lg font-black text-green-400">Pembayaran Terkonfirmasi!</p>
              <p className="text-xs text-[var(--text-dim)]">Plan & credits sudah diaktifkan. Halaman akan refresh otomatis.</p>
              {txHash && <p className="text-[10px] font-mono text-[var(--text-dim)] break-all">{txHash}</p>}
            </div>
          ) : status === 'expired' ? (
            <div className="text-center py-6 space-y-3">
              <AlertCircle size={40} className="text-red-400 mx-auto" />
              <p className="text-base font-black text-red-400">Invoice Kadaluarsa</p>
              <p className="text-xs text-[var(--text-dim)]">Buat invoice baru untuk melanjutkan pembayaran.</p>
              <button onClick={onClose} className="px-4 py-2 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/30 text-[var(--accent)] text-xs font-black">
                Buat Invoice Baru
              </button>
            </div>
          ) : (
            <>
              {/* Timer */}
              <div className="flex items-center justify-between bg-[var(--bg-panel)] rounded-xl px-4 py-2.5">
                <div className="flex items-center gap-2 text-[var(--text-dim)]">
                  <Clock size={13} />
                  <span className="text-[11px] font-bold">Berlaku selama</span>
                </div>
                <span className={`font-black font-mono text-sm ${timeLeft < 300 ? 'text-red-400' : 'text-[var(--accent)]'}`}>
                  {mins}:{secs}
                </span>
              </div>

              {/* Network badge */}
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[9px] font-black bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2.5 py-1 rounded-full uppercase tracking-widest">Ethereum ERC-20</span>
                <span className="text-[9px] font-black bg-green-500/10 text-green-400 border border-green-500/20 px-2.5 py-1 rounded-full uppercase tracking-widest">USDT Only</span>
                <span className="text-[9px] font-black bg-yellow-400/10 text-[var(--accent)] border border-yellow-400/20 px-2.5 py-1 rounded-full uppercase tracking-widest">Auto-detect</span>
              </div>

              {/* Amount */}
              <div className="bg-[var(--bg-panel)] border border-yellow-400/20 rounded-xl p-4">
                <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-1">Jumlah TEPAT yang harus dikirim</p>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-2xl font-black font-mono text-[var(--accent)]">{invoice?.amount_usdt} USDT</span>
                  <button
                    onClick={() => copyToClipboard(invoice?.amount_usdt, 'amount')}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-yellow-400/10 border border-yellow-400/20 text-[var(--accent)] text-[10px] font-black hover:bg-yellow-400/20 transition-colors"
                  >
                    {copied === 'amount' ? <Check size={11} /> : <Copy size={11} />}
                    {copied === 'amount' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <p className="text-[9px] text-red-400 font-bold mt-2">⚠️ Kirim jumlah TEPAT ini. Jumlah berbeda tidak akan terdeteksi.</p>
              </div>

              {/* Wallet */}
              <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-4">
                <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-1">Wallet Tujuan</p>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-[11px] font-mono text-[var(--text-secondary)] break-all leading-relaxed">{invoice?.wallet_address}</span>
                  <button
                    onClick={() => copyToClipboard(invoice?.wallet_address, 'wallet')}
                    className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--bg-hover)] border border-[var(--border-color)] text-[var(--text-dim)] text-[10px] font-black hover:border-[var(--accent)]/40 transition-colors"
                  >
                    {copied === 'wallet' ? <Check size={11} /> : <Copy size={11} />}
                    {copied === 'wallet' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
              </div>

              {/* Auto-polling indicator */}
              <div className="flex items-center gap-2 text-[var(--text-dim)]">
                <RefreshCw size={11} className="animate-spin" />
                <p className="text-[10px] font-bold">Memantau blockchain setiap 10 detik...</p>
              </div>

              {/* Manual TX verify */}
              <div className="border-t border-[var(--border-color)] pt-4 space-y-2">
                <p className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest">Sudah bayar? Paste TX Hash untuk verifikasi manual:</p>
                <div className="flex gap-2">
                  <input
                    value={manualHash}
                    onChange={e => setManualHash(e.target.value)}
                    placeholder="0x..."
                    className="flex-1 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl px-3 py-2 text-xs font-mono outline-none focus:border-[var(--accent)] text-[var(--text-primary)]"
                  />
                  <button
                    onClick={handleManualVerify}
                    disabled={!manualHash.trim() || verifying}
                    className="px-4 py-2 rounded-xl bg-[var(--accent)] text-black text-[10px] font-black hover:opacity-90 disabled:opacity-40 transition-all"
                  >
                    {verifying ? <RefreshCw size={12} className="animate-spin" /> : 'Verify'}
                  </button>
                </div>
              </div>

              {/* Bank Transfer Alternative */}
              {invoice?.bank_account && (
                <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-4">
                  <p className="text-[9px] font-black uppercase tracking-widest text-green-400 mb-2">🏦 Atau Transfer Bank (IDR)</p>
                  <p className="text-[11px] font-mono font-black text-[var(--text-primary)] break-all">{invoice.bank_account}</p>
                  <p className="text-[9px] text-[var(--text-dim)] font-bold mt-1.5">Setelah transfer, kirim bukti ke <span className="text-[var(--accent)]">support@gasstrategyai.xyz</span></p>
                </div>
              )}

              {/* Email confirmation notice */}
              <div className="flex items-start gap-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl px-3 py-2.5">
                <span className="text-xs mt-0.5">📧</span>
                <p className="text-[10px] text-[var(--text-dim)] font-bold leading-relaxed">
                  Detail invoice dikirim ke email kamu. Cek inbox untuk instruksi lengkap pembayaran.
                </p>
              </div>

              {/* Info */}
              <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl px-4 py-3">
                <p className="text-[10px] text-blue-400 font-bold leading-relaxed">
                  💡 Gunakan <strong>jaringan Ethereum</strong> saja. Jangan kirim via BSC, Tron, atau jaringan lain. Konfirmasi blockchain biasanya 1-5 menit.
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────
   MAIN COMPONENT
───────────────────────────────────────────────────────── */
const PricingView = ({ publicMode = false }) => {
  let authContext = null;
  try { authContext = useAuth(); } catch(e) {}
  const user = authContext?.user;
  const userPlan = authContext?.userPlan || 'free';
  const isAdmin = authContext?.isAdmin || false;
  const [isAnnual, setIsAnnual] = useState(false);
  const [processing, setProcessing] = useState(null);
  const [activeTab, setActiveTab] = useState('plans');
  const [billingStatus, setBillingStatus] = useState(null);
  const [paymentError, setPaymentError] = useState(null);
  const [paymentSuccess, setPaymentSuccess] = useState(null);
  const [invoice, setInvoice] = useState(null); // active ERC20 invoice

  // Fetch real billing status
  useEffect(() => {
    if (publicMode || !user) return;
    const token = user?.token || localStorage.getItem('gas-token');
    if (!token) return;
    axios.get('/web/api/v1/billing/status', {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => setBillingStatus(r.data)).catch(() => {});
  }, [user, publicMode]);

  const PLAN_CREDIT_TOTAL = { free: 20, trial: 10, essential: 100, plus: 200, premium: 400, ultimate: 700, ultra: 1500 };
  const mockStatus = billingStatus ? {
    plan: billingStatus.plan || 'free',
    credits: billingStatus.credits,
    creditsTotal: PLAN_CREDIT_TOTAL[billingStatus.plan] || 20,
    level: billingStatus.level || 1,
    xp: billingStatus.xp || 0,
    nextLevelXp: billingStatus.xp_to_next || 100,
    xpLabel: LEVELS[Math.min((billingStatus.level || 1) - 1, LEVELS.length - 1)]?.label || 'Rookie',
    is_admin: billingStatus.is_admin || false,
    is_trial: billingStatus.is_trial || false,
    trial_expires_dt: billingStatus.trial_expires_dt || '',
    booster: billingStatus.booster || '',
    booster_expires_ts: billingStatus.booster_expires_ts || 0,
  } : {
    plan: 'free',
    credits: 10,
    creditsTotal: 10,
    level: 1,
    xp: 0,
    nextLevelXp: 100,
    xpLabel: 'Rookie',
    is_admin: false,
    is_trial: false,
    trial_expires_dt: '',
    booster: '',
    booster_expires_ts: 0,
  };

  const handleCryptoPurchase = async (packageId, label) => {
    if (!user) {
      setPaymentError('Silakan login terlebih dahulu untuk membeli.');
      return;
    }
    setPaymentError(null);
    setPaymentSuccess(null);
    setProcessing(packageId);
    try {
      const token = localStorage.getItem('gas-token') || '';
      const res = await axios.post('/web/api/v1/payments/erc20/create-invoice', {
        package_id: packageId,
      }, { headers: { Authorization: `Bearer ${token}` } });

      // Admin bypass — backend instantly activates without payment
      if (res.data?.admin_bypass) {
        const msg = res.data.message || `✅ ${label} diaktifkan!`;
        setPaymentSuccess(msg);
        // Refresh billing status so UI shows updated plan/credits
        axios.get('/web/api/v1/billing/status', {
          headers: { Authorization: `Bearer ${token}` }
        }).then(r => setBillingStatus(r.data)).catch(() => {});
        setTimeout(() => setPaymentSuccess(null), 6000);
        return;
      }

      if (res.data?.order_id) {
        // Show ERC20 payment modal
        setInvoice(res.data);
      } else {
        setPaymentError('Gagal membuat invoice: response tidak valid dari server.');
      }
    } catch (e) {
      const detail = e?.response?.data?.detail || e.message || 'Unknown error';
      const status = e?.response?.status;
      if (status === 502 || status === 503) {
        setPaymentError('Payment gateway tidak tersedia. Coba beberapa saat lagi atau hubungi support.');
      } else if (status === 401) {
        setPaymentError('Sesi login habis. Silakan login ulang.');
      } else if (status === 400) {
        setPaymentError(`Package tidak valid: ${detail}`);
      } else {
        setPaymentError(`Gagal membuat invoice: ${detail}`);
      }
    } finally {
      setProcessing(null);
    }
  };

  const handleSubscribe = async (planId) => {
    if (!user) {
      setPaymentError('Silakan login terlebih dahulu untuk membeli.');
      return;
    }
    await handleCryptoPurchase(`plan_${planId}`, planId);
  };

  const handleBuyBooster = async (packId) => {
    if (!user) {
      setPaymentError('Silakan login terlebih dahulu untuk membeli.');
      return;
    }
    // packId from BOOSTERS array is "bronze"/"silver"/"gold"
    // backend expects "booster_bronze"/"booster_silver"/"booster_gold"
    const pkgId = packId.startsWith('booster_') ? packId : `booster_${packId}`;
    await handleCryptoPurchase(pkgId, packId);
  };

  const handlePaymentSuccess = useCallback((data) => {
    const xpMsg = data.booster_xp ? ` · +${data.booster_xp} XP` : '';
    const boosterMsg = data.booster ? ` 🏆 ${data.booster.charAt(0).toUpperCase() + data.booster.slice(1)} Badge aktif!` : '';
    const planMsg = data.plan ? ` · Plan: ${data.plan}` : '';
    setPaymentSuccess(`✅ Pembayaran berhasil! +${data.credits_added || ''} credits${xpMsg}${planMsg}${boosterMsg}`);
    // Refresh billing status
    const token = localStorage.getItem('gas-token') || '';
    axios.get('/web/api/v1/billing/status', {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => setBillingStatus(r.data)).catch(() => {});
    setTimeout(() => setPaymentSuccess(null), 8000);
  }, []);

  const xpPct = Math.min(100, Math.round(((mockStatus.xp - (LEVELS[mockStatus.level - 1]?.xp || 0)) / ((LEVELS[mockStatus.level]?.xp || 500) - (LEVELS[mockStatus.level - 1]?.xp || 0))) * 100));

  return (
    <div className="flex flex-col min-h-full bg-[var(--bg-main)]">

      {/* ── ERC20 PAYMENT MODAL ─────────────────────────── */}
      {invoice && (
        <ERC20PaymentModal
          invoice={invoice}
          onClose={() => setInvoice(null)}
          onSuccess={handlePaymentSuccess}
        />
      )}

      {/* ── PAYMENT NOTIFICATIONS ──────────────────────── */}
      {paymentError && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-3 rounded-xl bg-[var(--danger)]/10 border border-[var(--danger)]/40 text-[var(--danger)] text-sm font-bold shadow-2xl max-w-md">
          <X size={16} className="shrink-0" />
          <span>{paymentError}</span>
          <button onClick={() => setPaymentError(null)} className="ml-auto opacity-60 hover:opacity-100"><X size={12} /></button>
        </div>
      )}
      {paymentSuccess && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-3 rounded-xl bg-[var(--success)]/10 border border-[var(--success)]/40 text-[var(--success)] text-sm font-bold shadow-2xl max-w-md">
          <Check size={16} className="shrink-0" />
          <span>{paymentSuccess}</span>
        </div>
      )}

      {/* ── ADMIN BADGE ────────────────────────────────── */}
      {mockStatus.is_admin && (
        <div className="mx-4 mt-3 px-4 py-2 rounded-xl bg-gradient-to-r from-yellow-400/10 to-yellow-600/5 border border-yellow-400/30 flex items-center gap-3">
          <Crown size={16} className="text-[var(--accent)]" />
          <span className="text-xs font-black text-[var(--accent)] uppercase tracking-widest">Admin — Ultimate Full Access · Semua Fitur Aktif · Unlimited Credits</span>
        </div>
      )}

      {/* ── TRIAL BANNER ───────────────────────────────── */}
      {mockStatus.is_trial && (
        <div className="mx-4 mt-3 px-4 py-3 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/5 border border-blue-500/30 flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-500/15 flex items-center justify-center">
              <Zap size={16} className="text-blue-400" />
            </div>
            <div>
              <p className="text-xs font-black text-blue-400 uppercase tracking-wide">🎁 Trial Aktif — 10 Credits · 3 Hari</p>
              {mockStatus.trial_expires_dt && (
                <p className="text-[9px] text-[var(--text-dim)]">Berakhir: {mockStatus.trial_expires_dt}</p>
              )}
            </div>
          </div>
          <button
            onClick={() => setActiveTab('plans')}
            className="text-[9px] font-black px-3 py-1.5 rounded-lg bg-blue-500/20 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 transition-colors uppercase tracking-wide whitespace-nowrap"
          >
            Upgrade Sekarang →
          </button>
        </div>
      )}

      {/* ── ACTIVE BOOSTER BADGE ───────────────────────── */}
      {mockStatus.booster && (
        <div className="mx-4 mt-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500/10 to-amber-600/5 border border-amber-500/30 flex items-center gap-3">
          <span className="text-base">{mockStatus.booster === 'gold' ? '🥇' : mockStatus.booster === 'silver' ? '🥈' : '🥉'}</span>
          <span className="text-xs font-black text-amber-400 uppercase tracking-wide capitalize">{mockStatus.booster} Booster Aktif</span>
          {mockStatus.booster_expires_ts > 0 && (
            <span className="text-[9px] text-[var(--text-dim)] ml-auto">
              s/d {new Date(mockStatus.booster_expires_ts * 1000).toLocaleDateString('id-ID')}
            </span>
          )}
        </div>
      )}

      {/* ── TOP STATUS CARD ─────────────────────────────── */}
      {!publicMode && (
      <div className="border-b border-[var(--border-color)] bg-[var(--bg-card)] px-4 py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center gap-4">
          {/* Plan status */}
          <div className="flex items-center gap-4 flex-1">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400/20 to-yellow-600/10 border border-yellow-400/30 flex items-center justify-center shrink-0">
              <Crown size={22} className="text-[var(--accent)]" />
            </div>
            <div>
              <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">Current Plan</p>
              <p className="text-base font-black capitalize text-[var(--text-primary)]">
                {mockStatus.plan === 'trial' ? '🎁 Trial' : mockStatus.plan}
                {' '}<span className={`font-normal text-xs ${mockStatus.is_trial ? 'text-blue-400' : 'text-[var(--text-dim)]'}`}>
                  {mockStatus.is_trial ? '· 3 Hari' : '· Active'}
                </span>
              </p>
            </div>
          </div>
          {/* Credits */}
          <div className="flex items-center gap-4 flex-1">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">Credits Used</p>
                <p className="text-[10px] font-black text-[var(--text-primary)]">{mockStatus.credits} / {mockStatus.creditsTotal} cr</p>
              </div>
              <div className="h-2 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-yellow-400 to-yellow-500 transition-all duration-700"
                  style={{ width: `${(mockStatus.credits / mockStatus.creditsTotal) * 100}%` }}
                />
              </div>
            </div>
          </div>
          {/* Level */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)] flex items-center justify-center text-lg font-black text-[var(--accent)]">
              {mockStatus.level}
            </div>
            <div>
              <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">Level · {mockStatus.xpLabel}</p>
              <div className="flex items-center gap-2 mt-0.5">
                <div className="w-24 h-1.5 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full transition-all duration-700" style={{ width: `${xpPct}%` }} />
                </div>
                <p className="text-[9px] font-bold text-[var(--text-dim)]">{mockStatus.xp} XP</p>
              </div>
            </div>
          </div>
          {/* Upgrade CTA */}
          <button
            onClick={() => setActiveTab('plans')}
            className="shrink-0 flex items-center gap-2 bg-yellow-400 hover:bg-yellow-300 text-black text-xs font-black px-4 py-2 rounded-lg transition-all active:scale-95 shadow-[0_0_20px_rgba(250,204,21,0.2)]"
          >
            <Rocket size={14} /> Upgrade
          </button>
        </div>
      </div>
      )}

      {/* ── TABS ─────────────────────────────────────────── */}
      <div className="border-b border-[var(--border-color)] bg-[var(--bg-card)] sticky top-0 z-20">
        <div className="max-w-7xl mx-auto flex gap-0 overflow-x-auto scrollbar-none">
          {TABS.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-5 py-3.5 text-[11px] font-black uppercase tracking-widest shrink-0 border-b-2 transition-all
                  ${isActive
                    ? 'border-yellow-400 text-[var(--accent)] bg-yellow-400/5'
                    : 'border-transparent text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'
                  }`}
              >
                <Icon size={13} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── CONTENT ──────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 py-8 pb-24 space-y-10">

          {/* ════════════════════ PLANS TAB ════════════════ */}
          {activeTab === 'plans' && (
            <>
              {/* Header */}
              <div className="text-center space-y-2">
                <h1 className="text-3xl font-black font-display tracking-tight">
                  GAS <span className="text-[var(--accent)]">AI PLANS</span>
                </h1>
                <p className="text-xs text-[var(--text-dim)] font-bold uppercase tracking-widest">
                  Choose the plan that powers your edge
                </p>
              </div>

              {/* Billing toggle */}
              <div className="flex justify-center">
                <div className="flex items-center gap-1 bg-[var(--bg-card)] border border-[var(--border-color)] p-1 rounded-full">
                  <button
                    onClick={() => setIsAnnual(false)}
                    className={`px-5 py-2 rounded-full text-[11px] font-black transition-all ${!isAnnual ? 'bg-yellow-400 text-black shadow-lg' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}
                  >
                    Monthly
                  </button>
                  <button
                    onClick={() => setIsAnnual(true)}
                    className={`flex items-center gap-1.5 px-5 py-2 rounded-full text-[11px] font-black transition-all ${isAnnual ? 'bg-yellow-400 text-black shadow-lg' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}
                  >
                    Annual
                    <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-black ${isAnnual ? 'bg-black/20 text-black' : 'bg-green-500/20 text-green-400'}`}>SAVE 25%</span>
                  </button>
                </div>
              </div>

              {/* Plan cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
                {PLANS.map(plan => {
                  const isCurrent = plan.id === userPlan;
                  const price = isAnnual ? plan.annualPrice : plan.monthlyPrice;
                  const isProcessing = processing === plan.id;
                  const isPremium = plan.id === 'premium';
                  const isUltimate = plan.id === 'ultimate';

                  return (
                    <div
                      key={plan.id}
                      className={`relative flex flex-col rounded-2xl border-2 overflow-hidden transition-all duration-300 hover:translate-y-[-2px] bg-[var(--bg-card)]
                        ${isPremium ? 'border-yellow-400/60 ' + plan.glowClass : ''}
                        ${isUltimate ? 'border-purple-500/50 ' + plan.glowClass : ''}
                        ${!isPremium && !isUltimate ? plan.accentClass : ''}
                        ${isCurrent ? 'ring-2 ring-yellow-400/40' : ''}
                      `}
                    >
                      {/* Glow overlay for premium */}
                      {isPremium && (
                        <div className="absolute inset-0 bg-gradient-to-b from-yellow-400/5 via-transparent to-transparent pointer-events-none" />
                      )}
                      {isUltimate && (
                        <div className="absolute inset-0 bg-gradient-to-b from-purple-500/5 via-transparent to-transparent pointer-events-none" />
                      )}

                      {/* Badge */}
                      {plan.badge && (
                        <div className={`absolute top-3 right-3 z-10 ${isPremium ? 'bg-yellow-400 text-black' : 'bg-purple-500 text-white'} text-[9px] font-black px-2 py-1 rounded-full uppercase tracking-widest`}>
                          {plan.badge}
                        </div>
                      )}

                      <div className="p-6 flex flex-col gap-5 flex-1 relative z-10">
                        {/* Plan name */}
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xl">{plan.emoji}</span>
                            <span className="text-sm font-black uppercase tracking-widest" style={{ color: plan.color }}>{plan.name}</span>
                          </div>
                          {isCurrent && (
                            <span className="inline-flex items-center gap-1 bg-yellow-400/15 text-[var(--accent)] text-[9px] font-black px-2 py-0.5 rounded-full border border-yellow-400/25 uppercase tracking-widest">
                              <Check size={8} /> Current Plan
                            </span>
                          )}
                        </div>

                        {/* Price */}
                        <div>
                          <div className="flex items-baseline gap-1">
                            <span className="text-4xl font-black text-[var(--text-primary)]">${price.toFixed(2)}</span>
                            <span className="text-xs text-[var(--text-dim)] font-bold">/{isAnnual ? 'yr' : 'mo'}</span>
                          </div>
                          {isAnnual && (
                            <p className="text-[10px] text-green-400 font-bold mt-0.5">
                              ${plan.monthlyPrice.toFixed(2)}/mo · Save 25%
                            </p>
                          )}
                        </div>

                        {/* Credits */}
                        <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl px-3 py-2.5">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <Zap size={12} className="text-[var(--accent)]" />
                              <span className="text-[11px] font-black text-[var(--text-primary)]">{plan.credits} cr / mo</span>
                            </div>
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${plan.rollover ? 'bg-blue-500/15 text-blue-400' : 'bg-[var(--bg-hover)] text-[var(--text-dim)]'}`}>
                              {plan.rollover ? `${plan.rollover} rollover` : 'No rollover'}
                            </span>
                          </div>
                        </div>

                        {/* AI Models */}
                        <div>
                          <p className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest mb-2">AI Models</p>
                          <div className="space-y-1.5">
                            {plan.models.map(m => (
                              <div key={m.name} className="flex items-center justify-between">
                                <div className="flex items-center gap-1.5">
                                  <Bot size={10} className="text-[var(--text-dim)] shrink-0" />
                                  <span className="text-[10px] font-bold text-[var(--text-secondary)]">{m.name}</span>
                                </div>
                                <span className="text-[9px] font-black bg-[var(--bg-panel)] border border-[var(--border-color)] px-1.5 py-0.5 rounded text-[var(--text-dim)]">{m.mult}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Brokers */}
                        <div>
                          <p className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest mb-2">Broker Access</p>
                          <div className="space-y-1">
                            {plan.brokers.map(b => (
                              <div key={b} className="flex items-center gap-1.5">
                                <Check size={10} className="text-[var(--success)] shrink-0" />
                                <span className="text-[10px] text-[var(--text-secondary)]">{b}</span>
                              </div>
                            ))}
                            {plan.brokersNo.map(b => (
                              <div key={b} className="flex items-center gap-1.5">
                                <X size={10} className="text-[var(--text-dim)]/40 shrink-0" />
                                <span className="text-[10px] text-[var(--text-dim)]">{b}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Features summary */}
                        <div className="flex-1">
                          <p className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest mb-2">Key Features</p>
                          <div className="space-y-1">
                            {FEATURE_GROUPS.flatMap(g => g.features)
                              .filter(f => f[plan.id])
                              .slice(0, 6)
                              .map(f => (
                                <div key={f.name} className="flex items-center gap-1.5">
                                  <Check size={10} className="text-[var(--success)] shrink-0" />
                                  <span className="text-[10px] text-[var(--text-secondary)]">{f.name} <span className="text-[var(--text-dim)]">({f.cr} cr)</span></span>
                                </div>
                              ))}
                            {FEATURE_GROUPS.flatMap(g => g.features).filter(f => f[plan.id]).length > 6 && (
                              <button onClick={() => setActiveTab('features')} className="text-[10px] text-[var(--accent)] font-bold hover:underline flex items-center gap-1 mt-1">
                                +{FEATURE_GROUPS.flatMap(g => g.features).filter(f => f[plan.id]).length - 6} more features <ChevronRight size={10} />
                              </button>
                            )}
                          </div>
                        </div>

                        {/* CTA */}
                        <button
                          disabled={(!publicMode && isCurrent) || isProcessing}
                          onClick={() => publicMode ? window.location.href = '/signup' : handleSubscribe(plan.id)}
                          className={`w-full py-3 rounded-xl font-black text-xs tracking-widest transition-all flex items-center justify-center gap-2 mt-auto
                            ${isCurrent
                              ? 'bg-[var(--bg-panel)] text-[var(--text-dim)] cursor-default border border-[var(--border-color)]'
                              : isPremium
                                ? 'bg-yellow-400 hover:bg-yellow-300 text-black shadow-[0_8px_24px_rgba(250,204,21,0.25)] active:scale-95'
                                : isUltimate
                                  ? 'bg-purple-500 hover:bg-purple-400 text-white shadow-[0_8px_24px_rgba(168,85,247,0.25)] active:scale-95'
                                  : 'bg-[var(--bg-panel)] hover:bg-[var(--bg-hover)] text-[var(--text-primary)] border border-[var(--border-color)] active:scale-95'
                            }`}
                        >
                          {isProcessing ? (
                            <div className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin" />
                          ) : (!publicMode && isCurrent) ? (
                            <>Current Plan</>
                          ) : (
                            <>{publicMode ? 'Get Started' : plan.ctaLabel} <ChevronRight size={13} /></>
                          )}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* XP Multiplier note */}
              <div className="flex flex-wrap items-center justify-center gap-4">
                {PLANS.map(plan => (
                  <div key={plan.id} className="flex items-center gap-2 text-[10px] font-bold text-[var(--text-dim)]">
                    <span className="text-base">{plan.emoji}</span>
                    <span>{plan.name}:</span>
                    <span className="text-[var(--text-primary)]">{plan.planMultiplier} XP multiplier</span>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* ════════════════════ FEATURES TAB ════════════ */}
          {activeTab === 'features' && (
            <>
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-black font-display">18 AI <span className="text-[var(--accent)]">FEATURES</span></h2>
                <p className="text-xs text-[var(--text-dim)] font-bold uppercase tracking-widest">Full feature comparison across all plans</p>
              </div>

              <div className="rounded-2xl border border-[var(--border-color)] overflow-hidden bg-[var(--bg-card)]">
                {/* Header row */}
                <div className="grid grid-cols-[1fr_repeat(5,70px)] md:grid-cols-[1fr_repeat(5,90px)] bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                  <div className="px-4 py-3">
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Feature</p>
                  </div>
                  {PLANS.map(plan => (
                    <div key={plan.id} className="px-2 py-3 text-center border-l border-[var(--border-color)]">
                      <p className="text-[8px] font-black uppercase tracking-widest" style={{ color: plan.color }}>{plan.name}</p>
                    </div>
                  ))}
                </div>

                {FEATURE_GROUPS.map((group, gi) => (
                  <div key={group.label}>
                    {/* Group header */}
                    <div className={`px-4 py-2 border-b border-[var(--border-color)] ${group.label.includes('AI Agent') ? 'bg-rose-500/10' : 'bg-[var(--bg-panel)]/60'}`}>
                      <p className={`text-[9px] font-black uppercase tracking-widest ${group.label.includes('AI Agent') ? 'text-rose-400' : 'text-[var(--accent)]'}`}>{group.label}</p>
                    </div>
                    {/* Feature rows */}
                    {group.features.map((feature, fi) => (
                      <div
                        key={feature.name}
                        className={`grid grid-cols-[1fr_repeat(5,70px)] md:grid-cols-[1fr_repeat(5,90px)] border-b border-[var(--border-color)] transition-colors hover:bg-[var(--bg-hover)]
                          ${fi % 2 === 1 ? 'bg-[var(--bg-main)]/30' : ''}`}
                      >
                        <div className="px-4 py-2.5 flex items-center gap-2">
                          <p className="text-[11px] font-bold text-[var(--text-secondary)]">{feature.name}</p>
                          {feature.cr > 0 && <span className="text-[9px] text-[var(--text-dim)] font-black bg-[var(--bg-panel)] px-1.5 py-0.5 rounded border border-[var(--border-color)]">{feature.cr} cr</span>}
                        </div>
                        {(['essential', 'plus', 'premium', 'ultimate', 'ultra']).map(planId => (
                          <div key={planId} className={`flex items-center justify-center border-l border-[var(--border-color)] py-2.5 ${planId === 'ultra' ? 'bg-rose-500/5' : ''}`}>
                            {feature[planId] ? <CheckIcon /> : <CrossIcon />}
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </>
          )}

          {/* ════════════════════ BOOSTERS TAB ════════════ */}
          {activeTab === 'boosters' && (
            <>
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-black font-display">BOOSTER <span className="text-[var(--accent)]">SYSTEM</span></h2>
                <p className="text-xs text-[var(--text-dim)] font-bold uppercase tracking-widest">Temporary power-ups · Max 1 active booster at a time</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {BOOSTERS.map(boost => {
                  const isProcessing = processing === boost.id;
                  return (
                    <div
                      key={boost.id}
                      className={`relative rounded-2xl border-2 bg-[var(--bg-card)] overflow-hidden transition-all hover:scale-[1.01] hover:shadow-2xl ${boost.border}`}
                    >
                      <div className="absolute inset-0 bg-gradient-to-br opacity-5" style={{ backgroundImage: `linear-gradient(135deg, ${boost.color}, transparent)` }} />
                      <div className="relative z-10 p-6 flex flex-col gap-5">
                        {/* Header */}
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <span className="text-4xl">{boost.emoji}</span>
                            <div>
                              <p className="font-black text-base text-[var(--text-primary)]">{boost.name}</p>
                              <p className="text-[10px] text-[var(--text-dim)] font-bold">{boost.days} hari aktif</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-black" style={{ color: boost.color }}>${boost.price}</p>
                            <p className="text-[9px] text-[var(--text-dim)] font-bold">one-time</p>
                          </div>
                        </div>

                        {/* Benefits */}
                        <div className="space-y-2.5">
                          {[
                            { label: `+${boost.credits} Credits`, icon: Zap },
                            { label: `+${boost.xp} XP`, icon: Trophy },
                            { label: '+1 Tier (temporary)', icon: Crown },
                            { label: boost.badge, icon: Medal },
                          ].map((item, i) => {
                            const Icon = item.icon;
                            return (
                              <div key={i} className="flex items-center gap-2.5">
                                <div className="w-6 h-6 rounded-lg flex items-center justify-center" style={{ backgroundColor: boost.color + '20' }}>
                                  <Icon size={12} style={{ color: boost.color }} />
                                </div>
                                <span className="text-[11px] font-bold text-[var(--text-secondary)]">{item.label}</span>
                              </div>
                            );
                          })}
                        </div>

                        {/* CTA */}
                        <button
                          disabled={isProcessing}
                          onClick={() => publicMode ? window.location.href = '/signup' : handleBuyBooster(boost.id)}
                          className="w-full py-3 rounded-xl font-black text-xs tracking-widest flex items-center justify-center gap-2 transition-all active:scale-95"
                          style={{
                            backgroundColor: boost.color + '20',
                            color: boost.color,
                            border: `1px solid ${boost.color}40`,
                          }}
                          onMouseEnter={e => { e.currentTarget.style.backgroundColor = boost.color + '30'; }}
                          onMouseLeave={e => { e.currentTarget.style.backgroundColor = boost.color + '20'; }}
                        >
                          {isProcessing ? (
                            <div className="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin" />
                          ) : (
                            <><ShoppingCart size={13} /> {publicMode ? `Get ${boost.name}` : `Buy ${boost.name}`}</>
                          )}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Note */}
              <div className="flex items-center gap-3 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-4 py-3">
                <Shield size={16} className="text-[var(--text-dim)] shrink-0" />
                <p className="text-[11px] text-[var(--text-dim)] font-bold">
                  Max 1 active booster at a time. Tier upgrade is temporary and reverts after the booster period ends.
                </p>
              </div>
            </>
          )}

          {/* ════════════════════ ADD-ONS TAB ═════════════ */}
          {activeTab === 'addons' && (
            <>
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-black font-display">PLAN <span className="text-[var(--accent)]">ADD-ONS</span></h2>
                <p className="text-xs text-[var(--text-dim)] font-bold uppercase tracking-widest">Extend your plan capabilities</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {ADDONS.map(addon => {
                  const Icon = addon.icon;
                  return (
                    <div
                      key={addon.id}
                      className="group rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] p-5 flex flex-col gap-4 hover:border-yellow-400/30 transition-all hover:shadow-lg hover:shadow-yellow-400/5"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)] flex items-center justify-center shrink-0 group-hover:border-yellow-400/30 transition-colors">
                            <Icon size={16} className="text-[var(--accent)]" />
                          </div>
                          <div>
                            <p className="text-xs font-black text-[var(--text-primary)]">{addon.name}</p>
                            <p className="text-[10px] text-[var(--text-dim)] font-bold mt-0.5">{addon.desc}</p>
                          </div>
                        </div>
                        <div className="text-right shrink-0">
                          <p className="text-base font-black text-[var(--text-primary)]">${addon.price}<span className="text-[var(--text-dim)] text-[10px] font-bold">{addon.cycle}</span></p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-[9px] font-black bg-blue-500/10 text-blue-400 px-2 py-1 rounded-full border border-blue-500/20 uppercase tracking-widest">
                          {addon.eligible}
                        </span>
                        <button
                          onClick={() => publicMode ? window.location.href = '/signup' : null}
                          className="flex items-center gap-1.5 text-[10px] font-black text-[var(--accent)] hover:text-yellow-300 transition-colors"
                        >
                          Add <ChevronRight size={11} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {/* ════════════════════ CREDITS TAB ═════════════ */}
          {activeTab === 'credits' && (
            <>
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-black font-display">CREDIT <span className="text-[var(--accent)]">TOP-UP</span></h2>
                <p className="text-xs text-[var(--text-dim)] font-bold uppercase tracking-widest">Add credits to your account instantly</p>
              </div>

              {/* Current credits card */}
              <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6 flex items-center gap-6">
                <div className="w-14 h-14 rounded-xl bg-yellow-400/10 border border-yellow-400/20 flex items-center justify-center">
                  <Zap size={24} className="text-[var(--accent)]" />
                </div>
                <div className="flex-1">
                  <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest mb-1">Current Balance</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-[var(--accent)]">{mockStatus.credits}</span>
                    <span className="text-[var(--text-dim)] text-sm">/ {mockStatus.creditsTotal} cr</span>
                  </div>
                  <div className="mt-2 h-2 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-yellow-400 to-yellow-500"
                      style={{ width: `${(mockStatus.credits / mockStatus.creditsTotal) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Top-up options */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {TOPUPS.map((topup, i) => {
                  const isPopular = i === 1;
                  return (
                    <div
                      key={topup.id}
                      className={`relative rounded-2xl border-2 bg-[var(--bg-card)] p-6 flex flex-col gap-4 transition-all hover:scale-[1.02] hover:shadow-xl
                        ${isPopular ? 'border-yellow-400/50 shadow-[0_0_30px_rgba(250,204,21,0.10)]' : 'border-[var(--border-color)]'}`}
                    >
                      {isPopular && (
                        <div className="absolute top-3 right-3 bg-yellow-400 text-black text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-widest">
                          Best Value
                        </div>
                      )}
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${isPopular ? 'bg-yellow-400/15 border border-yellow-400/30' : 'bg-[var(--bg-panel)] border border-[var(--border-color)]'}`}>
                          <CreditCard size={20} className={isPopular ? 'text-[var(--accent)]' : 'text-[var(--text-dim)]'} />
                        </div>
                        <div>
                          <p className="text-2xl font-black text-[var(--text-primary)]">{topup.credits} <span className="text-base font-bold text-[var(--text-dim)]">cr</span></p>
                          <p className="text-[10px] text-[var(--text-dim)] font-bold">Credits</p>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-xl font-black text-[var(--text-primary)]">${topup.price}</p>
                          <p className="text-[10px] text-green-400 font-bold">${(topup.price / topup.credits * 100).toFixed(1)}¢ per 10 cr</p>
                        </div>
                        <button
                          disabled={processing === topup.id}
                          onClick={() => publicMode ? window.location.href = '/signup' : handleCryptoPurchase(topup.id, topup.credits + ' Credits')}
                          className={`flex items-center gap-2 py-2.5 px-4 rounded-xl text-xs font-black transition-all active:scale-95
                            ${isPopular ? 'bg-yellow-400 text-black hover:bg-yellow-300 shadow-[0_4px_16px_rgba(250,204,21,0.2)]' : 'bg-[var(--bg-panel)] text-[var(--text-primary)] hover:bg-[var(--bg-hover)] border border-[var(--border-color)]'}`}
                        >
                          {processing === topup.id
                            ? <div className="w-3 h-3 border-2 border-current/30 border-t-current rounded-full animate-spin" />
                            : <ShoppingCart size={12} />
                          }
                          {publicMode ? 'Get Started' : processing === topup.id ? 'Processing...' : 'Buy'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Credit usage table */}
              <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden">
                <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                  <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">Credit Cost Reference</p>
                </div>
                <div className="divide-y divide-[var(--border-color)]">
                  {FEATURE_GROUPS.flatMap(g => g.features).map(f => (
                    <div key={f.name} className="flex items-center justify-between px-5 py-2.5 hover:bg-[var(--bg-hover)] transition-colors">
                      <p className="text-[11px] font-bold text-[var(--text-secondary)]">{f.name}</p>
                      <span className="text-[10px] font-black text-[var(--accent)] bg-yellow-400/10 px-2 py-0.5 rounded border border-yellow-400/20">{f.cr} cr / call</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* ════════════════════ LEVELING TAB ════════════ */}
          {activeTab === 'leveling' && (
            <>
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-black font-display">LEVELING <span className="text-[var(--accent)]">SYSTEM</span></h2>
                <p className="text-xs text-[var(--text-dim)] font-bold uppercase tracking-widest">Earn XP · Unlock rewards · Become a GAS Legend</p>
              </div>

              {/* XP multiplier by plan */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {PLANS.map(plan => (
                  <div key={plan.id} className={`rounded-xl border bg-[var(--bg-card)] p-4 text-center ${plan.id === userPlan ? 'border-yellow-400/50' : 'border-[var(--border-color)]'}`}>
                    <span className="text-2xl">{plan.emoji}</span>
                    <p className="text-xs font-black text-[var(--text-secondary)] mt-1">{plan.name}</p>
                    <p className="text-xl font-black mt-1" style={{ color: plan.color }}>{plan.planMultiplier}</p>
                    <p className="text-[9px] text-[var(--text-dim)] font-bold uppercase tracking-widest">XP Multiplier</p>
                  </div>
                ))}
              </div>

              {/* Level progression */}
              <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden">
                <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)] flex items-center justify-between">
                  <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">Level Progression (1–20)</p>
                  <span className="text-[9px] font-black text-[var(--accent)] bg-yellow-400/10 px-2 py-0.5 rounded border border-yellow-400/20">Lv.20 = GAS GOD 🥇</span>
                </div>
                <div className="p-5 space-y-3">
                  {LEVELS.map((lvl, i) => {
                    const isCurrentLevel = lvl.level === mockStatus.level;
                    const isPassed = lvl.level < mockStatus.level;
                    const nextXp = LEVELS[i + 1]?.xp || lvl.xp + 1500;
                    const rangeXp = nextXp - lvl.xp;
                    const progressXp = isCurrentLevel ? Math.max(0, mockStatus.xp - lvl.xp) : isPassed ? rangeXp : 0;
                    const pct = Math.min(100, Math.round((progressXp / rangeXp) * 100));

                    return (
                      <div key={lvl.level} className={`flex items-center gap-4 p-3 rounded-xl transition-all
                        ${isCurrentLevel ? 'bg-yellow-400/8 border border-yellow-400/25' : isPassed ? 'bg-[var(--bg-panel)]/50' : 'opacity-50'}`}>
                        {/* Level badge with emoji */}
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-base shrink-0
                          ${isPassed ? 'bg-[var(--success)]/20' : isCurrentLevel ? 'bg-yellow-400/20' : 'bg-[var(--bg-panel)]'}`}>
                          {isPassed ? <Check size={14} className="text-[var(--success)]" /> : lvl.emoji}
                        </div>

                        {/* Label + XP */}
                        <div className="w-28 shrink-0">
                          <p className={`text-xs font-black ${isCurrentLevel ? 'text-[var(--accent)]' : 'text-[var(--text-secondary)]'}`}>{lvl.emoji} {lvl.label}</p>
                          <p className="text-[9px] text-[var(--text-dim)] font-bold">Lv.{lvl.level} · {lvl.xp.toLocaleString()} XP</p>
                        </div>

                        {/* Progress bar */}
                        <div className="flex-1 h-2 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-700 ${isPassed ? 'bg-[var(--success)]' : isCurrentLevel ? 'bg-gradient-to-r from-yellow-400 to-yellow-500' : 'bg-[var(--bg-hover)]'}`}
                            style={{ width: `${isPassed ? 100 : isCurrentLevel ? pct : 0}%` }}
                          />
                        </div>

                        {/* Pct */}
                        <div className="w-10 text-right shrink-0">
                          <span className={`text-[9px] font-black ${isCurrentLevel ? 'text-[var(--accent)]' : isPassed ? 'text-[var(--success)]' : 'text-[var(--text-dim)]'}`}>
                            {isPassed ? '100%' : isCurrentLevel ? `${pct}%` : '—'}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* How to earn XP */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden">
                  <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                    <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">How to Earn XP</p>
                  </div>
                  <div className="divide-y divide-[var(--border-color)]">
                    {[
                      { label: 'Use any AI feature', xp: '+1–20 XP', sub: 'Based on credit cost of feature' },
                      { label: 'Signal hits TP', xp: '+5 XP', sub: 'When GAS signal reaches take profit' },
                      { label: 'Daily Login', xp: '+1 XP', sub: 'Login bonus every day' },
                      { label: 'Referral signup', xp: '+10 XP', sub: 'Invite a friend who subscribes' },
                      { label: 'Trade Journal entry', xp: '+2 XP', sub: 'Log a completed trade' },
                      { label: 'Complete briefing', xp: '+3 XP', sub: 'Read daily AI market briefing' },
                    ].map((item, i) => (
                      <div key={i} className="flex items-center justify-between px-5 py-3 hover:bg-[var(--bg-hover)] transition-colors">
                        <div>
                          <p className="text-[11px] font-bold text-[var(--text-secondary)]">{item.label}</p>
                          <p className="text-[9px] text-[var(--text-dim)] font-bold">{item.sub}</p>
                        </div>
                        <span className="bg-yellow-400 text-black text-[9px] font-black px-2.5 py-1 rounded-lg shrink-0">{item.xp}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] overflow-hidden">
                  <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                    <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">Level Rewards</p>
                  </div>
                  <div className="divide-y divide-[var(--border-color)]">
                    {[
                      { level: '1–2', reward: 'Access to base features', icon: Star },
                      { level: '3–4', reward: '+5% bonus credits monthly', icon: Zap },
                      { level: '5–6', reward: '+10% bonus credits + priority queue', icon: Rocket },
                      { level: '7–8', reward: '+15% bonus credits + 5% off add-ons', icon: Shield },
                      { level: '9', reward: '+20% bonus credits + beta features', icon: Crown },
                      { level: '10', reward: 'GAS Legend: 20% off ALL plans lifetime!', icon: Trophy },
                    ].map((item, i) => {
                      const Icon = item.icon;
                      return (
                        <div key={i} className="flex items-center gap-3 px-5 py-3 hover:bg-[var(--bg-hover)] transition-colors">
                          <div className="w-8 h-8 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] flex items-center justify-center shrink-0">
                            <Icon size={13} className="text-[var(--accent)]" />
                          </div>
                          <div className="flex-1">
                            <p className="text-[10px] font-black text-[var(--accent)]">Lv. {item.level}</p>
                            <p className="text-[11px] font-bold text-[var(--text-secondary)]">{item.reward}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </>
          )}

        </div>
      </div>
    </div>
  );
};

export default PricingView;
