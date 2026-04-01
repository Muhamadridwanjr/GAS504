import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});
  @override State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final _api = ApiService();
  List<Map<String, dynamic>> _results = [];
  bool _loading  = false;
  String _filter = 'All';

  static const _filters = ['All','Bullish','Bearish','SMC','Breakout','Reversal'];

  Future<void> _run() async {
    setState(() { _loading = true; _results = []; });
    try {
      final r = await _api.callAIFeature('scanner', {'filter': _filter});
      final items = (r['signals'] as List?)?.cast<Map<String, dynamic>>()
          ?? (r['results'] as List?)?.cast<Map<String, dynamic>>() ?? [];
      if (mounted) setState(() { _results = items; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Market Scanner'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        SizedBox(
          height: 40,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: _filters.map((f) {
              final sel = _filter == f;
              return GestureDetector(
                onTap: () => setState(() => _filter = f),
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                  decoration: BoxDecoration(
                    color: sel ? AppColors.primary.withOpacity(0.15) : AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                    border: Border.all(color: sel ? AppColors.primary : AppColors.border),
                  ),
                  child: Text(f, style: AppTypography.labelMD.copyWith(
                      color: sel ? AppColors.primary : AppColors.textSecondary)),
                ),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),

        GASCard(
          backgroundColor: AppColors.bgTertiary,
          child: Row(children: [
            const Icon(Icons.bolt, color: AppColors.textGold, size: 16),
            const SizedBox(width: 6),
            Text('Cost: 15 credits per scan',
                style: AppTypography.bodySM.copyWith(color: AppColors.textGold)),
          ]),
        ),
        const SizedBox(height: AppSpacing.md),

        GASButton(
          label: _loading ? 'Scanning...' : 'Run Scanner',
          icon: Icons.search,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),

        const SizedBox(height: AppSpacing.xl),

        if (!_loading && _results.isEmpty)
          Center(
            child: Column(
              children: [
                const Icon(Icons.radar, size: 48, color: AppColors.textMuted),
                const SizedBox(height: AppSpacing.md),
                Text('Run scanner to find opportunities',
                    style: AppTypography.bodySM),
              ],
            ),
          ),

        ..._results.map(_resultCard),
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _resultCard(Map<String, dynamic> r) {
    final pair  = r['pair']       as String? ?? '';
    final setup = r['setup_type'] as String? ?? r['setup'] as String? ?? '';
    final conf  = (r['confidence'] as num?)?.toDouble() ?? 0;
    final tf    = r['timeframe']  as String? ?? '';
    final dir   = (r['direction'] as String? ?? '').toLowerCase();
    final dirColor = dir == 'buy' ? AppColors.bullish
        : dir == 'sell' ? AppColors.bearish : AppColors.textMuted;

    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.sm),
      child: GASCard(
        borderColor: dirColor.withOpacity(0.25),
        child: Column(
          children: [
            Row(
              children: [
                Text(pair, style: AppTypography.priceSM),
                const SizedBox(width: AppSpacing.sm),
                if (dir.isNotEmpty) Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: dirColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: dirColor.withOpacity(0.3)),
                  ),
                  child: Text(dir.toUpperCase(),
                      style: AppTypography.labelSM.copyWith(color: dirColor)),
                ),
                const Spacer(),
                Text(tf, style: AppTypography.bodyXS),
              ],
            ),
            const SizedBox(height: AppSpacing.sm),
            Row(
              children: [
                Text(setup, style: AppTypography.bodyMD),
                const Spacer(),
                SizedBox(
                  width: 100,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text('${conf.toStringAsFixed(0)}%',
                          style: AppTypography.priceXS.copyWith(
                              color: conf >= 75 ? AppColors.bullish
                                  : conf >= 60 ? AppColors.warning : AppColors.textMuted)),
                      const SizedBox(height: 4),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                        child: LinearProgressIndicator(
                          value: conf / 100,
                          minHeight: 3,
                          backgroundColor: AppColors.bgTertiary,
                          valueColor: AlwaysStoppedAnimation(
                              conf >= 75 ? AppColors.bullish
                                  : conf >= 60 ? AppColors.warning : AppColors.textMuted),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
