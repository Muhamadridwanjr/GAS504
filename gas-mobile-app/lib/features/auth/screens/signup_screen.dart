import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/constants/app_colors.dart';
import '../../../core/constants/app_typography.dart';
import '../../../core/constants/app_spacing.dart';
import '../../../core/services/auth_service.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});
  @override State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _auth          = AuthService();
  final _nameCtrl      = TextEditingController();
  final _usernameCtrl  = TextEditingController();
  final _emailCtrl     = TextEditingController();
  final _passCtrl      = TextEditingController();
  final _confCtrl      = TextEditingController();
  final _otpCtrl       = TextEditingController();
  final List<TextEditingController> _otpDigits =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _otpFocus = List.generate(6, (_) => FocusNode());

  bool _obscure    = true;
  bool _loading    = false;
  bool _otpSending = false;
  String? _error;
  bool _otpSent    = false;   // step: false=form  true=otp
  int  _cooldown   = 0;

  @override
  void dispose() {
    _nameCtrl.dispose(); _usernameCtrl.dispose();
    _emailCtrl.dispose(); _passCtrl.dispose();
    _confCtrl.dispose(); _otpCtrl.dispose();
    for (final c in _otpDigits) c.dispose();
    for (final f in _otpFocus)  f.dispose();
    super.dispose();
  }

  String? _validateForm() {
    if (_usernameCtrl.text.trim().length < 3) return 'Username minimal 3 karakter';
    if (!_emailCtrl.text.contains('@'))       return 'Email tidak valid';
    if (_passCtrl.text.length < 8)            return 'Password minimal 8 karakter';
    if (_passCtrl.text != _confCtrl.text)     return 'Password tidak cocok';
    return null;
  }

  Future<void> _sendOtp() async {
    final err = _validateForm();
    if (err != null) { setState(() => _error = err); return; }
    setState(() { _loading = true; _error = null; });
    try {
      await _auth.sendOtp(
        _emailCtrl.text.trim(),
        _usernameCtrl.text.trim(),
      );
      setState(() { _otpSent = true; _cooldown = 60; });
      _startCooldown();
    } catch (e) {
      setState(() => _error = _parseError(e));
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _resendOtp() async {
    if (_cooldown > 0) return;
    setState(() { _otpSending = true; _error = null; });
    try {
      await _auth.sendOtp(_emailCtrl.text.trim(), _usernameCtrl.text.trim());
      for (final c in _otpDigits) c.clear();
      setState(() { _cooldown = 60; });
      _startCooldown();
    } catch (e) {
      setState(() => _error = _parseError(e));
    } finally {
      setState(() => _otpSending = false);
    }
  }

  void _startCooldown() {
    Future.delayed(const Duration(seconds: 1), () {
      if (!mounted) return;
      setState(() => _cooldown--);
      if (_cooldown > 0) _startCooldown();
    });
  }

  Future<void> _register() async {
    final otp = _otpDigits.map((c) => c.text).join();
    if (otp.length < 6) {
      setState(() => _error = 'Masukkan 6 digit kode OTP');
      return;
    }
    setState(() { _loading = true; _error = null; });
    try {
      await _auth.register(
        username: _usernameCtrl.text.trim(),
        email:    _emailCtrl.text.trim(),
        password: _passCtrl.text,
        otp:      otp,
        fullName: _nameCtrl.text.trim(),
      );
      if (mounted) context.go('/dashboard');
    } catch (e) {
      setState(() { _loading = false; _error = _parseError(e); });
    }
  }

  String _parseError(Object e) {
    final s = e.toString();
    if (s.contains('detail')) {
      final match = RegExp(r'"detail"\s*:\s*"([^"]+)"').firstMatch(s);
      if (match != null) return match.group(1)!;
    }
    return s.replaceAll('Exception: ', '').replaceAll('DioException', 'Koneksi error');
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    body: SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(AppSpacing.xl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: AppSpacing.x3l),
            // Logo
            Center(
              child: Column(
                children: [
                  Container(
                    width: 56, height: 56,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(14),
                    ),
                    child: const Center(
                      child: Text('G', style: TextStyle(
                        color: Colors.black, fontSize: 30, fontWeight: FontWeight.w900,
                      )),
                    ),
                  ),
                  const SizedBox(height: AppSpacing.md),
                  Text(_otpSent ? 'Verifikasi Email' : 'Buat Akun',
                      style: AppTypography.h2),
                  const SizedBox(height: AppSpacing.xs),
                  Text(_otpSent
                      ? 'Kode OTP dikirim ke ${_emailCtrl.text}'
                      : 'Golden AI Strategy',
                      style: AppTypography.bodySM,
                      textAlign: TextAlign.center),
                ],
              ),
            ),
            const SizedBox(height: AppSpacing.x3l),

            // Step indicator
            Row(
              children: [
                _stepDot(1, !_otpSent),
                Expanded(child: Container(height: 1,
                    color: _otpSent ? AppColors.primary : AppColors.border)),
                _stepDot(2, _otpSent),
              ],
            ),
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
                  const Icon(Icons.error_outline, color: AppColors.error, size: 16),
                  const SizedBox(width: 8),
                  Expanded(child: Text(_error!,
                      style: AppTypography.bodySM.copyWith(color: AppColors.error))),
                ]),
              ),

            // ── STEP 1: Form ──────────────────────────────────────────────
            if (!_otpSent) ...[
              TextFormField(
                controller: _nameCtrl,
                style: AppTypography.bodyMD,
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(
                  labelText: 'Nama Lengkap',
                  prefixIcon: Icon(Icons.person_outline,
                      color: AppColors.textMuted, size: 18),
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: _usernameCtrl,
                style: AppTypography.bodyMD,
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(
                  labelText: 'Username *',
                  hintText: 'contoh: johndoe',
                  prefixIcon: Icon(Icons.alternate_email,
                      color: AppColors.textMuted, size: 18),
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: _emailCtrl,
                style: AppTypography.bodyMD,
                keyboardType: TextInputType.emailAddress,
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(
                  labelText: 'Email *',
                  prefixIcon: Icon(Icons.email_outlined,
                      color: AppColors.textMuted, size: 18),
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: _passCtrl,
                style: AppTypography.bodyMD,
                obscureText: _obscure,
                textInputAction: TextInputAction.next,
                decoration: InputDecoration(
                  labelText: 'Password * (min. 8 karakter)',
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
              ),
              const SizedBox(height: AppSpacing.md),
              TextFormField(
                controller: _confCtrl,
                style: AppTypography.bodyMD,
                obscureText: true,
                textInputAction: TextInputAction.done,
                onFieldSubmitted: (_) => _sendOtp(),
                decoration: const InputDecoration(
                  labelText: 'Konfirmasi Password *',
                  prefixIcon: Icon(Icons.lock_outline,
                      color: AppColors.textMuted, size: 18),
                ),
              ),
              const SizedBox(height: AppSpacing.x3l),
              SizedBox(
                width: double.infinity, height: 52,
                child: ElevatedButton(
                  onPressed: _loading ? null : _sendOtp,
                  child: _loading
                      ? const SizedBox(width: 20, height: 20,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.black))
                      : const Text('Kirim Kode OTP ke Email'),
                ),
              ),
            ],

            // ── STEP 2: OTP ───────────────────────────────────────────────
            if (_otpSent) ...[
              // 6-digit boxes
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(6, (i) => Container(
                  width: 44, height: 56,
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  child: TextField(
                    controller: _otpDigits[i],
                    focusNode: _otpFocus[i],
                    textAlign: TextAlign.center,
                    keyboardType: TextInputType.number,
                    maxLength: 1,
                    style: AppTypography.h3.copyWith(color: AppColors.primary),
                    decoration: InputDecoration(
                      counterText: '',
                      contentPadding: EdgeInsets.zero,
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
                        borderSide: BorderSide(
                          color: _otpDigits[i].text.isNotEmpty
                              ? AppColors.primary : AppColors.border,
                          width: 1.5,
                        ),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
                        borderSide: const BorderSide(
                            color: AppColors.primary, width: 2),
                      ),
                    ),
                    onChanged: (val) {
                      if (val.length == 1 && i < 5) {
                        _otpFocus[i + 1].requestFocus();
                      } else if (val.isEmpty && i > 0) {
                        _otpFocus[i - 1].requestFocus();
                      }
                      setState(() {});
                    },
                  ),
                )),
              ),
              const SizedBox(height: AppSpacing.xl),

              SizedBox(
                width: double.infinity, height: 52,
                child: ElevatedButton(
                  onPressed: _loading ? null : _register,
                  child: _loading
                      ? const SizedBox(width: 20, height: 20,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.black))
                      : const Text('Verifikasi & Buat Akun'),
                ),
              ),
              const SizedBox(height: AppSpacing.lg),

              // Resend + back
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  TextButton.icon(
                    onPressed: () => setState(() {
                      _otpSent = false; _error = null;
                      for (final c in _otpDigits) c.clear();
                    }),
                    icon: const Icon(Icons.arrow_back, size: 14),
                    label: const Text('Edit Data'),
                    style: TextButton.styleFrom(
                        foregroundColor: AppColors.textMuted),
                  ),
                  TextButton(
                    onPressed: (_cooldown > 0 || _otpSending) ? null : _resendOtp,
                    style: TextButton.styleFrom(
                        foregroundColor: AppColors.primary),
                    child: _otpSending
                        ? const SizedBox(width: 14, height: 14,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: AppColors.primary))
                        : Text(_cooldown > 0
                            ? 'Kirim ulang (${_cooldown}s)'
                            : 'Kirim ulang OTP'),
                  ),
                ],
              ),
            ],

            const SizedBox(height: AppSpacing.xl),
            Center(
              child: GestureDetector(
                onTap: () => context.go('/auth/login'),
                child: RichText(
                  text: TextSpan(
                    text: 'Sudah punya akun? ',
                    style: AppTypography.bodyMD,
                    children: [
                      TextSpan(
                        text: 'Login',
                        style: AppTypography.bodyMD.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w700),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.xl),
          ],
        ),
      ),
    ),
  );

  Widget _stepDot(int n, bool active) => Container(
    width: 28, height: 28,
    decoration: BoxDecoration(
      shape: BoxShape.circle,
      color: active ? AppColors.primary : AppColors.bgSecondary,
      border: Border.all(
        color: active ? AppColors.primary : AppColors.border,
        width: 1.5,
      ),
    ),
    child: Center(
      child: Text('$n', style: TextStyle(
        fontSize: 11, fontWeight: FontWeight.w900,
        color: active ? Colors.black : AppColors.textMuted,
      )),
    ),
  );
}
