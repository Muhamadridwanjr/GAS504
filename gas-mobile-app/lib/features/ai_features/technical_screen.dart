import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class TechnicalScreen extends StatefulWidget {
  final String pair;
  const TechnicalScreen({super.key, required this.pair});

  @override
  State<TechnicalScreen> createState() => _TechnicalScreenState();
}

class _TechnicalScreenState extends State<TechnicalScreen> {
  final _api = ApiService();

  static const _pairs = [
    'XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY',
    'BTCUSDT', 'ETHUSDT', 'USDCAD', 'AUDUSD',
  ];

  late String _selectedPair;
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
      final res = await _api.callAIFeature('technical', {'pair': _selectedPair});
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
      appBar: const GASAppBar(title: 'Technical Analysis'),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.pagePadH),
        children: [
          _PairSelector(
            pairs: _pairs,
            selected: _selectedPair,
            onSelect: (p) => setState(() { _selectedPair = p; _result = null; }),
          ),
          const SizedBox(height: AppSpacing.lg),
          _CreditBadge(cost: 'FREE', icon: Icons.analytics_outlined),
          const SizedBox(height: AppSpacing.sm),
          GASButton(
            label: 'Run Analysis',
            icon: Icons.play_arrow_rounded,
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
            ..._buildShimmers(),
          ],
          if (_result != null) ...[
            const SizedBox(height: AppSpacing.xxl),
            _buildResults(_result!),
          ],
        ],
      ),
    );
  }

  List<Widget> _buildShimmers() => List.generate(4, (i) => Padding(
    padding: const EdgeInsets.only(bottom: AppSpacing.md),
    child: _ShimmerBox(height: 90 + i * 10.0),
  ));

  Widget _buildResults(Map<String, dynamic> r) {
    final trend = r['trend'] as String? ?? 'Neutral';
    final support = (r['support_levels'] as List<dynamic>?) ?? [];
    final resistance = (r['resistance_levels'] as List<dynamic>?) ?? [];
    final indicators = r['indicators'] as Map<String, dynamic>? ?? {};
    final setup = r['trade_setup'] as String? ?? 'No clear setup at this time.';
    final isBullish = trend.toLowerCase().contains('bull');
    final isBearish = trend.toLowerCase().contains('bear');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Trend Card
        GASCard(
          borderColor: isBullish
              ? AppColors.bullish.withOpacity(0.5)
              : isBearish
                  ? AppColors.bearish.withOpacity(0.5)
                  : AppColors.border,
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.md, vertical: AppSpacing.xs),
                decoration: BoxDecoration(
                  color: isBullish
                      ? AppColors.bullish.withOpacity(0.15)
                      : isBearish
                          ? AppColors.bearish.withOpacity(0.15)
                          : AppColors.bgTertiary,
                  borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      isBullish
                          ? Icons.trending_up
                          : isBearish
                              ? Icons.trending_down
                              : Icons.trending_flat,
                      color: isBullish
                          ? AppColors.bullish
                          : isBearish
                              ? AppColors.bearish
                              : AppColors.neutral,
                      size: 18,
                    ),
                    const SizedBox(width: AppSpacing.xs),
                    Text(
                      trend.toUpperCase(),
                      style: AppTypography.labelLG.copyWith(
                        color: isBullish
                            ? AppColors.bullish
                            : isBearish
                                ? AppColors.bearish
                                : AppColors.neutral,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: AppSpacing.md),
              Text('Market Trend', style: AppTypography.bodyMD),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.md),

        // Key Levels
        GASCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _SectionHeader(icon: Icons.layers_outlined, label: 'Key Levels'),
              const SizedBox(height: AppSpacing.md),
              if (resistance.isNotEmpty) ...[
                Text('Resistance', style: AppTypography.labelMD.copyWith(
                    color: AppColors.bearish)),
                const SizedBox(height: AppSpacing.xs),
                ...resistance.map((l) => _LevelRow(
                    level: l.toString(), color: AppColors.bearish)),
                const SizedBox(height: AppSpacing.sm),
              ],
              if (support.isNotEmpty) ...[
                Text('Support', style: AppTypography.labelMD.copyWith(
                    color: AppColors.bullish)),
                const SizedBox(height: AppSpacing.xs),
                ...support.map((l) => _LevelRow(
                    level: l.toString(), color: AppColors.bullish)),
              ],
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.md),

        // Indicators
        if (indicators.isNotEmpty)
          GASCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _SectionHeader(
                    icon: Icons.bar_chart_rounded, label: 'Indicators'),
                const SizedBox(height: AppSpacing.md),
                ...indicators.entries.map((e) => _IndicatorRow(
                    name: e.key, value: e.value?.toString() ?? '-')),
              ],
            ),
          ),
        const SizedBox(height: AppSpacing.md),

        // Trade Setup
        GASGoldCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _SectionHeader(
                  icon: Icons.auto_awesome, label: 'Trade Setup',
                  color: AppColors.textGold),
              const SizedBox(height: AppSpacing.md),
              Text(setup,
                  style: AppTypography.bodyMD.copyWith(height: 1.6)),
            ],
          ),
        ),
      ],
    );
  }
}

// ── Shared Helpers ────────────────────────────────────────────────────────────

class _PairSelector extends StatelessWidget {
  final List<String> pairs;
  final String selected;
  final ValueChanged<String> onSelect;

  const _PairSelector({
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
                color: sel ? AppColors.primary : AppColors.border,
              ),
            ),
            child: Text(
              p,
              style: AppTypography.btnSM.copyWith(
                color: sel ? AppColors.bgDeep : AppColors.textSecondary,
              ),
            ),
          ),
        );
      },
    ),
  );
}

class _CreditBadge extends StatelessWidget {
  final String cost;
  final IconData icon;

  const _CreditBadge({required this.cost, required this.icon});

  @override
  Widget build(BuildContext context) => Row(
    children: [
      const Icon(Icons.toll_rounded, size: 14, color: AppColors.textGold),
      const SizedBox(width: AppSpacing.xs),
      Text(
        'Cost: $cost',
        style: AppTypography.bodySM.copyWith(color: AppColors.textGold),
      ),
    ],
  );
}

class _SectionHeader extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color? color;

  const _SectionHeader({
    required this.icon,
    required this.label,
    this.color,
  });

  @override
  Widget build(BuildContext context) => Row(
    children: [
      Icon(icon, size: 16, color: color ?? AppColors.textSecondary),
      const SizedBox(width: AppSpacing.sm),
      Text(
        label,
        style: AppTypography.labelLG.copyWith(
          color: color ?? AppColors.textSecondary,
        ),
      ),
    ],
  );
}

class _LevelRow extends StatelessWidget {
  final String level;
  final Color color;

  const _LevelRow({required this.level, required this.color});

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 3),
    child: Row(
      children: [
        Container(
          width: 6,
          height: 6,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: AppSpacing.sm),
        Text(level,
            style: AppTypography.priceSM.copyWith(color: AppColors.textPrimary)),
      ],
    ),
  );
}

class _IndicatorRow extends StatelessWidget {
  final String name;
  final String value;

  const _IndicatorRow({required this.name, required this.value});

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(name.toUpperCase(),
            style: AppTypography.labelMD),
        Text(value,
            style: AppTypography.priceSM),
      ],
    ),
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
          child: Text(
            message,
            style: AppTypography.bodySM.copyWith(color: AppColors.error),
          ),
        ),
      ],
    ),
  );
}

class _ShimmerBox extends StatefulWidget {
  final double height;
  const _ShimmerBox({required this.height});

  @override
  State<_ShimmerBox> createState() => _ShimmerBoxState();
}

class _ShimmerBoxState extends State<_ShimmerBox>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 1200))
      ..repeat(reverse: true);
    _anim = Tween<double>(begin: 0.3, end: 0.7).animate(
        CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: _anim,
    builder: (_, __) => Container(
      height: widget.height,
      decoration: BoxDecoration(
        color: AppColors.bgSecondary.withOpacity(_anim.value + 0.3),
        borderRadius: BorderRadius.circular(AppSpacing.radiusLG),
        border: Border.all(color: AppColors.border),
      ),
    ),
  );
}
