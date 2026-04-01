import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../core/services/auth_service.dart';
import '../../shared/widgets/gas_app_bar.dart';

class LeaderboardScreen extends StatefulWidget {
  const LeaderboardScreen({super.key});
  @override State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  final _api  = ApiService();
  final _auth = AuthService();
  List<Map<String, dynamic>> _board = [];
  bool _loading = true;
  String _period = 'weekly';

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await _api.getLeaderboard();
      if (mounted) setState(() {
        _board   = data.cast<Map<String, dynamic>>();
        _loading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Leaderboard', showDrawer: true, showBack: false),
    body: Column(
      children: [
        // Period filter
        Padding(
          padding: const EdgeInsets.all(AppSpacing.lg),
          child: Row(
            children: ['weekly','monthly','alltime'].map((p) {
              final sel = _period == p;
              return Expanded(
                child: GestureDetector(
                  onTap: () { setState(() => _period = p); _load(); },
                  child: Container(
                    margin: const EdgeInsets.only(right: 8),
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: sel ? AppColors.primary.withOpacity(0.15) : AppColors.bgSecondary,
                      borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
                      border: Border.all(color: sel ? AppColors.primary : AppColors.border),
                    ),
                    child: Text(
                      p == 'alltime' ? 'All Time' : p[0].toUpperCase() + p.substring(1),
                      style: AppTypography.labelMD.copyWith(
                          color: sel ? AppColors.primary : AppColors.textSecondary),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
        // Top 3 podium
        if (!_loading && _board.length >= 3)
          _podium(),
        const Divider(height: 1),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(
                  color: AppColors.primary))
              : RefreshIndicator(
                  color: AppColors.primary,
                  onRefresh: _load,
                  child: ListView.builder(
                    itemCount: _board.length > 3 ? _board.length - 3 : 0,
                    itemBuilder: (_, i) => _row(_board[i + 3], i + 4),
                  ),
                ),
        ),
      ],
    ),
  );

  Widget _podium() {
    if (_board.length < 3) return const SizedBox.shrink();
    final first  = _board[0];
    final second = _board[1];
    final third  = _board[2];

    return Padding(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.xl, vertical: AppSpacing.lg),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(child: _podiumCard(second, '2nd', 80,
              AppColors.planEssential)),
          Expanded(child: _podiumCard(first, '1st', 110,
              AppColors.planUltimate, crown: true)),
          Expanded(child: _podiumCard(third, '3rd', 65,
              const Color(0xFFCD7F32))),
        ],
      ),
    );
  }

  Widget _podiumCard(Map<String, dynamic> u, String place,
      double h, Color color, {bool crown = false}) {
    final name   = (u['full_name'] as String? ?? 'Trader').split(' ').first;
    final xp     = (u['xp'] as num?)?.toInt() ?? 0;
    final avatar = u['avatar_url'] as String?;

    return Column(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        if (crown)
          const Icon(Icons.emoji_events,
              color: AppColors.textGold, size: 24),
        const SizedBox(height: 4),
        CircleAvatar(
          radius: crown ? 28 : 22,
          backgroundColor: color.withOpacity(0.2),
          backgroundImage: avatar != null ? NetworkImage(avatar) : null,
          child: avatar == null
              ? Text(name[0].toUpperCase(),
                  style: AppTypography.h4.copyWith(color: color))
              : null,
        ),
        const SizedBox(height: 6),
        Text(name,
            style: AppTypography.labelMD
                .copyWith(color: AppColors.textPrimary),
            maxLines: 1, overflow: TextOverflow.ellipsis,
            textAlign: TextAlign.center),
        Text('$xp XP', style: AppTypography.bodyXS),
        const SizedBox(height: 6),
        Container(
          height: h,
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            borderRadius: const BorderRadius.vertical(
                top: Radius.circular(AppSpacing.radiusMD)),
            border: Border.all(color: color.withOpacity(0.4)),
          ),
          child: Center(
            child: Text(place,
                style: AppTypography.h4.copyWith(color: color)),
          ),
        ),
      ],
    );
  }

  Widget _row(Map<String, dynamic> u, int rank) {
    final name     = u['full_name']  as String? ?? 'Trader';
    final xp       = (u['xp'] as num?)?.toInt() ?? 0;
    final level    = (u['level'] as num?)?.toInt() ?? 1;
    final plan     = u['plan']       as String? ?? 'essential';
    final avatar   = u['avatar_url'] as String?;
    final myId     = _auth.currentUser?['id']?.toString();
    final isMe     = u['id']?.toString() == myId;

    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg, vertical: AppSpacing.md),
      decoration: BoxDecoration(
        color: isMe ? AppColors.primary.withOpacity(0.05) : Colors.transparent,
        border: Border(
          bottom: const BorderSide(color: AppColors.border),
          left: BorderSide(
              color: isMe ? AppColors.primary : Colors.transparent,
              width: 2),
        ),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 28,
            child: Text('$rank',
                style: AppTypography.priceSM
                    .copyWith(color: AppColors.textMuted),
                textAlign: TextAlign.center),
          ),
          const SizedBox(width: AppSpacing.md),
          CircleAvatar(
            radius: 18,
            backgroundColor: AppColors.bgTertiary,
            backgroundImage: avatar != null ? NetworkImage(avatar) : null,
            child: avatar == null
                ? Text(name[0].toUpperCase(),
                    style: AppTypography.labelMD
                        .copyWith(color: AppColors.textGold))
                : null,
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: AppTypography.bodyMD),
                Text('Lv.$level  •  $xp XP',
                    style: AppTypography.bodyXS),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: _planColor(plan).withOpacity(0.1),
              borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
              border: Border.all(color: _planColor(plan).withOpacity(0.3)),
            ),
            child: Text(plan.toUpperCase(),
                style: AppTypography.labelSM
                    .copyWith(color: _planColor(plan))),
          ),
        ],
      ),
    );
  }

  Color _planColor(String p) {
    switch (p) {
      case 'ultimate': return AppColors.planUltimate;
      case 'premium':  return AppColors.planPremium;
      case 'plus':     return AppColors.planPlus;
      default:         return AppColors.planEssential;
    }
  }
}
