class AppConstants {
  AppConstants._();

  // ── API base (change in production) ───────────────────────────────────────
  static const String apiBase    = 'https://gasstrategyai.xyz';
  static const String wsBase     = 'wss://gasstrategyai.xyz';
  static const String terminalWs = 'wss://gasstrategyai.xyz/ws/ticks';

  // ── Auth storage keys ─────────────────────────────────────────────────────
  static const String keyToken   = 'gas_token';
  static const String keyUser    = 'gas_user';
  static const String keyRefresh = 'gas_refresh';
  static const String keyBiometric = 'gas_biometric';

  // ── Plan IDs ──────────────────────────────────────────────────────────────
  static const String planEssential = 'essential';
  static const String planPlus      = 'plus';
  static const String planPremium   = 'premium';
  static const String planUltimate  = 'ultimate';

  // ── Credit costs ──────────────────────────────────────────────────────────
  static const Map<String, int> featureCosts = {
    'technical':   0,
    'signal':      0,
    'alert':       0,
    'session':     0,
    'correlation': 2,
    'fundamental': 2,
    'calendar':    2,
    'sentiment':   3,
    'risk':        2,
    'hybrid':      4,
    'drawdown':    4,
    'briefing':    5,
    'psychology':  5,
    'journal':     3,
    'propfirm':    5,
    'scanner':    15,
    'backtesting': 20,
    'mentor':     10,
  };

  // ── Pair list ─────────────────────────────────────────────────────────────
  static const List<String> forexPairs = [
    'XAUUSD', 'XAGUSD', 'EURUSD', 'GBPUSD', 'USDJPY',
    'GBPJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD',
    'EURGBP', 'EURJPY', 'GBPAUD', 'CADJPY',
  ];

  static const List<String> cryptoPairs = [
    'BTCUSD', 'ETHUSD', 'BNBUSD', 'SOLUSD', 'XRPUSD',
    'ADAUSD', 'DOTUSD', 'LINKUSD', 'AVAXUSD', 'MATICUSD',
  ];

  static const List<String> indexPairs = [
    'US30', 'US500', 'USTEC', 'DXY', 'GER40', 'UK100', 'JPN225',
  ];

  // ── Level XP thresholds ────────────────────────────────────────────────────
  static const List<int> levelXp = [
    0, 100, 300, 600, 1000, 1500, 2200, 3200, 4500, 6000,
  ];

  static const List<String> levelNames = [
    'Rookie', 'Bronze', 'Silver', 'Gold', 'Platinum',
    'Diamond', 'Master', 'Grandmaster', 'Elite', 'Legend',
  ];

  // ── Animation durations ───────────────────────────────────────────────────
  static const Duration animFast   = Duration(milliseconds: 150);
  static const Duration animNormal = Duration(milliseconds: 300);
  static const Duration animSlow   = Duration(milliseconds: 600);

  // ── Refresh intervals ─────────────────────────────────────────────────────
  static const Duration priceRefresh    = Duration(seconds: 5);
  static const Duration signalRefresh   = Duration(seconds: 30);
  static const Duration portfolioRefresh = Duration(seconds: 15);
}
