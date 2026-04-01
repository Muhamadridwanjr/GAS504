enum SignalDirection { buy, sell, neutral }

class TradingSignal {
  final String pair;
  final SignalDirection direction;
  final double confidence;
  final double? entryPrice;
  final double? sl;
  final double? tp1;
  final double? tp2;
  final double? tp3;
  final String? regime;
  final String? session;
  final String? notes;
  final String? bias;
  final DateTime timestamp;
  final String source;
  final Map<String, dynamic>? raw;

  const TradingSignal({
    required this.pair,
    required this.direction,
    required this.confidence,
    this.entryPrice,
    this.sl,
    this.tp1,
    this.tp2,
    this.tp3,
    this.regime,
    this.session,
    this.notes,
    this.bias,
    required this.timestamp,
    required this.source,
    this.raw,
  });

  factory TradingSignal.fromJson(Map<String, dynamic> j) {
    final dir = (j['direction'] as String? ?? '').toLowerCase();
    return TradingSignal(
      pair:       j['pair'] as String? ?? '',
      direction:  dir == 'buy'  ? SignalDirection.buy
                : dir == 'sell' ? SignalDirection.sell
                : SignalDirection.neutral,
      confidence: (j['confidence'] as num?)?.toDouble() ?? 0,
      entryPrice: (j['entry_price'] as num?)?.toDouble(),
      sl:         (j['sl']         as num?)?.toDouble()
               ?? (j['stop_loss']  as num?)?.toDouble(),
      tp1:        (j['tp1'] as num?)?.toDouble()
               ?? (j['take_profit'] as num?)?.toDouble(),
      tp2:        (j['tp2'] as num?)?.toDouble(),
      tp3:        (j['tp3'] as num?)?.toDouble(),
      regime:     j['regime']  as String?,
      session:    j['session'] as String?,
      notes:      j['notes']   as String? ?? j['reasoning'] as String?,
      bias:       j['bias']    as String?,
      timestamp: j['timestamp'] != null
          ? DateTime.fromMillisecondsSinceEpoch(
              ((j['timestamp'] as num) * 1000).toInt())
          : DateTime.now(),
      source: j['source'] as String? ?? 'engine',
      raw: j,
    );
  }

  bool get isBuy  => direction == SignalDirection.buy;
  bool get isSell => direction == SignalDirection.sell;

  String get directionLabel =>
      isBuy ? 'BUY' : isSell ? 'SELL' : 'NEUTRAL';

  String get confidenceLabel =>
      confidence >= 90 ? 'VERY HIGH'
    : confidence >= 75 ? 'HIGH'
    : confidence >= 60 ? 'MEDIUM' : 'LOW';

  double? get rr {
    if (entryPrice == null || sl == null || tp1 == null) return null;
    final risk   = (entryPrice! - sl!).abs();
    final reward = (tp1! - entryPrice!).abs();
    return risk > 0 ? reward / risk : null;
  }
}
