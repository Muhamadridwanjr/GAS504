import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/models/market_pair.dart';

class PriceTile extends StatelessWidget {
  final MarketPair pair;
  final VoidCallback? onTap;
  final bool showSpread;

  const PriceTile({
    super.key,
    required this.pair,
    this.onTap,
    this.showSpread = false,
  });

  @override
  Widget build(BuildContext context) {
    final isUp     = pair.isUp;
    final dirColor = isUp ? AppColors.bullish : AppColors.bearish;
    final isOpen   = pair.isOpen;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.lg, vertical: AppSpacing.md),
        decoration: const BoxDecoration(
          border: Border(bottom: BorderSide(color: AppColors.border)),
        ),
        child: Row(
          children: [
            // ── Symbol & name ───────────────────────────────────────────
            Expanded(
              flex: 3,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(pair.symbol,
                          style: AppTypography.priceSM.copyWith(
                              color: AppColors.textPrimary)),
                      const SizedBox(width: AppSpacing.xs),
                      // Market status dot
                      Container(
                        width: 6, height: 6,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: isOpen ? AppColors.bullish
                              : AppColors.sessionClosed,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(pair.name,
                      style: AppTypography.bodyXS,
                      maxLines: 1, overflow: TextOverflow.ellipsis),
                  if (!isOpen && pair.market != null)
                    Text(pair.market!.label,
                        style: AppTypography.bodyXS.copyWith(
                            color: AppColors.error, fontSize: 9)),
                ],
              ),
            ),

            // ── Price ───────────────────────────────────────────────────
            Expanded(
              flex: 3,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  pair.noData
                      ? Text('—',
                          style: AppTypography.priceSM.copyWith(
                              color: AppColors.textMuted))
                      : Text(pair.formatPrice(),
                          style: AppTypography.priceSM.copyWith(
                              color: pair.stale
                                  ? AppColors.textMuted
                                  : AppColors.textPrimary)),
                  if (showSpread && pair.spread != null && pair.spread! > 0)
                    Text('Spread ${pair.spread!.toStringAsFixed(1)}',
                        style: AppTypography.bodyXS),
                ],
              ),
            ),

            const SizedBox(width: AppSpacing.sm),

            // ── Change % ────────────────────────────────────────────────
            Expanded(
              flex: 2,
              child: Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.sm, vertical: 3),
                decoration: BoxDecoration(
                  color: pair.noData ? AppColors.bgTertiary
                      : dirColor.withOpacity(0.1),
                  borderRadius:
                      BorderRadius.circular(AppSpacing.radiusSM),
                ),
                child: Text(
                  pair.noData ? '—' : pair.formatChangePct(),
                  style: AppTypography.priceXS.copyWith(
                    color: pair.noData ? AppColors.textMuted : dirColor,
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
