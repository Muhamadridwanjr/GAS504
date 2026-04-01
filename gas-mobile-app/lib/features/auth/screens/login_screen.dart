import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_typography.dart';
import '../../../core/constants/app_spacing.dart';
import '../../../core/services/auth_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _form     = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passCtrl  = TextEditingController();
  final _auth      = AuthService();
  bool _loading    = false;
  bool _obscure    = true;
  String? _error;

  @override
  void dispose() { _emailCtrl.dispose(); _passCtrl.dispose(); super.dispose(); }

  Future<void> _login() async {
    if (!(_form.currentState?.validate() ?? false)) return;
    setState(() { _loading = true; _error = null; });
    try {
      await _auth.login(_emailCtrl.text.trim(), _passCtrl.text);
      if (mounted) context.go('/dashboard');
    } catch (e) {
      setState(() {
        _loading = false;
        _error = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    body: SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Form(
          key: _form,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: AppSpacing.x4l),
              // Logo
              Center(
                child: Column(
                  children: [
                    Container(
                      width: 64, height: 64,
                      decoration: BoxDecoration(
                        color: AppColors.primary,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Center(
                        child: Text('G', style: TextStyle(
                          color: Colors.black, fontSize: 36,
                          fontWeight: FontWeight.w900,
                        )),
                      ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    Text('GAS Terminal',
                        style: AppTypography.h2
                            .copyWith(color: AppColors.textGold)),
                    const SizedBox(height: AppSpacing.xs),
                    Text('Golden AI Strategy',
                        style: AppTypography.bodySM),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.x4l),
              Text('Welcome Back', style: AppTypography.h3),
              const SizedBox(height: AppSpacing.xs),
              Text('Sign in to your account',
                  style: AppTypography.bodySM),
              const SizedBox(height: AppSpacing.xxl),

              // Error banner
              if (_error != null)
                Container(
                  padding: const EdgeInsets.all(AppSpacing.md),
                  margin: const EdgeInsets.only(bottom: AppSpacing.md),
                  decoration: BoxDecoration(
                    color: AppColors.error.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
                    border: Border.all(color: AppColors.error.withOpacity(0.3)),
                  ),
                  child: Row(children: [
                    const Icon(Icons.error_outline,
                        color: AppColors.error, size: 16),
                    const SizedBox(width: 8),
                    Expanded(child: Text(_error!,
                        style: AppTypography.bodySM
                            .copyWith(color: AppColors.error))),
                  ]),
                ),

              // Email or Username
              TextFormField(
                controller: _emailCtrl,
                style: AppTypography.bodyMD,
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(
                  labelText: 'Email atau Username',
                  prefixIcon: Icon(Icons.person_outline,
                      color: AppColors.textMuted, size: 18),
                ),
                validator: (v) => (v?.trim().isNotEmpty ?? false) ? null : 'Wajib diisi',
              ),
              const SizedBox(height: AppSpacing.md),

              // Password
              TextFormField(
                controller: _passCtrl,
                style: AppTypography.bodyMD,
                obscureText: _obscure,
                decoration: InputDecoration(
                  labelText: 'Password',
                  prefixIcon: const Icon(Icons.lock_outline,
                      color: AppColors.textMuted, size: 18),
                  suffixIcon: GestureDetector(
                    onTap: () => setState(() => _obscure = !_obscure),
                    child: Icon(
                      _obscure ? Icons.visibility_off_outlined
                          : Icons.visibility_outlined,
                      color: AppColors.textMuted, size: 18,
                    ),
                  ),
                ),
                validator: (v) => (v?.length ?? 0) >= 6 ? null : 'Min 6 characters',
                onFieldSubmitted: (_) => _login(),
              ),
              const SizedBox(height: AppSpacing.x3l),

              // Login button
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: _loading ? null : _login,
                  child: _loading
                      ? const SizedBox(width: 20, height: 20,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.black))
                      : const Text('Login'),
                ),
              ),
              const SizedBox(height: AppSpacing.xl),

              // Sign up link
              Center(
                child: GestureDetector(
                  onTap: () => context.go('/auth/signup'),
                  child: RichText(
                    text: TextSpan(
                      text: "Don't have an account? ",
                      style: AppTypography.bodyMD,
                      children: [
                        TextSpan(
                          text: 'Sign Up',
                          style: AppTypography.bodyMD
                              .copyWith(color: AppColors.primary,
                                  fontWeight: FontWeight.w700),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
