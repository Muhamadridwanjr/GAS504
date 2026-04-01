import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_card.dart';
import '../../shared/widgets/gas_app_bar.dart';
import '../../shared/widgets/gas_button.dart';

class RiskCalcResult {
  final double positionSizeLots;
  final double riskAmount;
  final double pipValue;
  final double? riskReward;
  final String pair;
  final double accountBalance;
  final double riskPercent;
  final double entryPrice;
  final double slPrice;
  final double? tpPrice;
  final DateTime createdAt;

  RiskCalcResult({
    required this.positionSizeLots,
    required this.riskAmount,
    required this.pipValue,
    this.riskReward,
    required this.pair,
    required this.accountBalance,
    required this.riskPercent,
    required this.entryPrice,
    required this.slPrice,
    this.tpPrice,
    required this.createdAt,
  });
}

class RiskScreen extends StatefulWidget {
  const RiskScreen({super.key});

  @override
  State<RiskScreen> createState() => _RiskScreenState();
}

class _RiskScreenState extends State<RiskScreen> {
  final _balanceCtrl = TextEditingController(text: '10000');
  final _entryCtrl   = TextEditingController();
  final _slCtrl      = TextEditingController();
  final _tpCtrl      = TextEditingController();

  double _riskPercent = 1.0;
  String _selectedPair = 'EURUSD';
  RiskCalcResult? _result;
  final List<RiskCalcResult> _history = [];

  static const _pairs = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF',
    'AUDUSD', 'USDCAD', 'NZDUSD', 'XAUUSD',
    'BTCUSDT', 'ETHUSDT',
  ];

  // Pip size per pair
  static const Map<String, double> _pipSizes = {
    'EURUSD': 0.0001, 'GBPUSD': 0.0001, 'USDJPY': 0.01,
    'USDCHF': 0.0001, 'AUDUSD': 0.0001, 'USDCAD': 0.0001,
    'NZDUSD': 0.0001, 'XAUUSD': 0.01,  'BTCUSDT': 1.0,
    'ETHUSDT': 0.01,
  };

  // Pip value in USD per standard lot
  static const Map<String, double> _pipValues = {
    'EURUSD': 10.0, 'GBPUSD': 10.0, 'USDJPY': 9.09,
    'USDCHF': 10.0, 'AUDUSD': 10.0, 'USDCAD': 7.69,
    'NZDUSD': 10.0, 'XAUUSD': 10.0, 'BTCUSDT': 1.0,
    'ETHUSDT': 1.0,
  };

  void _calculate() {
    final balance = double.tryParse(_balanceCtrl.text.replaceAll(',', ''));
    final entry   = double.tryParse(_entryCtrl.text);
    final sl      = double.tryParse(_slCtrl.text);
    final tp      = double.tryParse(_tpCtrl.text);

    if (balance == null || entry == null || sl == null) {
      _showError('Please fill in Account Balance, Entry Price and SL Price.');
      return;
    }
    if (sl == entry) {
      _showError('Stop Loss cannot equal Entry Price.');
      return;
    }

    final pipSize  = _pipSizes[_selectedPair] ?? 0.0001;
    final pipVal   = _pipValues[_selectedPair] ?? 10.0;

    final slPips   = ((entry - sl).abs() / pipSize);
    final riskAmt  = balance * (_riskPercent / 100);
    final lots     = slPips > 0 ? (riskAmt / (slPips * pipVal)) : 0.0;
    final pipValue = lots * pipVal;

    double? rr;
    if (tp != null) {
      final tpPips = (tp - entry).abs() / pipSize;
      rr = slPips > 0 ? tpPips / slPips : null;
    }

    final calc = RiskCalcResult(
      positionSizeLots: lots,
      riskAmount: riskAmt,
      pipValue: pipValue,
      riskReward: rr,
      pair: _selectedPair,
      accountBalance: balance,
      riskPercent: _riskPercent,
      entryPrice: entry,
      slPrice: sl,
      tpPrice: tp,
      createdAt: DateTime.now(),
    );

    setState(() {
      _result = calc;
      _history.insert(0, calc);
      if (_history.length > 20) _history.removeLast();
    });
  }

  void _showError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg, style: AppTypography.bodySM),
        backgroundColor: AppColors.error,
      ),
    );
  }

  @override
  void dispose() {
    _balanceCtrl.dispose();
    _entryCtrl.dispose();
    _slCtrl.dispose();
    _tpCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      appBar: const GASAppBar(title: 'Risk Manager'),
      body: ListView(
        padding: const EdgeInsets.all(AppSpacing.pagePadH),
        children: [
          _buildInputSection(),
          const SizedBox(height: AppSpacing.lg),
          if (_result != null) ...[
            _buildResultSection(_result!),
            const SizedBox(height: AppSpacing.lg),
          ],
          if (_history.isNotEmpty) _buildHistory(),
        ],
      ),
    );
  }

  Widget _buildInputSection() {
    return GASCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Position Calculator', style: AppTypography.h3),
          const SizedBox(height: AppSpacing.lg),

          // Pair selector
          Text('Currency Pair', style: AppTypography.labelLG),
          const SizedBox(height: AppSpacing.sm),
          _buildDropdown(),
          const SizedBox(height: AppSpacing.lg),

          // Account balance
          _buildTextField(
            controller: _balanceCtrl,
            label: 'Account Balance (USD)',
            hint: '10000',
            prefix: '\$',
          ),
          const SizedBox(height: AppSpacing.lg),

          // Risk percent slider
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Risk per Trade', style: AppTypography.labelLG),
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: AppSpacing.md, vertical: AppSpacing.xs),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                  border: Border.all(color: AppColors.primary.withOpacity(0.3)),
                ),
                child: Text(
                  '${_riskPercent.toStringAsFixed(1)}%',
                  style: AppTypography.bodyMD.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: AppColors.primary,
              inactiveTrackColor: AppColors.border,
              thumbColor: AppColors.primary,
              overlayColor: AppColors.primary.withOpacity(0.15),
              trackHeight: 3,
            ),
            child: Slider(
              value: _riskPercent,
              min: 0.5,
              max: 5.0,
              divisions: 45,
              onChanged: (v) => setState(() => _riskPercent = v),
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('0.5%', style: AppTypography.bodyXS),
              Text('5.0%', style: AppTypography.bodyXS),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),

          // Entry + SL row
          Row(
            children: [
              Expanded(child: _buildTextField(
                controller: _entryCtrl,
                label: 'Entry Price',
                hint: '1.09500',
              )),
              const SizedBox(width: AppSpacing.md),
              Expanded(child: _buildTextField(
                controller: _slCtrl,
                label: 'Stop Loss',
                hint: '1.09200',
              )),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),

          // TP (optional)
          _buildTextField(
            controller: _tpCtrl,
            label: 'Take Profit (optional)',
            hint: '1.10200',
          ),
          const SizedBox(height: AppSpacing.xl),

          GASButton(
            label: 'Calculate',
            icon: Icons.calculate_outlined,
            onTap: _calculate,
            expand: true,
            size: GASButtonSize.lg,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown() {
    return Container(
      padding: const EdgeInsets.symmetric(
          horizontal: AppSpacing.md, vertical: AppSpacing.xs),
      decoration: BoxDecoration(
        color: AppColors.bgTertiary,
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        border: Border.all(color: AppColors.border),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: _selectedPair,
          dropdownColor: AppColors.bgSecondary,
          isExpanded: true,
          style: AppTypography.bodyMD,
          icon: const Icon(Icons.expand_more, color: AppColors.textSecondary),
          items: _pairs.map((p) => DropdownMenuItem(
            value: p,
            child: Text(p, style: AppTypography.bodyMD),
          )).toList(),
          onChanged: (v) => setState(() => _selectedPair = v!),
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required String hint,
    String? prefix,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTypography.labelLG),
        const SizedBox(height: AppSpacing.xs),
        TextField(
          controller: controller,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          style: AppTypography.bodyMD,
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: AppTypography.bodyMD.copyWith(color: AppColors.textMuted),
            prefixText: prefix,
            prefixStyle: AppTypography.bodyMD.copyWith(color: AppColors.textSecondary),
            filled: true,
            fillColor: AppColors.bgTertiary,
            contentPadding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.md, vertical: AppSpacing.md),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
              borderSide: const BorderSide(color: AppColors.border),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
              borderSide: const BorderSide(color: AppColors.border),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
              borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildResultSection(RiskCalcResult r) {
    final isGoodRisk = r.riskPercent <= 2.0;
    return GASCard(
      borderColor: AppColors.primary.withOpacity(0.4),
      borderWidth: 1.5,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.bar_chart_rounded,
                  color: AppColors.primary, size: 20),
              const SizedBox(width: AppSpacing.sm),
              Text('Calculation Result', style: AppTypography.h3),
            ],
          ),
          const SizedBox(height: AppSpacing.lg),

          // Main metric — position size
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(AppSpacing.lg),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.08),
              borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
              border: Border.all(color: AppColors.primary.withOpacity(0.2)),
            ),
            child: Column(
              children: [
                Text('Position Size', style: AppTypography.labelLG),
                const SizedBox(height: AppSpacing.xs),
                Text(
                  '${r.positionSizeLots.toStringAsFixed(2)} lots',
                  style: AppTypography.priceXL.copyWith(
                    color: AppColors.primary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: AppSpacing.lg),

          // Grid of metrics
          Row(
            children: [
              Expanded(child: _buildMetricTile(
                label: 'Risk Amount',
                value: '\$${r.riskAmount.toStringAsFixed(2)}',
                color: isGoodRisk ? AppColors.bullish : AppColors.warning,
              )),
              const SizedBox(width: AppSpacing.md),
              Expanded(child: _buildMetricTile(
                label: 'Pip Value',
                value: '\$${r.pipValue.toStringAsFixed(2)}',
                color: AppColors.info,
              )),
            ],
          ),
          if (r.riskReward != null) ...[
            const SizedBox(height: AppSpacing.md),
            _buildMetricTile(
              label: 'Risk : Reward',
              value: '1 : ${r.riskReward!.toStringAsFixed(2)}',
              color: r.riskReward! >= 2 ? AppColors.bullish : AppColors.warning,
              wide: true,
            ),
          ],

          const SizedBox(height: AppSpacing.md),
          Container(
            padding: const EdgeInsets.all(AppSpacing.md),
            decoration: BoxDecoration(
              color: (isGoodRisk ? AppColors.bullish : AppColors.warning)
                  .withOpacity(0.08),
              borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
            ),
            child: Row(
              children: [
                Icon(
                  isGoodRisk ? Icons.check_circle_outline : Icons.warning_amber_outlined,
                  color: isGoodRisk ? AppColors.bullish : AppColors.warning,
                  size: 16,
                ),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: Text(
                    isGoodRisk
                        ? 'Risk level is within safe parameters.'
                        : 'Risk > 2%. Consider reducing position size.',
                    style: AppTypography.bodySM.copyWith(
                      color: isGoodRisk ? AppColors.bullish : AppColors.warning,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricTile({
    required String label,
    required String value,
    required Color color,
    bool wide = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.bgTertiary,
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment:
            wide ? CrossAxisAlignment.center : CrossAxisAlignment.start,
        children: [
          Text(label, style: AppTypography.labelMD),
          const SizedBox(height: AppSpacing.xs),
          Text(value,
              style: AppTypography.priceMD.copyWith(color: color),
              textAlign: wide ? TextAlign.center : TextAlign.start),
        ],
      ),
    );
  }

  Widget _buildHistory() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Calculation History', style: AppTypography.h3),
            TextButton(
              onPressed: () => setState(() => _history.clear()),
              child: Text('Clear', style: AppTypography.bodySM
                  .copyWith(color: AppColors.textSecondary)),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.md),
        ...(_history.map((r) => _buildHistoryItem(r))),
      ],
    );
  }

  Widget _buildHistoryItem(RiskCalcResult r) {
    final time = '${r.createdAt.hour.toString().padLeft(2, '0')}:'
        '${r.createdAt.minute.toString().padLeft(2, '0')}';
    return Container(
      margin: const EdgeInsets.only(bottom: AppSpacing.sm),
      padding: const EdgeInsets.all(AppSpacing.md),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.sm, vertical: AppSpacing.xs),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.12),
              borderRadius: BorderRadius.circular(AppSpacing.radiusSM),
            ),
            child: Text(r.pair,
                style: AppTypography.labelLG.copyWith(color: AppColors.primary)),
          ),
          const SizedBox(width: AppSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('${r.positionSizeLots.toStringAsFixed(2)} lots  •  '
                    '\$${r.riskAmount.toStringAsFixed(2)} risk',
                    style: AppTypography.bodyMD),
                Text('${r.riskPercent.toStringAsFixed(1)}% of '
                    '\$${r.accountBalance.toStringAsFixed(0)}  •  $time',
                    style: AppTypography.bodySM),
              ],
            ),
          ),
          if (r.riskReward != null)
            Text('1:${r.riskReward!.toStringAsFixed(1)}',
                style: AppTypography.bodySM
                    .copyWith(color: AppColors.bullish)),
        ],
      ),
    );
  }
}
