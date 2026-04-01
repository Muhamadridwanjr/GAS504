import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class DrawdownScreen extends StatefulWidget {
  const DrawdownScreen({super.key});
  @override State<DrawdownScreen> createState() => _DrawdownScreenState();
}

class _DrawdownScreenState extends State<DrawdownScreen> {
  final _api      = ApiService();
  final _startCtrl = TextEditingController(text: '10000');
  final _currCtrl  = TextEditingController(text: '8500');
  bool _loading    = false;
  Map<String, dynamic>? _result;

  @override
  void dispose() { _startCtrl.dispose(); _currCtrl.dispose(); super.dispose(); }

  double get _ddPct {
    final s = double.tryParse(_startCtrl.text) ?? 0;
    final c = double.tryParse(_currCtrl.text)  ?? 0;
    if (s <= 0) return 0;
    return ((s - c) / s * 100).clamp(0.0, 100.0);
  }

  double get _recPct {
    final dd = _ddPct;
    if (dd >= 100) return double.infinity;
    return (dd / (100 - dd) * 100);
  }

  Future<void> _run() async {
    setState(() { _loading = true; _result = null; });
    try {
      final r = await _api.callAIFeature('drawdown', {
        'starting_balance': double.tryParse(_startCtrl.text) ?? 10000,
        'current_balance':  double.tryParse(_currCtrl.text)  ?? 8500,
      });
      if (mounted) setState(() { _result = r; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Drawdown Recovery'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        _field('Starting Balance (USD)', _startCtrl),
        const SizedBox(height: AppSpacing.md),
        _field('Current Balance (USD)', _currCtrl),
        const SizedBox(height: AppSpacing.lg),

        // Live stats
        AnimatedBuilder(
          animation: Listenable.merge([_startCtrl, _currCtrl]),
          builder: (_, __) => _statsRow(),
        ),
        const SizedBox(height: AppSpacing.lg),

        GASButton(
          label: 'AI Recovery Plan  •  4 credits',
          icon: Icons.trending_up,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),

        if (_result != null) ...[
          const SizedBox(height: AppSpacing.xl),
          if (_result!['steps'] is List)
            _stepsCard((_result!['steps'] as List).cast<String>()),
          if (_result!['plan'] is String) ...[
            const SizedBox(height: AppSpacing.md),
            GASCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Recovery Plan',
                      style: AppTypography.h4.copyWith(color: AppColors.textGold)),
                  const SizedBox(height: AppSpacing.sm),
                  Text(_result!['plan'] as String, style: AppTypography.bodyMD),
                ],
              ),
            ),
          ],
        ],
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _field(String label, TextEditingController ctrl) => TextField(
    controller: ctrl,
    style: AppTypography.bodyMD,
    keyboardType: TextInputType.number,
    onChanged: (_) => setState(() {}),
    decoration: InputDecoration(labelText: label),
  );

  Widget _statsRow() {
    final dd  = _ddPct;
    final rec = _recPct;
    final ddColor = dd < 10 ? AppColors.bullish
        : dd < 20 ? AppColors.warning : AppColors.bearish;

    return Row(
      children: [
        Expanded(child: GASCard(
          borderColor: ddColor.withOpacity(0.3),
          child: Column(
            children: [
              Text('Drawdown', style: AppTypography.labelMD),
              const SizedBox(height: 4),
              Text('${dd.toStringAsFixed(1)}%',
                  style: AppTypography.priceMD.copyWith(color: ddColor)),
            ],
          ),
        )),
        const SizedBox(width: AppSpacing.sm),
        Expanded(child: GASCard(
          child: Column(
            children: [
              Text('Recovery Needed', style: AppTypography.labelMD),
              const SizedBox(height: 4),
              Text('${rec.isInfinite ? '∞' : rec.toStringAsFixed(1)}%',
                  style: AppTypography.priceMD.copyWith(color: AppColors.warning)),
            ],
          ),
        )),
      ],
    );
  }

  Widget _stepsCard(List<String> steps) => GASCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Recovery Steps',
            style: AppTypography.h4.copyWith(color: AppColors.textGold)),
        const SizedBox(height: AppSpacing.sm),
        ...steps.asMap().entries.map((e) => Padding(
          padding: const EdgeInsets.only(bottom: AppSpacing.sm),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 24, height: 24,
                margin: const EdgeInsets.only(right: 10, top: 1),
                decoration: const BoxDecoration(
                    color: AppColors.bgTertiary, shape: BoxShape.circle),
                child: Center(
                  child: Text('${e.key + 1}',
                      style: AppTypography.bodyXS.copyWith(
                          color: AppColors.primary,
                          fontWeight: FontWeight.bold)),
                ),
              ),
              Expanded(child: Text(e.value, style: AppTypography.bodyMD)),
            ],
          ),
        )),
      ],
    ),
  );
}
