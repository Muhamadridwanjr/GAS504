import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class CorrelationScreen extends StatefulWidget {
  const CorrelationScreen({super.key});
  @override State<CorrelationScreen> createState() => _CorrelationScreenState();
}

class _CorrelationScreenState extends State<CorrelationScreen> {
  final _api = ApiService();
  bool _loading = false;
  Map<String, dynamic>? _result;
  String _tf = '1D';

  static const _pairs = ['XAUUSD','EURUSD','GBPUSD','USDJPY','BTCUSD','US30','USDCAD','AUDUSD'];
  static const _tfs = ['1D','1W','1M'];

  Future<void> _run() async {
    setState(() { _loading = true; _result = null; });
    try {
      final r = await _api.callAIFeature('correlation', {
        'pairs': _pairs, 'timeframe': _tf,
      });
      if (mounted) setState(() { _result = r; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Correlation Matrix'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        // Timeframe chips
        Row(
          children: _tfs.map((t) {
            final sel = _tf == t;
            return GestureDetector(
              onTap: () => setState(() => _tf = t),
              child: Container(
                margin: const EdgeInsets.only(right: 8),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                decoration: BoxDecoration(
                  color: sel
                      ? AppColors.primary.withOpacity(0.15)
                      : AppColors.bgSecondary,
                  borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                  border: Border.all(
                      color: sel ? AppColors.primary : AppColors.border),
                ),
                child: Text(t, style: AppTypography.labelMD.copyWith(
                    color: sel ? AppColors.primary : AppColors.textSecondary)),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: AppSpacing.lg),
        GASButton(
          label: 'Load Correlation  •  2 credits',
          icon: Icons.grid_on,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),
        if (_result != null) ...[
          const SizedBox(height: AppSpacing.xl),
          _matrix(),
          const SizedBox(height: AppSpacing.md),
          _legend(),
        ],
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _matrix() {
    final matrix = _result?['matrix'] as Map<String, dynamic>?;

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header row
          Row(
            children: [
              const SizedBox(width: 60),
              ..._pairs.map((p) => SizedBox(
                width: 52,
                child: Text(p.substring(0, 3),
                    style: AppTypography.labelSM,
                    textAlign: TextAlign.center),
              )),
            ],
          ),
          const SizedBox(height: 4),
          ..._pairs.map((rowP) => Row(
            children: [
              SizedBox(
                width: 60,
                child: Text(rowP.substring(0, 3),
                    style: AppTypography.labelSM),
              ),
              ..._pairs.map((colP) {
                double val = 0;
                if (matrix != null && matrix[rowP] is Map) {
                  val = (matrix[rowP][colP] as num?)?.toDouble() ?? 0;
                } else if (rowP == colP) {
                  val = 1.0;
                }
                return Container(
                  width: 52, height: 40,
                  margin: const EdgeInsets.all(1),
                  decoration: BoxDecoration(
                    color: _corrColor(val),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Center(
                    child: Text(
                      val.toStringAsFixed(2),
                      style: AppTypography.bodyXS.copyWith(
                          color: val.abs() > 0.5
                              ? Colors.white : AppColors.textMuted),
                    ),
                  ),
                );
              }),
            ],
          )),
        ],
      ),
    );
  }

  Color _corrColor(double v) {
    if (v >=  0.7) return AppColors.bullish.withOpacity(0.8);
    if (v >=  0.3) return AppColors.bullish.withOpacity(0.4);
    if (v <= -0.7) return AppColors.bearish.withOpacity(0.8);
    if (v <= -0.3) return AppColors.bearish.withOpacity(0.4);
    return AppColors.bgTertiary;
  }

  Widget _legend() => Row(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      _legendDot(AppColors.bearish, 'Strong -'),
      const SizedBox(width: 12),
      _legendDot(AppColors.bgTertiary, 'Neutral'),
      const SizedBox(width: 12),
      _legendDot(AppColors.bullish, 'Strong +'),
    ],
  );

  Widget _legendDot(Color c, String label) => Row(
    children: [
      Container(width: 12, height: 12,
          decoration: BoxDecoration(color: c, borderRadius: BorderRadius.circular(3))),
      const SizedBox(width: 6),
      Text(label, style: AppTypography.bodyXS),
    ],
  );
}
