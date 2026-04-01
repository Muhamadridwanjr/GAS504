import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/auth_service.dart';

class GASDrawer extends StatelessWidget {
  GASDrawer({super.key});
  final _auth = AuthService();

  @override
  Widget build(BuildContext context) {
    final user = _auth.currentUser;
    final plan  = user?['plan'] as String? ?? 'essential';

    return Drawer(
      backgroundColor: AppColors.bgSecondary,
      child: Column(
        children: [
          // ── Header ──────────────────────────────────────────────────────
          Container(
            width: double.infinity,
            padding: EdgeInsets.only(
              top: MediaQuery.of(context).padding.top + AppSpacing.xl,
              left: AppSpacing.xl,
              right: AppSpacing.xl,
              bottom: AppSpacing.xl,
            ),
            decoration: const BoxDecoration(
              gradient: AppColors.cardGradient,
              border: Border(bottom: BorderSide(color: AppColors.border)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Avatar
                CircleAvatar(
                  radius: 30,
                  backgroundColor: AppColors.bgTertiary,
                  backgroundImage: user?['avatar_url'] != null
                      ? NetworkImage(user!['avatar_url'] as String) : null,
                  child: user?['avatar_url'] == null
                      ? Text(
                          (user?['full_name'] as String? ?? 'G')
                              .substring(0, 1).toUpperCase(),
                          style: AppTypography.h3.copyWith(
                              color: AppColors.textGold),
                        )
                      : null,
                ),
                const SizedBox(height: AppSpacing.md),
                Text(user?['full_name'] as String? ?? 'Trader',
                    style: AppTypography.h4),
                const SizedBox(height: AppSpacing.xs),
                Text(user?['email'] as String? ?? '',
                    style: AppTypography.bodySM),
                const SizedBox(height: AppSpacing.sm),
                // Plan badge
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.sm, vertical: 3),
                  decoration: BoxDecoration(
                    color: _planColor(plan).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                    border: Border.all(color: _planColor(plan), width: 1),
                  ),
                  child: Text(
                    plan.toUpperCase(),
                    style: AppTypography.labelSM
                        .copyWith(color: _planColor(plan)),
                  ),
                ),
              ],
            ),
          ),

          // ── Navigation items ────────────────────────────────────────────
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
              children: [
                _section('MAIN'),
                _tile(context, Icons.dashboard, 'Dashboard',  '/dashboard'),
                _tile(context, Icons.show_chart, 'Markets',   '/markets'),
                _tile(context, Icons.bolt,       'Signal',    '/signal'),
                _tile(context, Icons.event,      'Calendar',  '/calendar'),

                _section('AI FEATURES'),
                _tile(context, Icons.analytics,    'Technical Analysis', '/ai/technical'),
                _tile(context, Icons.link,         'Correlation',        '/ai/correlation'),
                _tile(context, Icons.bar_chart,    'Fundamental',        '/ai/fundamental'),
                _tile(context, Icons.sentiment_satisfied, 'Sentiment',   '/ai/sentiment'),
                _tile(context, Icons.schedule,     'Session',            '/ai/session'),
                _tile(context, Icons.merge_type,   'Hybrid System',      '/ai/hybrid'),
                _tile(context, Icons.auto_awesome, 'Market Briefing',    '/ai/briefing'),
                _tile(context, Icons.psychology,   'Psychology Coach',   '/ai/psychology'),
                _tile(context, Icons.school,       'Mentor Mode',        '/ai/mentor'),
                _tile(context, Icons.business,     'Prop Firm',          '/ai/propfirm'),

                _section('TOOLS'),
                _tile(context, Icons.shield,          'Risk Manager',  '/risk'),
                _tile(context, Icons.trending_down,   'Drawdown',      '/drawdown'),
                _tile(context, Icons.book,            'Journal',       '/journal'),
                _tile(context, Icons.science,         'Backtesting',   '/backtest'),
                _tile(context, Icons.search,          'Scanner',       '/scanner'),
                _tile(context, Icons.notifications,   'Alerts',        '/alerts'),
                _tile(context, Icons.leaderboard,     'Leaderboard',   '/leaderboard'),

                if (_auth.isAdmin) ...[
                  _section('ADMIN'),
                  _tile(context, Icons.admin_panel_settings,
                      'Admin Panel', '/admin',
                      color: AppColors.warning),
                ],
              ],
            ),
          ),

          // ── Logout ──────────────────────────────────────────────────────
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.logout, color: AppColors.error),
            title: Text('Logout',
                style: AppTypography.bodyMD.copyWith(
                    color: AppColors.error)),
            onTap: () async {
              Navigator.pop(context);
              await _auth.logout();
              if (context.mounted) context.go('/auth/login');
            },
          ),
          SizedBox(height: MediaQuery.of(context).padding.bottom + 8),
        ],
      ),
    );
  }

  Widget _section(String label) => Padding(
    padding: const EdgeInsets.fromLTRB(
        AppSpacing.xl, AppSpacing.md, AppSpacing.xl, AppSpacing.xs),
    child: Text(label, style: AppTypography.labelSM),
  );

  Widget _tile(BuildContext context, IconData icon, String label, String path,
      {Color? color}) =>
      ListTile(
        leading: Icon(icon,
            size: 20, color: color ?? AppColors.textSecondary),
        title: Text(label,
            style: AppTypography.bodyMD.copyWith(
                color: color ?? AppColors.textPrimary)),
        dense: true,
        onTap: () {
          Navigator.pop(context);
          context.go(path);
        },
      );

  Color _planColor(String plan) {
    switch (plan) {
      case 'ultimate': return AppColors.planUltimate;
      case 'premium':  return AppColors.planPremium;
      case 'plus':     return AppColors.planPlus;
      default:         return AppColors.planEssential;
    }
  }
}
