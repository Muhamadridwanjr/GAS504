import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class SentimentScreen extends StatefulWidget {
  final String pair;
  const SentimentScreen({super.key, this.pair = 'XAUUSD'});
  @override State<SentimentScreen> createState() => _SentimentScreenState();
}

class _SentimentScreenState extends State<SentimentScreen> {
  final _api = ApiService();
  late String _pair;
  bool _loading = false;
  Map<String, dynamic>? _result;
  static const _pairs = ['XAUUSD','EURUSD','GBPUSD','BTCUSD','USDJPY','US30'];

  @override
  void initState() { super.initState(); _pair = widget.pair; }

  Future<void> _run() async {
    setState(() { _loading = true; _result = null; });
    try {
      final r = await _api.callAIFeature('sentiment', {'pair': _pair});
      if (mounted) setState(() { _result = r; _loading = false; });
    } catch (e) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(title: 'Sentiment Analysis'),
    body: ListView(
      padding: const EdgeInsets.all(AppSpacing.pagePadH),
      children: [
        // Pair chips
        SizedBox(
          height: 40,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: _pairs.map((p) {
              final sel = _pair == p;
              return GestureDetector(
                onTap: () => setState(() => _pair = p),
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                  decoration: BoxDecoration(
                    color: sel
                        ? AppColors.primary.withOpacity(0.15)
                        : AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                    border: Border.all(
                        color: sel ? AppColors.primary : AppColors.border),
                  ),
                  child: Text(p, style: AppTypography.labelMD.copyWith(
                      color: sel ? AppColors.primary : AppColors.textSecondary)),
                ),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        GASButton(
          label: 'Analyze Sentiment  •  3 credits',
          icon: Icons.sentiment_satisfied_alt,
          expand: true,
          isLoading: _loading,
          onTap: _run,
        ),
        if (_result != null) ...[
          const SizedBox(height: AppSpacing.xl),
          _gauge(),
          const SizedBox(height: AppSpacing.md),
          _row('News Sentiment',
              (_result!['news_sentiment'] as num?)?.toDouble() ?? 0),
          const SizedBox(height: AppSpacing.sm),
          _row('Social Sentiment',
              (_result!['social_sentiment'] as num?)?.toDouble() ?? 0),
          const SizedBox(height: AppSpacing.sm),
          _row('Institutional Positioning',
              (_result!['institutional'] as num?)?.toDouble() ?? 0),
        ],
        const SizedBox(height: 40),
      ],
    ),
  );

  Widget _gauge() {
    final score = (_result!['overall'] as num?)?.toDouble() ?? 0;
    final clamp = score.clamp(-100.0, 100.0);
    final pct = (clamp + 100) / 200; // 0..1
    final color = score > 20 ? AppColors.bullish
        : score < -20 ? AppColors.bearish : AppColors.warning;

    return GASGoldCard(
      child: Column(
        children: [
          Text('Overall Sentiment', style: AppTypography.h4),
          const SizedBox(height: AppSpacing.lg),
          Stack(
            alignment: Alignment.centerLeft,
            children: [
              Container(
                height: 12,
                decoration: BoxDecoration(
                  color: AppColors.bgTertiary,
                  borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                ),
              ),
              FractionallySizedBox(
                widthFactor: pct,
                child: Container(
                  height: 12,
                  decoration: BoxDecoration(
                    color: color,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Bearish', style: AppTypography.labelSM),
              Text('${score > 0 ? '+' : ''}${score.toStringAsFixed(0)}',
                  style: AppTypography.priceMD.copyWith(color: color)),
              Text('Bullish', style: AppTypography.labelSM),
            ],
          ),
        ],
      ),
    );
  }

  Widget _row(String label, double score) {
    final color = score > 20 ? AppColors.bullish
        : score < -20 ? AppColors.bearish : AppColors.warning;
    final pct = ((score + 100) / 200).clamp(0.0, 1.0);
    return GASCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: AppTypography.bodyMD),
              Text('${score > 0 ? '+' : ''}${score.toStringAsFixed(0)}',
                  style: AppTypography.priceSM.copyWith(color: color)),
            ],
          ),
          const SizedBox(height: AppSpacing.sm),
          ClipRRect(
            borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
            child: LinearProgressIndicator(
              value: pct,
              minHeight: 4,
              backgroundColor: AppColors.bgTertiary,
              valueColor: AlwaysStoppedAnimation(color),
            ),
          ),
        ],
      ),
    );
  }
}
