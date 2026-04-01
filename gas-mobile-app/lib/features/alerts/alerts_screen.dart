import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_app_bar.dart';

class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});
  @override State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen>
    with SingleTickerProviderStateMixin {
  final _api = ApiService();
  late TabController _tab;
  List<Map<String, dynamic>> _alerts = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _tab = TabController(length: 2, vsync: this);
    _load();
  }

  @override
  void dispose() { _tab.dispose(); super.dispose(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await _api.getAlerts();
      if (mounted) setState(() {
        _alerts  = data.cast<Map<String, dynamic>>();
        _loading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  List<Map<String, dynamic>> get _active =>
      _alerts.where((a) => a['read'] != true).toList();
  List<Map<String, dynamic>> get _history =>
      _alerts.where((a) => a['read'] == true).toList();

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(
      title: 'Alerts',
      actions: [
        TextButton(
          onPressed: () => setState(() {
            for (var a in _alerts) a['read'] = true;
          }),
          child: Text('Mark all read',
              style: AppTypography.bodySM
                  .copyWith(color: AppColors.primary)),
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
          tabs: [
            Tab(text: 'Active (${_active.length})'),
            const Tab(text: 'History'),
          ],
        ),
        const Divider(height: 1),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(
                  color: AppColors.primary))
              : TabBarView(
                  controller: _tab,
                  children: [
                    _alertList(_active, active: true),
                    _alertList(_history, active: false),
                  ],
                ),
        ),
      ],
    ),
  );

  Widget _alertList(List<Map<String, dynamic>> list, {required bool active}) {
    if (list.isEmpty) return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(active ? Icons.notifications_off_outlined
              : Icons.history, size: 48, color: AppColors.textMuted),
          const SizedBox(height: AppSpacing.md),
          Text(active ? 'No active alerts' : 'No alert history',
              style: AppTypography.bodySM),
        ],
      ),
    );
    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: _load,
      child: ListView.builder(
        itemCount: list.length,
        itemBuilder: (_, i) => _alertRow(list[i], active: active),
      ),
    );
  }

  Widget _alertRow(Map<String, dynamic> a, {required bool active}) {
    final type = (a['type'] as String? ?? 'info').toLowerCase();
    final color = type == 'signal' ? AppColors.bullish
        : type == 'warning' ? AppColors.warning
        : type == 'error'   ? AppColors.bearish : AppColors.accent;

    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg, vertical: AppSpacing.md),
      decoration: BoxDecoration(
        color: active ? AppColors.bgSecondary : Colors.transparent,
        border: const Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36, height: 36,
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(_alertIcon(type), size: 18, color: color),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(a['title'] as String? ?? a['message'] as String? ?? '',
                    style: AppTypography.bodyMD
                        .copyWith(color: active
                            ? AppColors.textPrimary : AppColors.textSecondary)),
                if (a['body'] != null) ...[
                  const SizedBox(height: 4),
                  Text(a['body'] as String,
                      style: AppTypography.bodySM,
                      maxLines: 2, overflow: TextOverflow.ellipsis),
                ],
                const SizedBox(height: 4),
                Text(a['time'] as String? ?? '',
                    style: AppTypography.bodyXS),
              ],
            ),
          ),
          if (active)
            GestureDetector(
              onTap: () => setState(() => a['read'] = true),
              child: const Icon(Icons.close,
                  size: 16, color: AppColors.textMuted),
            ),
        ],
      ),
    );
  }

  IconData _alertIcon(String type) {
    switch (type) {
      case 'signal':  return Icons.bolt;
      case 'warning': return Icons.warning_outlined;
      case 'error':   return Icons.error_outline;
      default:        return Icons.notifications_outlined;
    }
  }
}
