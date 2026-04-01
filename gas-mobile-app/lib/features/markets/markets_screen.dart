import 'dart:async';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/price_tile.dart';
import '../../core/models/market_pair.dart';

class MarketsScreen extends StatefulWidget {
  const MarketsScreen({super.key});
  @override State<MarketsScreen> createState() => _MarketsScreenState();
}

class _MarketsScreenState extends State<MarketsScreen>
    with SingleTickerProviderStateMixin {
  final _api = ApiService();
  late TabController _tab;
  List<MarketPair> _pairs = [];
  bool _loading = true;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _tab = TabController(length: 4, vsync: this);
    _load();
    _timer = Timer.periodic(const Duration(seconds: 5), (_) => _load());
  }

  @override
  void dispose() {
    _tab.dispose();
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final data = await _api.getOverview();
      final raw  = (data['pairs'] as List?)?.cast<Map<String, dynamic>>() ?? [];
      if (mounted) setState(() {
        _pairs   = raw.map(MarketPair.fromJson).toList();
        _loading = false;
      });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  List<MarketPair> _filtered(String type) =>
      _pairs.where((p) => p.type == type).toList();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: GASAppBar(
        title: 'Markets',
        showDrawer: true,
        showBack: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_outlined,
                color: AppColors.textSecondary, size: 20),
            onPressed: _load,
          ),
        ],
      ),
      body: Column(
        children: [
          // TabBar
          Container(
            color: AppColors.bgPrimary,
            child: TabBar(
              controller: _tab,
              indicatorColor: AppColors.primary,
              indicatorWeight: 2,
              labelStyle: AppTypography.btnSM,
              labelColor: AppColors.primary,
              unselectedLabelColor: AppColors.textMuted,
              tabs: const [
                Tab(text: 'Forex'),
                Tab(text: 'Crypto'),
                Tab(text: 'Indices'),
                Tab(text: 'IDX'),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator(
                    color: AppColors.primary))
                : TabBarView(
                    controller: _tab,
                    children: [
                      _pairList('Forex'),
                      _pairList('Crypto'),
                      _pairList('Index'),
                      _idxTab(),
                    ],
                  ),
          ),
        ],
      ),
    );
  }

  Widget _pairList(String type) {
    final list = _filtered(type);
    if (list.isEmpty) return _empty('No $type pairs available');
    return RefreshIndicator(
      color: AppColors.primary,
      onRefresh: _load,
      child: ListView.builder(
        itemCount: list.length,
        itemBuilder: (_, i) => PriceTile(
          pair: list[i],
          onTap: () =>
              context.go('/markets/chart/${list[i].symbol}'),
          showSpread: true,
        ),
      ),
    );
  }

  Widget _idxTab() => Center(
    child: Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(Icons.show_chart,
            color: AppColors.textMuted, size: 48),
        const SizedBox(height: AppSpacing.md),
        Text('IDX Stocks',
            style: AppTypography.h4),
        const SizedBox(height: AppSpacing.sm),
        Text('Coming via web terminal',
            style: AppTypography.bodySM),
      ],
    ),
  );

  Widget _empty(String msg) => Center(
    child: Text(msg, style: AppTypography.bodySM),
  );
}
