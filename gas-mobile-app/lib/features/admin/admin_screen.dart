import 'dart:async';
import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../core/services/auth_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';

class AdminScreen extends StatefulWidget {
  const AdminScreen({super.key});
  @override State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen>
    with SingleTickerProviderStateMixin {
  final _api  = ApiService();
  final _auth = AuthService();

  late TabController _tab;
  Map<String, dynamic>? _stats;
  List<Map<String, dynamic>> _users = [];
  bool _loadingStats = true;
  bool _loadingUsers = true;
  int _activeSessions = 0;
  Timer? _sessionTimer;
  final _searchCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tab = TabController(length: 3, vsync: this);
    _loadStats();
    _loadUsers();
    _loadActiveSessions();
    // Refresh active session count every 30s
    _sessionTimer = Timer.periodic(
        const Duration(seconds: 30), (_) => _loadActiveSessions());
  }

  @override
  void dispose() {
    _tab.dispose();
    _sessionTimer?.cancel();
    _searchCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadStats() async {
    try {
      final data = await _api.getAdminStats();
      if (mounted) setState(() { _stats = data; _loadingStats = false; });
    } catch (_) {
      if (mounted) setState(() => _loadingStats = false);
    }
  }

  Future<void> _loadUsers({String? search}) async {
    setState(() => _loadingUsers = true);
    try {
      final data = await _api.getAdminUsers(search: search);
      if (mounted) setState(() {
        _users = data.cast<Map<String, dynamic>>();
        _loadingUsers = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loadingUsers = false);
    }
  }

  Future<void> _loadActiveSessions() async {
    try {
      final data = await _api.getActiveSessionsCount();
      if (mounted) setState(() {
        _activeSessions = (data['active_sessions'] as num?)?.toInt()
            ?? (data['count'] as num?)?.toInt() ?? 0;
      });
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: GASAppBar(
        title: 'Admin Panel',
        subtitle: 'GAS Control Center',
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined,
                color: AppColors.textSecondary),
            onPressed: () {
              _loadStats();
              _loadUsers();
              _loadActiveSessions();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          TabBar(
            controller: _tab,
            indicatorColor: AppColors.primary,
            labelColor: AppColors.primary,
            unselectedLabelColor: AppColors.textMuted,
            labelStyle: AppTypography.btnSM,
            tabs: const [
              Tab(text: 'Overview'),
              Tab(text: 'Users'),
              Tab(text: 'Sessions'),
            ],
          ),
          const Divider(height: 1),
          Expanded(
            child: TabBarView(
              controller: _tab,
              children: [
                _overviewTab(),
                _usersTab(),
                _sessionsTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Overview Tab ─────────────────────────────────────────────────────────
  Widget _overviewTab() {
    if (_loadingStats) {
      return const Center(child: CircularProgressIndicator(
          color: AppColors.primary));
    }
    final s = _stats ?? {};
    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: _loadStats,
      child: ListView(
        padding: const EdgeInsets.all(AppSpacing.pagePadH),
        children: [
          // Active users banner
          GASGoldCard(
            child: Row(
              children: [
                Container(
                  width: 48, height: 48,
                  decoration: BoxDecoration(
                    color: AppColors.bullish.withOpacity(0.15),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.people,
                      color: AppColors.bullish, size: 24),
                ),
                const SizedBox(width: AppSpacing.lg),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Active Sessions (Live)',
                        style: AppTypography.labelMD),
                    const SizedBox(height: 4),
                    Text('$_activeSessions',
                        style: AppTypography.priceXL
                            .copyWith(color: AppColors.bullish)),
                    Text('users currently logged in',
                        style: AppTypography.bodyXS),
                  ],
                ),
                const Spacer(),
                Container(
                  width: 8, height: 8,
                  decoration: const BoxDecoration(
                    color: AppColors.bullish,
                    shape: BoxShape.circle,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // Stats grid
          GridView.count(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: AppSpacing.sm,
            mainAxisSpacing: AppSpacing.sm,
            childAspectRatio: 1.8,
            children: [
              _statCard('Total Users',    _fmt(s['total_users']),    Icons.group, AppColors.accent),
              _statCard('New Today',      _fmt(s['new_today']),      Icons.person_add, AppColors.bullish),
              _statCard('Essential',      _fmt(s['plan_essential']), Icons.star_outline, AppColors.planEssential),
              _statCard('Plus',           _fmt(s['plan_plus']),      Icons.star_half, AppColors.planPlus),
              _statCard('Premium',        _fmt(s['plan_premium']),   Icons.star, AppColors.planPremium),
              _statCard('Ultimate',       _fmt(s['plan_ultimate']),  Icons.workspace_premium, AppColors.planUltimate),
              _statCard('Total Revenue',  '\$${_fmt(s['revenue'])}', Icons.attach_money, AppColors.textGold),
              _statCard('AI Calls Today', _fmt(s['ai_calls_today']), Icons.bolt, AppColors.primary),
            ],
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  // ── Users Tab ─────────────────────────────────────────────────────────────
  Widget _usersTab() => Column(
    children: [
      Padding(
        padding: const EdgeInsets.all(AppSpacing.md),
        child: TextField(
          controller: _searchCtrl,
          style: AppTypography.bodyMD,
          onSubmitted: (v) => _loadUsers(search: v),
          decoration: InputDecoration(
            hintText: 'Search users...',
            prefixIcon: const Icon(Icons.search,
                color: AppColors.textMuted, size: 18),
            suffixIcon: _searchCtrl.text.isNotEmpty
                ? GestureDetector(
                    onTap: () {
                      _searchCtrl.clear();
                      _loadUsers();
                    },
                    child: const Icon(Icons.clear,
                        color: AppColors.textMuted, size: 16),
                  )
                : null,
          ),
        ),
      ),
      Expanded(
        child: _loadingUsers
            ? const Center(child: CircularProgressIndicator(
                color: AppColors.primary))
            : RefreshIndicator(
                color: AppColors.primary,
                onRefresh: () => _loadUsers(),
                child: _users.isEmpty
                    ? Center(child: Text('No users found',
                        style: AppTypography.bodySM))
                    : ListView.builder(
                        itemCount: _users.length,
                        itemBuilder: (_, i) => _userRow(_users[i]),
                      ),
              ),
      ),
    ],
  );

  Widget _userRow(Map<String, dynamic> u) {
    final name    = u['full_name'] as String? ?? 'Trader';
    final email   = u['email']    as String? ?? '';
    final plan    = u['plan']     as String? ?? 'essential';
    final credits = (u['credits'] as num?)?.toInt() ?? 0;
    final avatar  = u['avatar_url'] as String?;
    final online  = u['is_online'] as bool? ?? false;
    final isAdmin = u['is_admin'] as bool? ?? u['role'] == 'admin';

    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg, vertical: AppSpacing.md),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          Stack(
            children: [
              CircleAvatar(
                radius: 20,
                backgroundColor: AppColors.bgTertiary,
                backgroundImage: avatar != null ? NetworkImage(avatar) : null,
                child: avatar == null
                    ? Text(name[0].toUpperCase(),
                        style: AppTypography.labelMD
                            .copyWith(color: AppColors.textGold))
                    : null,
              ),
              if (online) Positioned(
                bottom: 0, right: 0,
                child: Container(
                  width: 10, height: 10,
                  decoration: BoxDecoration(
                    color: AppColors.bullish,
                    shape: BoxShape.circle,
                    border: Border.all(
                        color: AppColors.bgPrimary, width: 1.5),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(name, style: AppTypography.bodyMD),
                    if (isAdmin) ...[
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 1),
                        decoration: BoxDecoration(
                          color: AppColors.warning.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(3),
                        ),
                        child: Text('ADMIN',
                            style: AppTypography.bodyXS
                                .copyWith(color: AppColors.warning)),
                      ),
                    ],
                  ],
                ),
                Text(email, style: AppTypography.bodyXS),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: _planColor(plan).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(plan.toUpperCase(),
                    style: AppTypography.labelSM
                        .copyWith(color: _planColor(plan))),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.bolt,
                      size: 12, color: AppColors.textGold),
                  const SizedBox(width: 2),
                  Text('$credits',
                      style: AppTypography.bodyXS
                          .copyWith(color: AppColors.textGold)),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ── Sessions Tab ──────────────────────────────────────────────────────────
  Widget _sessionsTab() => ListView(
    padding: const EdgeInsets.all(AppSpacing.pagePadH),
    children: [
      GASGoldCard(
        child: Column(
          children: [
            Text('Currently Online', style: AppTypography.h4),
            const SizedBox(height: AppSpacing.md),
            Text(
              '$_activeSessions',
              style: AppTypography.priceXL.copyWith(
                  color: AppColors.bullish),
            ),
            const SizedBox(height: AppSpacing.sm),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 8, height: 8,
                  decoration: const BoxDecoration(
                    color: AppColors.bullish,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                Text('Live  •  refreshes every 30s',
                    style: AppTypography.bodySM),
              ],
            ),
          ],
        ),
      ),
      const SizedBox(height: AppSpacing.xl),
      GASCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Session Statistics',
                style: AppTypography.h4),
            const SizedBox(height: AppSpacing.md),
            _sessionStat('Peak Today',
                _fmt(_stats?['peak_sessions_today']), AppColors.textGold),
            _sessionStat('Avg Session Duration',
                _stats?['avg_session_duration'] as String? ?? '—',
                AppColors.textSecondary),
            _sessionStat('New Logins Today',
                _fmt(_stats?['logins_today']), AppColors.bullish),
            _sessionStat('Failed Logins',
                _fmt(_stats?['failed_logins']), AppColors.bearish),
          ],
        ),
      ),
    ],
  );

  Widget _sessionStat(String label, String val, Color color) => Padding(
    padding: const EdgeInsets.only(bottom: AppSpacing.sm),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: AppTypography.bodyMD),
        Text(val, style: AppTypography.priceSM.copyWith(color: color)),
      ],
    ),
  );

  // ── Helpers ───────────────────────────────────────────────────────────────
  Widget _statCard(String label, String val,
      IconData icon, Color color) => GASCard(
    padding: const EdgeInsets.all(AppSpacing.md),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Icon(icon, color: color, size: 20),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(val, style: AppTypography.priceMD.copyWith(color: color)),
            Text(label, style: AppTypography.labelSM),
          ],
        ),
      ],
    ),
  );

  String _fmt(dynamic v) => v?.toString() ?? '0';

  Color _planColor(String p) {
    switch (p) {
      case 'ultimate': return AppColors.planUltimate;
      case 'premium':  return AppColors.planPremium;
      case 'plus':     return AppColors.planPlus;
      default:         return AppColors.planEssential;
    }
  }
}
