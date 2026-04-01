import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});
  @override State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  final _api = ApiService();
  List<Map<String, dynamic>> _events = [];
  bool _loading = true;
  String _filter = 'All';

  static const _filters = ['All', 'High', 'Medium', 'Low', 'USD', 'EUR', 'GBP', 'JPY'];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await _api.getCalendar();
      final events = (data['events'] as List?)?.cast<Map<String, dynamic>>()
          ?? (data is List ? (data as List).cast<Map<String, dynamic>>() : []);
      if (mounted) setState(() { _events = events; _loading = false; });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  List<Map<String, dynamic>> get _filtered {
    if (_filter == 'All') return _events;
    if (['High','Medium','Low'].contains(_filter)) {
      return _events.where((e) =>
          (e['impact'] as String? ?? '').toLowerCase() ==
          _filter.toLowerCase()).toList();
    }
    return _events.where((e) =>
        (e['currency'] as String? ?? '') == _filter).toList();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Economic Calendar', showDrawer: true, showBack: false),
    body: Column(
      children: [
        // Filter chips
        SizedBox(
          height: 48,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md, vertical: 8),
            children: _filters.map((f) {
              final sel = _filter == f;
              return GestureDetector(
                onTap: () => setState(() => _filter = f),
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                  decoration: BoxDecoration(
                    color: sel
                        ? AppColors.primary.withOpacity(0.15)
                        : AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                    border: Border.all(
                        color: sel ? AppColors.primary : AppColors.border),
                  ),
                  child: Text(f,
                      style: AppTypography.labelMD.copyWith(
                          color: sel ? AppColors.primary
                              : AppColors.textSecondary)),
                ),
              );
            }).toList(),
          ),
        ),
        const Divider(height: 1),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(
                  color: AppColors.primary))
              : _filtered.isEmpty
                  ? Center(
                      child: Text('No events scheduled',
                          style: AppTypography.bodySM))
                  : RefreshIndicator(
                      color: AppColors.primary,
                      onRefresh: _load,
                      child: ListView.builder(
                        itemCount: _filtered.length,
                        itemBuilder: (_, i) => _eventRow(_filtered[i]),
                      ),
                    ),
        ),
      ],
    ),
  );

  Widget _eventRow(Map<String, dynamic> e) {
    final impact   = (e['impact'] as String? ?? '').toLowerCase();
    final impColor = impact == 'high' ? AppColors.bearish
        : impact == 'medium' ? AppColors.warning : AppColors.textMuted;
    final currency = e['currency'] as String? ?? '';
    final title    = e['title']    as String? ?? e['name'] as String? ?? '';
    final time     = e['time']     as String? ?? '';
    final forecast = e['forecast'] as String? ?? '—';
    final actual   = e['actual']   as String? ?? '—';
    final prev     = e['previous'] as String? ?? '—';

    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg, vertical: AppSpacing.md),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Impact dot
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Container(
              width: 8, height: 8,
              decoration: BoxDecoration(
                  color: impColor, shape: BoxShape.circle),
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(currency,
                        style: AppTypography.labelMD
                            .copyWith(color: AppColors.accent)),
                    const SizedBox(width: AppSpacing.sm),
                    Text(time, style: AppTypography.bodyXS),
                  ],
                ),
                const SizedBox(height: 4),
                Text(title,
                    style: AppTypography.bodyMD,
                    maxLines: 2, overflow: TextOverflow.ellipsis),
                const SizedBox(height: 6),
                Row(
                  children: [
                    _valChip('F', forecast, AppColors.textMuted),
                    const SizedBox(width: 8),
                    _valChip('A', actual, actual != '—'
                        ? AppColors.bullish : AppColors.textMuted),
                    const SizedBox(width: 8),
                    _valChip('P', prev, AppColors.textMuted),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _valChip(String label, String val, Color color) => Row(
    children: [
      Text('$label:', style: AppTypography.bodyXS),
      const SizedBox(width: 3),
      Text(val, style: AppTypography.priceXS.copyWith(color: color)),
    ],
  );
}
