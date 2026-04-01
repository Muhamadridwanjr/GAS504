import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Star, LogOut } from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './components/LandingPage';
import LoginPage from './components/LoginPage';
import SignupPage from './components/SignupPage';
import AuthCallback from './components/AuthCallback';

import { PAIRS, MACRO_DATA, AI_ANALYSIS, NEWS_FEED } from './constants';
import { fetchOverview, fetchLatestSignal, fetchLiveNews, fetchBreakingNews } from './services/api';
import { useWebSocket } from './hooks/useWebSocket';

import LoadingScreen from './components/LoadingScreen';
import EmptyView from './components/EmptyView';
import PortfolioView from './components/PortfolioView';
import CalendarView from './components/CalendarView';
import SettingsView from './components/SettingsView';
import MarketsView from './components/MarketsView';
import PricingView from './components/PricingView';
import ProfileView from './components/ProfileView';
import TerminalWidget from './components/TerminalWidget';
import AlertsView from './components/AlertsView';
import AdminPanelView from './components/AdminPanelView';
import DashboardView from './components/DashboardView';
import LinkTelegramPage from './components/LinkTelegramPage';

function getPrefs() {
  try { return JSON.parse(localStorage.getItem('gas-preferences') || '{}'); } catch { return {}; }
}

const PAGE_LABELS = [
  {id:'dashboard',lb:'Dashboard'},
  {id:'markets',lb:'Markets'},
  {id:'portfolio',lb:'Portfolio'},
  {id:'watchlist',lb:'Favorit'},
  {id:'calendars',lb:'Economic Calendar'},
  {id:'alerts',lb:'Smart Alert'},
  {id:'pricing',lb:'Pricing'},
  {id:'profile',lb:'Profile'},
  {id:'settings',lb:'Settings'},
  {id:'admin',lb:'Admin Panel'},
  {id:'telegram_bot',lb:'AI via Telegram Bot'},
];

function TelegramBotView() {
  const BOT_USERNAME = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'GoldenAIStrategyBot';
  const SITE_URL = window.location.origin;
  return (
    <div style={{ padding: '32px 24px', maxWidth: 720, margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <div style={{ fontSize: 64, marginBottom: 16 }}>🤖</div>
        <h1 style={{ fontSize: 28, fontWeight: 900, color: 'var(--text-primary)', marginBottom: 8 }}>
          Golden AI Strategy Bot
        </h1>
        <p style={{ fontSize: 15, color: 'var(--text-dim)', lineHeight: 1.7 }}>
          Semua fitur AI analisis tersedia di Telegram Bot kami.<br />
          Sinyal real-time, multi-timeframe, grade SS/S/A+ langsung di chat.
        </p>
      </div>

      {/* Feature grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 40 }}>
        {[
          { icon: '⚡', title: 'Forex AI Signal', desc: '22 pair · SS/S/A+ grade' },
          { icon: '₿', title: 'Crypto AI Signal', desc: 'BTC, ETH, BNB, SOL, dll' },
          { icon: '🥇', title: 'Gold & Komoditas', desc: 'XAUUSD, XAGUSD, Oil' },
          { icon: '📈', title: 'Indices AI', desc: 'US30, US500, USTEC, dll' },
          { icon: '⚙️', title: '4 Gaya Trading', desc: 'Scalping · Day · Swing · Position' },
          { icon: '💳', title: 'Credit System', desc: 'Bayar per analisis, hemat biaya' },
          { icon: '🔔', title: 'Instant Notif', desc: 'Sinyal langsung ke Telegram kamu' },
          { icon: '📊', title: 'Entry/SL/TP', desc: 'Lengkap dengan RR ratio' },
        ].map((f, i) => (
          <div key={i} style={{
            background: 'var(--bg-panel)',
            border: '1px solid var(--border-color)',
            borderRadius: 12,
            padding: '16px',
          }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>{f.icon}</div>
            <div style={{ fontWeight: 800, color: 'var(--text-primary)', fontSize: 13, marginBottom: 4 }}>{f.title}</div>
            <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>{f.desc}</div>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(250,204,21,0.08) 0%, rgba(250,204,21,0.03) 100%)',
        border: '1px solid rgba(250,204,21,0.2)',
        borderRadius: 16,
        padding: '32px',
        textAlign: 'center',
        marginBottom: 24,
      }}>
        <div style={{ fontSize: 20, fontWeight: 900, color: 'var(--text-primary)', marginBottom: 8 }}>
          Mulai Gunakan AI Bot Sekarang
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-dim)', marginBottom: 24, lineHeight: 1.6 }}>
          Hubungkan akun GAS kamu ke bot Telegram, lalu gunakan perintah <code style={{ background: 'var(--bg-main)', padding: '1px 6px', borderRadius: 4, fontSize: 12 }}>/start</code> untuk memulai.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <a
            href={`https://t.me/${BOT_USERNAME}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: '#229ED9', color: 'white', border: 'none',
              borderRadius: 10, padding: '12px 24px', fontSize: 14, fontWeight: 800,
              textDecoration: 'none', cursor: 'pointer',
            }}
          >
            <i className="fa-brands fa-telegram" /> Buka Telegram Bot
          </a>
          <a
            href={`${SITE_URL}/link-tg`}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 8,
              background: 'rgba(250,204,21,0.1)', color: '#facc15',
              border: '1px solid rgba(250,204,21,0.3)',
              borderRadius: 10, padding: '12px 24px', fontSize: 14, fontWeight: 800,
              textDecoration: 'none', cursor: 'pointer',
            }}
          >
            <i className="fa-solid fa-link" /> Hubungkan Akun
          </a>
        </div>
      </div>

      {/* Steps */}
      <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 12, padding: '24px' }}>
        <div style={{ fontWeight: 900, fontSize: 14, color: 'var(--text-primary)', marginBottom: 16 }}>Cara Menggunakan</div>
        {[
          { n: '1', t: 'Daftar / Login', d: 'Buat akun GAS di halaman ini (sudah selesai ✅)' },
          { n: '2', t: 'Buka Bot', d: `Cari @${BOT_USERNAME} di Telegram dan klik /start` },
          { n: '3', t: 'Hubungkan Akun', d: 'Klik /link di bot → ikuti langkah → akun terhubung' },
          { n: '4', t: 'Analisis AI', d: 'Pilih pasar → pair → gaya trading → dapatkan sinyal premium' },
        ].map((s, i) => (
          <div key={i} style={{ display: 'flex', gap: 16, marginBottom: i < 3 ? 16 : 0, alignItems: 'flex-start' }}>
            <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'rgba(250,204,21,0.15)', border: '1px solid rgba(250,204,21,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontWeight: 900, fontSize: 12, color: '#facc15' }}>{s.n}</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 13, color: 'var(--text-primary)' }}>{s.t}</div>
              <div style={{ fontSize: 12, color: 'var(--text-dim)', marginTop: 2 }}>{s.d}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Terminal() {
  const { user, logout, isAdmin, userPlan } = useAuth();
  const [activeMenu, setActiveMenu] = useState('dashboard');
  const [prefs, setPrefs] = useState(getPrefs);
  useEffect(() => { setPrefs(getPrefs()); }, [activeMenu]);
  const [theme, setTheme] = useState(() => localStorage.getItem('gas-theme') || 'dark');
  const [activePair, setActivePair] = useState('XAUUSD');
  const [pairs, setPairs] = useState(PAIRS);
  const [prices, setPrices] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [eta, setEta] = useState(15);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [openSubmenu, setOpenSubmenu] = useState(null);
  const [showAlert, setShowAlert] = useState(false);
  const [chartPair, setChartPair] = useState(PAIRS[0]);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [news, setNews] = useState(NEWS_FEED);
  const [breakingNews, setBreakingNews] = useState([]);

  const profileMenuRef = useRef(null);
  const audioRef = useRef(null);
  const prevPricesRef = useRef({});
  const startTimeRef = useRef(Date.now());

  useEffect(() => {
    const handler = (e) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(e.target))
        setShowProfileMenu(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('gas-theme', theme);
  }, [theme]);

  const wsUrl = (() => {
    const envUrl = import.meta.env.VITE_WS_BASE_URL;
    if (envUrl) return window.location.protocol === 'https:' ? envUrl.replace(/^ws:\/\//, 'wss://') : envUrl;
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    return `${proto}://${window.location.host}/terminal/ws`;
  })();

  const { isConnected, send } = useWebSocket(wsUrl, (data) => {
    if (data.type === 'price') setPrices(prev => ({ ...prev, [data.symbol]: data.price }));
    if (data.type === 'signal') {
      setShowAlert(true);
      startTimeRef.current = Date.now(); setEta(15);
      if (soundEnabled) {
        if (!audioRef.current) {
          audioRef.current = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
          audioRef.current.volume = 0.3;
        }
        audioRef.current.currentTime = 0;
        audioRef.current.play().catch(() => {});
      }
      setTimeout(() => setShowAlert(false), 5000);
    }
  });

  useEffect(() => { return () => { if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; } }; }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        const overview = await fetchOverview();
        if (overview) {
          const initialPrices = {};
          if (overview.pairs) overview.pairs.forEach(p => { const rp = p.price || p.prev_close; if (p.symbol && rp) initialPrices[p.symbol] = rp; });
          PAIRS.forEach(p => { if (!initialPrices[p.symbol] && p.base) initialPrices[p.symbol] = p.base; });
          setPrices(initialPrices);
          if (overview.news) setNews(overview.news.map(n => n.title || n));
          const selPair = PAIRS.find(p => p.symbol === 'XAUUSD');
          if (selPair) setChartPair(selPair);
        }
      } catch {
        const ip = {}; PAIRS.forEach(p => { ip[p.symbol] = p.base; }); setPrices(ip);
      } finally { setIsLoading(false); }
    };
    setTimeout(loadData, 800);

    const loadNews = async () => {
      try {
        const [liveRes, breakRes] = await Promise.all([fetchLiveNews(), fetchBreakingNews()]);
        if (liveRes?.news?.length > 0) setNews(liveRes.news.map(n => `[${n.time} WIB] ${n.title} — ${n.source || 'GAS'}`));
        if (breakRes?.active && breakRes.items?.length > 0) setBreakingNews(breakRes.items);
        else setBreakingNews([]);
      } catch (_) {}
    };
    loadNews();
    const newsIv = setInterval(loadNews, 60000);
    const timerIv = setInterval(() => { const diff = Math.floor((Date.now() - startTimeRef.current) / 1000); setEta(15 - (diff % 15)); }, 1000);
    return () => { clearInterval(newsIv); clearInterval(timerIv); };
  }, []);

  const priceDirections = useMemo(() => {
    const map = {};
    pairs.forEach(p => { const cur = prices[p.symbol], prev = prevPricesRef.current[p.symbol]; if (cur && prev) map[p.symbol] = cur > prev ? 'up' : cur < prev ? 'down' : null; });
    return map;
  }, [prices, pairs]);

  useEffect(() => { prevPricesRef.current = prices; }, [prices]);

  const loopPrices = useMemo(() => {
    const e = Object.entries(prices);
    return e.length < 12 && e.length > 0 ? [...e, ...e, ...e] : e;
  }, [prices]);

  const handleSelectPair = async (symbol) => {
    if (navigator.vibrate) navigator.vibrate(30);
    const pair = pairs.find(p => p.symbol === symbol);
    setActivePair(symbol);
    if (pair) setChartPair(pair);
    if (isConnected) send({ command: 'subscribe', symbol });
    setActiveMenu('markets');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    if (isConnected && pairs.length > 0) pairs.forEach(p => send({ command: 'subscribe', symbol: p.symbol }));
  }, [isConnected, pairs]);

  if (isLoading) return <LoadingScreen />;

  const navTo = (id) => { setActiveMenu(id); setSidebarOpen(false); };
  const toggleSub = (key) => setOpenSubmenu(p => p === key ? null : key);

  const SideNavItem = ({ id, icon, label, badge }) => (
    <div className={`gas-nav-item${activeMenu === id ? ' gas-nav-item--on' : ''}`} onClick={() => navTo(id)}>
      <i className={`${icon} gas-nav-ic`} /><span className="gas-nav-lbl">{label}</span>
      {badge && <span className="gas-nav-badge">{badge}</span>}
    </div>
  );

  const SubItem = ({ id, icon, label }) => (
    <div className={`gas-sub-item${activeMenu === id ? ' gas-sub-item--on' : ''}`} onClick={() => navTo(id)}>
      <i className={`${icon} gas-sub-ic`} />{label}
    </div>
  );

  return (
    <div className="fixed inset-0 flex flex-col" style={{ background: 'var(--bg-main)', color: 'var(--text-primary)', fontFamily: "'Exo 2','Plus Jakarta Sans',sans-serif" }}>

      {/* ROW 1 — LIVE NEWS TICKER */}
      {prefs.showLiveNews !== false && (
        <div style={{ height: '26px', display: 'flex', alignItems: 'center', overflow: 'hidden', flexShrink: 0, background: 'var(--bg-panel)', borderBottom: '1px solid var(--border-subtle)', zIndex: 50 }}>
          <div style={{ flexShrink: 0, padding: '0 12px', display: 'flex', alignItems: 'center', gap: '6px', height: '100%', background: 'rgba(240,170,0,0.06)', borderRight: '1px solid var(--gas-bdim)' }}>
            <i className="fa-solid fa-bolt" style={{ color: 'var(--gas-gold)', fontSize: '9px' }} />
            <span style={{ fontSize: '9px', fontWeight: 800, letterSpacing: '2px', color: 'var(--gas-gold)', textTransform: 'uppercase', whiteSpace: 'nowrap' }}>GAS NEWS</span>
          </div>
          <div className="ticker-wrap">
            <div className="ticker-scroll" style={{ '--ticker-dur': `${prefs.tickerSpeed || 120}s` }}>
              {[...news, ...news].map((n, i) => (
                <span key={i} style={{ fontSize: '10px', color: 'var(--gas-txt-sec)', padding: '0 18px', borderRight: '1px solid var(--gas-bfaint)' }}>
                  {typeof n === 'string' ? n : `[${n.time} WIB] ${n.title} — ${n.source || 'GAS'}`}
                </span>
              ))}
            </div>
          </div>
          <div style={{ flexShrink: 0, padding: '0 10px', borderLeft: '1px solid var(--gas-bfaint)' }}>
            <button onClick={() => setSoundEnabled(!soundEnabled)} style={{ color: 'var(--gas-txt-muted)', fontSize: '10px', background: 'none', border: 'none', cursor: 'pointer' }}>
              {soundEnabled ? '🔊' : '🔇'}
            </button>
          </div>
        </div>
      )}

      {/* MOBILE OVERLAY */}
      {sidebarOpen && <div className="gas-sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

      {/* BODY = SIDEBAR + MAIN */}
      <div className="flex flex-1 overflow-hidden min-h-0">

        {/* ═══════ SIDEBAR ═══════ */}
        <aside className={`gas-sidebar${sidebarCollapsed ? ' gas-sidebar--col' : ''}${sidebarOpen ? ' gas-sidebar--open' : ''}`}>

          <div className="gas-sb-logo">
            <img src="https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg" alt="GAS" style={{ width: '34px', height: '34px', borderRadius: '8px', objectFit: 'cover', flexShrink: 0, border: '1.5px solid var(--gas-gold-dim)' }} />
            <div className="gas-sb-text">
              <div className="gas-sb-name">GAS</div>
              <div className="gas-sb-sub">Golden AI Strategy</div>
            </div>
          </div>

          <nav className="gas-sb-nav">

            <div className="gas-nav-gl">Overview</div>
            <SideNavItem id="dashboard" icon="fa-solid fa-gauge-high" label="Dashboard" />

            {/* Telegram Bot CTA — prominent */}
            <div className="gas-nav-gl">AI Analysis</div>
            <SideNavItem id="telegram_bot" icon="fa-brands fa-telegram" label="AI via Telegram Bot" badge="NEW" />

            <div className="gas-nav-gl">Market Data</div>
            <SideNavItem id="markets"   icon="fa-solid fa-chart-line"    label="Markets" />
            <SideNavItem id="calendars" icon="fa-solid fa-calendar-days" label="Economic Calendar" />
            <SideNavItem id="alerts"    icon="fa-solid fa-bell"          label="Smart Alert" />

            <div className="gas-nav-gl">Workspace</div>
            <SideNavItem id="portfolio" icon="fa-solid fa-briefcase" label="Portfolio" />
            <SideNavItem id="watchlist" icon="fa-solid fa-star"      label="Favorit" />

            <div className="gas-nav-gl">Account</div>
            <div className={`gas-nav-item${openSubmenu === 'system' ? ' gas-nav-item--exp' : ''}`} onClick={() => toggleSub('system')}>
              <i className="fa-solid fa-gear gas-nav-ic" /><span className="gas-nav-lbl">Account</span>
              <i className="fa-solid fa-chevron-right gas-nav-arr" />
            </div>
            <div className={`gas-sub-menu${openSubmenu === 'system' ? ' gas-sub-menu--open' : ''}`}>
              <SubItem id="pricing"  icon="fa-solid fa-credit-card"          label="Pricing" />
              <SubItem id="profile"  icon="fa-solid fa-user"                 label="Profile" />
              <SubItem id="settings" icon="fa-solid fa-sliders"              label="Settings" />
              {isAdmin && <SubItem id="admin" icon="fa-solid fa-screwdriver-wrench" label="Admin Panel" />}
            </div>

          </nav>

          <div className="gas-sb-status">
            <div className="gas-sb-dot" />
            <span className="gas-sb-status-txt">{isConnected ? 'GAS v3.0.4 · LIVE' : 'GAS v3.0.4 · OFFLINE'}</span>
          </div>
          <div className="gas-sb-toggle" onClick={() => setSidebarCollapsed(p => !p)}>
            <i className={`fa-solid ${sidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'}`} />
          </div>
        </aside>

        {/* ═══════ MAIN ═══════ */}
        <div className="flex flex-1 flex-col overflow-hidden min-w-0">

          {/* TOPBAR */}
          <header className="gas-topbar">
            <button className="gas-tb-btn gas-tb-mobile-menu" onClick={() => setSidebarOpen(true)}>
              <i className="fa-solid fa-bars" />
            </button>

            <span className="gas-tb-page-title">
              {PAGE_LABELS.find(m => m.id === activeMenu)?.lb || ''}
            </span>

            <div className="gas-tb-search">
              <i className="fa-solid fa-search" style={{ color: 'var(--gas-txt-muted)', fontSize: '11px' }} />
              <input type="text" placeholder="Search pair..." />
            </div>

            <div className="gas-tb-ticker">
              <div className="gas-tb-ticker-track">
                {[...loopPrices, ...loopPrices].map(([k, v], i) => {
                  const pair = pairs.find(p => p.symbol === k) || PAIRS.find(p => p.symbol === k);
                  const base = pair?.base || 1;
                  const chg = ((v - base) / base * 100);
                  const isUp = chg >= 0;
                  return (
                    <div key={i} className="gas-tick-item" onClick={() => handleSelectPair(k)}>
                      <span className="gas-tick-pair">{k}</span>
                      <span className="gas-tick-price">{v ? v.toFixed(pair?.type === 'Forex' ? 4 : 2) : '--'}</span>
                      <span className={`gas-tick-chg ${isUp ? 'gas-tick-up' : 'gas-tick-dn'}`}>{isUp ? '▲' : '▼'}{Math.abs(chg).toFixed(2)}%</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="gas-tb-actions">
              <div className="gas-tb-btn-group">
                {[{ t: 'dark', i: 'fa-solid fa-moon' }, { t: 'light', i: 'fa-solid fa-sun' }, { t: 'term', i: 'fa-solid fa-terminal' }].map(({ t, i }) => (
                  <button key={t} className={`gas-tb-btn${theme === t ? ' gas-tb-btn--on' : ''}`} onClick={() => setTheme(t === 'term' ? 'dark' : t)}>
                    <i className={i} />
                  </button>
                ))}
              </div>
              <button className="gas-tb-btn" title="Smart Alert" onClick={() => navTo('alerts')}>
                <i className="fa-solid fa-bell" />
                <div className="gas-tb-notif-dot" />
              </button>
              <div style={{ position: 'relative' }} ref={profileMenuRef}>
                <div className="gas-tb-avatar" onClick={() => setShowProfileMenu(p => !p)}>
                  {user?.avatar_url
                    ? <img src={user.avatar_url} alt="av" style={{ width: '100%', height: '100%', borderRadius: '7px', objectFit: 'cover' }} />
                    : <span style={{ fontFamily: "'Orbitron',monospace", fontSize: '11px', fontWeight: 900 }}>
                        {user?.full_name ? user.full_name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) : user?.email?.slice(0, 2).toUpperCase() || 'GA'}
                      </span>
                  }
                </div>
                {showProfileMenu && (
                  <div className="gas-profile-menu">
                    <div className="gas-profile-menu-header">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <p style={{ fontSize: '12px', fontWeight: 800, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: 'var(--gas-txt-bright)' }}>
                          {user?.full_name || user?.username}
                        </p>
                        {isAdmin && <span style={{ fontSize: '8px', background: '#dc2626', color: 'white', padding: '1px 5px', borderRadius: '4px', fontWeight: 800, flexShrink: 0 }}>ADMIN</span>}
                      </div>
                      <p style={{ fontSize: '10px', color: 'var(--gas-txt-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{user?.email}</p>
                      <p style={{ marginTop: '5px' }}>
                        <span style={{ fontSize: '9px', fontWeight: 800, padding: '2px 7px', borderRadius: '10px', background: 'var(--gas-gold-sm)', color: 'var(--gas-gold)', border: '1px solid var(--gas-gold-dim)' }}>
                          {isAdmin ? '👑 Ultimate (Admin)' : `Plan: ${userPlan?.charAt(0).toUpperCase() + userPlan?.slice(1)}`}
                        </span>
                      </p>
                    </div>
                    {[
                      { icon: '👤', label: 'Profil Saya', action: () => { navTo('profile'); setShowProfileMenu(false); } },
                      { icon: '💳', label: 'Plan & Usage', action: () => { navTo('pricing'); setShowProfileMenu(false); } },
                      { icon: '⚙️', label: 'Pengaturan', action: () => { navTo('settings'); setShowProfileMenu(false); } },
                      { icon: '🤖', label: 'AI via Telegram', action: () => { navTo('telegram_bot'); setShowProfileMenu(false); } },
                      ...(!isAdmin ? [{ icon: '👑', label: 'Upgrade Plan', action: () => { navTo('pricing'); setShowProfileMenu(false); } }]
                                   : [{ icon: '🛡️', label: 'Admin Panel', action: () => { navTo('admin'); setShowProfileMenu(false); } }]),
                    ].map((item, i) => (
                      <button key={i} onClick={item.action} className="gas-profile-menu-item">
                        <span>{item.icon}</span>{item.label}
                      </button>
                    ))}
                    <div style={{ borderTop: '1px solid var(--gas-bfaint)' }}>
                      <button onClick={logout} className="gas-profile-menu-item" style={{ color: '#f87171' }}>
                        <LogOut size={12} /> Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </header>

          {/* BREAKING NEWS */}
          {prefs.showBreakingNews !== false && breakingNews.length > 0 && (
            <div style={{ height: '30px', display: 'flex', alignItems: 'center', overflow: 'hidden', flexShrink: 0, background: '#160405', borderBottom: '1px solid #7f1d1d', zIndex: 20 }}>
              <div style={{ flexShrink: 0, padding: '0 12px', display: 'flex', alignItems: 'center', gap: '6px', height: '100%', background: '#7f1d1d', borderRight: '1px solid #991b1b' }}>
                <span style={{ display: 'inline-block', width: '7px', height: '7px', borderRadius: '50%', background: 'white', animation: 'gasStatusPulse 1s infinite' }} />
                <span style={{ fontSize: '9px', fontWeight: 800, color: 'white', textTransform: 'uppercase', letterSpacing: '2px', whiteSpace: 'nowrap' }}>🚨 BREAKING</span>
              </div>
              <div className="ticker-wrap">
                <div className="breaking-scroll" style={{ '--breaking-dur': `${Math.round((prefs.tickerSpeed || 120) * 2)}s` }}>
                  {[...breakingNews, ...breakingNews, ...breakingNews].map((b, i) => (
                    <span key={i} style={{ fontSize: '10px', fontWeight: 700, color: '#fca5a5', padding: '0 28px', borderRight: '1px solid #7f1d1d' }}>
                      {b.tag === 'URGENT' ? '🚨' : '⚠️'} {b.text}{b.source ? ` — ${b.source}` : ''}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* CONTENT AREA */}
          <div className={`flex-1 ${activeMenu === 'markets' ? 'overflow-hidden' : 'overflow-y-auto'} scrollbar-none relative`}>
            {activeMenu === 'markets'      && <MarketsView pairs={pairs} prices={prices} directions={priceDirections} onSelect={handleSelectPair} activePair={activePair} theme={theme} chartPair={chartPair} />}
            {activeMenu === 'watchlist'    && <EmptyView icon={<Star size={32} />} label="Favorit Kosong" sub="Tambahkan aset ke daftar favorit Anda" />}
            {activeMenu === 'portfolio'    && <PortfolioView theme={theme} />}
            {activeMenu === 'pricing'      && <PricingView />}
            {activeMenu === 'profile'      && <ProfileView />}
            {activeMenu === 'settings'     && <SettingsView theme={theme} setTheme={setTheme} />}
            {activeMenu === 'alerts'       && <AlertsView prices={prices} />}
            {activeMenu === 'calendars'    && <CalendarView />}
            {activeMenu === 'admin'        && isAdmin && <AdminPanelView />}
            {activeMenu === 'dashboard'    && <DashboardView onSelectMode={setActiveMenu} prices={prices} pairs={pairs} />}
            {activeMenu === 'telegram_bot' && <TelegramBotView />}
          </div>

        </div>{/* /MAIN */}
      </div>{/* /BODY */}

      {/* BOTTOM NAV — mobile */}
      <nav className="gas-bottom-nav">
        {[
          { id: 'dashboard',    ic: 'fa-solid fa-gauge-high',    lb: 'Home' },
          { id: 'telegram_bot', ic: 'fa-brands fa-telegram',     lb: 'AI Bot' },
          { id: 'markets',      ic: 'fa-solid fa-chart-line',    lb: 'Markets' },
          { id: 'calendars',    ic: 'fa-solid fa-calendar-days', lb: 'Calendar' },
          { id: 'settings',     ic: 'fa-solid fa-gear',          lb: 'Settings' },
        ].map(item => (
          <button key={item.id} className={`gas-bnav-item${activeMenu === item.id ? ' gas-bnav-item--on' : ''}`} onClick={() => setActiveMenu(item.id)}>
            <i className={`${item.ic} gas-bnav-ic`} />
            <span className="gas-bnav-lb">{item.lb}</span>
          </button>
        ))}
      </nav>

      {/* FLOATING ALERT */}
      {showAlert && (
        <div className="fixed top-16 right-4 z-[300] slide-in">
          <div style={{ background: 'var(--gas-elevated)', border: '1px solid rgba(240,170,0,0.25)', borderRadius: '12px', padding: '14px 16px', display: 'flex', alignItems: 'center', gap: '14px', boxShadow: '0 8px 32px rgba(0,0,0,.5)', minWidth: '260px', overflow: 'hidden', position: 'relative' }}>
            <div style={{ width: '38px', height: '38px', borderRadius: '8px', background: 'rgba(240,170,0,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <i className="fa-solid fa-bolt" style={{ color: 'var(--gas-gold)', fontSize: '16px' }} />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{ fontSize: '9px', color: 'var(--gas-gold)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '2px', marginBottom: '2px' }}>New Signal</p>
              <p style={{ fontSize: '13px', fontWeight: 700, color: 'white' }}>Check Telegram Bot</p>
            </div>
            <div className="absolute bottom-0 left-0 h-[2px] bg-yellow-400 alert-bar" />
          </div>
        </div>
      )}

      <TerminalWidget />
    </div>
  );
}

function AuthGate() {
  const { user, loading } = useAuth();
  const path = window.location.pathname;
  if (loading) return null;
  if (path === '/auth/callback') return <AuthCallback />;
  if (path === '/link-tg') return <LinkTelegramPage />;
  if (user) return <Terminal />;
  if (path === '/login') return <LoginPage />;
  if (path === '/signup') return <SignupPage />;
  return <LandingPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <AuthGate />
    </AuthProvider>
  );
}
