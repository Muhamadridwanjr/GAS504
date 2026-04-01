import 'dart:async';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../core/services/auth_service.dart';
import '../../core/models/signal.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_drawer.dart';
import '../../shared/widgets/signal_card.dart';
import '../../shared/widgets/confidence_ring.dart';
// (theme toggle is in MainShell floating button)

// ── Feature definition used by the AI features grid ──────────────────────────
class _FeatureDef {
  final String key;
  final String label;
  final IconData icon;
  final String plan;
  final int credits;
  final String route;

  const _FeatureDef({
    required this.key,
    required this.label,
    required this.icon,
    required this.plan,
    required this.credits,
    required this.route,
  });
}

const List<_FeatureDef> _dashboardFeatures = [
  // Essential — free
  _FeatureDef(key: 'technical',   label: 'Technical AI',   icon: Icons.analytics_outlined,      plan: 'essential', credits: 0,  route: '/ai/technical'),
  _FeatureDef(key: 'signal',      label: 'Signal',         icon: Icons.bolt_outlined,            plan: 'essential', credits: 0,  route: '/signal'),
  _FeatureDef(key: 'alerts',      label: 'Alerts',         icon: Icons.notifications_outlined,   plan: 'essential', credits: 0,  route: '/alerts'),
  _FeatureDef(key: 'session',     label: 'Session',        icon: Icons.access_time_outlined,     plan: 'essential', credits: 0,  route: '/ai/session'),
  // Plus
  _FeatureDef(key: 'correlation', label: 'Correlation',    icon: Icons.grid_view_outlined,       plan: 'plus',      credits: 3,  route: '/ai/correlation'),
  _FeatureDef(key: 'fundamental', label: 'Fundamental',    icon: Icons.account_balance_outlined, plan: 'plus',      credits: 3,  route: '/ai/fundamental'),
  _FeatureDef(key: 'calendar',    label: 'Calendar',       icon: Icons.event_outlined,           plan: 'plus',      credits: 2,  route: '/calendar'),
  _FeatureDef(key: 'sentiment',   label: 'Sentiment',      icon: Icons.sentiment_satisfied_alt,  plan: 'plus',      credits: 3,  route: '/ai/sentiment'),
  _FeatureDef(key: 'risk',        label: 'Risk Manager',   icon: Icons.shield_outlined,          plan: 'plus',      credits: 3,  route: '/risk'),
  // Premium
  _FeatureDef(key: 'hybrid',      label: 'Hybrid AI',      icon: Icons.merge_type,               plan: 'premium',   credits: 4,  route: '/ai/hybrid'),
  _FeatureDef(key: 'drawdown',    label: 'Drawdown',       icon: Icons.trending_down,            plan: 'premium',   credits: 4,  route: '/drawdown'),
  _FeatureDef(key: 'briefing',    label: 'AI Briefing',    icon: Icons.auto_awesome_outlined,    plan: 'premium',   credits: 5,  route: '/ai/briefing'),
  _FeatureDef(key: 'psychology',  label: 'Psychology',     icon: Icons.psychology_outlined,      plan: 'premium',   credits: 5,  route: '/ai/psychology'),
  _FeatureDef(key: 'journal',     label: 'Journal',        icon: Icons.book_outlined,            plan: 'premium',   credits: 0,  route: '/journal'),
  _FeatureDef(key: 'propfirm',    label: 'Prop Firm',      icon: Icons.workspace_premium_outlined, plan: 'premium', credits: 5,  route: '/ai/propfirm'),
  // Ultimate
  _FeatureDef(key: 'scanner',     label: 'Scanner',        icon: Icons.radar,                    plan: 'ultimate',  credits: 15, route: '/scanner'),
  _FeatureDef(key: 'backtesting', label: 'Backtesting',    icon: Icons.history_outlined,         plan: 'ultimate',  credits: 20, route: '/backtest'),
  _FeatureDef(key: 'mentor',      label: 'AI Mentor',      icon: Icons.school_outlined,          plan: 'ultimate',  credits: 10, route: '/ai/mentor'),
];

// ─────────────────────────────────────────────────────────────────────────────
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  // ── Services ─────────────────────────────────────────────────────────────
  final _api  = ApiService();
  final _auth = AuthService();

  // ── State ────────────────────────────────────────────────────────────────
  bool _loading   = true;
  String? _error;
  Map<String, dynamic> _overview = {};
  late final _clockTimer = Stream.periodic(const Duration(seconds: 1))
      .listen((_) { if (mounted) setState(() {}); });

  // Parsed data
  List<_MarketCard>  _pairs   = [];
  TradingSignal?     _signal;
  List<_NewsItem>    _news    = [];

  // ── Lifecycle ────────────────────────────────────────────────────────────
  @override
  void initState() {
    super.initState();
    _loadOverview();
    _clockTimer; // start clock
  }

  @override
  void dispose() {
    _clockTimer.cancel();
    super.dispose();
  }

  Future<void> _loadOverview() async {
    if (!mounted) return;
    setState(() { _loading = true; _error = null; });

    try {
      final data = await _api.getOverview();
      _parseOverview(data);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _parseOverview(Map<String, dynamic> data) {
    _overview = data;

    // Parse pairs
    final rawPairs = data['pairs'] as List<dynamic>? ?? [];
    _pairs = rawPairs
        .map((p) => _MarketCard.fromJson(p as Map<String, dynamic>))
        .toList();

    // Fallback static pairs when API returns nothing
    if (_pairs.isEmpty) {
      _pairs = _staticPairs();
    }

    // Parse latest signal
    final rawSignal = data['signal'] as Map<String, dynamic>?;
    if (rawSignal != null) {
      try {
        _signal = TradingSignal.fromJson(rawSignal);
      } catch (_) {
        _signal = null;
      }
    }

    // Parse news
    final rawNews = data['news'] as List<dynamic>? ?? [];
    _news = rawNews
        .take(3)
        .map((n) => _NewsItem.fromJson(n as Map<String, dynamic>))
        .toList();
  }

  // ── GMT+7 / WIB helpers ──────────────────────────────────────────────────
  static final _wib = DateTime.now().timeZoneOffset == const Duration(hours: 7)
      ? null                                     // device already WIB
      : const Duration(hours: 7);               // offset to add

  DateTime get _nowWib {
    final utc = DateTime.now().toUtc();
    return utc.add(const Duration(hours: 7));   // always add 7h from UTC
  }

  // ── Greeting ─────────────────────────────────────────────────────────────
  String get _greeting {
    final h = _nowWib.hour;
    if (h < 5)  return 'Selamat malam';
    if (h < 12) return 'Selamat pagi';
    if (h < 17) return 'Selamat siang';
    return 'Selamat sore';
  }

  String get _userName =>
      _auth.currentUser?['full_name'] as String? ??
      _auth.currentUser?['username'] as String? ?? 'Trader';

  String get _wibTime {
    final now = _nowWib;
    final h  = now.hour.toString().padLeft(2, '0');
    final m  = now.minute.toString().padLeft(2, '0');
    final s  = now.second.toString().padLeft(2, '0');
    const days = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
    const months = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];
    final dayName = days[now.weekday % 7];
    final date = '${now.day} ${months[now.month - 1]} ${now.year}';
    return '$h:$m:$s WIB • $dayName, $date';
  }

  // ── Build ─────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: GASLogoAppBar(
        actions: [
          // Credit badge
          if (_overview['credits'] != null)
            Padding(
              padding: const EdgeInsets.only(right: AppSpacing.sm),
              child: _CreditBadge(credits: _overview['credits'] as int),
            ),
          // Notification bell
          IconButton(
            icon: Stack(
              clipBehavior: Clip.none,
              children: [
                const Icon(Icons.notifications_outlined,
                    color: AppColors.textSecondary),
                if ((_overview['unread_alerts'] as int? ?? 0) > 0)
                  Positioned(
                    top: -2, right: -2,
                    child: Container(
                      width: 8, height: 8,
                      decoration: const BoxDecoration(
                        color: AppColors.bearish,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ),
              ],
            ),
            onPressed: () => context.push('/alerts'),
            tooltip: 'Alerts',
          ),
        ],
      ),
      drawer: GASDrawer(),
      body: _loading
          ? _buildSkeleton()
          : _error != null
              ? _buildError()
              : RefreshIndicator(
                  color: AppColors.primary,
                  backgroundColor: AppColors.bgSecondary,
                  onRefresh: _loadOverview,
                  child: _buildBody(),
                ),
    );
  }

  // ── Skeleton loader ───────────────────────────────────────────────────────
  Widget _buildSkeleton() => const Center(
    child: CircularProgressIndicator(
      valueColor: AlwaysStoppedAnimation(AppColors.primary),
    ),
  );

  // ── Error state ───────────────────────────────────────────────────────────
  Widget _buildError() => Center(
    child: Padding(
      padding: const EdgeInsets.all(AppSpacing.xxl),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.wifi_off_rounded,
              color: AppColors.textMuted, size: 48),
          const SizedBox(height: AppSpacing.lg),
          Text('Could not load data',
              style: AppTypography.h4.copyWith(color: AppColors.textSecondary)),
          const SizedBox(height: AppSpacing.sm),
          Text(_error ?? '', style: AppTypography.bodySM,
              textAlign: TextAlign.center),
          const SizedBox(height: AppSpacing.xl),
          ElevatedButton.icon(
            onPressed: _loadOverview,
            icon: const Icon(Icons.refresh, size: 16),
            label: const Text('Retry'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              foregroundColor: Colors.black,
            ),
          ),
        ],
      ),
    ),
  );

  // ── Main body ─────────────────────────────────────────────────────────────
  Widget _buildBody() => ListView(
    padding: EdgeInsets.zero,
    children: [
      // 1. Greeting header
      _buildGreeting(),

      // 2. Market cards horizontal scroll
      _buildMarketCardsSection(),

      // 3. Latest signal
      _buildLatestSignalSection(),

      // 4. AI features grid
      _buildAIFeaturesSection(),

      // 5. Market news
      _buildNewsSection(),

      // Bottom padding for bottom nav bar
      const SizedBox(height: 80),
    ],
  );

  // ── Section 1: Greeting ───────────────────────────────────────────────────
  Widget _buildGreeting() {
    final plan = _auth.currentUser?['plan'] as String? ?? 'essential';
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.fromLTRB(
          AppSpacing.lg, AppSpacing.xl, AppSpacing.lg, AppSpacing.lg),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark
              ? [const Color(0xFF0F0F20), AppColors.bgPrimary]
              : [const Color(0xFFF0F0F8), const Color(0xFFF4F4F9)],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('$_greeting,', style: AppTypography.bodySM),
                const SizedBox(height: 2),
                Text(
                  _userName,
                  style: AppTypography.h2.copyWith(color: AppColors.textGold),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: AppSpacing.sm),
                Row(
                  children: [
                    const Icon(Icons.location_on_outlined,
                        size: 12, color: AppColors.textMuted),
                    const SizedBox(width: 4),
                    Flexible(
                      child: Text(_wibTime,
                        style: AppTypography.bodyXS,
                        overflow: TextOverflow.ellipsis),
                    ),
                    const SizedBox(width: AppSpacing.md),
                    _PlanBadge(plan: plan),
                  ],
                ),
              ],
            ),
          ),
          // Level circle
          if (_overview['level'] != null)
            _LevelCircle(level: _overview['level'] as int? ?? 1),
        ],
      ),
    );
  }

  // ── Section 2: Market cards ───────────────────────────────────────────────
  Widget _buildMarketCardsSection() => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      _sectionHeader('Markets', onTap: () => context.go('/markets')),
      SizedBox(
        height: 100,
        child: ListView.separated(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
          itemCount: _pairs.length,
          separatorBuilder: (_, __) => const SizedBox(width: AppSpacing.sm),
          itemBuilder: (_, i) => _MarketCardWidget(card: _pairs[i]),
        ),
      ),
      const SizedBox(height: AppSpacing.lg),
    ],
  );

  // ── Section 3: Latest signal ──────────────────────────────────────────────
  Widget _buildLatestSignalSection() => Padding(
    padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionHeader('Latest Signal', onTap: () => context.go('/signal')),
        const SizedBox(height: AppSpacing.sm),
        if (_signal != null)
          SignalCard(
            signal: _signal!,
            compact: true,
            onTap: () => context.push('/signal'),
          )
        else
          _EmptySignalCard(),
        const SizedBox(height: AppSpacing.xl),
      ],
    ),
  );

  // ── Section 4: AI features grid ───────────────────────────────────────────
  Widget _buildAIFeaturesSection() => Padding(
    padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionHeader('AI Features (18)', onTap: null),
        const SizedBox(height: AppSpacing.sm),
        _buildFeatureGroup('ESSENTIAL', AppColors.planEssential,
            _dashboardFeatures.where((f) => f.plan == 'essential').toList()),
        const SizedBox(height: AppSpacing.sm),
        _buildFeatureGroup('PLUS', AppColors.planPlus,
            _dashboardFeatures.where((f) => f.plan == 'plus').toList()),
        const SizedBox(height: AppSpacing.sm),
        _buildFeatureGroup('PREMIUM', AppColors.planPremium,
            _dashboardFeatures.where((f) => f.plan == 'premium').toList()),
        const SizedBox(height: AppSpacing.sm),
        _buildFeatureGroup('ULTIMATE', AppColors.planUltimate,
            _dashboardFeatures.where((f) => f.plan == 'ultimate').toList()),
        const SizedBox(height: AppSpacing.xl),
      ],
    ),
  );

  Widget _buildFeatureGroup(String label, Color color, List<_FeatureDef> features) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Category label
        Row(children: [
          Container(width: 3, height: 14,
              decoration: BoxDecoration(color: color,
                  borderRadius: BorderRadius.circular(2))),
          const SizedBox(width: 6),
          Text(label, style: AppTypography.labelSM.copyWith(color: color, fontSize: 10)),
          const SizedBox(width: 8),
          Expanded(child: Divider(height: 1, color: color.withOpacity(0.2))),
        ]),
        const SizedBox(height: 8),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            crossAxisSpacing: AppSpacing.xs,
            mainAxisSpacing: AppSpacing.xs,
            childAspectRatio: 1.15,
          ),
          itemCount: features.length,
          itemBuilder: (_, i) => _AIFeatureCard(
            feature: features[i],
            onTap: () => context.push(features[i].route),
          ),
        ),
      ],
    );
  }

  // ── Section 5: News ───────────────────────────────────────────────────────
  Widget _buildNewsSection() => Padding(
    padding: const EdgeInsets.symmetric(horizontal: AppSpacing.lg),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionHeader('Market News', onTap: () => context.go('/calendar')),
        const SizedBox(height: AppSpacing.sm),
        if (_news.isEmpty)
          GASCard(
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(AppSpacing.xl),
                child: Text('No news available',
                    style: AppTypography.bodySM),
              ),
            ),
          )
        else
          ...List.generate(_news.length, (i) => Padding(
            padding: EdgeInsets.only(
                bottom: i < _news.length - 1 ? AppSpacing.sm : 0),
            child: _NewsCard(item: _news[i]),
          )),
        const SizedBox(height: AppSpacing.lg),
      ],
    ),
  );

  // ── Section header helper ─────────────────────────────────────────────────
  Widget _sectionHeader(String title, {VoidCallback? onTap}) => Padding(
    padding: const EdgeInsets.fromLTRB(0, 0, 0, AppSpacing.xs),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(title, style: AppTypography.h4),
        if (onTap != null)
          GestureDetector(
            onTap: onTap,
            child: Text('See all',
                style: AppTypography.bodySM.copyWith(
                    color: AppColors.primary)),
          ),
      ],
    ),
  );

  // ── Static fallback pairs ─────────────────────────────────────────────────
  List<_MarketCard> _staticPairs() => const [
    _MarketCard(symbol: 'XAUUSD', name: 'Gold',        price: 2314.50, changePct: 0.42),
    _MarketCard(symbol: 'EURUSD', name: 'Euro/Dollar',  price: 1.08230, changePct: -0.15),
    _MarketCard(symbol: 'BTCUSD', name: 'Bitcoin',      price: 67200.0, changePct: 1.82),
    _MarketCard(symbol: 'US30',   name: 'Dow Jones',    price: 38450.0, changePct: 0.28),
  ];
}

// ─────────────────────────────────────────────────────────────────────────────
// Data models (lightweight, dashboard-specific)
// ─────────────────────────────────────────────────────────────────────────────

class _MarketCard {
  final String symbol;
  final String name;
  final double price;
  final double changePct;

  const _MarketCard({
    required this.symbol,
    required this.name,
    required this.price,
    required this.changePct,
  });

  factory _MarketCard.fromJson(Map<String, dynamic> j) => _MarketCard(
    symbol:    j['symbol']     as String? ?? '',
    name:      j['name']       as String? ?? '',
    price:     (j['price']     as num?)?.toDouble() ?? 0,
    changePct: (j['change_pct'] as num?)?.toDouble() ?? 0,
  );

  bool get isUp => changePct >= 0;

  String get formattedPrice {
    if (symbol == 'BTCUSD' || symbol == 'US30' || symbol == 'US500')
      return price.toStringAsFixed(2);
    if (symbol == 'XAUUSD') return price.toStringAsFixed(2);
    return price.toStringAsFixed(5);
  }

  String get formattedChange {
    final sign = isUp ? '+' : '';
    return '$sign${changePct.toStringAsFixed(2)}%';
  }
}

class _NewsItem {
  final String title;
  final String? source;
  final String? impact;
  final DateTime? time;

  const _NewsItem({
    required this.title,
    this.source,
    this.impact,
    this.time,
  });

  factory _NewsItem.fromJson(Map<String, dynamic> j) => _NewsItem(
    title:  j['title']  as String? ?? '',
    source: j['source'] as String?,
    impact: j['impact'] as String?,
    time: j['time'] != null
        ? DateTime.tryParse(j['time'] as String)
        : null,
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-widgets
// ─────────────────────────────────────────────────────────────────────────────

class _MarketCardWidget extends StatelessWidget {
  final _MarketCard card;
  const _MarketCardWidget({required this.card});

  @override
  Widget build(BuildContext context) {
    final dirColor = card.isUp ? AppColors.bullish : AppColors.bearish;

    return GASCard(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md, vertical: AppSpacing.sm),
      backgroundColor: AppColors.bgSecondary,
      borderColor: dirColor.withOpacity(0.2),
      onTap: () => context.push('/markets/chart/${card.symbol}'),
      child: SizedBox(
        width: 130,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Symbol row
            Row(
              children: [
                Text(card.symbol,
                    style: AppTypography.priceSM.copyWith(
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.w700)),
                const Spacer(),
                Icon(
                  card.isUp
                      ? Icons.trending_up_rounded
                      : Icons.trending_down_rounded,
                  size: 14,
                  color: dirColor,
                ),
              ],
            ),
            const SizedBox(height: 2),
            Text(card.name,
                style: AppTypography.bodyXS,
                maxLines: 1,
                overflow: TextOverflow.ellipsis),
            const Spacer(),
            // Price
            Text(card.formattedPrice,
                style: AppTypography.priceSM.copyWith(
                    color: AppColors.textPrimary, fontSize: 13)),
            const SizedBox(height: 2),
            // Change %
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.xs, vertical: 2),
              decoration: BoxDecoration(
                color: dirColor.withOpacity(0.12),
                borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
              ),
              child: Text(card.formattedChange,
                  style: AppTypography.priceXS.copyWith(
                      color: dirColor, fontWeight: FontWeight.w600)),
            ),
          ],
        ),
      ),
    );
  }
}

// ── AI Feature card (3-column compact square) ─────────────────────────────────
class _AIFeatureCard extends StatelessWidget {
  final _FeatureDef feature;
  final VoidCallback onTap;
  const _AIFeatureCard({required this.feature, required this.onTap});

  Color get _planColor {
    switch (feature.plan) {
      case 'ultimate': return AppColors.planUltimate;
      case 'premium':  return AppColors.planPremium;
      case 'plus':     return AppColors.planPlus;
      default:         return AppColors.planEssential;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardBg = isDark ? AppColors.bgSecondary : Colors.white;
    final textColor = isDark ? AppColors.textPrimary : const Color(0xFF1A1A2E);
    return GASCard(
      padding: const EdgeInsets.all(AppSpacing.sm),
      backgroundColor: cardBg,
      borderColor: _planColor.withOpacity(0.2),
      onTap: onTap,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Icon circle
          Container(
            width: 38, height: 38,
            decoration: BoxDecoration(
              color: _planColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
            ),
            child: Icon(feature.icon, size: 20, color: _planColor),
          ),
          const SizedBox(height: 6),
          Text(feature.label,
              style: TextStyle(
                fontFamily: 'Roboto',
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: textColor,
              ),
              maxLines: 2,
              textAlign: TextAlign.center,
              overflow: TextOverflow.ellipsis),
          if (feature.credits > 0) ...[
            const SizedBox(height: 2),
            Text('${feature.credits}cr',
                style: TextStyle(
                  fontFamily: 'Roboto',
                  fontSize: 9,
                  color: AppColors.textGold.withOpacity(0.9),
                  fontWeight: FontWeight.w600,
                )),
          ],
        ],
      ),
    );
  }
}

// ── News card ─────────────────────────────────────────────────────────────────
class _NewsCard extends StatelessWidget {
  final _NewsItem item;
  const _NewsCard({required this.item});

  Color get _impactColor {
    switch ((item.impact ?? '').toLowerCase()) {
      case 'high':   return AppColors.bearish;
      case 'medium': return AppColors.warning;
      case 'low':    return AppColors.bullish;
      default:       return AppColors.textMuted;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GASCard(
      padding: const EdgeInsets.all(AppSpacing.md),
      backgroundColor: AppColors.bgSecondary,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Impact dot
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Container(
              width: 6, height: 6,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _impactColor,
              ),
            ),
          ),
          const SizedBox(width: AppSpacing.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.title,
                    style: AppTypography.bodySM.copyWith(
                        color: AppColors.textPrimary),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis),
                const SizedBox(height: 4),
                Row(
                  children: [
                    if (item.source != null)
                      Text(item.source!,
                          style: AppTypography.bodyXS),
                    if (item.source != null && item.time != null)
                      Text(' · ', style: AppTypography.bodyXS),
                    if (item.time != null)
                      Text(_formatTime(item.time!),
                          style: AppTypography.bodyXS),
                  ],
                ),
              ],
            ),
          ),
          // Impact chip
          if (item.impact != null && item.impact!.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(left: AppSpacing.sm),
              child: Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.xs, vertical: 2),
                decoration: BoxDecoration(
                  color: _impactColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
                ),
                child: Text(item.impact!.toUpperCase(),
                    style: AppTypography.labelSM
                        .copyWith(color: _impactColor, fontSize: 9)),
              ),
            ),
        ],
      ),
    );
  }

  String _formatTime(DateTime dt) {
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 1)  return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24)   return '${diff.inHours}h ago';
    return '${diff.inDays}d ago';
  }
}

// ── Empty signal placeholder ──────────────────────────────────────────────────
class _EmptySignalCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) => GASCard(
    child: Row(
      children: [
        const Icon(Icons.bolt_outlined,
            color: AppColors.textMuted, size: 24),
        const SizedBox(width: AppSpacing.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('No active signal',
                  style: AppTypography.bodyMD.copyWith(
                      color: AppColors.textSecondary)),
              Text('Pull down to refresh or check back later',
                  style: AppTypography.bodySM),
            ],
          ),
        ),
        const ConfidenceRing(value: 0, size: 36),
      ],
    ),
  );
}

// ── Plan badge ────────────────────────────────────────────────────────────────
class _PlanBadge extends StatelessWidget {
  final String plan;
  const _PlanBadge({required this.plan});

  Color get _color {
    switch (plan) {
      case 'ultimate': return AppColors.planUltimate;
      case 'premium':  return AppColors.planPremium;
      case 'plus':     return AppColors.planPlus;
      default:         return AppColors.planEssential;
    }
  }

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
    decoration: BoxDecoration(
      color: _color.withOpacity(0.15),
      borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
      border: Border.all(color: _color.withOpacity(0.5), width: 0.5),
    ),
    child: Text(plan.toUpperCase(),
        style: AppTypography.labelSM.copyWith(color: _color, fontSize: 9)),
  );
}

// ── Credit badge ──────────────────────────────────────────────────────────────
class _CreditBadge extends StatelessWidget {
  final int credits;
  const _CreditBadge({required this.credits});

  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.sm, vertical: AppSpacing.xs),
    decoration: BoxDecoration(
      color: AppColors.primary.withOpacity(0.12),
      borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
      border: Border.all(
          color: AppColors.primary.withOpacity(0.3), width: 0.5),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(Icons.monetization_on_outlined,
            size: 12, color: AppColors.primary),
        const SizedBox(width: 3),
        Text('$credits',
            style: AppTypography.labelMD.copyWith(
                color: AppColors.primary)),
      ],
    ),
  );
}

// ── Level circle ──────────────────────────────────────────────────────────────
class _LevelCircle extends StatelessWidget {
  final int level;
  const _LevelCircle({required this.level});

  @override
  Widget build(BuildContext context) => Container(
    width: 44, height: 44,
    decoration: BoxDecoration(
      shape: BoxShape.circle,
      gradient: AppColors.goldGradient,
      boxShadow: [
        BoxShadow(
          color: AppColors.primary.withOpacity(0.3),
          blurRadius: 8, spreadRadius: 1,
        ),
      ],
    ),
    child: Center(
      child: Text('$level',
          style: AppTypography.h4.copyWith(
              color: Colors.black, fontWeight: FontWeight.w900)),
    ),
  );
}
