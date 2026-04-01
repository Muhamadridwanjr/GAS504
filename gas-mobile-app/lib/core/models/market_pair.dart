class MarketStatus {
  final bool open;
  final String session;
  final String label;

  const MarketStatus({
    required this.open,
    required this.session,
    required this.label,
  });

  factory MarketStatus.fromJson(Map<String, dynamic> j) => MarketStatus(
    open:    j['open']    as bool? ?? false,
    session: j['session'] as String? ?? '',
    label:   j['label']   as String? ?? '',
  );
}

class MarketPair {
  final String symbol;
  final String name;
  final String type;
  final int decimals;
  final double? price;
  final double? bid;
  final double? ask;
  final double? spread;
  final double? openPrice;
  final double? high;
  final double? low;
  final double? prevClose;
  final double change;
  final double changePct;
  final double? volume;
  final String source;
  final bool stale;
  final bool noData;
  final MarketStatus? market;

  const MarketPair({
    required this.symbol,
    required this.name,
    required this.type,
    required this.decimals,
    this.price,
    this.bid,
    this.ask,
    this.spread,
    this.openPrice,
    this.high,
    this.low,
    this.prevClose,
    required this.change,
    required this.changePct,
    this.volume,
    required this.source,
    required this.stale,
    required this.noData,
    this.market,
  });

  factory MarketPair.fromJson(Map<String, dynamic> j) => MarketPair(
    symbol:    j['symbol']    as String? ?? '',
    name:      j['name']      as String? ?? '',
    type:      j['type']      as String? ?? '',
    decimals:  (j['decimals'] as num?)?.toInt() ?? 5,
    price:     (j['price']     as num?)?.toDouble(),
    bid:       (j['bid']       as num?)?.toDouble(),
    ask:       (j['ask']       as num?)?.toDouble(),
    spread:    (j['spread']    as num?)?.toDouble(),
    openPrice: (j['open_price'] as num?)?.toDouble(),
    high:      (j['high']      as num?)?.toDouble(),
    low:       (j['low']       as num?)?.toDouble(),
    prevClose: (j['prev_close'] as num?)?.toDouble(),
    change:    (j['change']    as num?)?.toDouble() ?? 0,
    changePct: (j['change_pct'] as num?)?.toDouble() ?? 0,
    volume:    (j['volume']    as num?)?.toDouble(),
    source:    j['source']    as String? ?? 'unknown',
    stale:     j['stale']     as bool? ?? false,
    noData:    j['no_data']   as bool? ?? false,
    market: j['market'] != null
        ? MarketStatus.fromJson(j['market'] as Map<String, dynamic>) : null,
  );

  bool get isUp   => changePct >= 0;
  bool get isOpen => market?.open ?? false;

  String formatPrice() {
    if (price == null) return '—';
    return price!.toStringAsFixed(decimals);
  }

  String formatChangePct() {
    final sign = isUp ? '+' : '';
    return '$sign${changePct.toStringAsFixed(2)}%';
  }
}
