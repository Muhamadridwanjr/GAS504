// helper: quick trend array
const T = (a) => a;

export const PAIRS = [
    // ══════════════════════════════════════════════════════════
    // ── Crypto Spot (Binance) — 100 pairs ─────────────────────
    // ══════════════════════════════════════════════════════════
    // ── Mega Cap ──────────────────────────────────────────────
    { symbol: 'BTC/USDT',      name: 'Bitcoin',              base: 68783.71, vol: 50.0,   type: 'Crypto', trend: T([50,40,70,60,90,80,100,85,95,90]) },
    { symbol: 'ETH/USDT',      name: 'Ethereum',             base: 3505.41,  vol: 2.0,    type: 'Crypto', trend: T([70,65,75,85,80,95,100,90,98,92]) },
    { symbol: 'BNB/USDT',      name: 'BNB',                  base: 580.4,    vol: 1.5,    type: 'Crypto', trend: T([60,65,70,75,80,85,90,95,100,105]) },
    { symbol: 'SOL/USDT',      name: 'Solana',               base: 145.2,    vol: 1.0,    type: 'Crypto', trend: T([60,50,80,70,90,85,110,95,105,100]) },
    { symbol: 'XRP/USDT',      name: 'Ripple',               base: 0.62,     vol: 0.01,   type: 'Crypto', trend: T([40,45,50,55,60,65,70,75,80,85]) },
    { symbol: 'ADA/USDT',      name: 'Cardano',              base: 0.48,     vol: 0.01,   type: 'Crypto', trend: T([30,35,40,38,45,50,55,52,60,58]) },
    { symbol: 'AVAX/USDT',     name: 'Avalanche',            base: 38.5,     vol: 0.1,    type: 'Crypto', trend: T([40,45,55,50,65,60,75,70,80,78]) },
    { symbol: 'DOT/USDT',      name: 'Polkadot',             base: 7.8,      vol: 0.01,   type: 'Crypto', trend: T([30,28,35,33,40,38,45,42,48,46]) },
    { symbol: 'TRX/USDT',      name: 'TRON',                 base: 0.13,     vol: 0.001,  type: 'Crypto', trend: T([25,30,28,35,33,40,38,45,42,48]) },
    { symbol: 'TON/USDT',      name: 'Toncoin',              base: 5.5,      vol: 0.1,    type: 'Crypto', trend: T([35,40,50,55,65,60,70,65,75,72]) },
    // ── Large Cap ─────────────────────────────────────────────
    { symbol: 'LINK/USDT',     name: 'Chainlink',            base: 17.2,     vol: 0.05,   type: 'Crypto', trend: T([35,40,50,45,60,55,65,62,70,68]) },
    { symbol: 'MATIC/USDT',    name: 'Polygon',              base: 0.85,     vol: 0.01,   type: 'Crypto', trend: T([30,35,45,40,55,50,60,58,65,63]) },
    { symbol: 'LTC/USDT',      name: 'Litecoin',             base: 85.0,     vol: 0.1,    type: 'Crypto', trend: T([35,40,38,45,43,50,48,55,52,58]) },
    { symbol: 'BCH/USDT',      name: 'Bitcoin Cash',         base: 380.0,    vol: 0.5,    type: 'Crypto', trend: T([30,35,40,45,50,55,60,58,65,63]) },
    { symbol: 'ETC/USDT',      name: 'Ethereum Classic',     base: 28.0,     vol: 0.05,   type: 'Crypto', trend: T([25,28,32,30,36,34,38,36,42,40]) },
    { symbol: 'UNI/USDT',      name: 'Uniswap',              base: 10.5,     vol: 0.05,   type: 'Crypto', trend: T([28,32,38,35,42,40,48,45,52,50]) },
    { symbol: 'ATOM/USDT',     name: 'Cosmos',               base: 9.2,      vol: 0.05,   type: 'Crypto', trend: T([30,35,32,40,38,45,42,50,47,54]) },
    { symbol: 'FTM/USDT',      name: 'Fantom',               base: 0.65,     vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,34,32,38,36,42,40]) },
    { symbol: 'NEAR/USDT',     name: 'NEAR Protocol',        base: 7.4,      vol: 0.05,   type: 'Crypto', trend: T([30,35,40,38,45,43,50,48,55,52]) },
    { symbol: 'ALGO/USDT',     name: 'Algorand',             base: 0.19,     vol: 0.001,  type: 'Crypto', trend: T([20,22,25,23,28,26,30,28,33,31]) },
    { symbol: 'XLM/USDT',      name: 'Stellar',              base: 0.12,     vol: 0.001,  type: 'Crypto', trend: T([18,20,24,22,26,24,28,26,30,28]) },
    { symbol: 'VET/USDT',      name: 'VeChain',              base: 0.038,    vol: 0.0005, type: 'Crypto', trend: T([15,18,20,18,22,20,24,22,26,24]) },
    { symbol: 'HBAR/USDT',     name: 'Hedera',               base: 0.085,    vol: 0.001,  type: 'Crypto', trend: T([18,22,26,24,28,26,30,28,32,30]) },
    { symbol: 'KSM/USDT',      name: 'Kusama',               base: 28.0,     vol: 0.05,   type: 'Crypto', trend: T([25,28,32,30,35,33,38,36,42,40]) },
    { symbol: 'EOS/USDT',      name: 'EOS',                  base: 0.72,     vol: 0.005,  type: 'Crypto', trend: T([20,22,26,24,28,26,30,28,32,30]) },
    { symbol: 'THETA/USDT',    name: 'Theta Network',        base: 1.8,      vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,33,31,36,34,39,37]) },
    { symbol: 'EGLD/USDT',     name: 'MultiversX',           base: 38.0,     vol: 0.05,   type: 'Crypto', trend: T([30,34,38,36,42,40,46,44,50,48]) },
    { symbol: 'FLOW/USDT',     name: 'Flow',                 base: 0.72,     vol: 0.005,  type: 'Crypto', trend: T([18,22,26,24,28,26,30,28,32,30]) },
    // ── DeFi ──────────────────────────────────────────────────
    { symbol: 'AAVE/USDT',     name: 'Aave',                 base: 145.0,    vol: 0.1,    type: 'Crypto', trend: T([40,45,52,48,56,54,62,58,66,64]) },
    { symbol: 'MKR/USDT',      name: 'Maker',                base: 2450.0,   vol: 1.0,    type: 'Crypto', trend: T([45,50,55,52,60,58,65,62,70,68]) },
    { symbol: 'CRV/USDT',      name: 'Curve Finance',        base: 0.55,     vol: 0.005,  type: 'Crypto', trend: T([18,22,26,24,28,26,30,28,32,30]) },
    { symbol: 'SNX/USDT',      name: 'Synthetix',            base: 2.1,      vol: 0.01,   type: 'Crypto', trend: T([20,24,28,26,30,28,32,30,34,32]) },
    { symbol: 'COMP/USDT',     name: 'Compound',             base: 55.0,     vol: 0.05,   type: 'Crypto', trend: T([30,34,38,36,42,40,46,44,50,48]) },
    { symbol: 'YFI/USDT',      name: 'Yearn Finance',        base: 8500.0,   vol: 2.0,    type: 'Crypto', trend: T([40,45,50,48,55,52,58,56,62,60]) },
    { symbol: 'SUSHI/USDT',    name: 'SushiSwap',            base: 1.0,      vol: 0.005,  type: 'Crypto', trend: T([15,18,22,20,24,22,26,24,28,26]) },
    { symbol: '1INCH/USDT',    name: '1inch Network',        base: 0.42,     vol: 0.002,  type: 'Crypto', trend: T([14,16,20,18,22,20,24,22,26,24]) },
    { symbol: 'DYDX/USDT',     name: 'dYdX',                 base: 1.8,      vol: 0.01,   type: 'Crypto', trend: T([20,24,28,26,32,30,36,34,40,38]) },
    { symbol: 'GMX/USDT',      name: 'GMX',                  base: 28.0,     vol: 0.05,   type: 'Crypto', trend: T([25,28,32,30,35,33,38,36,42,40]) },
    { symbol: 'LDO/USDT',      name: 'Lido DAO',             base: 2.1,      vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,34,32,38,36,42,40]) },
    { symbol: 'CAKE/USDT',     name: 'PancakeSwap',          base: 2.2,      vol: 0.01,   type: 'Crypto', trend: T([20,24,28,26,30,28,32,30,34,32]) },
    { symbol: 'PENDLE/USDT',   name: 'Pendle',               base: 3.5,      vol: 0.01,   type: 'Crypto', trend: T([25,30,35,32,38,36,42,40,46,44]) },
    { symbol: 'RDNT/USDT',     name: 'Radiant Capital',      base: 0.085,    vol: 0.001,  type: 'Crypto', trend: T([12,15,18,16,20,18,22,20,24,22]) },
    // ── Layer 2 & Interop ─────────────────────────────────────
    { symbol: 'ARB/USDT',      name: 'Arbitrum',             base: 1.12,     vol: 0.01,   type: 'Crypto', trend: T([25,30,40,35,50,45,55,52,60,58]) },
    { symbol: 'OP/USDT',       name: 'Optimism',             base: 2.45,     vol: 0.01,   type: 'Crypto', trend: T([30,35,45,40,55,50,60,58,65,63]) },
    { symbol: 'IMX/USDT',      name: 'Immutable X',          base: 2.1,      vol: 0.01,   type: 'Crypto', trend: T([25,28,32,30,35,33,38,36,42,40]) },
    { symbol: 'STRK/USDT',     name: 'Starknet',             base: 0.9,      vol: 0.005,  type: 'Crypto', trend: T([18,22,26,24,28,26,30,28,32,30]) },
    { symbol: 'ZRO/USDT',      name: 'LayerZero',            base: 3.5,      vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,34,32,38,36,42,40]) },
    { symbol: 'W/USDT',        name: 'Wormhole',             base: 0.35,     vol: 0.002,  type: 'Crypto', trend: T([14,16,20,18,22,20,24,22,26,24]) },
    { symbol: 'CELR/USDT',     name: 'Celer Network',        base: 0.018,    vol: 0.0002, type: 'Crypto', trend: T([10,12,14,12,16,14,18,16,20,18]) },
    // ── AI & Web3 Infra ──────────────────────────────────────
    { symbol: 'FET/USDT',      name: 'Fetch.ai',             base: 2.3,      vol: 0.01,   type: 'Crypto', trend: T([28,33,38,35,42,39,46,43,50,47]) },
    { symbol: 'RNDR/USDT',     name: 'Render',               base: 8.5,      vol: 0.05,   type: 'Crypto', trend: T([30,35,42,38,46,43,50,47,54,51]) },
    { symbol: 'GRT/USDT',      name: 'The Graph',            base: 0.28,     vol: 0.001,  type: 'Crypto', trend: T([20,22,26,24,28,26,30,28,32,30]) },
    { symbol: 'INJ/USDT',      name: 'Injective',            base: 28.5,     vol: 0.1,    type: 'Crypto', trend: T([40,50,60,55,70,65,80,75,85,82]) },
    { symbol: 'WLD/USDT',      name: 'Worldcoin',            base: 2.5,      vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,34,32,38,36,42,40]) },
    { symbol: 'CYBER/USDT',    name: 'CyberConnect',         base: 3.5,      vol: 0.01,   type: 'Crypto', trend: T([20,24,28,26,30,28,32,30,34,32]) },
    // ── Storage & Identity ────────────────────────────────────
    { symbol: 'FIL/USDT',      name: 'Filecoin',             base: 6.2,      vol: 0.05,   type: 'Crypto', trend: T([25,28,32,30,35,33,38,36,42,40]) },
    { symbol: 'ICP/USDT',      name: 'Internet Computer',    base: 12.8,     vol: 0.05,   type: 'Crypto', trend: T([28,32,36,34,38,36,42,40,46,44]) },
    { symbol: 'STX/USDT',      name: 'Stacks',               base: 2.1,      vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,33,31,36,34,39,37]) },
    { symbol: 'ENS/USDT',      name: 'ENS',                  base: 18.0,     vol: 0.05,   type: 'Crypto', trend: T([28,32,36,34,38,36,42,40,46,44]) },
    { symbol: 'MASK/USDT',     name: 'Mask Network',         base: 2.8,      vol: 0.01,   type: 'Crypto', trend: T([20,24,28,26,30,28,32,30,34,32]) },
    // ── Layer 1 Alternatives ─────────────────────────────────
    { symbol: 'APT/USDT',      name: 'Aptos',                base: 9.2,      vol: 0.05,   type: 'Crypto', trend: T([30,35,45,40,55,50,60,58,65,63]) },
    { symbol: 'SUI/USDT',      name: 'Sui',                  base: 1.85,     vol: 0.01,   type: 'Crypto', trend: T([35,40,50,45,60,55,65,62,70,68]) },
    { symbol: 'SEI/USDT',      name: 'Sei',                  base: 0.62,     vol: 0.01,   type: 'Crypto', trend: T([25,28,32,30,35,33,38,36,42,40]) },
    { symbol: 'TIA/USDT',      name: 'Celestia',             base: 9.5,      vol: 0.05,   type: 'Crypto', trend: T([30,35,42,38,46,43,50,47,54,51]) },
    { symbol: 'ZETA/USDT',     name: 'ZetaChain',            base: 0.62,     vol: 0.005,  type: 'Crypto', trend: T([16,20,24,22,26,24,28,26,30,28]) },
    { symbol: 'KAVA/USDT',     name: 'Kava',                 base: 0.52,     vol: 0.002,  type: 'Crypto', trend: T([18,20,24,22,26,24,28,26,30,28]) },
    { symbol: 'ONE/USDT',      name: 'Harmony',              base: 0.015,    vol: 0.0002, type: 'Crypto', trend: T([8,10,12,10,13,11,14,12,15,13]) },
    { symbol: 'ZIL/USDT',      name: 'Zilliqa',              base: 0.017,    vol: 0.0002, type: 'Crypto', trend: T([8,10,12,10,13,11,14,12,15,13]) },
    { symbol: 'ROSE/USDT',     name: 'Oasis Network',        base: 0.085,    vol: 0.001,  type: 'Crypto', trend: T([12,15,18,16,20,18,22,20,24,22]) },
    { symbol: 'HOOK/USDT',     name: 'Hooked Protocol',      base: 0.65,     vol: 0.005,  type: 'Crypto', trend: T([16,20,24,22,26,24,28,26,30,28]) },
    { symbol: 'ACE/USDT',      name: 'Fusionist',            base: 4.5,      vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,32,30,34,32,36,34]) },
    // ── Gaming & Metaverse ────────────────────────────────────
    { symbol: 'AXS/USDT',      name: 'Axie Infinity',        base: 6.5,      vol: 0.05,   type: 'Crypto', trend: T([25,28,32,30,35,33,38,36,42,40]) },
    { symbol: 'SAND/USDT',     name: 'The Sandbox',          base: 0.42,     vol: 0.002,  type: 'Crypto', trend: T([18,20,24,22,26,24,28,26,30,28]) },
    { symbol: 'MANA/USDT',     name: 'Decentraland',         base: 0.38,     vol: 0.002,  type: 'Crypto', trend: T([16,18,22,20,24,22,26,24,28,26]) },
    { symbol: 'GALA/USDT',     name: 'Gala',                 base: 0.032,    vol: 0.0003, type: 'Crypto', trend: T([10,12,15,13,17,15,19,17,21,19]) },
    { symbol: 'CHZ/USDT',      name: 'Chiliz',               base: 0.075,    vol: 0.001,  type: 'Crypto', trend: T([12,15,18,16,20,18,22,20,24,22]) },
    { symbol: 'APE/USDT',      name: 'ApeCoin',              base: 1.45,     vol: 0.01,   type: 'Crypto', trend: T([20,22,26,24,28,26,30,28,32,30]) },
    // ── Memes & Culture ──────────────────────────────────────
    { symbol: 'DOGE/USDT',     name: 'Dogecoin',             base: 0.16,     vol: 0.001,  type: 'Crypto', trend: T([20,25,35,30,45,40,55,50,60,58]) },
    { symbol: 'SHIB/USDT',     name: 'Shiba Inu',            base: 0.0000245,vol: 0.0001, type: 'Crypto', trend: T([20,25,30,28,35,32,40,38,45,42]) },
    { symbol: 'PEPE/USDT',     name: 'Pepe',                 base: 0.0000132,vol: 0.0001, type: 'Crypto', trend: T([20,25,35,30,45,55,65,60,70,68]) },
    { symbol: 'WIF/USDT',      name: 'dogwifhat',            base: 2.8,      vol: 0.01,   type: 'Crypto', trend: T([20,25,30,35,45,40,55,50,60,58]) },
    { symbol: 'FLOKI/USDT',    name: 'Floki',                base: 0.00016,  vol: 0.0001, type: 'Crypto', trend: T([12,15,20,18,24,22,28,26,32,30]) },
    { symbol: 'BONK/USDT',     name: 'Bonk',                 base: 0.000027, vol: 0.0001, type: 'Crypto', trend: T([10,13,18,15,22,19,26,23,30,27]) },
    { symbol: 'BOME/USDT',     name: 'BOOK OF MEME',         base: 0.0085,   vol: 0.0001, type: 'Crypto', trend: T([10,14,18,16,22,20,26,24,30,28]) },
    { symbol: 'MEME/USDT',     name: 'Memecoin',             base: 0.022,    vol: 0.0002, type: 'Crypto', trend: T([10,12,16,14,18,16,20,18,22,20]) },
    { symbol: 'DOGS/USDT',     name: 'Dogs',                 base: 0.00085,  vol: 0.0001, type: 'Crypto', trend: T([8,10,13,11,15,13,17,15,19,17]) },
    { symbol: 'HMSTR/USDT',    name: 'Hamster Kombat',       base: 0.0042,   vol: 0.0001, type: 'Crypto', trend: T([8,10,13,11,15,13,17,15,19,17]) },
    { symbol: 'POPCAT/USDT',   name: 'Popcat',               base: 0.85,     vol: 0.005,  type: 'Crypto', trend: T([14,18,22,20,26,24,30,28,34,32]) },
    // ── New Ecosystem (2024-2025) ─────────────────────────────
    { symbol: 'JUP/USDT',      name: 'Jupiter',              base: 1.2,      vol: 0.01,   type: 'Crypto', trend: T([20,24,28,26,32,30,36,34,40,38]) },
    { symbol: 'PYTH/USDT',     name: 'Pyth Network',         base: 0.45,     vol: 0.002,  type: 'Crypto', trend: T([16,20,24,22,26,24,28,26,30,28]) },
    { symbol: 'JTO/USDT',      name: 'Jito',                 base: 3.8,      vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,34,32,38,36,42,40]) },
    { symbol: 'ENA/USDT',      name: 'Ethena',               base: 0.85,     vol: 0.005,  type: 'Crypto', trend: T([18,22,26,24,28,26,30,28,32,30]) },
    { symbol: 'NOT/USDT',      name: 'Notcoin',              base: 0.012,    vol: 0.0001, type: 'Crypto', trend: T([10,12,15,13,17,15,19,17,21,19]) },
    { symbol: 'ORDI/USDT',     name: 'ORDI',                 base: 35.0,     vol: 0.1,    type: 'Crypto', trend: T([30,35,42,38,46,43,50,47,54,51]) },
    { symbol: 'EIGEN/USDT',    name: 'Eigenlayer',           base: 2.1,      vol: 0.01,   type: 'Crypto', trend: T([18,22,26,24,28,26,30,28,32,30]) },
    { symbol: 'ETHFI/USDT',    name: 'Ether.fi',             base: 2.8,      vol: 0.01,   type: 'Crypto', trend: T([20,24,28,26,30,28,32,30,34,32]) },
    { symbol: 'LISTA/USDT',    name: 'Lista DAO',            base: 0.42,     vol: 0.002,  type: 'Crypto', trend: T([14,16,20,18,22,20,24,22,26,24]) },
    { symbol: 'IO/USDT',       name: 'io.net',               base: 3.8,      vol: 0.01,   type: 'Crypto', trend: T([22,26,30,28,34,32,38,36,42,40]) },
    { symbol: 'CATI/USDT',     name: 'Catizen',              base: 0.45,     vol: 0.002,  type: 'Crypto', trend: T([14,18,22,20,24,22,26,24,28,26]) },
    { symbol: 'BLUR/USDT',     name: 'Blur',                 base: 0.28,     vol: 0.001,  type: 'Crypto', trend: T([14,16,20,18,22,20,24,22,26,24]) },
    { symbol: 'JASMY/USDT',    name: 'JasmyCoin',            base: 0.018,    vol: 0.0002, type: 'Crypto', trend: T([8,10,13,11,15,13,17,15,19,17]) },
    // ══════════════════════════════════════════════════════════
    // ── Crypto Futures (Binance USDT-M Perp) ──────────────────
    // ══════════════════════════════════════════════════════════
    { symbol: 'BTC/USDT:USDT', name: 'BTC Perp Futures',     base: 68800.0,  vol: 55.0,   type: 'Futures', trend: T([50,45,75,65,95,85,105,90,100,95]) },
    { symbol: 'ETH/USDT:USDT', name: 'ETH Perp Futures',     base: 3510.0,   vol: 3.0,    type: 'Futures', trend: T([65,60,70,80,75,90,95,85,93,88]) },
    { symbol: 'SOL/USDT:USDT', name: 'SOL Perp Futures',     base: 146.0,    vol: 1.2,    type: 'Futures', trend: T([55,45,75,65,85,80,105,90,100,95]) },
    { symbol: 'BNB/USDT:USDT', name: 'BNB Perp Futures',     base: 582.0,    vol: 2.0,    type: 'Futures', trend: T([60,65,70,75,80,85,90,95,100,105]) },
    { symbol: 'XRP/USDT:USDT', name: 'XRP Perp Futures',     base: 0.621,    vol: 0.5,    type: 'Futures', trend: T([40,45,50,55,60,65,70,75,80,85]) },
    { symbol: 'ARB/USDT:USDT', name: 'ARB Perp Futures',     base: 1.12,     vol: 0.2,    type: 'Futures', trend: T([25,30,40,35,50,45,55,52,60,58]) },
    { symbol: 'DOGE/USDT:USDT',name: 'DOGE Perp Futures',    base: 0.16,     vol: 0.3,    type: 'Futures', trend: T([20,25,35,30,45,40,55,50,60,58]) },
    { symbol: 'AVAX/USDT:USDT',name: 'AVAX Perp Futures',    base: 38.5,     vol: 0.5,    type: 'Futures', trend: T([40,45,55,50,65,60,75,70,80,78]) },
    { symbol: 'INJ/USDT:USDT', name: 'INJ Perp Futures',     base: 28.5,     vol: 0.3,    type: 'Futures', trend: T([40,50,60,55,70,65,80,75,85,82]) },
    { symbol: 'SUI/USDT:USDT', name: 'SUI Perp Futures',     base: 1.85,     vol: 0.2,    type: 'Futures', trend: T([35,40,50,45,60,55,65,62,70,68]) },
    // ══════════════════════════════════════════════════════════
    // ── MT5 / Exness Markets ──────────────────────────────────
    // ══════════════════════════════════════════════════════════
    // ── Forex Major Pairs (7) ────────────────────────────────
    { symbol: 'AUDUSD', name: 'AUD / USD',        base: 0.6580,  vol: 0.0001, type: 'Forex', subType: 'Major', trend: T([30,35,32,40,38,45,42,48,44,50]) },
    { symbol: 'EURUSD', name: 'EUR / USD',        base: 1.0855,  vol: 0.0001, type: 'Forex', subType: 'Major', trend: T([20,25,22,30,28,35,32,38,30,36]) },
    { symbol: 'GBPUSD', name: 'GBP / USD',        base: 1.2635,  vol: 0.0001, type: 'Forex', subType: 'Major', trend: T([40,45,42,50,48,55,52,58,50,56]) },
    { symbol: 'NZDUSD', name: 'NZD / USD',        base: 0.6040,  vol: 0.0001, type: 'Forex', subType: 'Major', trend: T([25,28,26,32,30,36,33,38,35,40]) },
    { symbol: 'USDCAD', name: 'USD / CAD',        base: 1.3742,  vol: 0.0001, type: 'Forex', subType: 'Major', trend: T([35,38,40,44,42,48,45,50,47,52]) },
    { symbol: 'USDCHF', name: 'USD / CHF',        base: 0.9002,  vol: 0.0001, type: 'Forex', subType: 'Major', trend: T([30,33,35,38,36,42,39,44,41,45]) },
    { symbol: 'USDJPY', name: 'USD / JPY',        base: 153.88,  vol: 0.01,   type: 'Forex', subType: 'Major', trend: T([40,50,45,55,60,58,65,62,70,67]) },
    // ── Forex Minor / Cross Pairs (25) ──────────────────────
    { symbol: 'AUDCAD', name: 'AUD / CAD',        base: 0.9054,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([28,30,33,31,35,33,37,35,39,37]) },
    { symbol: 'AUDCHF', name: 'AUD / CHF',        base: 0.5912,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([24,26,29,27,31,29,33,31,35,33]) },
    { symbol: 'AUDJPY', name: 'AUD / JPY',        base: 101.32,  vol: 0.01,   type: 'Forex', subType: 'Minor', trend: T([30,35,38,33,40,37,43,40,46,43]) },
    { symbol: 'AUDNZD', name: 'AUD / NZD',        base: 1.0893,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([26,28,31,29,33,31,35,33,37,35]) },
    { symbol: 'CADCHF', name: 'CAD / CHF',        base: 0.6552,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([22,24,27,25,29,27,31,29,33,31]) },
    { symbol: 'CADJPY', name: 'CAD / JPY',        base: 111.98,  vol: 0.01,   type: 'Forex', subType: 'Minor', trend: T([32,36,39,34,41,38,44,41,47,44]) },
    { symbol: 'CHFJPY', name: 'CHF / JPY',        base: 170.98,  vol: 0.01,   type: 'Forex', subType: 'Minor', trend: T([36,40,43,38,45,42,48,45,51,48]) },
    { symbol: 'EURAUD', name: 'EUR / AUD',        base: 1.6498,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([28,30,33,31,35,33,37,35,39,37]) },
    { symbol: 'EURCAD', name: 'EUR / CAD',        base: 1.4900,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([26,28,31,29,33,31,35,33,37,35]) },
    { symbol: 'EURCHF', name: 'EUR / CHF',        base: 0.9768,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([24,26,29,27,31,29,33,31,35,33]) },
    { symbol: 'EURGBP', name: 'EUR / GBP',        base: 0.8590,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([22,24,27,25,29,27,31,29,33,31]) },
    { symbol: 'EURJPY', name: 'EUR / JPY',        base: 166.98,  vol: 0.01,   type: 'Forex', subType: 'Minor', trend: T([34,38,41,36,43,40,46,43,49,46]) },
    { symbol: 'EURNZD', name: 'EUR / NZD',        base: 1.7966,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([28,30,33,31,35,33,37,35,39,37]) },
    { symbol: 'GBPAUD', name: 'GBP / AUD',        base: 1.9198,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([30,32,35,33,37,35,39,37,41,39]) },
    { symbol: 'GBPCAD', name: 'GBP / CAD',        base: 1.7345,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([28,30,33,31,35,33,37,35,39,37]) },
    { symbol: 'GBPCHF', name: 'GBP / CHF',        base: 1.1374,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([26,28,31,29,33,31,35,33,37,35]) },
    { symbol: 'GBPJPY', name: 'GBP / JPY',        base: 194.50,  vol: 0.01,   type: 'Forex', subType: 'Minor', trend: T([35,40,38,48,45,55,52,58,54,62]) },
    { symbol: 'GBPNZD', name: 'GBP / NZD',        base: 2.0924,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([30,32,35,33,37,35,39,37,41,39]) },
    { symbol: 'HKDJPY', name: 'HKD / JPY',        base: 19.72,   vol: 0.001,  type: 'Forex', subType: 'Minor', trend: T([22,24,26,24,28,26,30,28,32,30]) },
    { symbol: 'NZDCAD', name: 'NZD / CAD',        base: 0.8304,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([22,24,27,25,29,27,31,29,33,31]) },
    { symbol: 'NZDCHF', name: 'NZD / CHF',        base: 0.5432,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([20,22,25,23,27,25,29,27,31,29]) },
    { symbol: 'NZDJPY', name: 'NZD / JPY',        base: 92.98,   vol: 0.01,   type: 'Forex', subType: 'Minor', trend: T([28,32,35,30,37,34,40,37,43,40]) },
    { symbol: 'USDCNH', name: 'USD / CNH',        base: 7.2490,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([30,32,35,33,37,35,39,37,41,39]) },
    { symbol: 'USDHKD', name: 'USD / HKD',        base: 7.8200,  vol: 0.0001, type: 'Forex', subType: 'Minor', trend: T([20,21,22,21,22,21,22,21,22,21]) },
    { symbol: 'USDTHB', name: 'USD / THB',        base: 36.450,  vol: 0.001,  type: 'Forex', subType: 'Minor', trend: T([28,30,32,30,34,32,36,34,38,36]) },
    // ── Precious Metals ──────────────────────────────────────
    { symbol: 'XAUUSD', name: 'Gold / USD',       base: 2389.87, vol: 0.5,    type: 'Commodity', subType: 'Precious',   trend: T([30,45,40,60,55,75,70,65,80,75]) },
    { symbol: 'XAGUSD', name: 'Silver / USD',     base: 28.45,   vol: 0.01,   type: 'Commodity', subType: 'Precious',   trend: T([25,30,35,40,45,50,55,50,60,58]) },
    { symbol: 'XAGAUD', name: 'Silver / AUD',     base: 43.32,   vol: 0.01,   type: 'Commodity', subType: 'Precious',   trend: T([22,27,32,37,42,47,52,47,57,55]) },
    { symbol: 'XAGGBP', name: 'Silver / GBP',     base: 22.48,   vol: 0.01,   type: 'Commodity', subType: 'Precious',   trend: T([22,27,32,37,42,47,52,47,57,55]) },
    { symbol: 'XAGEUR', name: 'Silver / EUR',     base: 26.25,   vol: 0.01,   type: 'Commodity', subType: 'Precious',   trend: T([22,27,32,37,42,47,52,47,57,55]) },
    { symbol: 'XPDUSD', name: 'Palladium / USD',  base: 990.50,  vol: 0.5,    type: 'Commodity', subType: 'Precious',   trend: T([40,35,38,42,40,45,43,48,45,50]) },
    { symbol: 'XPTUSD', name: 'Platinum / USD',   base: 890.30,  vol: 0.5,    type: 'Commodity', subType: 'Precious',   trend: T([35,38,40,44,42,48,45,50,47,52]) },
    // ── Industrial Metals ────────────────────────────────────
    { symbol: 'XALUSD', name: 'Aluminium / USD',  base: 2250.0,  vol: 1.0,    type: 'Commodity', subType: 'Industrial', trend: T([30,33,36,34,38,36,40,38,42,40]) },
    { symbol: 'XCUUSD', name: 'Copper / USD',     base: 4.320,   vol: 0.001,  type: 'Commodity', subType: 'Industrial', trend: T([32,35,38,36,40,38,42,40,44,42]) },
    { symbol: 'XNIUSD', name: 'Nickel / USD',     base: 16500.0, vol: 5.0,    type: 'Commodity', subType: 'Industrial', trend: T([28,30,33,31,35,33,37,35,39,37]) },
    { symbol: 'XPBUSD', name: 'Lead / USD',       base: 2050.0,  vol: 1.0,    type: 'Commodity', subType: 'Industrial', trend: T([25,27,30,28,32,30,34,32,36,34]) },
    { symbol: 'XZNUSD', name: 'Zinc / USD',       base: 2480.0,  vol: 1.0,    type: 'Commodity', subType: 'Industrial', trend: T([26,28,31,29,33,31,35,33,37,35]) },
    // ── Energy ───────────────────────────────────────────────
    { symbol: 'USOIL',  name: 'Crude Oil WTI',    base: 78.30,   vol: 0.1,    type: 'Commodity', subType: 'Energy',     trend: T([40,35,50,45,55,60,65,60,70,68]) },
    { symbol: 'UKOIL',  name: 'Crude Oil Brent',  base: 82.50,   vol: 0.1,    type: 'Commodity', subType: 'Energy',     trend: T([38,33,48,43,53,58,63,58,68,66]) },
    { symbol: 'XNGUSD', name: 'Natural Gas / USD',base: 1.780,   vol: 0.001,  type: 'Commodity', subType: 'Energy',     trend: T([30,25,35,40,38,45,42,50,47,52]) },
    // ── US Indices ───────────────────────────────────────────
    { symbol: 'US30',       name: 'Dow Jones 30',     base: 38700.0, vol: 1.0, type: 'Index', subType: 'US',     trend: T([40,45,50,55,60,65,70,68,75,73]) },
    { symbol: 'US500',      name: 'S&P 500',           base: 5270.0,  vol: 0.5, type: 'Index', subType: 'US',     trend: T([42,48,53,58,63,68,73,70,78,76]) },
    { symbol: 'USTEC',      name: 'Nasdaq 100',        base: 18250.0, vol: 1.0, type: 'Index', subType: 'US',     trend: T([45,50,55,60,65,70,75,72,80,78]) },
    { symbol: 'US30_x10',   name: 'US30 x10',          base: 38700.0, vol: 1.0, type: 'Index', subType: 'US',     trend: T([40,45,50,55,60,65,70,68,75,73]) },
    { symbol: 'US500_x100', name: 'S&P 500 x100',      base: 5270.0,  vol: 0.5, type: 'Index', subType: 'US',     trend: T([42,48,53,58,63,68,73,70,78,76]) },
    { symbol: 'USTEC_x100', name: 'Nasdaq 100 x100',   base: 18250.0, vol: 1.0, type: 'Index', subType: 'US',     trend: T([45,50,55,60,65,70,75,72,80,78]) },
    // ── Europe Indices ───────────────────────────────────────
    { symbol: 'DE30',    name: 'DAX Germany 30',   base: 18200.0, vol: 1.0, type: 'Index', subType: 'Europe', trend: T([38,43,48,53,58,63,68,65,72,70]) },
    { symbol: 'UK100',   name: 'FTSE 100 UK',      base: 8090.0,  vol: 1.0, type: 'Index', subType: 'Europe', trend: T([36,40,45,50,55,60,65,62,70,68]) },
    { symbol: 'FR40',    name: 'CAC 40 France',    base: 7940.0,  vol: 1.0, type: 'Index', subType: 'Europe', trend: T([38,42,47,52,57,62,67,64,71,69]) },
    { symbol: 'STOXX50', name: 'Euro Stoxx 50',    base: 4980.0,  vol: 0.5, type: 'Index', subType: 'Europe', trend: T([36,40,45,50,55,60,65,62,70,68]) },
    // ── Asia-Pacific Indices ─────────────────────────────────
    { symbol: 'JP225',  name: 'Nikkei 225 Japan',  base: 40100.0, vol: 5.0, type: 'Index', subType: 'Asia',   trend: T([40,45,50,55,60,65,70,68,75,73]) },
    { symbol: 'HK50',   name: 'Hang Seng HK 50',   base: 18500.0, vol: 5.0, type: 'Index', subType: 'Asia',   trend: T([30,35,40,38,45,42,48,45,52,50]) },
    { symbol: 'AUS200', name: 'ASX 200 Australia', base: 7780.0,  vol: 1.0, type: 'Index', subType: 'Asia',   trend: T([35,40,45,50,55,60,65,62,68,66]) },
    // ── Other Index ──────────────────────────────────────────
    { symbol: 'DXY',    name: 'US Dollar Index',   base: 104.20,  vol: 0.01, type: 'Index', subType: 'Other',  trend: T([45,42,40,44,42,46,43,47,44,48]) },
    // ── US Stocks ────────────────────────────────────────────
    { symbol: 'AAPL',   name: 'Apple Inc.',            base: 189.30,  vol: 0.01, type: 'StockUS', trend: T([50,55,60,58,65,62,68,65,72,70]) },
    { symbol: 'MSFT',   name: 'Microsoft Corp.',       base: 418.50,  vol: 0.01, type: 'StockUS', trend: T([55,60,65,63,70,67,73,70,77,75]) },
    { symbol: 'GOOGL',  name: 'Alphabet Inc.',         base: 175.40,  vol: 0.01, type: 'StockUS', trend: T([48,53,58,56,62,60,66,63,69,67]) },
    { symbol: 'AMZN',   name: 'Amazon.com Inc.',       base: 194.80,  vol: 0.01, type: 'StockUS', trend: T([52,57,62,60,67,64,70,67,74,72]) },
    { symbol: 'TSLA',   name: 'Tesla Inc.',            base: 175.20,  vol: 0.01, type: 'StockUS', trend: T([40,50,45,55,50,60,55,65,60,68]) },
    { symbol: 'META',   name: 'Meta Platforms',        base: 527.80,  vol: 0.01, type: 'StockUS', trend: T([55,60,68,65,72,70,78,75,82,80]) },
    { symbol: 'NVDA',   name: 'NVIDIA Corp.',          base: 880.50,  vol: 0.01, type: 'StockUS', trend: T([60,70,75,80,85,90,95,88,98,95]) },
    { symbol: 'NFLX',   name: 'Netflix Inc.',          base: 645.30,  vol: 0.01, type: 'StockUS', trend: T([45,50,55,53,60,57,63,60,67,65]) },
    { symbol: 'AMD',    name: 'Advanced Micro Dev.',   base: 162.40,  vol: 0.01, type: 'StockUS', trend: T([40,48,52,58,55,62,60,68,65,72]) },
    { symbol: 'INTC',   name: 'Intel Corp.',           base: 31.20,   vol: 0.01, type: 'StockUS', trend: T([30,28,32,30,35,32,36,34,38,36]) },
    { symbol: 'V',      name: 'Visa Inc.',             base: 275.40,  vol: 0.01, type: 'StockUS', trend: T([45,50,55,52,58,55,61,58,64,62]) },
    { symbol: 'MA',     name: 'Mastercard Inc.',       base: 475.80,  vol: 0.01, type: 'StockUS', trend: T([47,52,57,54,60,57,63,60,66,64]) },
    { symbol: 'JPM',    name: 'JPMorgan Chase',        base: 198.50,  vol: 0.01, type: 'StockUS', trend: T([45,50,55,52,58,55,61,58,64,62]) },
    { symbol: 'BAC',    name: 'Bank of America',       base: 37.80,   vol: 0.01, type: 'StockUS', trend: T([35,38,42,40,45,43,48,45,50,48]) },
    { symbol: 'WMT',    name: 'Walmart Inc.',          base: 68.50,   vol: 0.01, type: 'StockUS', trend: T([40,43,47,45,50,48,53,50,55,53]) },
    { symbol: 'DIS',    name: 'Walt Disney Co.',       base: 105.30,  vol: 0.01, type: 'StockUS', trend: T([35,38,42,40,45,43,48,45,50,48]) },
    { symbol: 'CRM',    name: 'Salesforce Inc.',       base: 298.40,  vol: 0.01, type: 'StockUS', trend: T([42,47,52,50,56,53,59,56,62,60]) },
    { symbol: 'PYPL',   name: 'PayPal Holdings',       base: 65.30,   vol: 0.01, type: 'StockUS', trend: T([30,33,37,35,40,38,43,40,45,43]) },
    { symbol: 'UBER',   name: 'Uber Technologies',     base: 74.50,   vol: 0.01, type: 'StockUS', trend: T([38,42,46,44,49,47,52,49,54,52]) },
    { symbol: 'COIN',   name: 'Coinbase Global',       base: 213.40,  vol: 0.01, type: 'StockUS', trend: T([40,50,55,60,65,70,75,68,78,75]) },
    { symbol: 'PLTR',   name: 'Palantir Technologies', base: 24.80,   vol: 0.01, type: 'StockUS', trend: T([35,40,45,43,50,47,53,50,56,54]) },
    // ── Global Stocks ────────────────────────────────────────
    { symbol: 'BABA',   name: 'Alibaba Group',         base: 72.80,   vol: 0.01, type: 'StockGlobal', trend: T([30,35,40,38,43,41,46,43,48,46]) },
    { symbol: 'TSM',    name: 'Taiwan Semi. (TSMC)',   base: 144.50,  vol: 0.01, type: 'StockGlobal', trend: T([45,50,55,52,58,55,61,58,64,62]) },
    { symbol: 'BIDU',   name: 'Baidu Inc.',            base: 98.30,   vol: 0.01, type: 'StockGlobal', trend: T([28,32,36,34,38,36,40,38,42,40]) },
    { symbol: 'NIO',    name: 'NIO Inc.',              base: 4.98,    vol: 0.001,type: 'StockGlobal', trend: T([20,24,28,26,30,28,32,30,34,32]) },
    { symbol: 'SONY',   name: 'Sony Group Corp.',      base: 86.40,   vol: 0.01, type: 'StockGlobal', trend: T([38,42,46,44,49,47,52,49,54,52]) },
    { symbol: 'SAP',    name: 'SAP SE',                base: 192.30,  vol: 0.01, type: 'StockGlobal', trend: T([42,46,50,48,53,51,56,53,58,56]) },
    { symbol: 'ASML',   name: 'ASML Holding',         base: 912.40,  vol: 0.1,  type: 'StockGlobal', trend: T([50,55,60,58,65,62,68,65,72,70]) },
    { symbol: 'SHOP',   name: 'Shopify Inc.',          base: 72.30,   vol: 0.01, type: 'StockGlobal', trend: T([38,42,47,45,50,48,53,50,55,53]) },
    { symbol: 'MELI',   name: 'MercadoLibre Inc.',     base: 1685.0,  vol: 0.1,  type: 'StockGlobal', trend: T([45,50,55,52,58,55,61,58,64,62]) },
    { symbol: 'SE',     name: 'Sea Limited',           base: 52.80,   vol: 0.01, type: 'StockGlobal', trend: T([32,36,40,38,43,41,46,43,48,46]) },
    { symbol: 'GRAB',   name: 'Grab Holdings',         base: 3.62,    vol: 0.001,type: 'StockGlobal', trend: T([22,26,30,28,32,30,34,32,36,34]) },
    { symbol: 'VALE',   name: 'Vale S.A.',             base: 13.50,   vol: 0.001,type: 'StockGlobal', trend: T([28,30,34,32,36,34,38,36,40,38]) },
    { symbol: 'BHP',    name: 'BHP Group',             base: 58.40,   vol: 0.01, type: 'StockGlobal', trend: T([35,38,42,40,45,43,48,45,50,48]) },
    { symbol: 'RIO',    name: 'Rio Tinto Group',       base: 74.20,   vol: 0.01, type: 'StockGlobal', trend: T([33,36,40,38,43,41,46,43,48,46]) },
    { symbol: 'HSBA',   name: 'HSBC Holdings',         base: 41.80,   vol: 0.01, type: 'StockGlobal', trend: T([30,33,37,35,40,38,43,40,45,43]) },
];


export const GLOBAL_INDICES = [
    { name: 'S&P 500', value: 5274.39, change: -14.39, pct: -0.27 },
    { name: 'DOW30', value: 38772.81, change: -213.81, pct: -0.55 },
    { name: 'HANGSENG', value: 25183.57, change: +123.57, pct: +0.49 },
    { name: 'NIKKEI225', value: 40142.15, change: +122.15, pct: +0.31 },
    { name: 'SHANGHAI', value: 3829.23, change: -12.23, pct: -0.32 },
    { name: 'FTSE', value: 9624.89, change: -122.89, pct: -1.26 },
];

export const NEWS_FEED = [
    "🔥 FED beri sinyal tahan suku bunga Q3",
    "📈 Emas melonjak usai rilis data CPI rendah",
    "🚀 BTC tembus resistensi kuat $65k",
    "💡 Pasar global reli didorong sektor teknologi",
    "⚡ NVIDIA catat rekor pendapatan Q4",
];

export const AI_ANALYSIS = {
    trend: "BULLISH", strength: 8.7,
    logic: [
        "Liquidity sweep terdeteksi di 2028.50",
        "Order block tervalidasi pada H1",
        "Momentum bullish divergence (RSI)",
    ],
};

export const MACRO_DATA = [
    { title: "Fed Rate", value: "5.50%", impact: "HIGH", bias: "BEARISH USD" },
    { title: "CPI YoY", value: "3.2%", impact: "HIGH", bias: "BULLISH GOLD" },
    { title: "NFP", value: "187K", impact: "MEDIUM", bias: "USD NEUTRAL" },
    { title: "DXY", value: "104.2", impact: "MEDIUM", bias: "USD STRONG" },
];

import {
    Zap, BrainCircuit, Activity, ShieldCheck, Filter, Calendar, BarChart2, Droplet,
    Bell, Bot, Webhook, BookOpen, Users, Trophy, CreditCard, Layers, Brain,
    Newspaper, TrendingDown, ScanLine, GraduationCap, Building2, Link
} from 'lucide-react';

// All 18 AI features from gasfiturmap.md
export const MORE_CATEGORIES = [
    {
        title: "📊 Technical Analysis System", highlight: true, items: [
            { id: 'signal', label: 'Signal AI', icon: Zap, pro: false, credit: '3 cr', plan: 'Essential+' },
            { id: 'technical', label: 'Technical Analysis', icon: BarChart2, pro: false, credit: '3 cr', plan: 'Essential+' },
            { id: 'alerts', label: 'Smart Alert', icon: Bell, pro: false, credit: '1 cr', plan: 'Essential+' },
            { id: 'session', label: 'Session Optimizer', icon: Calendar, pro: false, credit: '1 cr', plan: 'Essential+' },
        ]
    },
    {
        title: "📊 Advanced Technical", highlight: true, items: [
            { id: 'correlation', label: 'Correlation Tracker', icon: Link, pro: true, credit: '3 cr', plan: 'Plus+' },
            { id: 'screener', label: 'Multi-Symbol Scanner', icon: ScanLine, pro: true, credit: '15 cr', plan: 'Ultimate' },
        ]
    },
    {
        title: "🌍 Fundamental Analysis System", items: [
            { id: 'fundamental', label: 'Fundamental AI', icon: BrainCircuit, pro: true, credit: '5 cr', plan: 'Plus+' },
            { id: 'calendars', label: 'Economic Calendar AI', icon: Calendar, pro: true, credit: '4 cr', plan: 'Plus+' },
            { id: 'sentiment', label: 'Sentiment Market AI', icon: Droplet, pro: true, credit: '5 cr', plan: 'Plus+' },
            { id: 'briefing', label: 'AI Market Briefing', icon: Newspaper, pro: true, credit: '10 cr', plan: 'Premium+' },
        ]
    },
    {
        title: "⚡ Hybrid & Risk System", items: [
            { id: 'hybrid', label: 'Hybrid System AI', icon: Layers, pro: true, credit: '8 cr', plan: 'Premium+' },
            { id: 'risk_manager', label: 'Risk Manager AI', icon: ShieldCheck, pro: true, credit: '3 cr', plan: 'Plus+' },
            { id: 'drawdown', label: 'Drawdown Recovery', icon: TrendingDown, pro: true, credit: '5 cr', plan: 'Premium+' },
            { id: 'ai_backtest', label: 'AI Backtesting', icon: Activity, pro: true, credit: '20 cr', plan: 'Ultimate' },
        ]
    },
    {
        title: "🧠 Psychology & Growth", items: [
            { id: 'psychology', label: 'Psychology Coach AI', icon: Brain, pro: true, credit: '5 cr', plan: 'Premium+' },
            { id: 'journal', label: 'AI Trade Journal', icon: BookOpen, pro: true, credit: '8 cr', plan: 'Premium+' },
            { id: 'mentor', label: 'AI Mentor Mode', icon: GraduationCap, pro: true, credit: '10 cr', plan: 'Ultimate' },
            { id: 'propfirm', label: 'Prop Firm Assistant', icon: Building2, pro: true, credit: '8 cr', plan: 'Premium+' },
        ]
    },
    {
        title: "🛠️ Platform & Komunitas", items: [
            { id: 'telegram', label: 'Bot Telegram', icon: Bot },
            { id: 'webhook', label: 'API / Webhook', icon: Webhook },
            { id: 'forum', label: 'Forum VIP', icon: Users },
            { id: 'leaderboard', label: 'Papan Peringkat', icon: Trophy },
            { id: 'pricing', label: 'Upgrade Plan', icon: CreditCard },
        ]
    },
];
