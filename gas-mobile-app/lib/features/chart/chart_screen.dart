import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../shared/widgets/gas_app_bar.dart';

class ChartScreen extends StatefulWidget {
  final String symbol;
  final String timeframe;
  const ChartScreen({super.key, required this.symbol, this.timeframe = '60'});
  @override State<ChartScreen> createState() => _ChartScreenState();
}

class _ChartScreenState extends State<ChartScreen> {
  late final WebViewController _wv;
  bool _ready = false;
  late String _tf;
  late String _sym;

  static const _tfMap = {
    '1m': '1', '5m': '5', '15m': '15', '30m': '30',
    '1H': '60', '4H': '240', '1D': 'D', '1W': 'W',
  };

  static final _symMap = {
    'XAUUSD': 'OANDA:XAUUSD', 'XAGUSD': 'OANDA:XAGUSD',
    'EURUSD': 'OANDA:EURUSD', 'GBPUSD': 'OANDA:GBPUSD',
    'USDJPY': 'OANDA:USDJPY', 'GBPJPY': 'OANDA:GBPJPY',
    'AUDUSD': 'OANDA:AUDUSD', 'USDCAD': 'OANDA:USDCAD',
    'BTCUSD': 'BINANCE:BTCUSDT', 'ETHUSD': 'BINANCE:ETHUSDT',
    'US30':   'TVC:DJI',  'US500':  'SP:SPX',
    'USTEC':  'NASDAQ:NDX', 'DXY': 'TVC:DXY',
  };

  @override
  void initState() {
    super.initState();
    _sym = widget.symbol;
    _tf  = widget.timeframe;
    _wv  = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(AppColors.bgPrimary)
      ..setNavigationDelegate(NavigationDelegate(
        onPageFinished: (_) {
          if (mounted) setState(() => _ready = true);
        },
      ))
      ..loadHtmlString(_buildHtml());
  }

  String _buildHtml() {
    final tvSym = _symMap[_sym] ?? 'OANDA:${_sym}';
    final tvTf  = _tfMap[_tf]   ?? '60';
    return '''<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { width:100%; height:100%; background:#0A0A0F; }
  #tv_chart { width:100%; height:100vh; }
</style>
</head>
<body>
<div id="tv_chart"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
{
  "autosize": true,
  "symbol": "$tvSym",
  "interval": "$tvTf",
  "timezone": "Etc/UTC",
  "theme": "dark",
  "style": "1",
  "locale": "en",
  "toolbar_bg": "#0A0A0F",
  "enable_publishing": false,
  "backgroundColor": "#0A0A0F",
  "gridColor": "#1E1E3A",
  "hide_top_toolbar": false,
  "hide_legend": false,
  "save_image": false,
  "withdateranges": true,
  "studies": ["Volume@tv-basicstudies","RSI@tv-basicstudies","MACD@tv-basicstudies"],
  "container_id": "tv_chart"
}
</script>
</body>
</html>''';
  }

  void _setTf(String tf) {
    setState(() { _tf = tf; _ready = false; });
    _wv.loadHtmlString(_buildHtml());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: GASAppBar(
        title: _sym,
        subtitle: _symMap[_sym] ?? _sym,
      ),
      body: Column(
        children: [
          // Timeframe selector
          SizedBox(
            height: 44,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.md, vertical: AppSpacing.xs),
              children: _tfMap.keys.map((tf) {
                final sel = _tf == tf;
                return GestureDetector(
                  onTap: () => _setTf(tf),
                  child: Container(
                    margin: const EdgeInsets.only(right: AppSpacing.sm),
                    padding: const EdgeInsets.symmetric(
                        horizontal: AppSpacing.md, vertical: 6),
                    decoration: BoxDecoration(
                      color: sel
                          ? AppColors.primary.withOpacity(0.15)
                          : AppColors.bgSecondary,
                      borderRadius: BorderRadius.circular(
                          AppSpacing.radiusFull),
                      border: Border.all(
                        color: sel ? AppColors.primary : AppColors.border,
                      ),
                    ),
                    child: Text(tf,
                        style: AppTypography.labelMD.copyWith(
                            color: sel
                                ? AppColors.primary
                                : AppColors.textSecondary)),
                  ),
                );
              }).toList(),
            ),
          ),
          // WebView
          Expanded(
            child: Stack(
              children: [
                WebViewWidget(controller: _wv),
                if (!_ready)
                  const Center(
                    child: CircularProgressIndicator(
                        color: AppColors.primary),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
