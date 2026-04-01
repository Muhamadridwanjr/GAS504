import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/constants/app_constants.dart';
import '../../core/services/auth_service.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';
import '../../shared/widgets/confidence_ring.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _auth = AuthService();
  final _api  = ApiService();

  Map<String, dynamic>? _level;
  Map<String, dynamic>? _plan;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final results = await Future.wait([
        _api.getUserLevel(),
        _api.getPlanStatus(),
      ]);
      if (mounted) setState(() {
        _level   = results[0];
        _plan    = results[1];
        _loading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = _auth.currentUser;
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: GASAppBar(
        title: 'Profile',
        showDrawer: true,
        showBack: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit_outlined,
                color: AppColors.textSecondary),
            onPressed: () => _showEditSheet(context),
          ),
        ],
      ),
      body: _loading
          ? const Center(
              child: CircularProgressIndicator(color: AppColors.primary))
          : RefreshIndicator(
              color: AppColors.primary,
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(AppSpacing.pagePadH),
                children: [
                  // ── Avatar + name ──────────────────────────────────────
                  _avatarSection(user),
                  const SizedBox(height: AppSpacing.xl),

                  // ── Level / XP ─────────────────────────────────────────
                  if (_level != null) _levelCard(),
                  const SizedBox(height: AppSpacing.md),

                  // ── Plan & credits ─────────────────────────────────────
                  _planCard(user),
                  const SizedBox(height: AppSpacing.md),

                  // ── Stats ──────────────────────────────────────────────
                  _statsRow(),
                  const SizedBox(height: AppSpacing.md),

                  // ── Settings ───────────────────────────────────────────
                  _settingsSection(context),
                  const SizedBox(height: AppSpacing.xl),

                  // ── Logout ─────────────────────────────────────────────
                  GASButton(
                    label: 'Logout',
                    variant: GASButtonVariant.danger,
                    icon: Icons.logout,
                    expand: true,
                    onTap: () async {
                      await _auth.logout();
                      if (context.mounted) context.go('/auth/login');
                    },
                  ),
                  const SizedBox(height: AppSpacing.x3l),
                ],
              ),
            ),
    );
  }

  Widget _avatarSection(Map<String, dynamic>? user) {
    final name     = user?['full_name'] as String? ?? 'Trader';
    final email    = user?['email']     as String? ?? '';
    final avatar   = user?['avatar_url'] as String?;
    final initials = name.isNotEmpty ? name[0].toUpperCase() : 'G';
    final plan     = user?['plan'] as String? ?? 'essential';

    return Center(
      child: Column(
        children: [
          Stack(
            children: [
              CircleAvatar(
                radius: 48,
                backgroundColor: AppColors.bgTertiary,
                backgroundImage: avatar != null
                    ? NetworkImage(avatar) : null,
                child: avatar == null
                    ? Text(initials, style: AppTypography.h1
                        .copyWith(color: AppColors.textGold))
                    : null,
              ),
              Positioned(
                bottom: 0, right: 0,
                child: GestureDetector(
                  onTap: () => _showEditSheet(context),
                  child: Container(
                    width: 32, height: 32,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      shape: BoxShape.circle,
                      border: Border.all(
                          color: AppColors.bgPrimary, width: 2),
                    ),
                    child: const Icon(Icons.camera_alt,
                        size: 16, color: Colors.black),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          Text(name, style: AppTypography.h3),
          const SizedBox(height: AppSpacing.xs),
          Text(email, style: AppTypography.bodySM),
          const SizedBox(height: AppSpacing.sm),
          _planBadge(plan),
        ],
      ),
    );
  }

  Widget _planBadge(String plan) {
    final color = _planColor(plan);
    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg, vertical: AppSpacing.xs),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
        border: Border.all(color: color, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.workspace_premium, size: 14, color: color),
          const SizedBox(width: AppSpacing.xs),
          Text(plan.toUpperCase(),
              style: AppTypography.labelMD.copyWith(color: color)),
        ],
      ),
    );
  }

  Widget _levelCard() {
    final lvl     = (_level?['level']      as num?)?.toInt() ?? 1;
    final xp      = (_level?['xp']         as num?)?.toInt() ?? 0;
    final nextXp  = (_level?['xp_to_next'] as num?)?.toInt() ?? 100;
    final name    = _level?['level_name']  as String? ?? 'Rookie';
    final prog    = nextXp > 0 ? (xp / nextXp).clamp(0.0, 1.0) : 0.0;

    return GASGoldCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text('Level $lvl', style: AppTypography.h3),
              const SizedBox(width: AppSpacing.sm),
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.sm, vertical: 2),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(
                      AppSpacing.radiusFull),
                ),
                child: Text(name,
                    style: AppTypography.labelMD
                        .copyWith(color: AppColors.textGold)),
              ),
              const Spacer(),
              Text('$xp / $nextXp XP',
                  style: AppTypography.bodySM),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          ClipRRect(
            borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
            child: LinearProgressIndicator(
              value: prog.toDouble(),
              minHeight: 6,
              backgroundColor: AppColors.bgTertiary,
              valueColor: const AlwaysStoppedAnimation(AppColors.primary),
            ),
          ),
        ],
      ),
    );
  }

  Widget _planCard(Map<String, dynamic>? user) {
    final plan    = user?['plan']    as String? ?? 'essential';
    final credits = (user?['credits'] as num?)?.toInt() ?? 0;

    return GASCard(
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Current Plan',
                    style: AppTypography.labelMD),
                const SizedBox(height: AppSpacing.xs),
                Text(plan.toUpperCase(),
                    style: AppTypography.h4
                        .copyWith(color: _planColor(plan))),
              ],
            ),
          ),
          Container(
            width: 1, height: 40,
            color: AppColors.border,
          ),
          const SizedBox(width: AppSpacing.lg),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('Credits', style: AppTypography.labelMD),
              const SizedBox(height: AppSpacing.xs),
              Row(
                children: [
                  const Icon(Icons.bolt,
                      size: 16, color: AppColors.textGold),
                  const SizedBox(width: 4),
                  Text('$credits',
                      style: AppTypography.h4
                          .copyWith(color: AppColors.textGold)),
                ],
              ),
            ],
          ),
          const SizedBox(width: AppSpacing.md),
          GASButton(
            label: 'Upgrade',
            size: GASButtonSize.sm,
            onTap: () {/* TODO: upgrade flow */},
          ),
        ],
      ),
    );
  }

  Widget _statsRow() {
    final user  = _auth.currentUser;
    final level = (_level?['level'] as num?)?.toInt() ?? 1;
    return Row(
      children: [
        _statCard('Level', '$level', Icons.star),
        const SizedBox(width: AppSpacing.sm),
        _statCard('Streak', '7d', Icons.local_fire_department),
        const SizedBox(width: AppSpacing.sm),
        _statCard('Trades', '24', Icons.swap_horiz),
      ],
    );
  }

  Widget _statCard(String label, String value, IconData icon) =>
      Expanded(
        child: GASCard(
          padding: const EdgeInsets.all(AppSpacing.md),
          child: Column(
            children: [
              Icon(icon, color: AppColors.textGold, size: 20),
              const SizedBox(height: AppSpacing.xs),
              Text(value, style: AppTypography.h4),
              const SizedBox(height: 2),
              Text(label, style: AppTypography.labelSM),
            ],
          ),
        ),
      );

  Widget _settingsSection(BuildContext context) => GASCard(
    child: Column(
      children: [
        _settingRow(Icons.notifications_outlined, 'Notifications',
            () {}),
        const Divider(height: 1),
        _settingRow(Icons.security_outlined, 'Security & PIN',
            () {}),
        const Divider(height: 1),
        _settingRow(Icons.help_outline, 'Help & Support', () {}),
        if (_auth.isAdmin) ...[
          const Divider(height: 1),
          _settingRow(Icons.admin_panel_settings,
              'Admin Panel', () => context.go('/admin'),
              color: AppColors.warning),
        ],
      ],
    ),
  );

  Widget _settingRow(IconData icon, String label,
      VoidCallback onTap, {Color? color}) =>
      ListTile(
        leading: Icon(icon,
            color: color ?? AppColors.textSecondary, size: 20),
        title: Text(label,
            style: AppTypography.bodyMD
                .copyWith(color: color ?? AppColors.textPrimary)),
        trailing: const Icon(Icons.chevron_right,
            color: AppColors.textMuted),
        dense: true,
        contentPadding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.sm),
        onTap: onTap,
      );

  void _showEditSheet(BuildContext context) {
    final nameCtrl   = TextEditingController(
        text: _auth.currentUser?['full_name'] as String? ?? '');
    final avatarCtrl = TextEditingController(
        text: _auth.currentUser?['avatar_url'] as String? ?? '');
    bool saving = false;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.bgModal,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
            top: Radius.circular(AppSpacing.radiusXL)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setS) => Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(ctx).viewInsets.bottom,
            left: AppSpacing.xl, right: AppSpacing.xl,
            top: AppSpacing.xl,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Edit Profile', style: AppTypography.h3),
              const SizedBox(height: AppSpacing.xl),
              TextField(
                controller: nameCtrl,
                style: AppTypography.bodyMD,
                decoration: const InputDecoration(
                    labelText: 'Full Name'),
              ),
              const SizedBox(height: AppSpacing.md),
              TextField(
                controller: avatarCtrl,
                style: AppTypography.bodyMD,
                decoration: const InputDecoration(
                    labelText: 'Avatar URL'),
              ),
              const SizedBox(height: AppSpacing.xl),
              GASButton(
                label: 'Save Changes',
                expand: true,
                isLoading: saving,
                onTap: () async {
                  setS(() => saving = true);
                  try {
                    await _auth.updateProfile({
                      'full_name':  nameCtrl.text,
                      'avatar_url': avatarCtrl.text,
                    });
                    if (context.mounted) {
                      Navigator.pop(ctx);
                      setState(() {});
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                            content: Text('Profile updated!')));
                    }
                  } catch (e) {
                    setS(() => saving = false);
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Error: $e')));
                    }
                  }
                },
              ),
              const SizedBox(height: AppSpacing.xl),
            ],
          ),
        ),
      ),
    );
  }

  Color _planColor(String plan) {
    switch (plan) {
      case 'ultimate': return AppColors.planUltimate;
      case 'premium':  return AppColors.planPremium;
      case 'plus':     return AppColors.planPlus;
      default:         return AppColors.planEssential;
    }
  }
}
