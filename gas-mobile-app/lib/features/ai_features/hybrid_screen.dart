import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:math' as math;
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class HybridScreen extends StatefulWidget {
  final String pair;
  const HybridScreen({super.key, required this.pair});

  @override
  State<HybridScreen> createState() => _HybridScreenState();
}

class _HybridScreenState extends State<HybridScreen> {
  final _api = ApiService();

  static const _pairs = [
    'XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSDT', 'ETHUSDT',
  ];

  late String _selectedPair;
  double _taWeight    = 40;
  double _faWeight    = 30;
  double _sentWeight  = 30;
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _result;

  @override
  void initState() {
    super.initState();
    _selectedPair = _pairs.contains(widget.pair) ? widget.pair : _pairs[0];
  }

  Future<void> _runAnalysis() async {
    setState(() { _loading = true; _error = null; _result = null; });
    try {
      final res = await _api.callAIFeature('hybrid', {
        'pair': _selectedPair,
        'ta_weight': _taWeight.round(),
        'fa_weight': _faWeight.round(),
        'sentiment_weight': _sentWeight.round(),
      });
      setState(() { _result = res; });
    } catch (e) {
      setState(() { _error = e.toString(); });
    } finally {
      setState(() { _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: const GASAppBar(title: 'Hybrid System'),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.pagePadH),
        children: [
          // Pair selector
          _PairChips(
            pairs: _pairs,
            selected: _selectedPair,
            onSelect: (p) => setState(() { _selectedPair = p; _result = null; }),
          ),
          const SizedBox(height: AppSpacing.lg),

          // Weight sliders
          GASCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Analysis Weights',
                    style: AppTypography.h4.copyWith(color: AppColors.textGold)),
                const SizedBox(height: AppSpacing.md),
                _WeightSlider(
                  label: 'Technical Analysis',
                  value: _taWeight,
                  color: AppColors.accent,
                  onChanged: (v) => setState(() => _taWeight = v),
                ),
                const SizedBox(height: AppSpacing.sm),
                _WeightSlider(
                  label: 'Fundamental Data',
                  value: _faWeight,
                  color: AppColors.info,
                  onChanged: (v) => setState(() => _faWeight = v),
                ),
                const SizedBox(height: AppSpacing.sm),
                _WeightSlider(
                  label: 'Sentiment',
                  value: _sentWeight,
                  color: AppColors.warning,
                  onChanged: (v) => setState(() => _sentWeight = v),
                ),
                const SizedBox(height: AppSpacing.md),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.md, vertical: AppSpacing.sm),
                  decoration: BoxDecoration(
                    color: AppColors.bgTertiary,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Total',
                          style: AppTypography.labelLG.copyWith(
                              color: AppColors.textSecondary)),
                      Text(
                        '${(_taWeight + _faWeight + _sentWeight).round()}%',
                        style: AppTypography.priceSM.copyWith(
                          color: (_taWeight + _faWeight + _sentWeight).round() == 100
                              ? AppColors.bullish
                              : AppColors.warning,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // Run button
          _CreditBadge(cost: '4 Credits'),
          const SizedBox(height: AppSpacing.sm),
          GASButton(
            label: 'Run Hybrid Analysis',
            icon: Icons.merge_type_rounded,
            expand: true,
            size: GASButtonSize.lg,
            isLoading: _loading,
            onTap: _loading ? null : _runAnalysis,
          ),

          if (_error != null) ...[
            const SizedBox(height: AppSpacing.lg),
            _ErrorCard(message: _error!),
          ],
          if (_loading) ...[
            const SizedBox(height: AppSpacing.xxl),
            const Center(child: _ConfluenceRingPlaceholder()),
          ],
          if (_result != null) ...[
            const SizedBox(height: AppSpacing.xxl),
            _buildResults(_result!),
          ],
        ],
      ),
    );
  }

  Widget _buildResults(Map<String, dynamic> r) {
    final confluence = (r['confluence_score'] as num?)?.toDouble() ?? 0.0;
    final taScore    = (r['ta_score']         as num?)?.toDouble() ?? 0.0;
    final faScore    = (r['fa_score']         as num?)?.toDouble() ?? 0.0;
    final sentScore  = (r['sentiment_score']  as num?)?.toDouble() ?? 0.0;
    final rec        = r['recommendation'] as String? ?? 'NEUTRAL';
    final summary    = r['summary'] as String? ?? '';

    final isBull = rec.contains('BUY') || rec.contains('LONG');
    final isBear = rec.contains('SELL') || rec.contains('SHORT');

    return Column(
      children: [
        // Confluence ring
        GASCard(
          child: Column(
            children: [
              Text('Confluence Score',
                  style: AppTypography.labelLG),
              const SizedBox(height: AppSpacing.lg),
              SizedBox(
                width: 160,
                height: 160,
                child: _ConfluenceRing(score: confluence),
              ),
              const SizedBox(height: AppSpacing.lg),
              if (summary.isNotEmpty)
                Text(summary,
                    style: AppTypography.bodySM,
                    textAlign: TextAlign.center),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.md),

        // Individual scores
        Row(
          children: [
            Expanded(
              child: _ScoreCard(
                label: 'Technical',
                score: taScore,
                color: AppColors.accent,
                icon: Icons.candlestick_chart_outlined,
              ),
            ),
            const SizedBox(width: AppSpacing.sm),
            Expanded(
              child: _ScoreCard(
                label: 'Fundamental',
                score: faScore,
                color: AppColors.info,
                icon: Icons.account_balance_outlined,
              ),
            ),
            const SizedBox(width: AppSpacing.sm),
            Expanded(
              child: _ScoreCard(
                label: 'Sentiment',
                score: sentScore,
                color: AppColors.warning,
                icon: Icons.mood_outlined,
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.md),

        // Final recommendation
        GASCard(
          borderColor: isBull
              ? AppColors.bullish.withOpacity(0.5)
              : isBear
                  ? AppColors.bearish.withOpacity(0.5)
                  : AppColors.border,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                isBull ? Icons.trending_up
                    : isBear ? Icons.trending_down
                    : Icons.trending_flat,
                color: isBull ? AppColors.bullish
                    : isBear ? AppColors.bearish
                    : AppColors.neutral,
                size: 24,
              ),
              const SizedBox(width: AppSpacing.sm),
              Text(
                rec,
                style: AppTypography.h3.copyWith(
                  color: isBull ? AppColors.bullish
                      : isBear ? AppColors.bearish
                      : AppColors.neutral,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// ── Widgets ───────────────────────────────────────────────────────────────────

class _WeightSlider extends StatelessWidget {
  final String label;
  final double value;
  final Color color;
  final ValueChanged<double> onChanged;

  const _WeightSlider({
    required this.label,
    required this.value,
    required this.color,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: AppTypography.bodyMD),
          Text('${value.round()}%',
              style: AppTypography.priceSM.copyWith(color: color)),
        ],
      ),
      SliderTheme(
        data: SliderThemeData(
          trackHeight: 3,
          thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 8),
          activeTrackColor: color,
          inactiveTrackColor: color.withOpacity(0.2),
          thumbColor: color,
          overlayColor: color.withOpacity(0.1),
        ),
        child: Slider(
          value: value,
          min: 0,
          max: 100,
          divisions: 20,
          onChanged: onChanged,
        ),
      ),
    ],
  );
}

class _ConfluenceRing extends StatelessWidget {
  final double score;
  const _ConfluenceRing({required this.score});

  @override
  Widget build(BuildContext context) {
    final pct = score.clamp(0.0, 100.0) / 100.0;
    final color = pct >= 0.75
        ? AppColors.bullish
        : pct >= 0.5
            ? AppColors.warning
            : AppColors.bearish;

    return CustomPaint(
      painter: _RingPainter(progress: pct, color: color),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '${score.round()}%',
              style: AppTypography.h2.copyWith(color: color),
            ),
            Text(
              pct >= 0.75 ? 'STRONG' : pct >= 0.5 ? 'MODERATE' : 'WEAK',
              style: AppTypography.labelMD.copyWith(color: color),
            ),
          ],
        ),
      ),
    );
  }
}

class _ConfluenceRingPlaceholder extends StatelessWidget {
  const _ConfluenceRingPlaceholder();

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 160,
    height: 160,
    child: CustomPaint(
      painter: _RingPainter(progress: 0.0, color: AppColors.border),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('--', style: AppTypography.h2),
            Text('LOADING', style: AppTypography.labelMD),
          ],
        ),
      ),
    ),
  );
}

class _RingPainter extends CustomPainter {
  final double progress;
  final Color color;

  const _RingPainter({required this.progress, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final radius = math.min(cx, cy) - 10;
    final strokeW = 12.0;

    final bgPaint = Paint()
      ..color = AppColors.bgTertiary
      ..strokeWidth = strokeW
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final fgPaint = Paint()
      ..color = color
      ..strokeWidth = strokeW
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(Offset(cx, cy), radius, bgPaint);
    canvas.drawArc(
      Rect.fromCircle(center: Offset(cx, cy), radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      fgPaint,
    );
  }

  @override
  bool shouldRepaint(_RingPainter old) =>
      old.progress != progress || old.color != color;
}

class _ScoreCard extends StatelessWidget {
  final String label;
  final double score;
  final Color color;
  final IconData icon;

  const _ScoreCard({
    required this.label,
    required this.score,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) => GASCard(
    padding: const EdgeInsets.all(AppSpacing.md),
    child: Column(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(height: AppSpacing.xs),
        Text(
          '${score.round()}%',
          style: AppTypography.priceMD.copyWith(color: color),
        ),
        Text(label,
            style: AppTypography.bodyXS,
            textAlign: TextAlign.center),
      ],
    ),
  );
}

class _PairChips extends StatelessWidget {
  final List<String> pairs;
  final String selected;
  final ValueChanged<String> onSelect;

  const _PairChips({
    required this.pairs,
    required this.selected,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) => SizedBox(
    height: 38,
    child: ListView.separated(
      scrollDirection: Axis.horizontal,
      itemCount: pairs.length,
      separatorBuilder: (_, __) => const SizedBox(width: AppSpacing.sm),
      itemBuilder: (_, i) {
        final p = pairs[i];
        final sel = p == selected;
        return GestureDetector(
          onTap: () => onSelect(p),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 150),
            padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md, vertical: AppSpacing.xs),
            decoration: BoxDecoration(
              color: sel ? AppColors.primary : AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
              border: Border.all(
                  color: sel ? AppColors.primary : AppColors.border),
            ),
            child: Text(p,
                style: AppTypography.btnSM.copyWith(
                    color: sel ? AppColors.bgDeep : AppColors.textSecondary)),
          ),
        );
      },
    ),
  );
}

class _CreditBadge extends StatelessWidget {
  final String cost;
  const _CreditBadge({required this.cost});

  @override
  Widget build(BuildContext context) => Row(
    children: [
      const Icon(Icons.toll_rounded, size: 14, color: AppColors.textGold),
      const SizedBox(width: AppSpacing.xs),
      Text('Cost: $cost',
          style: AppTypography.bodySM.copyWith(color: AppColors.textGold)),
    ],
  );
}

class _ErrorCard extends StatelessWidget {
  final String message;
  const _ErrorCard({required this.message});

  @override
  Widget build(BuildContext context) => GASCard(
    borderColor: AppColors.error.withOpacity(0.4),
    child: Row(
      children: [
        const Icon(Icons.error_outline, color: AppColors.error, size: 18),
        const SizedBox(width: AppSpacing.sm),
        Expanded(
          child: Text(message,
              style: AppTypography.bodySM.copyWith(color: AppColors.error)),
        ),
      ],
    ),
  );
}
