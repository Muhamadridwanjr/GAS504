// ═══════════════════════════════════════════════════════════════════════════
// GAS Platform — Master Pairs & Instruments Configuration
// Logo sources already used across the platform:
//   crypto  → cryptocurrency-icons CDN (jsdelivr)
//   forex   → flagcdn.com
//   stocks  → clearbit logo CDN
//   IDX     → sector emoji (no public CDN available)
// ═══════════════════════════════════════════════════════════════════════════

const CRYPTO_ICON = (sym) =>
  `https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@master/128/color/${sym.toLowerCase()}.png`;

const FLAG = (cc) =>
  `https://flagcdn.com/w40/${cc.toLowerCase()}.png`;

const STOCK_LOGO = (domain) =>
  `https://logo.clearbit.com/${domain}`;

// ── Binance / Crypto Major 10 ────────────────────────────────────────────────
export const CRYPTO_MAJOR = [
  { symbol: 'BTC/USDT',   ccxt: 'BTCUSDT',   name: 'Bitcoin',   short: 'BTC',   logo: CRYPTO_ICON('btc'),   color: '#f7931a', emoji: '₿'  },
  { symbol: 'ETH/USDT',   ccxt: 'ETHUSDT',   name: 'Ethereum',  short: 'ETH',   logo: CRYPTO_ICON('eth'),   color: '#627eea', emoji: '⬡'  },
  { symbol: 'BNB/USDT',   ccxt: 'BNBUSDT',   name: 'BNB',       short: 'BNB',   logo: CRYPTO_ICON('bnb'),   color: '#f3ba2f', emoji: '⬟'  },
  { symbol: 'SOL/USDT',   ccxt: 'SOLUSDT',   name: 'Solana',    short: 'SOL',   logo: CRYPTO_ICON('sol'),   color: '#9945ff', emoji: '◎'  },
  { symbol: 'XRP/USDT',   ccxt: 'XRPUSDT',   name: 'XRP',       short: 'XRP',   logo: CRYPTO_ICON('xrp'),   color: '#346aa9', emoji: '✕'  },
  { symbol: 'ADA/USDT',   ccxt: 'ADAUSDT',   name: 'Cardano',   short: 'ADA',   logo: CRYPTO_ICON('ada'),   color: '#0033ad', emoji: '◈'  },
  { symbol: 'DOGE/USDT',  ccxt: 'DOGEUSDT',  name: 'Dogecoin',  short: 'DOGE',  logo: CRYPTO_ICON('doge'),  color: '#c2a633', emoji: '🐶' },
  { symbol: 'TRX/USDT',   ccxt: 'TRXUSDT',   name: 'TRON',      short: 'TRX',   logo: CRYPTO_ICON('trx'),   color: '#c23631', emoji: '♦'  },
  { symbol: 'DOT/USDT',   ccxt: 'DOTUSDT',   name: 'Polkadot',  short: 'DOT',   logo: CRYPTO_ICON('dot'),   color: '#e6007a', emoji: '●'  },
  { symbol: 'MATIC/USDT', ccxt: 'MATICUSDT', name: 'Polygon',   short: 'MATIC', logo: CRYPTO_ICON('matic'), color: '#8247e5', emoji: '⬡'  },
];

// ── Binance / Crypto New Listings 10 ────────────────────────────────────────
export const CRYPTO_NEW_LISTINGS = [
  { symbol: 'JUP/USDT',   ccxt: 'JUPUSDT',   name: 'Jupiter',      short: 'JUP',   logo: CRYPTO_ICON('jup'),   color: '#c7a229', emoji: '🪐' },
  { symbol: 'WIF/USDT',   ccxt: 'WIFUSDT',   name: 'dogwifhat',    short: 'WIF',   logo: CRYPTO_ICON('wif'),   color: '#9945ff', emoji: '🐕' },
  { symbol: 'ENA/USDT',   ccxt: 'ENAUSDT',   name: 'Ethena',       short: 'ENA',   logo: CRYPTO_ICON('ena'),   color: '#7b61ff', emoji: '🔮' },
  { symbol: 'IO/USDT',    ccxt: 'IOUSDT',    name: 'io.net',       short: 'IO',    logo: CRYPTO_ICON('io'),    color: '#00d4ff', emoji: '🌐' },
  { symbol: 'EIGEN/USDT', ccxt: 'EIGENUSDT', name: 'Eigenlayer',   short: 'EIGEN', logo: CRYPTO_ICON('eigen'), color: '#6366f1', emoji: '⚙'  },
  { symbol: 'NOT/USDT',   ccxt: 'NOTUSDT',   name: 'Notcoin',      short: 'NOT',   logo: CRYPTO_ICON('not'),   color: '#e5ac00', emoji: '🔔' },
  { symbol: 'CATI/USDT',  ccxt: 'CATIUSDT',  name: 'Catizen',      short: 'CATI',  logo: CRYPTO_ICON('cati'),  color: '#ff9900', emoji: '🐱' },
  { symbol: 'HMSTR/USDT', ccxt: 'HMSTRUSDT', name: 'Hamster Kombat',short: 'HMSTR',logo: CRYPTO_ICON('hmstr'), color: '#ff6b35', emoji: '🐹' },
  { symbol: 'BOME/USDT',  ccxt: 'BOMEUSDT',  name: 'Book of Meme', short: 'BOME',  logo: CRYPTO_ICON('bome'),  color: '#ff6b35', emoji: '📖' },
  { symbol: 'DOGS/USDT',  ccxt: 'DOGSUSDT',  name: 'Dogs',         short: 'DOGS',  logo: CRYPTO_ICON('dogs'),  color: '#c2a633', emoji: '🐾' },
];

// ── Binance / Futures Perp Major 10 ─────────────────────────────────────────
export const CRYPTO_FUTURES = [
  { symbol: 'BTC/USDT:USDT',  ccxt: 'BTCUSDT',  name: 'Bitcoin Perp',   short: 'BTC',  logo: CRYPTO_ICON('btc'),  color: '#f7931a', emoji: '₿'  },
  { symbol: 'ETH/USDT:USDT',  ccxt: 'ETHUSDT',  name: 'Ethereum Perp',  short: 'ETH',  logo: CRYPTO_ICON('eth'),  color: '#627eea', emoji: '⬡'  },
  { symbol: 'SOL/USDT:USDT',  ccxt: 'SOLUSDT',  name: 'Solana Perp',    short: 'SOL',  logo: CRYPTO_ICON('sol'),  color: '#9945ff', emoji: '◎'  },
  { symbol: 'BNB/USDT:USDT',  ccxt: 'BNBUSDT',  name: 'BNB Perp',       short: 'BNB',  logo: CRYPTO_ICON('bnb'),  color: '#f3ba2f', emoji: '⬟'  },
  { symbol: 'XRP/USDT:USDT',  ccxt: 'XRPUSDT',  name: 'XRP Perp',       short: 'XRP',  logo: CRYPTO_ICON('xrp'),  color: '#346aa9', emoji: '✕'  },
  { symbol: 'DOGE/USDT:USDT', ccxt: 'DOGEUSDT', name: 'Dogecoin Perp',  short: 'DOGE', logo: CRYPTO_ICON('doge'), color: '#c2a633', emoji: '🐶' },
  { symbol: 'ADA/USDT:USDT',  ccxt: 'ADAUSDT',  name: 'Cardano Perp',   short: 'ADA',  logo: CRYPTO_ICON('ada'),  color: '#0033ad', emoji: '◈'  },
  { symbol: 'AVAX/USDT:USDT', ccxt: 'AVAXUSDT', name: 'Avalanche Perp', short: 'AVAX', logo: CRYPTO_ICON('avax'), color: '#e84142', emoji: '▲'  },
  { symbol: 'LINK/USDT:USDT', ccxt: 'LINKUSDT', name: 'Chainlink Perp', short: 'LINK', logo: CRYPTO_ICON('link'), color: '#375bd2', emoji: '⬡'  },
  { symbol: 'ARB/USDT:USDT',  ccxt: 'ARBUSDT',  name: 'Arbitrum Perp',  short: 'ARB',  logo: CRYPTO_ICON('arb'),  color: '#28a0f0', emoji: '◇'  },
];

// ── MT5 / Exness — Forex Major 10 ───────────────────────────────────────────
export const FOREX_MAJOR = [
  { symbol: 'EURUSD', name: 'Euro / USD',    logo: FLAG('eu'), decimals: 4, type: 'forex' },
  { symbol: 'GBPUSD', name: 'Pound / USD',   logo: FLAG('gb'), decimals: 4, type: 'forex' },
  { symbol: 'USDJPY', name: 'USD / Yen',     logo: FLAG('jp'), decimals: 2, type: 'forex' },
  { symbol: 'USDCHF', name: 'USD / Franc',   logo: FLAG('ch'), decimals: 4, type: 'forex' },
  { symbol: 'AUDUSD', name: 'Aussie / USD',  logo: FLAG('au'), decimals: 4, type: 'forex' },
  { symbol: 'NZDUSD', name: 'Kiwi / USD',    logo: FLAG('nz'), decimals: 4, type: 'forex' },
  { symbol: 'USDCAD', name: 'USD / CAD',     logo: FLAG('ca'), decimals: 4, type: 'forex' },
  { symbol: 'EURGBP', name: 'Euro / Pound',  logo: FLAG('eu'), decimals: 4, type: 'forex' },
  { symbol: 'EURJPY', name: 'Euro / Yen',    logo: FLAG('eu'), decimals: 2, type: 'forex' },
  { symbol: 'GBPJPY', name: 'Pound / Yen',   logo: FLAG('gb'), decimals: 2, type: 'forex' },
];

// ── MT5 / Exness — Commodities 10 ───────────────────────────────────────────
export const COMMODITIES = [
  { symbol: 'XAUUSD', name: 'Gold / USD',      emoji: '🥇', decimals: 2, type: 'commodity' },
  { symbol: 'XAGUSD', name: 'Silver / USD',    emoji: '🥈', decimals: 3, type: 'commodity' },
  { symbol: 'XPTUSD', name: 'Platinum / USD',  emoji: '⬜', decimals: 2, type: 'commodity' },
  { symbol: 'XPDUSD', name: 'Palladium / USD', emoji: '🔘', decimals: 2, type: 'commodity' },
  { symbol: 'UKOIL',  name: 'Brent Crude',     emoji: '🛢️', decimals: 2, type: 'energy'    },
  { symbol: 'USOIL',  name: 'WTI Crude',       emoji: '⛽', decimals: 2, type: 'energy'    },
  { symbol: 'COCOA',  name: 'Cocoa',           emoji: '🍫', decimals: 2, type: 'soft'      },
  { symbol: 'COFFEE', name: 'Coffee',          emoji: '☕', decimals: 2, type: 'soft'      },
  { symbol: 'SUGAR',  name: 'Sugar',           emoji: '🍬', decimals: 3, type: 'soft'      },
  { symbol: 'COTTON', name: 'Cotton',          emoji: '🌿', decimals: 3, type: 'soft'      },
];

// ── MT5 / Exness — Indices 10 ────────────────────────────────────────────────
export const INDICES = [
  { symbol: 'US30',   name: 'Dow Jones 30', logo: FLAG('us'), decimals: 0, type: 'index' },
  { symbol: 'US500',  name: 'S&P 500',      logo: FLAG('us'), decimals: 1, type: 'index' },
  { symbol: 'USTEC',  name: 'Nasdaq 100',   logo: FLAG('us'), decimals: 1, type: 'index' },
  { symbol: 'UK100',  name: 'FTSE 100',     logo: FLAG('gb'), decimals: 1, type: 'index' },
  { symbol: 'GER40',  name: 'DAX 40',       logo: FLAG('de'), decimals: 1, type: 'index' },
  { symbol: 'EU50',   name: 'Euro Stoxx 50',logo: FLAG('eu'), decimals: 1, type: 'index' },
  { symbol: 'HK50',   name: 'Hang Seng 50', logo: FLAG('hk'), decimals: 0, type: 'index' },
  { symbol: 'JP225',  name: 'Nikkei 225',   logo: FLAG('jp'), decimals: 0, type: 'index' },
  { symbol: 'AUS200', name: 'ASX 200',      logo: FLAG('au'), decimals: 1, type: 'index' },
  { symbol: 'FR40',   name: 'CAC 40',       logo: FLAG('fr'), decimals: 1, type: 'index' },
];

// ── MT5 / Exness — US Stocks 10 ─────────────────────────────────────────────
export const STOCKS_US = [
  { symbol: 'AAPL',  name: 'Apple',          logo: STOCK_LOGO('apple.com'),        decimals: 2 },
  { symbol: 'AMZN',  name: 'Amazon',         logo: STOCK_LOGO('amazon.com'),       decimals: 2 },
  { symbol: 'GOOGL', name: 'Alphabet',       logo: STOCK_LOGO('google.com'),       decimals: 2 },
  { symbol: 'MSFT',  name: 'Microsoft',      logo: STOCK_LOGO('microsoft.com'),    decimals: 2 },
  { symbol: 'TSLA',  name: 'Tesla',          logo: STOCK_LOGO('tesla.com'),        decimals: 2 },
  { symbol: 'NFLX',  name: 'Netflix',        logo: STOCK_LOGO('netflix.com'),      decimals: 2 },
  { symbol: 'META',  name: 'Meta Platforms', logo: STOCK_LOGO('meta.com'),         decimals: 2 },
  { symbol: 'NVDA',  name: 'NVIDIA',         logo: STOCK_LOGO('nvidia.com'),       decimals: 2 },
  { symbol: 'KO',    name: 'Coca-Cola',      logo: STOCK_LOGO('coca-cola.com'),    decimals: 2 },
  { symbol: 'JPM',   name: 'JPMorgan Chase', logo: STOCK_LOGO('jpmorganchase.com'),decimals: 2 },
];

// ── IDX — Major 25 ───────────────────────────────────────────────────────────
export const IDX_MAJOR = [
  'BBCA','BBRI','BMRI','BBNI','BRIS',
  'TLKM','ISAT','EXCL','GOTO','EMTK',
  'BREN','ADRO','PTBA','BYAN','CUAN',
  'INCO','ANTM','MDKA','AMMN','NCKL',
  'ASII','UNVR','ICBP','INDF','HMSP',
];

// ── IDX — New Listings 10 ────────────────────────────────────────────────────
export const IDX_NEW_LISTINGS = [
  'PGEO','WIFI','HEAL','DSSA','HRTA',
  'RATU','CUAN','AMMN','BREN','NCKL',
];

// ── IDX — Combined watchlist (no duplicates) ─────────────────────────────────
export const IDX_WATCHLIST = [...new Set([...IDX_MAJOR, ...IDX_NEW_LISTINGS])];

// ── Binance WebSocket streams — Spot ────────────────────────────────────────
// lowercase CCXT format used by websocket_manager.py
export const WS_SPOT_PAIRS = [
  // Crypto Major 10
  'btcusdt','ethusdt','bnbusdt','solusdt','xrpusdt',
  'adausdt','dogeusdt','trxusdt','dotusdt','maticusdt',
  // Extended large-cap
  'linkusdt','avaxusdt','ltcusdt','uniusdt','atomusdt',
  'nearusdt','arbusdt','opusdt','injusdt','aptusdt',
  'suiusdt','seiusdt','imxusdt','fetusdt','rndrusdt',
  // New listings
  'jupusdt','wifusdt','enausdt','eigenusdt','notusdt',
  'catiusdt','hmstrusdt','bomeusdt','dogsusdt','pepeusdt',
];

// ── Binance WebSocket streams — Futures ─────────────────────────────────────
export const WS_FUTURES_PAIRS = [
  // Major 10
  'btcusdt','ethusdt','bnbusdt','solusdt','xrpusdt',
  'adausdt','dogeusdt','trxusdt','dotusdt','maticusdt',
  // Extended
  'linkusdt','avaxusdt','ltcusdt','uniusdt','atomusdt',
  'nearusdt','arbusdt','opusdt','injusdt','aptusdt',
  'suiusdt','seiusdt','tiausdt','wifusdt','pepeusdt',
  'flokiusdt','wldusdt','blurusdt','fetusdt','rndrusdt',
];
