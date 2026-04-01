import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class PropFirmScreen extends StatefulWidget {
  const PropFirmScreen({super.key});
  @override State<PropFirmScreen> createState() => _PropFirmScreenState();
}

class _PropFirmScreenState extends State<PropFirmScreen> {
  final _api = ApiService();
  final _balCtrl   = TextEditingController(text: '100000');
  final _dailyCtrl = TextEditingController(text: '5');
  final _ddCtrl    = TextEditingController(text: '10');
  String _phase    = 'Challenge';
  bool _loading    = false;
  Map<String, dynamic>? _result;

  static const _phases = ['Challenge', 'Verification', 'Funded'];

  @override
  void dispose() {
    _balCtrl.dispose();
    _dailyCtrl.dispose();
    _ddCtrl.dispose();
    super.dispose();
  }

  Future<void> _run() async {
    setState(() { _loading = true; _result = null; });
    try {
      final r = await _api.callAIFeature('propfirm', {
        'account_size': double.tryParse(_balCtrl.text) ?? 100000,
        'daily_loss_limit': double.tryParse(_dailyCtrl.text) ?? 5,
        'max_drawdown': double.tryParse(_ddCtrl.text) ?? 10,
        'phase': _phase,
      });
      if (mounted) setState(() { _result = r; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Prop Firm Mode'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        // Phase selector
        Row(
          children: _phases.map((p) {
            final sel = _phase == p;
            return Expanded(
              child: GestureDetector(
                onTap: () => setState(() => _phase = p),
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(vertical: 8),
                  decoration: BoxDecoration(
                    color: sel ? AppColors.primary.withOpacity(0.15) : AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
                    border: Border.all(color: sel ? AppColors.primary : AppColors.border),
                  ),
                  child: Text(p,
                      style: AppTypography.labelMD.copyWith(
                          color: sel ? AppColors.primary : AppColors.textSecondary),
                      textAlign: TextAlign.center),
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: AppSpacing.lg),
        _field('Account Size (USD)', _balCtrl),
        const SizedBox(height: AppSpacing.md),
        _field('Daily Loss Limit (%)', _dailyCtrl),
        const SizedBox(height: AppSpacing.md),
        _field('Max Drawdown (%)', _ddCtrl),
        const SizedBox(height: AppSpacing.lg),
        GASButton(
          label: 'Analyze  •  5 credits',
          icon: Icons.business_center,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),
        if (_result != null) ...[
          const SizedBox(height: AppSpacing.xl),
          _riskScore(),
          const SizedBox(height: AppSpacing.md),
          _positionSizes(),
          const SizedBox(height: AppSpacing.md),
          _compliance(),
          const SizedBox(height: AppSpacing.md),
          if (_result!['recommendations'] is List)
            _recommendations(),
        ],
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _field(String label, TextEditingController ctrl) => TextField(
    controller: ctrl,
    style: AppTypography.bodyMD,
    keyboardType: TextInputType.number,
    decoration: InputDecoration(labelText: label),
  );

  Widget _riskScore() {
    final score = (_result!['risk_score'] as num?)?.toDouble() ?? 0;
    final color = score < 40 ? AppColors.bullish
        : score < 70 ? AppColors.warning : AppColors.bearish;
    return GASCard(
      borderColor: color.withOpacity(0.3),
      child: Row(
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Risk Score', style: AppTypography.labelMD),
              const SizedBox(height: 4),
              Text('${score.toStringAsFixed(0)}/100',
                  style: AppTypography.priceLG.copyWith(color: color)),
            ],
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.15),
              borderRadius: BorderRadius.circular(AppSpacing.radiusLG),
              border: Border.all(color: color.withOpacity(0.4)),
            ),
            child: Text(
              score < 40 ? 'SAFE' : score < 70 ? 'CAUTION' : 'DANGER',
              style: AppTypography.labelLG.copyWith(color: color),
            ),
          ),
        ],
      ),
    );
  }

  Widget _positionSizes() {
    final sizes = _result!['position_sizes'] as Map<String, dynamic>?;
    if (sizes == null) return const SizedBox.shrink();
    return GASCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Recommended Position Sizes',
              style: AppTypography.h4.copyWith(color: AppColors.textGold)),
          const SizedBox(height: AppSpacing.sm),
          ...sizes.entries.map((e) => Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(e.key, style: AppTypography.bodyMD),
                Text(e.value.toString(),
                    style: AppTypography.priceSM
                        .copyWith(color: AppColors.textGold)),
              ],
            ),
          )),
        ],
      ),
    );
  }

  Widget _compliance() {
    final rules = (_result!['rules'] as List?)?.cast<Map<String, dynamic>>() ?? [];
    if (rules.isEmpty) return const SizedBox.shrink();
    return GASCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Rules Compliance',
              style: AppTypography.h4.copyWith(color: AppColors.textGold)),
          const SizedBox(height: AppSpacing.sm),
          ...rules.map((r) {
            final pass = r['pass'] as bool? ?? false;
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Icon(pass ? Icons.check_circle : Icons.cancel,
                      size: 16,
                      color: pass ? AppColors.bullish : AppColors.bearish),
                  const SizedBox(width: 8),
                  Expanded(child: Text(r['rule'] as String? ?? '',
                      style: AppTypography.bodyMD)),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _recommendations() {
    final recs = (_result!['recommendations'] as List).cast<String>();
    return GASCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Strategy Recommendations',
              style: AppTypography.h4.copyWith(color: AppColors.textGold)),
          const SizedBox(height: AppSpacing.sm),
          ...recs.map((r) => Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.arrow_right,
                    color: AppColors.primary, size: 16),
                const SizedBox(width: 4),
                Expanded(child: Text(r, style: AppTypography.bodyMD)),
              ],
            ),
          )),
        ],
      ),
    );
  }
}
