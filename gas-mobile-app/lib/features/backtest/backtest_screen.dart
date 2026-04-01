import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class BacktestScreen extends StatefulWidget {
  const BacktestScreen({super.key});
  @override State<BacktestScreen> createState() => _BacktestScreenState();
}

class _BacktestScreenState extends State<BacktestScreen> {
  final _api      = ApiService();
  final _riskCtrl = TextEditingController(text: '1');
  String _pair     = 'XAUUSD';
  String _strategy = 'SMC';
  bool _loading    = false;
  Map<String, dynamic>? _result;

  static const _pairs      = ['XAUUSD','EURUSD','GBPUSD','BTCUSD','US30'];
  static const _strategies = ['SMC','EMA Cross','RSI Divergence','MACD','Support/Resistance'];

  Future<void> _run() async {
    setState(() { _loading = true; _result = null; });
    try {
      final r = await _api.callAIFeature('backtesting', {
        'pair':      _pair,
        'strategy':  _strategy,
        'risk_pct':  double.tryParse(_riskCtrl.text) ?? 1.0,
      });
      if (mounted) setState(() { _result = r; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Backtesting'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        // Config
        _label('Pair'),
        const SizedBox(height: AppSpacing.sm),
        SizedBox(
          height: 40,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: _pairs.map((p) => _chip(p, _pair == p,
                () => setState(() => _pair = p))).toList(),
          ),
        ),
        const SizedBox(height: AppSpacing.md),
        _label('Strategy'),
        const SizedBox(height: AppSpacing.sm),
        SizedBox(
          height: 40,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: _strategies.map((s) => _chip(s, _strategy == s,
                () => setState(() => _strategy = s))).toList(),
          ),
        ),
        const SizedBox(height: AppSpacing.md),
        TextField(
          controller: _riskCtrl,
          keyboardType: TextInputType.number,
          style: AppTypography.bodyMD,
          decoration: const InputDecoration(labelText: 'Risk per trade (%)'),
        ),
        const SizedBox(height: AppSpacing.lg),

        GASCard(
          backgroundColor: AppColors.bgTertiary,
          borderColor: AppColors.warning.withOpacity(0.2),
          child: Row(
            children: [
              const Icon(Icons.bolt, color: AppColors.warning, size: 16),
              const SizedBox(width: 6),
              Text('Cost: 20 credits per backtest',
                  style: AppTypography.bodySM.copyWith(color: AppColors.warning)),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.md),

        GASButton(
          label: 'Run Backtest',
          icon: Icons.science,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),

        if (_result != null) ...[
          const SizedBox(height: AppSpacing.xl),
          _resultStats(),
          const SizedBox(height: AppSpacing.md),
          if ((_result!['trades'] as List?)?.isNotEmpty == true)
            _tradesList(),
        ],
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _chip(String label, bool sel, VoidCallback onTap) => GestureDetector(
    onTap: onTap,
    child: Container(
      margin: const EdgeInsets.only(right: 8),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: sel ? AppColors.primary.withOpacity(0.15) : AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
        border: Border.all(color: sel ? AppColors.primary : AppColors.border),
      ),
      child: Text(label, style: AppTypography.labelMD.copyWith(
          color: sel ? AppColors.primary : AppColors.textSecondary)),
    ),
  );

  Widget _label(String t) => Text(t, style: AppTypography.labelMD);

  Widget _resultStats() {
    final stats = [
      ('Total Trades', _result!['total_trades']?.toString() ?? '0', AppColors.textPrimary),
      ('Win Rate',     '${(_result!['win_rate'] as num?)?.toStringAsFixed(1) ?? '0'}%', AppColors.bullish),
      ('Profit Factor','${(_result!['profit_factor'] as num?)?.toStringAsFixed(2) ?? '0'}', AppColors.textGold),
      ('Max DD',       '${(_result!['max_drawdown'] as num?)?.toStringAsFixed(1) ?? '0'}%', AppColors.bearish),
      ('Net P/L',      '\$${(_result!['net_pl'] as num?)?.toStringAsFixed(0) ?? '0'}',
          ((_result!['net_pl'] as num?)?.toDouble() ?? 0) >= 0
              ? AppColors.bullish : AppColors.bearish),
    ];
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: AppSpacing.sm,
      mainAxisSpacing: AppSpacing.sm,
      childAspectRatio: 2.5,
      children: stats.map((s) => GASCard(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(s.$1, style: AppTypography.labelSM),
            const SizedBox(height: 4),
            Text(s.$2,
                style: AppTypography.priceSM.copyWith(color: s.$3)),
          ],
        ),
      )).toList(),
    );
  }

  Widget _tradesList() {
    final trades = (_result!['trades'] as List).cast<Map<String, dynamic>>();
    return GASCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Recent Trades',
              style: AppTypography.h4.copyWith(color: AppColors.textGold)),
          const SizedBox(height: AppSpacing.sm),
          ...trades.take(10).map((t) {
            final pl = (t['pl'] as num?)?.toDouble() ?? 0;
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Icon(pl >= 0 ? Icons.arrow_upward : Icons.arrow_downward,
                      size: 14,
                      color: pl >= 0 ? AppColors.bullish : AppColors.bearish),
                  const SizedBox(width: 8),
                  Expanded(child: Text(t['date'] as String? ?? '',
                      style: AppTypography.bodyXS)),
                  Text('\$${pl.toStringAsFixed(2)}',
                      style: AppTypography.priceSM.copyWith(
                          color: pl >= 0 ? AppColors.bullish : AppColors.bearish)),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }
}
