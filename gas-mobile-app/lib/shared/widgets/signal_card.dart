import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/models/signal.dart';
import 'gas_card.dart';
import 'confidence_ring.dart';

class SignalCard extends StatelessWidget {
  final TradingSignal signal;
  final VoidCallback? onTap;
  final bool compact;

  const SignalCard({
    super.key,
    required this.signal,
    this.onTap,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    final isBuy = signal.isBuy;
    final dirColor = isBuy ? AppColors.bullish : AppColors.bearish;
    final gradient = isBuy
        ? AppColors.bullishGradient.scale(0.15)
        : AppColors.bearishGradient.scale(0.15);

    return GASCard(
      onTap: onTap,
      backgroundColor: AppColors.bgSecondary,
      borderColor: dirColor.withOpacity(0.3),
      borderWidth: 1.5,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header ────────────────────────────────────────────────────
          Row(
            children: [
              // Direction badge
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.md, vertical: AppSpacing.xs),
                decoration: BoxDecoration(
                  color: dirColor.withOpacity(0.15),
                  borderRadius:
                      BorderRadius.circular(AppSpacing.radiusFull),
                  border: Border.all(color: dirColor.withOpacity(0.4)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      isBuy
                          ? Icons.arrow_upward
                          : Icons.arrow_downward,
                      size: 14,
                      color: dirColor,
                    ),
                    const SizedBox(width: 4),
                    Text(signal.directionLabel,
                        style: AppTypography.labelMD
                            .copyWith(color: dirColor)),
                  ],
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              Text(signal.pair, style: AppTypography.h4),
              const Spacer(),
              ConfidenceRing(
                  value: signal.confidence / 100, size: 36),
            ],
          ),

          if (!compact) ...[
            const SizedBox(height: AppSpacing.md),

            // ── Price levels ──────────────────────────────────────────
            _levels(),

            if (signal.regime != null) ...[
              const SizedBox(height: AppSpacing.sm),
              _chip('Regime', signal.regime!, AppColors.accent),
            ],

            if (signal.notes != null && signal.notes!.isNotEmpty) ...[
              const SizedBox(height: AppSpacing.sm),
              Text(signal.notes!,
                  style: AppTypography.bodySM,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis),
            ],
          ],

          const SizedBox(height: AppSpacing.sm),
          // ── Footer ────────────────────────────────────────────────────
          Row(
            children: [
              Icon(Icons.access_time_outlined,
                  size: 12, color: AppColors.textMuted),
              const SizedBox(width: 4),
              Text(_timeAgo(signal.timestamp),
                  style: AppTypography.bodyXS),
              const Spacer(),
              if (signal.rr != null)
                Text('RR ${signal.rr!.toStringAsFixed(1)}:1',
                    style: AppTypography.priceSM
                        .copyWith(color: AppColors.textGold)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _levels() => Row(
    children: [
      if (signal.entryPrice != null)
        _priceBox('Entry', signal.entryPrice!, AppColors.textPrimary),
      const SizedBox(width: AppSpacing.sm),
      if (signal.sl != null)
        _priceBox('SL', signal.sl!, AppColors.bearish),
      const SizedBox(width: AppSpacing.sm),
      if (signal.tp1 != null)
        _priceBox('TP1', signal.tp1!, AppColors.bullish),
    ],
  );

  Widget _priceBox(String label, double price, Color color) => Expanded(
    child: Container(
      padding: const EdgeInsets.all(AppSpacing.sm),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        children: [
          Text(label, style: AppTypography.labelSM),
          const SizedBox(height: 2),
          Text(price.toStringAsFixed(5),
              style: AppTypography.priceXS.copyWith(color: color),
              maxLines: 1, overflow: TextOverflow.ellipsis),
        ],
      ),
    ),
  );

  Widget _chip(String label, String value, Color color) => Container(
    padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.sm, vertical: 3),
    decoration: BoxDecoration(
      color: color.withOpacity(0.1),
      borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
      border: Border.all(color: color.withOpacity(0.3)),
    ),
    child: Text('$label: $value',
        style: AppTypography.labelSM.copyWith(color: color)),
  );

  String _timeAgo(DateTime dt) {
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}

// Gradient scale helper
extension GradientScale on LinearGradient {
  LinearGradient scale(double opacity) => LinearGradient(
    colors: colors.map((c) => c.withOpacity(opacity)).toList(),
    begin: begin,
    end: end,
  );
}
