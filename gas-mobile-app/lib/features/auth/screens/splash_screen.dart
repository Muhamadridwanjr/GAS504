import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_typography.dart';
import '../../../core/services/auth_service.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});
  @override State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _fade;
  late final Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 900));
    _fade  = Tween<double>(begin: 0, end: 1).animate(
        CurvedAnimation(parent: _ctrl, curve: Curves.easeIn));
    _scale = Tween<double>(begin: 0.7, end: 1).animate(
        CurvedAnimation(parent: _ctrl, curve: Curves.elasticOut));
    _ctrl.forward();
    _init();
  }

  Future<void> _init() async {
    await Future.delayed(const Duration(milliseconds: 1500));
    try {
      final ok = await AuthService().restoreSession();
      if (mounted) context.go(ok ? '/dashboard' : '/auth/login');
    } catch (_) {
      if (mounted) context.go('/auth/login');
    }
  }

  @override
  void dispose() { _ctrl.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgDeep,
    body: Center(
      child: FadeTransition(
        opacity: _fade,
        child: ScaleTransition(
          scale: _scale,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 88, height: 88,
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(22),
                  boxShadow: [BoxShadow(
                    color: AppColors.primary.withOpacity(0.4),
                    blurRadius: 32, spreadRadius: 4,
                  )],
                ),
                child: const Center(
                  child: Text('G', style: TextStyle(
                    color: Colors.black, fontSize: 52,
                    fontWeight: FontWeight.w900,
                  )),
                ),
              ),
              const SizedBox(height: 20),
              Text('GAS Terminal',
                  style: AppTypography.h2
                      .copyWith(color: AppColors.textGold)),
              const SizedBox(height: 8),
              Text('Golden AI Strategy',
                  style: AppTypography.bodySM),
              const SizedBox(height: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppColors.primary.withOpacity(0.4)),
                ),
                child: const Text('v2.0.0', style: TextStyle(
                  fontSize: 11, fontWeight: FontWeight.w700,
                  color: AppColors.primary, letterSpacing: 1,
                )),
              ),
              const SizedBox(height: 48),
              const SizedBox(
                width: 24, height: 24,
                child: CircularProgressIndicator(
                  color: AppColors.primary,
                  strokeWidth: 2,
                ),
              ),
              const SizedBox(height: 12),
              Text('Initializing...',
                  style: AppTypography.bodySM
                      .copyWith(color: AppColors.textMuted)),
            ],
          ),
        ),
      ),
    ),
  );
}
