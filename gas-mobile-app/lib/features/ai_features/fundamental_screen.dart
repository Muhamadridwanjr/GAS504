import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class FundamentalScreen extends StatefulWidget {
  final String pair;
  const FundamentalScreen({super.key, this.pair = 'XAUUSD'});
  @override State<FundamentalScreen> createState() => _FundamentalScreenState();
}

class _FundamentalScreenState extends State<FundamentalScreen> {
  final _api = ApiService();
  late String _pair;
  bool _loading = false;
  Map<String, dynamic>? _result;

  static const _pairs = ['XAUUSD','EURUSD','GBPUSD','USDJPY','AUDUSD','USDCAD'];

  @override
  void initState() { super.initState(); _pair = widget.pair; }

  Future<void> _run() async {
    setState(() { _loading = true; _result = null; });
    try {
      final r = await _api.callAIFeature('fundamental', {'pair': _pair});
      if (mounted) setState(() { _result = r; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Fundamental Data'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        SizedBox(
          height: 40,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: _pairs.map((p) {
              final sel = _pair == p;
              return GestureDetector(
                onTap: () => setState(() => _pair = p),
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                  decoration: BoxDecoration(
                    color: sel ? AppColors.primary.withOpacity(0.15) : AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                    border: Border.all(color: sel ? AppColors.primary : AppColors.border),
                  ),
                  child: Text(p, style: AppTypography.labelMD.copyWith(
                      color: sel ? AppColors.primary : AppColors.textSecondary)),
                ),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        GASButton(
          label: 'Run AI Analysis  •  2 credits',
          icon: Icons.bar_chart,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),
        if (_result != null) ...[
          const SizedBox(height: AppSpacing.xl),
          if (_result!['data'] is List)
            ...(_result!['data'] as List).cast<Map<String, dynamic>>()
                .map(_dataCard)
          else ...[
            _infoCard('GDP',           _result!['gdp']?.toString()           ?? '—'),
            _infoCard('Interest Rate', _result!['interest_rate']?.toString() ?? '—'),
            _infoCard('CPI',           _result!['cpi']?.toString()           ?? '—'),
            _infoCard('PMI',           _result!['pmi']?.toString()           ?? '—'),
          ],
          if (_result!['analysis'] is String) ...[
            const SizedBox(height: AppSpacing.md),
            GASGoldCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('AI Interpretation',
                      style: AppTypography.h4.copyWith(color: AppColors.textGold)),
                  const SizedBox(height: AppSpacing.sm),
                  Text(_result!['analysis'] as String,
                      style: AppTypography.bodyMD),
                ],
              ),
            ),
          ],
        ],
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _dataCard(Map<String, dynamic> d) => Padding(
    padding: const EdgeInsets.only(bottom: AppSpacing.sm),
    child: GASCard(
      child: Row(
        children: [
          Expanded(
            child: Text(d['label'] as String? ?? '',
                style: AppTypography.bodyMD),
          ),
          Text(d['value']?.toString() ?? '—',
              style: AppTypography.priceSM),
          const SizedBox(width: AppSpacing.sm),
          if (d['trend'] != null)
            Icon(
              d['trend'] == 'up' ? Icons.arrow_upward : Icons.arrow_downward,
              size: 14,
              color: d['trend'] == 'up' ? AppColors.bullish : AppColors.bearish,
            ),
        ],
      ),
    ),
  );

  Widget _infoCard(String label, String value) => Padding(
    padding: const EdgeInsets.only(bottom: AppSpacing.sm),
    child: GASCard(
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: AppTypography.bodyMD),
          Text(value, style: AppTypography.priceSM
              .copyWith(color: AppColors.textGold)),
        ],
      ),
    ),
  );
}
