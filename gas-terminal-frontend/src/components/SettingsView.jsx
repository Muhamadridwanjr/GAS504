import React, { useState, useEffect } from 'react';
import {
  Moon, Sun, Bell, RefreshCw, BarChart2, Zap, Palette,
  Globe, Smartphone, Download, Check, Radio
} from 'lucide-react';

const DEFAULT_PREFS = {
  theme: 'dark',
  language: 'id',
  timezone: 'Asia/Jakarta',
  defaultPair: 'XAUUSD',
  defaultTimeframe: 'H4',
  notifications: true,
  signalSound: true,
  priceAlertSound: false,
  autoRefresh: true,
  showPnL: true,
  compactMode: false,
  chartType: 'candlestick',
  showVolume: true,
  showEMA: true,
  riskPerTrade: '1',
  // Ticker settings
  showLiveNews: true,
  showBreakingNews: true,
  showLivePair: true,
  tickerSpeed: '120',
};

function loadPrefs() {
  try {
    const stored = localStorage.getItem('gas-preferences');
    return stored ? { ...DEFAULT_PREFS, ...JSON.parse(stored) } : { ...DEFAULT_PREFS };
  } catch { return { ...DEFAULT_PREFS }; }
}

function savePrefs(prefs) {
  localStorage.setItem('gas-preferences', JSON.stringify(prefs));
}

function Toggle({ value, onChange }) {
  return (
    <button
      onClick={() => onChange(!value)}
      className={`w-11 h-6 rounded-full relative transition-all duration-200 focus:outline-none ${value ? 'bg-[var(--accent)]' : 'bg-[var(--bg-hover)] border border-[var(--border-color)]'}`}
    >
      <div className={`absolute top-[3px] w-[18px] h-[18px] rounded-full transition-all duration-200 shadow-sm ${value ? 'left-[22px] bg-black' : 'left-[3px] bg-[var(--text-dim)]'}`} />
    </button>
  );
}

function Sel({ value, onChange, options }) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className="bg-[var(--bg-hover)] border border-[var(--border-color)] text-[var(--text-primary)] text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-[var(--accent)] cursor-pointer"
    >
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  );
}

function Section({ title, icon, children }) {
  return (
    <div>
      <div className="flex items-center gap-2 px-1 mb-2">
        <div className="w-6 h-6 rounded-md bg-[var(--accent-soft)] flex items-center justify-center text-[var(--accent)]">{icon}</div>
        <h3 className="text-[11px] font-bold text-[var(--text-dim)] uppercase tracking-widest">{title}</h3>
      </div>
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden divide-y divide-[var(--border-subtle)]">
        {children}
      </div>
    </div>
  );
}

function Row({ label, sub, children }) {
  return (
    <div className="flex items-center justify-between px-4 py-3.5 hover:bg-[var(--bg-hover)] transition-colors">
      <div className="flex-1 min-w-0 mr-4">
        <p className="text-sm font-semibold text-[var(--text-primary)]">{label}</p>
        {sub && <p className="text-[11px] text-[var(--text-dim)] mt-0.5 leading-relaxed">{sub}</p>}
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  );
}

export default function SettingsView({ theme, setTheme }) {
  const [prefs, setPrefs] = useState(loadPrefs);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (theme && theme !== prefs.theme) {
      setPrefs(p => ({ ...p, theme }));
    }
  }, [theme]);

  function update(key, value) {
    const next = { ...prefs, [key]: value };
    setPrefs(next);
    savePrefs(next);
    if (key === 'theme' && setTheme) setTheme(value);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  }

  return (
    <div className="p-4 md:p-6 pb-24 md:pb-8 max-w-2xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-display font-black text-[var(--text-primary)] uppercase tracking-tight">Pengaturan Terminal</h2>
          <p className="text-xs text-[var(--text-dim)] mt-1">Konfigurasi pengalaman trading Anda</p>
        </div>
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all duration-300 ${saved ? 'bg-[var(--success-soft)] text-[var(--success)]' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)]'}`}>
          <Check size={11} />{saved ? 'Tersimpan' : 'Auto-save'}
        </div>
      </div>

      {/* APPEARANCE */}
      <Section title="Tampilan" icon={<Palette size={13} />}>
        <Row label="Mode Warna" sub="Tema gelap atau terang untuk terminal">
          <div className="flex items-center gap-1 p-1 bg-[var(--bg-main)] rounded-lg border border-[var(--border-color)]">
            {[
              { value: 'dark', icon: <Moon size={12} />, label: 'Gelap' },
              { value: 'light', icon: <Sun size={12} />, label: 'Terang' },
            ].map(t => (
              <button
                key={t.value}
                onClick={() => update('theme', t.value)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-bold transition-all ${prefs.theme === t.value ? 'bg-[var(--accent)] text-black shadow-sm' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </div>
        </Row>
        <Row label="Mode Kompak" sub="Kurangi padding elemen UI untuk layar kecil">
          <Toggle value={prefs.compactMode} onChange={v => update('compactMode', v)} />
        </Row>
        <Row label="Tampilkan P&L" sub="Tampilkan estimasi profit/loss di portofolio">
          <Toggle value={prefs.showPnL} onChange={v => update('showPnL', v)} />
        </Row>
      </Section>

      {/* NOTIFICATIONS */}
      <Section title="Notifikasi & Suara" icon={<Bell size={13} />}>
        <Row label="Notifikasi Browser" sub="Push notifikasi saat sinyal AI baru masuk">
          <Toggle value={prefs.notifications} onChange={v => {
            if (v && Notification.permission !== 'granted') {
              Notification.requestPermission().then(p => update('notifications', p === 'granted'));
            } else {
              update('notifications', v);
            }
          }} />
        </Row>
        <Row label="Suara Sinyal Baru" sub="Bunyi ping saat sinyal HOT atau HIGH masuk">
          <Toggle value={prefs.signalSound} onChange={v => update('signalSound', v)} />
        </Row>
        <Row label="Suara Alert Harga" sub="Bunyi saat harga mencapai level target">
          <Toggle value={prefs.priceAlertSound} onChange={v => update('priceAlertSound', v)} />
        </Row>
        <Row label="Auto Refresh Data" sub="Perbarui harga dan sinyal otomatis via WebSocket">
          <Toggle value={prefs.autoRefresh} onChange={v => update('autoRefresh', v)} />
        </Row>
      </Section>

      {/* TRADING DEFAULTS */}
      <Section title="Default Trading" icon={<BarChart2 size={13} />}>
        <Row label="Pair Default" sub="Pair yang dipilih otomatis saat buka terminal">
          <Sel value={prefs.defaultPair} onChange={v => update('defaultPair', v)} options={[
            { value: 'XAUUSD', label: 'XAU/USD — Gold' },
            { value: 'EURUSD', label: 'EUR/USD' },
            { value: 'GBPUSD', label: 'GBP/USD' },
            { value: 'USDJPY', label: 'USD/JPY' },
            { value: 'BTCUSDT', label: 'BTC/USDT' },
          ]} />
        </Row>
        <Row label="Timeframe Default" sub="Timeframe chart saat pertama dibuka">
          <Sel value={prefs.defaultTimeframe} onChange={v => update('defaultTimeframe', v)} options={[
            { value: 'M5', label: '5 Menit' }, { value: 'M15', label: '15 Menit' },
            { value: 'M30', label: '30 Menit' }, { value: 'H1', label: '1 Jam' },
            { value: 'H4', label: '4 Jam' }, { value: 'D1', label: '1 Hari' },
          ]} />
        </Row>
        <Row label="Tipe Chart" sub="Gaya tampilan chart default">
          <Sel value={prefs.chartType} onChange={v => update('chartType', v)} options={[
            { value: 'candlestick', label: 'Candlestick' },
            { value: 'bar', label: 'Bar Chart' },
            { value: 'line', label: 'Line Chart' },
          ]} />
        </Row>
        <Row label="Risk per Trade" sub="Persentase modal yang dipertaruhkan per transaksi">
          <Sel value={prefs.riskPerTrade} onChange={v => update('riskPerTrade', v)} options={[
            { value: '0.5', label: '0.5%' }, { value: '1', label: '1%' },
            { value: '1.5', label: '1.5%' }, { value: '2', label: '2%' },
            { value: '3', label: '3%' },
          ]} />
        </Row>
        <Row label="Tampilkan Volume" sub="Bar volume di bawah chart">
          <Toggle value={prefs.showVolume} onChange={v => update('showVolume', v)} />
        </Row>
        <Row label="Overlay EMA" sub="EMA 20/50/200 di chart secara default">
          <Toggle value={prefs.showEMA} onChange={v => update('showEMA', v)} />
        </Row>
      </Section>

      {/* TICKER & FEED */}
      <Section title="Ticker & Feed" icon={<Radio size={13} />}>
        <Row label="Live News Ticker" sub="Running news dari livenews.md di bagian atas">
          <Toggle value={prefs.showLiveNews !== false} onChange={v => update('showLiveNews', v)} />
        </Row>
        <Row label="Breaking News" sub="Strip merah dari breakingnews.md di bawah header">
          <Toggle value={prefs.showBreakingNews !== false} onChange={v => update('showBreakingNews', v)} />
        </Row>
        <Row label="Live Pair Ticker" sub="Harga pair berjalan di atas bottom nav">
          <Toggle value={prefs.showLivePair !== false} onChange={v => update('showLivePair', v)} />
        </Row>
        <Row label="Kecepatan Ticker" sub="Seberapa cepat running text berjalan">
          <Sel value={String(prefs.tickerSpeed || '120')} onChange={v => update('tickerSpeed', v)} options={[
            { value: '200', label: '🐌 Sangat Lambat' },
            { value: '150', label: '🐢 Lambat' },
            { value: '120', label: '▶️ Normal' },
            { value: '80',  label: '⚡ Cepat' },
            { value: '50',  label: '🚀 Sangat Cepat' },
          ]} />
        </Row>
      </Section>

      {/* REGIONAL */}
      <Section title="Regional" icon={<Globe size={13} />}>
        <Row label="Bahasa" sub="Bahasa antarmuka terminal">
          <Sel value={prefs.language} onChange={v => update('language', v)} options={[
            { value: 'id', label: '🇮🇩 Bahasa Indonesia' },
            { value: 'en', label: '🇺🇸 English' },
          ]} />
        </Row>
        <Row label="Zona Waktu" sub="Semua waktu sesi dan kalender">
          <Sel value={prefs.timezone} onChange={v => update('timezone', v)} options={[
            { value: 'Asia/Jakarta', label: 'WIB (UTC+7)' },
            { value: 'Asia/Makassar', label: 'WITA (UTC+8)' },
            { value: 'Asia/Jayapura', label: 'WIT (UTC+9)' },
            { value: 'UTC', label: 'UTC' },
          ]} />
        </Row>
      </Section>

      {/* APP */}
      <Section title="Aplikasi" icon={<Smartphone size={13} />}>
        <Row label="Android App" sub="Download aplikasi GAS untuk Android (APK)">
          <a
            href="/download/gas-trading.apk"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[var(--accent-soft)] border border-[var(--accent-mid)] text-[var(--accent)] text-xs font-bold rounded-lg hover:bg-[var(--accent-mid)] transition-colors"
          >
            <Download size={11} /> Download APK
          </a>
        </Row>
        <Row label="Versi Terminal" sub="Gas Terminal v2.5.0 — Build 2026.03">
          <span className="text-xs text-[var(--text-dim)] font-mono">v2.5.0</span>
        </Row>
        <Row label="Reset Pengaturan" sub="Kembalikan semua pengaturan ke default">
          <button
            onClick={() => {
              if (window.confirm('Reset semua pengaturan ke default?')) {
                savePrefs(DEFAULT_PREFS);
                setPrefs({ ...DEFAULT_PREFS });
                if (setTheme) setTheme('dark');
              }
            }}
            className="px-3 py-1.5 bg-[var(--danger-soft)] border border-[rgba(239,68,68,0.2)] text-[var(--danger)] text-xs font-bold rounded-lg hover:bg-[rgba(239,68,68,0.15)] transition-colors"
          >
            Reset
          </button>
        </Row>
      </Section>

      {/* Keyboard shortcuts */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4">
        <div className="flex items-center gap-2 mb-3">
          <Zap size={13} className="text-[var(--accent)]" />
          <span className="text-[11px] font-bold text-[var(--text-dim)] uppercase tracking-widest">Shortcut Keyboard</span>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {[['S','Sinyal AI'],['M','Markets'],['C','Calendar'],['A','Alerts'],['P','Portfolio'],['Esc','Tutup Panel']].map(([key, label]) => (
            <div key={key} className="flex items-center gap-2">
              <kbd className="px-2 py-0.5 bg-[var(--bg-hover)] border border-[var(--border-color)] rounded text-[10px] font-mono text-[var(--text-secondary)] min-w-[28px] text-center">{key}</kbd>
              <span className="text-[11px] text-[var(--text-dim)]">{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
