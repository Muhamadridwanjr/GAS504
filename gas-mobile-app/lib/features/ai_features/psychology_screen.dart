import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class PsychologyScreen extends StatefulWidget {
  const PsychologyScreen({super.key});
  @override State<PsychologyScreen> createState() => _PsychologyScreenState();
}

class _PsychologyScreenState extends State<PsychologyScreen> {
  final _api     = ApiService();
  final _noteCtrl = TextEditingController();

  String? _emotion;
  bool _loading = false;
  Map<String, dynamic>? _result;

  static const _emotions = [
    {'label': 'Fear',          'icon': Icons.sentiment_very_dissatisfied, 'color': AppColors.bearish},
    {'label': 'Greed',         'icon': Icons.attach_money, 'color': AppColors.warning},
    {'label': 'FOMO',          'icon': Icons.trending_up, 'color': AppColors.conf50},
    {'label': 'Overconfident', 'icon': Icons.emoji_emotions, 'color': AppColors.conf60},
    {'label': 'Calm',          'icon': Icons.self_improvement, 'color': AppColors.bullish},
    {'label': 'Disciplined',   'icon': Icons.check_circle, 'color': AppColors.conf90},
  ];

  @override
  void dispose() { _noteCtrl.dispose(); super.dispose(); }

  Future<void> _run() async {
    if (_emotion == null) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Select an emotion first')));
      return;
    }
    setState(() { _loading = true; _result = null; });
    try {
      final r = await _api.callAIFeature('psychology', {
        'emotion': _emotion,
        'situation': _noteCtrl.text,
      });
      if (mounted) setState(() { _result = r; _loading = false; });
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Psychology Coach'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        Text('How are you feeling right now?',
            style: AppTypography.h4),
        const SizedBox(height: AppSpacing.md),

        // Emotion grid
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 3,
          crossAxisSpacing: AppSpacing.sm,
          mainAxisSpacing: AppSpacing.sm,
          childAspectRatio: 1.3,
          children: _emotions.map((e) {
            final label = e['label'] as String;
            final color = e['color'] as Color;
            final sel   = _emotion == label;
            return GestureDetector(
              onTap: () => setState(() => _emotion = label),
              child: Container(
                decoration: BoxDecoration(
                  color: sel ? color.withOpacity(0.15) : AppColors.bgSecondary,
                  borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
                  border: Border.all(
                      color: sel ? color : AppColors.border,
                      width: sel ? 1.5 : 1),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(e['icon'] as IconData,
                        color: sel ? color : AppColors.textMuted, size: 24),
                    const SizedBox(height: 6),
                    Text(label,
                        style: AppTypography.labelMD.copyWith(
                            color: sel ? color : AppColors.textSecondary),
                        textAlign: TextAlign.center),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: AppSpacing.lg),

        TextField(
          controller: _noteCtrl,
          style: AppTypography.bodyMD,
          maxLines: 3,
          decoration: const InputDecoration(
            labelText: 'Describe your situation (optional)',
            alignLabelWithHint: true,
          ),
        ),
        const SizedBox(height: AppSpacing.lg),

        GASButton(
          label: 'Get Coaching  •  5 credits',
          icon: Icons.psychology,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),

        if (_result != null) ...[
          const SizedBox(height: AppSpacing.xl),
          // Score
          GASGoldCard(
            child: Row(
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Emotional Score',
                        style: AppTypography.labelMD),
                    const SizedBox(height: 4),
                    Text(
                      '${(_result!['score'] as num?)?.toInt() ?? 0}/100',
                      style: AppTypography.priceLG
                          .copyWith(color: AppColors.textGold),
                    ),
                  ],
                ),
                const Spacer(),
                Text(_emotion ?? '',
                    style: AppTypography.h3
                        .copyWith(color: AppColors.textSecondary)),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          _card('Coaching',
              _result!['message'] as String? ?? ''),
          const SizedBox(height: AppSpacing.md),
          _steps(),
          const SizedBox(height: AppSpacing.md),
          _affirmation(),
        ],
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _card(String title, String content) => GASCard(
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: AppTypography.h4
            .copyWith(color: AppColors.textGold)),
        const SizedBox(height: AppSpacing.sm),
        Text(content.isEmpty ? '—' : content,
            style: AppTypography.bodyMD),
      ],
    ),
  );

  Widget _steps() {
    final steps = (_result?['steps'] as List?)?.cast<String>() ?? [];
    if (steps.isEmpty) return const SizedBox.shrink();
    return GASCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Action Steps',
              style: AppTypography.h4.copyWith(color: AppColors.textGold)),
          const SizedBox(height: AppSpacing.sm),
          ...steps.asMap().entries.map((e) => Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.sm),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 22, height: 22,
                  margin: const EdgeInsets.only(right: 10, top: 1),
                  decoration: const BoxDecoration(
                    color: AppColors.bgTertiary,
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text('${e.key + 1}',
                        style: AppTypography.bodyXS
                            .copyWith(color: AppColors.primary,
                                fontWeight: FontWeight.bold)),
                  ),
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

  Widget _affirmation() {
    final quote = _result?['affirmation'] as String?;
    if (quote == null || quote.isEmpty) return const SizedBox.shrink();
    return GASCard(
      borderColor: AppColors.accent.withOpacity(0.3),
      child: Row(
        children: [
          const Icon(Icons.format_quote,
              color: AppColors.accent, size: 32),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Text(quote,
                style: AppTypography.bodyMD
                    .copyWith(fontStyle: FontStyle.italic)),
          ),
        ],
      ),
    );
  }
}
