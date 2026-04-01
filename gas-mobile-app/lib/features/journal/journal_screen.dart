import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class JournalScreen extends StatefulWidget {
  const JournalScreen({super.key});
  @override State<JournalScreen> createState() => _JournalScreenState();
}

class _JournalScreenState extends State<JournalScreen> {
  final _api = ApiService();
  List<Map<String, dynamic>> _entries = [];
  bool _loading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await _api.getJournal();
      if (mounted) setState(() {
        _entries = data.cast<Map<String, dynamic>>();
        _loading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  double get _totalPL => _entries.fold(0, (s, e) =>
      s + ((e['pl'] as num?)?.toDouble() ?? 0));

  int get _winCount => _entries.where((e) =>
      ((e['pl'] as num?)?.toDouble() ?? 0) > 0).length;

  double get _winRate =>
      _entries.isEmpty ? 0 : _winCount / _entries.length * 100;

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(
      title: 'Trading Journal',
      actions: [
        IconButton(
          icon: const Icon(Icons.add, color: AppColors.primary),
          onPressed: () => _showAddSheet(context),
        ),
      ],
    ),
    body: Column(
      children: [
        // Stats header
        Container(
          padding: const EdgeInsets.all(AppSpacing.lg),
          decoration: const BoxDecoration(
            border: Border(bottom: BorderSide(color: AppColors.border)),
          ),
          child: Row(
            children: [
              _stat('Trades', '${_entries.length}', AppColors.textPrimary),
              _stat('Win Rate', '${_winRate.toStringAsFixed(0)}%', AppColors.bullish),
              _stat('Net P/L', '\$${_totalPL.toStringAsFixed(0)}',
                  _totalPL >= 0 ? AppColors.bullish : AppColors.bearish),
            ],
          ),
        ),
        Expanded(
          child: _loading
              ? const Center(child: CircularProgressIndicator(
                  color: AppColors.primary))
              : _entries.isEmpty
                  ? _empty()
                  : RefreshIndicator(
                      color: AppColors.primary,
                      onRefresh: _load,
                      child: ListView.builder(
                        itemCount: _entries.length,
                        itemBuilder: (_, i) => Dismissible(
                          key: Key(_entries[i]['id']?.toString() ?? '$i'),
                          direction: DismissDirection.endToStart,
                          background: Container(
                            alignment: Alignment.centerRight,
                            padding: const EdgeInsets.only(right: 20),
                            color: AppColors.bearish.withOpacity(0.1),
                            child: const Icon(Icons.delete_outline,
                                color: AppColors.bearish),
                          ),
                          onDismissed: (_) async {
                            final id = _entries[i]['id']?.toString() ?? '';
                            setState(() => _entries.removeAt(i));
                            try { await _api.deleteJournalEntry(id); }
                            catch (_) { _load(); }
                          },
                          child: _entryRow(_entries[i]),
                        ),
                      ),
                    ),
        ),
      ],
    ),
    floatingActionButton: FloatingActionButton(
      onPressed: () => _showAddSheet(context),
      backgroundColor: AppColors.primary,
      child: const Icon(Icons.add, color: Colors.black),
    ),
  );

  Widget _stat(String label, String val, Color color) => Expanded(
    child: Column(
      children: [
        Text(val, style: AppTypography.priceMD.copyWith(color: color)),
        const SizedBox(height: 2),
        Text(label, style: AppTypography.labelSM),
      ],
    ),
  );

  Widget _entryRow(Map<String, dynamic> e) {
    final dir  = (e['direction'] as String? ?? '').toLowerCase();
    final pl   = (e['pl'] as num?)?.toDouble() ?? 0;
    final pair = e['pair'] as String? ?? '';
    final note = e['notes'] as String? ?? '';
    final plColor = pl >= 0 ? AppColors.bullish : AppColors.bearish;

    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.lg, vertical: AppSpacing.md),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          Container(
            width: 32, height: 32,
            decoration: BoxDecoration(
              color: (dir == 'buy' ? AppColors.bullish : AppColors.bearish)
                  .withOpacity(0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(
              dir == 'buy' ? Icons.arrow_upward : Icons.arrow_downward,
              size: 16,
              color: dir == 'buy' ? AppColors.bullish : AppColors.bearish,
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(pair, style: AppTypography.priceSM),
                if (note.isNotEmpty)
                  Text(note, style: AppTypography.bodySM,
                      maxLines: 1, overflow: TextOverflow.ellipsis),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('\$${pl.toStringAsFixed(2)}',
                  style: AppTypography.priceSM.copyWith(color: plColor)),
              Text(e['date'] as String? ?? '',
                  style: AppTypography.bodyXS),
            ],
          ),
        ],
      ),
    );
  }

  Widget _empty() => Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(Icons.book_outlined,
            size: 48, color: AppColors.textMuted),
        const SizedBox(height: AppSpacing.md),
        Text('No journal entries yet',
            style: AppTypography.bodySM),
        const SizedBox(height: AppSpacing.sm),
        GASButton(
          label: 'Add First Trade',
          size: GASButtonSize.sm,
          onTap: () => _showAddSheet(context),
        ),
      ],
    ),
  );

  void _showAddSheet(BuildContext context) {
    final pairCtrl  = TextEditingController();
    final entryCtrl = TextEditingController();
    final exitCtrl  = TextEditingController();
    final plCtrl    = TextEditingController();
    final noteCtrl  = TextEditingController();
    String dir = 'buy';
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
            left: AppSpacing.xl,
            right: AppSpacing.xl,
            top: AppSpacing.xl,
          ),
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('New Trade Entry', style: AppTypography.h3),
                const SizedBox(height: AppSpacing.lg),
                TextField(controller: pairCtrl,
                    decoration: const InputDecoration(labelText: 'Pair (e.g. XAUUSD)')),
                const SizedBox(height: AppSpacing.sm),
                Row(
                  children: ['buy', 'sell'].map((d) {
                    final sel = dir == d;
                    final c   = d == 'buy' ? AppColors.bullish : AppColors.bearish;
                    return Expanded(
                      child: GestureDetector(
                        onTap: () => setS(() => dir = d),
                        child: Container(
                          margin: const EdgeInsets.only(right: 8),
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: sel ? c.withOpacity(0.15) : AppColors.bgTertiary,
                            borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
                            border: Border.all(color: sel ? c : AppColors.border),
                          ),
                          child: Text(d.toUpperCase(),
                              style: AppTypography.btnSM.copyWith(
                                  color: sel ? c : AppColors.textSecondary),
                              textAlign: TextAlign.center),
                        ),
                      ),
                    );
                  }).toList(),
                ),
                const SizedBox(height: AppSpacing.sm),
                TextField(controller: entryCtrl,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Entry Price')),
                const SizedBox(height: AppSpacing.sm),
                TextField(controller: exitCtrl,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Exit Price')),
                const SizedBox(height: AppSpacing.sm),
                TextField(controller: plCtrl,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'P/L (USD)')),
                const SizedBox(height: AppSpacing.sm),
                TextField(controller: noteCtrl, maxLines: 2,
                    decoration: const InputDecoration(labelText: 'Notes')),
                const SizedBox(height: AppSpacing.lg),
                GASButton(
                  label: 'Save Entry',
                  expand: true,
                  isLoading: saving,
                  onTap: () async {
                    setS(() => saving = true);
                    try {
                      await _api.createJournalEntry({
                        'pair':      pairCtrl.text,
                        'direction': dir,
                        'entry':     double.tryParse(entryCtrl.text),
                        'exit':      double.tryParse(exitCtrl.text),
                        'pl':        double.tryParse(plCtrl.text) ?? 0,
                        'notes':     noteCtrl.text,
                        'date':      DateTime.now().toIso8601String(),
                      });
                      if (context.mounted) {
                        Navigator.pop(ctx);
                        _load();
                      }
                    } catch (e) {
                      setS(() => saving = false);
                    }
                  },
                ),
                const SizedBox(height: AppSpacing.xl),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
