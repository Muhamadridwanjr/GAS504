import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';

class SessionScreen extends StatefulWidget {
  const SessionScreen({super.key});
  @override State<SessionScreen> createState() => _SessionScreenState();
}

class _SessionScreenState extends State<SessionScreen> {
  late final _now = DateTime.now().toUtc();

  String get _currentSession {
    final h = _now.hour;
    final wd = _now.weekday; // 1=Mon, 7=Sun
    if (wd == 6 || wd == 7) return 'Weekend (Closed)';
    if (h >= 22 || h < 7)  return 'Sydney / Tokyo';
    if (h >= 7  && h < 8)  return 'Tokyo / London';
    if (h >= 8  && h < 12) return 'London';
    if (h >= 12 && h < 17) return 'London / New York';
    if (h >= 17 && h < 21) return 'New York';
    return 'NY Close';
  }

  static const _sessions = [
    {'name': 'Sydney',   'start': 22, 'end': 7,  'color': AppColors.sessionSydney, 'pairs': 'AUDUSD, NZDUSD, AUDJPY'},
    {'name': 'Tokyo',    'start': 0,  'end': 9,  'color': AppColors.sessionTokyo,  'pairs': 'USDJPY, EURJPY, GBPJPY'},
    {'name': 'London',   'start': 8,  'end': 17, 'color': AppColors.sessionLondon, 'pairs': 'EURUSD, GBPUSD, EURGBP'},
    {'name': 'New York', 'start': 13, 'end': 22, 'color': AppColors.sessionNewYork,'pairs': 'EURUSD, GBPUSD, USDCAD'},
  ];

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Session Analyzer'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        // Current session highlight
        GASGoldCard(
          child: Column(
            children: [
              Row(
                children: [
                  Container(
                    width: 10, height: 10,
                    decoration: const BoxDecoration(
                      color: AppColors.bullish, shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text('CURRENT SESSION', style: AppTypography.labelMD),
                ],
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(_currentSession,
                  style: AppTypography.h2
                      .copyWith(color: AppColors.textGold)),
              const SizedBox(height: 4),
              Text('${_now.hour.toString().padLeft(2,'0')}:${_now.minute.toString().padLeft(2,'0')} UTC',
                  style: AppTypography.bodySM),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.xl),

        Text('ALL SESSIONS', style: AppTypography.labelMD),
        const SizedBox(height: AppSpacing.sm),

        ..._sessions.map((s) {
          final active = _currentSession.contains(s['name'] as String);
          final color  = s['color'] as Color;
          return Padding(
            padding: const EdgeInsets.only(bottom: AppSpacing.sm),
            child: GASCard(
              borderColor: active ? color : AppColors.border,
              borderWidth: active ? 1.5 : 1,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 8, height: 8,
                        decoration: BoxDecoration(
                          color: active ? color : AppColors.sessionClosed,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(s['name'] as String,
                          style: AppTypography.h4.copyWith(
                              color: active ? color : AppColors.textPrimary)),
                      const Spacer(),
                      Text(
                        '${(s['start'] as int).toString().padLeft(2,'0')}:00 – '
                        '${(s['end'] as int).toString().padLeft(2,'0')}:00 UTC',
                        style: AppTypography.priceXS,
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text('Best pairs: ${s['pairs']}',
                      style: AppTypography.bodySM),
                ],
              ),
            ),
          );
        }),

        const SizedBox(height: AppSpacing.xl),
        Text('OVERLAP ZONES', style: AppTypography.labelMD),
        const SizedBox(height: AppSpacing.sm),
        _overlapCard('Tokyo / London', '08:00 – 09:00 UTC', 'High volatility: EURJPY, GBPJPY'),
        const SizedBox(height: AppSpacing.sm),
        _overlapCard('London / New York', '13:00 – 17:00 UTC', 'Highest liquidity: EURUSD, GBPUSD — Best for trading!',
            highlight: true),
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _overlapCard(String title, String time, String desc, {bool highlight = false}) =>
      GASCard(
        borderColor: highlight ? AppColors.primary.withOpacity(0.4) : AppColors.border,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                if (highlight)
                  const Padding(
                    padding: EdgeInsets.only(right: 6),
                    child: Icon(Icons.star, size: 14, color: AppColors.textGold),
                  ),
                Text(title, style: AppTypography.h4),
                const Spacer(),
                Text(time, style: AppTypography.priceXS),
              ],
            ),
            const SizedBox(height: 4),
            Text(desc, style: AppTypography.bodySM),
          ],
        ),
      );
}
