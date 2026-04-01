import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_spacing.dart';

class GASCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final Color? backgroundColor;
  final Color? borderColor;
  final double? borderWidth;
  final double? borderRadius;
  final Gradient? gradient;
  final VoidCallback? onTap;
  final double? elevation;

  const GASCard({
    super.key,
    required this.child,
    this.padding,
    this.backgroundColor,
    this.borderColor,
    this.borderWidth,
    this.borderRadius,
    this.gradient,
    this.onTap,
    this.elevation,
  });

  @override
  Widget build(BuildContext context) {
    Widget content = Container(
      padding: padding ?? const EdgeInsets.all(AppSpacing.cardPad),
      decoration: BoxDecoration(
        color: gradient == null
            ? (backgroundColor ?? AppColors.bgSecondary) : null,
        gradient: gradient,
        borderRadius: BorderRadius.circular(
            borderRadius ?? AppSpacing.radiusLG),
        border: Border.all(
          color: borderColor ?? AppColors.border,
          width: borderWidth ?? 1.0,
        ),
        boxShadow: elevation != null && elevation! > 0
            ? [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: elevation! * 4,
                  offset: Offset(0, elevation! * 2),
                )
              ]
            : null,
      ),
      child: child,
    );

    if (onTap != null) {
      return GestureDetector(
        onTap: onTap,
        child: content,
      );
    }
    return content;
  }
}

/// Gold-bordered card (used for featured/premium content)
class GASGoldCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final VoidCallback? onTap;

  const GASGoldCard({
    super.key,
    required this.child,
    this.padding,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) => GASCard(
    child: child,
    padding: padding,
    backgroundColor: AppColors.bgSecondary,
    borderColor: AppColors.primary.withOpacity(0.4),
    borderWidth: 1.5,
    onTap: onTap,
  );
}

/// Gradient card (used for signal buy/sell highlight)
class GASGradientCard extends StatelessWidget {
  final Widget child;
  final Gradient gradient;
  final EdgeInsetsGeometry? padding;
  final double? borderRadius;
  final VoidCallback? onTap;

  const GASGradientCard({
    super.key,
    required this.child,
    required this.gradient,
    this.padding,
    this.borderRadius,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) => GASCard(
    child: child,
    padding: padding,
    gradient: gradient,
    borderColor: Colors.transparent,
    borderRadius: borderRadius,
    onTap: onTap,
  );
}
