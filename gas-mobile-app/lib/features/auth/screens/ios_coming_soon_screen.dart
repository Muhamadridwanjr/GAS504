import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_typography.dart';
import '../../../core/constants/app_spacing.dart';

class IosComingSoonScreen extends StatelessWidget {
  const IosComingSoonScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    body: SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          children: [
            Align(
              alignment: Alignment.topLeft,
              child: IconButton(
                icon: const Icon(Icons.arrow_back_ios_new,
                    color: AppColors.textSecondary),
                onPressed: () {
                  if (context.canPop()) context.pop();
                  else context.go('/auth/login');
                },
              ),
            ),
            const Spacer(),
            Container(
              width: 100, height: 100,
              decoration: BoxDecoration(
                border: Border.all(color: AppColors.primary, width: 2),
                borderRadius: BorderRadius.circular(AppSpacing.radiusXL),
                boxShadow: [BoxShadow(
                  color: AppColors.primary.withOpacity(0.2),
                  blurRadius: 24, spreadRadius: 4,
                )],
              ),
              child: const Center(
                child: Icon(Icons.apple, size: 52,
                    color: AppColors.textPrimary),
              ),
            ),
            const SizedBox(height: AppSpacing.x3l),
            Text('iOS Coming Soon',
                style: AppTypography.h1
                    .copyWith(color: AppColors.primary)),
            const SizedBox(height: AppSpacing.md),
            Text('We\'re working on the iOS version.\nStay tuned for the release!',
                style: AppTypography.bodyLG
                    .copyWith(color: AppColors.textSecondary),
                textAlign: TextAlign.center),
            const SizedBox(height: AppSpacing.x3l),
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.xl, vertical: AppSpacing.md),
              decoration: BoxDecoration(
                color: AppColors.bullish.withOpacity(0.1),
                borderRadius: BorderRadius.circular(AppSpacing.radiusLG),
                border: Border.all(color: AppColors.bullish.withOpacity(0.3)),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.android,
                      color: AppColors.bullish, size: 20),
                  const SizedBox(width: AppSpacing.sm),
                  Text('Android APK Available Now',
                      style: AppTypography.bodyMD
                          .copyWith(color: AppColors.bullish)),
                ],
              ),
            ),
            const Spacer(),
            Text('GAS Terminal', style: AppTypography.labelMD),
            const SizedBox(height: AppSpacing.lg),
          ],
        ),
      ),
    ),
  );
}
