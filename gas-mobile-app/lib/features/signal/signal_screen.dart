import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';
import '../../shared/widgets/confidence_ring.dart';

class SignalScreen extends StatefulWidget {
  final String pair;

  const SignalScreen({super.key, this.pair = 'XAUUSD'});

  @override
  State<SignalScreen> createState() => _SignalScreenState();
}

class _SignalScreenState extends State<SignalScreen> {
  static const List<String> _pairs = [
    'XAUUSD', 'EURUSD', 'GBPUSD', 'BTCUSD', 'US30',
  ];

  late String _selectedPair;
  Map<String, dynamic>? _signal;
  bool _isLoading = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _selectedPair = widget.pair;
    _fetchSignal();
  }

  Future<void> _fetchSignal() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final data = await ApiService().getSignal(_selectedPair);
      if (mounted) setState(() => _signal = data);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _onPairSelected(String pair) {
    setState(() {
      _selectedPair = pair;
      _signal = null;
    });
    _fetchSignal();
  }

  Color _directionColor(String? dir) {
    switch (dir?.toUpperCase()) {
      case 'BUY':  return AppColors.bullish;
      case 'SELL': return AppColors.bearish;
      default:     return AppColors.neutral;
    }
  }

  LinearGradient _directionGradient(String? dir) {
    switch (dir?.toUpperCase()) {
      case 'BUY':  return AppColors.bullishGradient;
      case 'SELL': return AppColors.bearishGradient;
      default:     return const LinearGradient(
        colors: [Color(0xFF2A2A3F), Color(0xFF1A1A2E)],
      );
    }
  }

  IconData _directionIcon(String? dir) {
    switch (dir?.toUpperCase()) {
      case 'BUY':  return Icons.trending_up_rounded;
      case 'SELL': return Icons.trending_down_rounded;
      default:     return Icons.trending_flat_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: GASAppBar(
        title: 'Signal Analysis',
        showBack: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded,
                color: AppColors.textSecondary),
            onPressed: _isLoading ? null : _fetchSignal,
          ),
        ],
      ),
      body: Column(
        children: [
          // Pair selector chips
          _PairSelector(
            pairs: _pairs,
            selected: _selectedPair,
            onSelect: _onPairSelected,
          ),
          Expanded(
            child: _isLoading
                ? _SignalSkeleton()
                : _error != null
                    ? _ErrorState(
                        message: _error!,
                        onRetry: _fetchSignal,
                      )
                    : _signal == null || _signal!.isEmpty
                        ? _EmptyState(pair: _selectedPair)
                        : _SignalContent(
                            signal: _signal!,
                            pair: _selectedPair,
                            directionColor: _directionColor,
                            directionGradient: _directionGradient,
                            directionIcon: _directionIcon,
                          ),
          ),
          // Refresh button pinned at bottom
          Padding(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.pagePadH,
              AppSpacing.sm,
              AppSpacing.pagePadH,
              AppSpacing.xl,
            ),
            child: GASButton(
              label: 'Refresh Signal',
              icon: Icons.refresh_rounded,
              expand: true,
              size: GASButtonSize.lg,
              isLoading: _isLoading,
              onTap: _isLoading ? null : _fetchSignal,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Pair selector
// ─────────────────────────────────────────────────────────────────────────────

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
  Widget build(BuildContext context) {
    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(color: AppColors.border, width: 1),
        ),
      ),
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: AppSpacing.pagePadH),
        itemCount: pairs.length,
        separatorBuilder: (_, __) => const SizedBox(width: AppSpacing.sm),
        itemBuilder: (_, i) {
          final pair = pairs[i];
          final isSelected = pair == selected;
          return GestureDetector(
            onTap: () => onSelect(pair),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md,
                vertical: AppSpacing.xs,
              ),
              decoration: BoxDecoration(
                color: isSelected
                    ? AppColors.primary.withOpacity(0.15)
                    : AppColors.bgSecondary,
                borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                border: Border.all(
                  color: isSelected ? AppColors.primary : AppColors.border,
                  width: isSelected ? 1.5 : 1.0,
                ),
              ),
              child: Text(
                pair,
                style: AppTypography.btnSM.copyWith(
                  color: isSelected
                      ? AppColors.textGold
                      : AppColors.textSecondary,
                  fontWeight: isSelected
                      ? FontWeight.w700
                      : FontWeight.w500,
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Main signal content
// ─────────────────────────────────────────────────────────────────────────────

class _SignalContent extends StatelessWidget {
  final Map<String, dynamic> signal;
  final String pair;
  final Color Function(String?) directionColor;
  final LinearGradient Function(String?) directionGradient;
  final IconData Function(String?) directionIcon;

  const _SignalContent({
    required this.signal,
    required this.pair,
    required this.directionColor,
    required this.directionGradient,
    required this.directionIcon,
  });

  @override
  Widget build(BuildContext context) {
    final direction = signal['direction'] as String? ?? 'NEUTRAL';
    final confidence = ((signal['confidence'] as num?) ?? 0).toDouble() / 100;
    final entry  = signal['entry']  as String? ?? signal['entry_price']?.toString()  ?? '—';
    final sl     = signal['sl']     as String? ?? signal['stop_loss']?.toString()    ?? '—';
    final tp1    = signal['tp1']    as String? ?? signal['take_profit_1']?.toString() ?? '—';
    final tp2    = signal['tp2']    as String? ?? signal['take_profit_2']?.toString() ?? '—';
    final tp3    = signal['tp3']    as String? ?? signal['take_profit_3']?.toString() ?? '—';
    final rr     = signal['rr']     as String? ?? signal['risk_reward']?.toString()  ?? '—';
    final regime  = signal['regime']  as String? ?? '—';
    final session = signal['session'] as String? ?? '—';
    final notes   = signal['notes']   as String? ??
                    signal['analysis'] as String? ?? '';

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // ── Direction hero card ─────────────────────────────────────────
          GASGradientCard(
            gradient: directionGradient(direction),
            padding: const EdgeInsets.all(AppSpacing.xl),
            child: Column(
              children: [
                // Direction badge
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.lg,
                    vertical: AppSpacing.sm,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.3),
                    borderRadius:
                        BorderRadius.circular(AppSpacing.radiusFull),
                    border: Border.all(
                      color: directionColor(direction).withOpacity(0.5),
                      width: 1.5,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        directionIcon(direction),
                        color: directionColor(direction),
                        size: 20,
                      ),
                      const SizedBox(width: AppSpacing.sm),
                      Text(
                        direction.toUpperCase(),
                        style: AppTypography.h3.copyWith(
                          color: directionColor(direction),
                          letterSpacing: 2,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: AppSpacing.xl),

                // Confidence ring — large 80px
                ConfidenceRing(
                  value: confidence,
                  size: 80,
                  strokeWidth: 7,
                  showLabel: true,
                ),

                const SizedBox(height: AppSpacing.md),

                Text(
                  'Confidence',
                  style: AppTypography.bodySM.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),

                const SizedBox(height: AppSpacing.md),

                // Pair name
                Text(
                  pair,
                  style: AppTypography.h2.copyWith(
                    color: AppColors.textPrimary,
                    letterSpacing: 1,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: AppSpacing.lg),

          // ── Price levels ────────────────────────────────────────────────
          Text(
            'PRICE LEVELS',
            style: AppTypography.labelMD.copyWith(
              color: AppColors.textMuted,
              letterSpacing: 1.5,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          GridView.count(
            crossAxisCount: 2,
            crossAxisSpacing: AppSpacing.sm,
            mainAxisSpacing: AppSpacing.sm,
            childAspectRatio: 2.6,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: [
              _PriceLevelCard(label: 'Entry', value: entry,
                  color: AppColors.textGold),
              _PriceLevelCard(label: 'Stop Loss', value: sl,
                  color: AppColors.bearish),
              _PriceLevelCard(label: 'TP 1', value: tp1,
                  color: AppColors.bullish),
              _PriceLevelCard(label: 'TP 2', value: tp2,
                  color: AppColors.bullish),
              _PriceLevelCard(label: 'TP 3', value: tp3,
                  color: AppColors.bullish),
              // Risk/Reward highlighted
              _RRCard(rr: rr),
            ],
          ),

          const SizedBox(height: AppSpacing.lg),

          // ── Regime & Session ────────────────────────────────────────────
          Text(
            'MARKET CONTEXT',
            style: AppTypography.labelMD.copyWith(
              color: AppColors.textMuted,
              letterSpacing: 1.5,
            ),
          ),
          const SizedBox(height: AppSpacing.sm),
          Wrap(
            spacing: AppSpacing.sm,
            runSpacing: AppSpacing.sm,
            children: [
              _ContextChip(
                icon: Icons.auto_graph_rounded,
                label: 'Regime',
                value: regime,
                color: AppColors.accent,
              ),
              _ContextChip(
                icon: Icons.access_time_rounded,
                label: 'Session',
                value: session,
                color: AppColors.sessionLondon,
              ),
            ],
          ),

          if (notes.isNotEmpty) ...[
            const SizedBox(height: AppSpacing.lg),

            // ── Analysis notes ──────────────────────────────────────────
            Text(
              'ANALYSIS',
              style: AppTypography.labelMD.copyWith(
                color: AppColors.textMuted,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: AppSpacing.sm),
            GASCard(
              padding: const EdgeInsets.all(AppSpacing.lg),
              child: Text(
                notes,
                style: AppTypography.bodyMD.copyWith(
                  color: AppColors.textSecondary,
                  height: 1.6,
                ),
              ),
            ),
          ],

          // Bottom spacer for the pinned button
          const SizedBox(height: AppSpacing.sm),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Price level card
// ─────────────────────────────────────────────────────────────────────────────

class _PriceLevelCard extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _PriceLevelCard({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return GASCard(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            label.toUpperCase(),
            style: AppTypography.labelSM.copyWith(
              color: AppColors.textMuted,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: AppTypography.priceSM.copyWith(color: color),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Risk/Reward card
// ─────────────────────────────────────────────────────────────────────────────

class _RRCard extends StatelessWidget {
  final String rr;

  const _RRCard({required this.rr});

  @override
  Widget build(BuildContext context) {
    return GASCard(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm,
      ),
      borderColor: AppColors.primary.withOpacity(0.4),
      backgroundColor: AppColors.primary.withOpacity(0.05),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            'RISK / REWARD',
            style: AppTypography.labelSM.copyWith(
              color: AppColors.textGold.withOpacity(0.7),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            'RR: $rr',
            style: AppTypography.priceSM.copyWith(
              color: AppColors.textGold,
              fontWeight: FontWeight.w700,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Context chip
// ─────────────────────────────────────────────────────────────────────────────

class _ContextChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _ContextChip({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.md,
        vertical: AppSpacing.sm,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: AppSpacing.xs),
          Text(
            '$label: ',
            style: AppTypography.bodySM.copyWith(
              color: AppColors.textMuted,
            ),
          ),
          Text(
            value,
            style: AppTypography.bodySM.copyWith(
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Loading skeleton
// ─────────────────────────────────────────────────────────────────────────────

class _SignalSkeleton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _SkeletonBox(height: 220, radius: AppSpacing.radiusLG),
          const SizedBox(height: AppSpacing.lg),
          _SkeletonBox(height: 16, width: 120, radius: AppSpacing.radiusSM),
          const SizedBox(height: AppSpacing.sm),
          GridView.count(
            crossAxisCount: 2,
            crossAxisSpacing: AppSpacing.sm,
            mainAxisSpacing: AppSpacing.sm,
            childAspectRatio: 2.6,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            children: List.generate(6,
              (_) => _SkeletonBox(height: 56, radius: AppSpacing.radiusLG)),
          ),
          const SizedBox(height: AppSpacing.lg),
          _SkeletonBox(height: 16, width: 140, radius: AppSpacing.radiusSM),
          const SizedBox(height: AppSpacing.sm),
          Row(
            children: [
              _SkeletonBox(height: 36, width: 140, radius: AppSpacing.radiusMD),
              const SizedBox(width: AppSpacing.sm),
              _SkeletonBox(height: 36, width: 130, radius: AppSpacing.radiusMD),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),
          _SkeletonBox(height: 16, width: 100, radius: AppSpacing.radiusSM),
          const SizedBox(height: AppSpacing.sm),
          _SkeletonBox(height: 100, radius: AppSpacing.radiusLG),
        ],
      ),
    );
  }
}

class _SkeletonBox extends StatelessWidget {
  final double height;
  final double? width;
  final double radius;

  const _SkeletonBox({
    required this.height,
    this.width,
    required this.radius,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      width: width,
      decoration: BoxDecoration(
        color: AppColors.bgTertiary,
        borderRadius: BorderRadius.circular(radius),
        border: Border.all(color: AppColors.border, width: 1),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Error state
// ─────────────────────────────────────────────────────────────────────────────

class _ErrorState extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorState({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline_rounded,
                color: AppColors.bearish, size: 48),
            const SizedBox(height: AppSpacing.md),
            Text(
              'Failed to load signal',
              style: AppTypography.h4.copyWith(color: AppColors.textPrimary),
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              message,
              style: AppTypography.bodySM,
              textAlign: TextAlign.center,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: AppSpacing.xl),
            GASButton(
              label: 'Retry',
              icon: Icons.refresh_rounded,
              onTap: onRetry,
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Empty state
// ─────────────────────────────────────────────────────────────────────────────

class _EmptyState extends StatelessWidget {
  final String pair;

  const _EmptyState({required this.pair});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.signal_cellular_off_rounded,
              color: AppColors.textMuted,
              size: 56,
            ),
            const SizedBox(height: AppSpacing.lg),
            Text(
              'No Signal Available',
              style: AppTypography.h3.copyWith(color: AppColors.textPrimary),
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              'No active signal found for $pair.\nCheck back during market hours.',
              style: AppTypography.bodySM,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
