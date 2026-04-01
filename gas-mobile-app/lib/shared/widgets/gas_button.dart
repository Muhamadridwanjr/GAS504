import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';

enum GASButtonVariant { primary, secondary, outline, ghost, danger }
enum GASButtonSize    { sm, md, lg }

class GASButton extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;
  final GASButtonVariant variant;
  final GASButtonSize size;
  final IconData? icon;
  final bool isLoading;
  final bool expand;
  final Color? color;

  const GASButton({
    super.key,
    required this.label,
    this.onTap,
    this.variant  = GASButtonVariant.primary,
    this.size     = GASButtonSize.md,
    this.icon,
    this.isLoading = false,
    this.expand    = false,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final (bg, fg, border) = _colors();
    final h = size == GASButtonSize.sm ? 36.0
            : size == GASButtonSize.lg ? 56.0 : 46.0;
    final textStyle = size == GASButtonSize.sm ? AppTypography.btnSM
                    : size == GASButtonSize.lg ? AppTypography.btnLG
                    : AppTypography.btnMD;
    final iconSz = size == GASButtonSize.sm ? 14.0
                 : size == GASButtonSize.lg ? 22.0 : 18.0;
    final hPad   = size == GASButtonSize.sm ? AppSpacing.md
                 : size == GASButtonSize.lg ? AppSpacing.xl
                 : AppSpacing.lg;

    Widget content = Row(
      mainAxisSize: expand ? MainAxisSize.max : MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        if (isLoading)
          SizedBox(width: iconSz, height: iconSz,
            child: CircularProgressIndicator(
                strokeWidth: 2, color: fg)),
        if (!isLoading && icon != null) ...[
          Icon(icon, size: iconSz, color: fg),
          const SizedBox(width: AppSpacing.sm),
        ],
        if (!isLoading)
          Text(label, style: textStyle.copyWith(color: fg)),
      ],
    );

    return AnimatedOpacity(
      opacity: onTap == null ? 0.4 : 1.0,
      duration: AppConstants2.animFast,
      child: GestureDetector(
        onTap: isLoading ? null : onTap,
        child: Container(
          height: h,
          padding: EdgeInsets.symmetric(horizontal: hPad),
          width: expand ? double.infinity : null,
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
            border: border != null ? Border.all(color: border) : null,
          ),
          child: content,
        ),
      ),
    );
  }

  (Color bg, Color fg, Color? border) _colors() {
    final c = color;
    switch (variant) {
      case GASButtonVariant.primary:
        return (c ?? AppColors.primary, AppColors.bgDeep, null);
      case GASButtonVariant.secondary:
        return (AppColors.bgTertiary, AppColors.textPrimary, null);
      case GASButtonVariant.outline:
        return (Colors.transparent, c ?? AppColors.textPrimary,
            c ?? AppColors.border);
      case GASButtonVariant.ghost:
        return (Colors.transparent, c ?? AppColors.textSecondary, null);
      case GASButtonVariant.danger:
        return (AppColors.error.withOpacity(0.1), AppColors.error,
            AppColors.error.withOpacity(0.3));
    }
  }
}

// Tiny constant class to avoid circular import
class AppConstants2 {
  static const animFast = Duration(milliseconds: 150);
}
