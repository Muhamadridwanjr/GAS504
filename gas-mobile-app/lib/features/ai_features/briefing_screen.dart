import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class BriefingScreen extends StatefulWidget {
  const BriefingScreen({super.key});
  @override State<BriefingScreen> createState() => _BriefingScreenState();
}

class _BriefingScreenState extends State<BriefingScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _result;
  bool _loading = false;
  String _period = 'daily';

  Future<void> _run() async {
    setState(() { _loading = true; _result = null; });
    try {
      final r = await _api.callAIFeature('briefing', {'period': _period});
      if (mounted) setState(() { _result = r; _loading = false; });
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Market Briefing'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        // Period toggle
        Row(
          children: ['daily', 'weekly'].map((p) {
            final sel = _period == p;
            return GestureDetector(
              onTap: () => setState(() => _period = p),
              child: Container(
                margin: const EdgeInsets.only(right: AppSpacing.sm),
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.lg, vertical: AppSpacing.xs),
                decoration: BoxDecoration(
                  color: sel
                      ? AppColors.primary.withOpacity(0.15)
                      : AppColors.bgSecondary,
                  borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                  border: Border.all(
                      color: sel ? AppColors.primary : AppColors.border),
                ),
                child: Text(p.toUpperCase(),
                    style: AppTypography.labelMD.copyWith(
                        color: sel ? AppColors.primary
                            : AppColors.textSecondary)),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: AppSpacing.lg),

        GASCard(
          backgroundColor: AppColors.bgTertiary,
          borderColor: AppColors.primary.withOpacity(0.2),
          child: Row(
            children: [
              const Icon(Icons.bolt, color: AppColors.textGold, size: 16),
              const SizedBox(width: 6),
              Text('Cost: 5 credits per briefing',
                  style: AppTypography.bodySM
                      .copyWith(color: AppColors.textGold)),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.lg),

        GASButton(
          label: 'Generate ${_period == 'daily' ? 'Daily' : 'Weekly'} Briefing',
          icon: Icons.auto_awesome,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),

        if (_result != null) ...[
          const SizedBox(height: AppSpacing.xl),
          _section('Market Overview',
              _result?['overview'] as String? ?? ''),
          const SizedBox(height: AppSpacing.md),
          _listSection('Key Events',
              (_result?['key_events'] as List?)?.cast<String>() ?? []),
          const SizedBox(height: AppSpacing.md),
          _listSection('Trade Opportunities',
              (_result?['opportunities'] as List?)?.cast<String>() ?? []),
          const SizedBox(height: AppSpacing.md),
          _listSection('Risk Factors',
              (_result?['risks'] as List?)?.cast<String>() ?? [],
              color: AppColors.bearish),
        ],
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _section(String title, String content) => GASCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: AppTypography.h4
            .copyWith(color: AppColors.textGold)),
        const SizedBox(height: AppSpacing.sm),
        Text(content.isEmpty ? 'No data available'
            : content, style: AppTypography.bodyMD),
      ],
    ),
  );

  Widget _listSection(String title, List<String> items,
      {Color? color}) => GASCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: AppTypography.h4
            .copyWith(color: color ?? AppColors.textGold)),
        const SizedBox(height: AppSpacing.sm),
        if (items.isEmpty)
          Text('No data', style: AppTypography.bodySM)
        else
          ...items.asMap().entries.map((e) => Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.xs),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 20, height: 20,
                  margin: const EdgeInsets.only(right: AppSpacing.sm, top: 2),
                  decoration: BoxDecoration(
                    color: (color ?? AppColors.primary).withOpacity(0.15),
                    shape: BoxShape.circle,
                  ),
                  child: Center(child: Text('${e.key + 1}',
                      style: AppTypography.bodyXS
                          .copyWith(color: color ?? AppColors.primary))),
                ),
                Expanded(child: Text(e.value,
                    style: AppTypography.bodyMD)),
              ],
            ),
          )),
      ],
    ),
  );
}
