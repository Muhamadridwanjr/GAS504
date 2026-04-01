import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';

class GASAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final String? subtitle;
  final List<Widget>? actions;
  final bool showDrawer;
  final bool showBack;
  final Widget? leading;
  final Color? backgroundColor;

  const GASAppBar({
    super.key,
    required this.title,
    this.subtitle,
    this.actions,
    this.showDrawer  = false,
    this.showBack    = true,
    this.leading,
    this.backgroundColor,
  });

  @override
  Size get preferredSize => Size.fromHeight(
      subtitle != null ? kToolbarHeight + 20 : kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    Widget? effectiveLeading;

    if (leading != null) {
      effectiveLeading = leading;
    } else if (showDrawer) {
      effectiveLeading = IconButton(
        icon: const Icon(Icons.menu, color: AppColors.textPrimary),
        onPressed: () => Scaffold.of(context).openDrawer(),
      );
    } else if (showBack && context.canPop()) {
      effectiveLeading = IconButton(
        icon: const Icon(Icons.arrow_back_ios_new,
            color: AppColors.textPrimary, size: 20),
        onPressed: () => context.pop(),
      );
    }

    return AppBar(
      backgroundColor: backgroundColor ?? AppColors.bgPrimary,
      elevation: 0,
      automaticallyImplyLeading: false,
      leading: effectiveLeading,
      title: subtitle != null
          ? Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(title, style: AppTypography.h4),
                Text(subtitle!, style: AppTypography.bodySM),
              ],
            )
          : Text(title, style: AppTypography.h4),
      actions: actions,
      bottom: const PreferredSize(
        preferredSize: Size.fromHeight(1),
        child: Divider(height: 1),
      ),
    );
  }
}

class GASLogoAppBar extends StatelessWidget implements PreferredSizeWidget {
  final List<Widget>? actions;
  const GASLogoAppBar({super.key, this.actions});

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) => AppBar(
    backgroundColor: AppColors.bgPrimary,
    elevation: 0,
    automaticallyImplyLeading: false,
    leading: Builder(builder: (ctx) => IconButton(
      icon: const Icon(Icons.menu, color: AppColors.textSecondary),
      onPressed: () => Scaffold.of(ctx).openDrawer(),
    )),
    title: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 28, height: 28,
          decoration: BoxDecoration(
            color: AppColors.primary,
            borderRadius: BorderRadius.circular(6),
          ),
          child: const Center(
            child: Text('G', style: TextStyle(
              color: Colors.black,
              fontWeight: FontWeight.w900,
              fontSize: 16,
            )),
          ),
        ),
        const SizedBox(width: 8),
        const Text('GAS Terminal',
            style: TextStyle(
              color: AppColors.textPrimary,
              fontSize: 16,
              fontWeight: FontWeight.w700,
            )),
      ],
    ),
    actions: actions,
    bottom: const PreferredSize(
      preferredSize: Size.fromHeight(1),
      child: Divider(height: 1),
    ),
  );
}
