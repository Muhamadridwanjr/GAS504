import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';
import '../../core/constants/app_spacing.dart';
import '../../core/services/api_service.dart';
import '../../shared/widgets/gas_app_bar.dart';

class MentorScreen extends StatefulWidget {
  const MentorScreen({super.key});
  @override State<MentorScreen> createState() => _MentorScreenState();
}

class _MentorScreenState extends State<MentorScreen> {
  final _api     = ApiService();
  final _ctrl    = TextEditingController();
  final _scroll  = ScrollController();
  final _msgs    = <Map<String, dynamic>>[];
  bool _loading  = false;

  static const _quick = [
    'Explain SMC concepts', 'Best session to trade XAUUSD?',
    'Risk management rules', 'What is liquidity sweep?',
    'How to identify FVG?',
  ];

  @override
  void dispose() { _ctrl.dispose(); _scroll.dispose(); super.dispose(); }

  Future<void> _send(String q) async {
    if (q.trim().isEmpty || _loading) return;
    setState(() {
      _msgs.add({'role': 'user', 'text': q});
      _loading = true;
      _ctrl.clear();
    });
    _scrollDown();
    try {
      final r = await _api.callAIFeature('mentor', {'question': q});
      final answer = r['answer'] as String? ?? r['response'] as String? ?? 'No response';
      if (mounted) setState(() {
        _msgs.add({'role': 'mentor', 'text': answer});
        _loading = false;
      });
      _scrollDown();
    } catch (e) {
      if (mounted) setState(() {
        _msgs.add({'role': 'mentor', 'text': 'Error: $e'});
        _loading = false;
      });
    }
  }

  void _scrollDown() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scroll.hasClients) {
        _scroll.animateTo(
          _scroll.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    backgroundColor: AppColors.bgPrimary,
    appBar: GASAppBar(
      title: 'Mentor Mode',
      subtitle: '10 credits per session',
    ),
    body: Column(
      children: [
        // Quick questions
        if (_msgs.isEmpty)
          SizedBox(
            height: 48,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.md, vertical: 8),
              children: _quick.map((q) => GestureDetector(
                onTap: () => _send(q),
                child: Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppColors.bgSecondary,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: Text(q, style: AppTypography.labelMD),
                ),
              )).toList(),
            ),
          ),
        const Divider(height: 1),

        // Chat messages
        Expanded(
          child: ListView.builder(
            controller: _scroll,
            padding: const EdgeInsets.all(AppSpacing.lg),
            itemCount: _msgs.length + (_loading ? 1 : 0),
            itemBuilder: (_, i) {
              if (i == _msgs.length && _loading) {
                return _bubble({'role': 'mentor', 'text': '...'}, typing: true);
              }
              return _bubble(_msgs[i]);
            },
          ),
        ),

        // Input bar
        Container(
          padding: EdgeInsets.only(
            left: AppSpacing.md,
            right: AppSpacing.md,
            top: AppSpacing.sm,
            bottom: MediaQuery.of(context).padding.bottom + AppSpacing.sm,
          ),
          decoration: const BoxDecoration(
            border: Border(top: BorderSide(color: AppColors.border)),
            color: AppColors.bgPrimary,
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _ctrl,
                  style: AppTypography.bodyMD,
                  onSubmitted: _send,
                  decoration: const InputDecoration(
                    hintText: 'Ask your mentor...',
                    isDense: true,
                    contentPadding: EdgeInsets.symmetric(
                        horizontal: 16, vertical: 10),
                  ),
                ),
              ),
              const SizedBox(width: AppSpacing.sm),
              GestureDetector(
                onTap: () => _send(_ctrl.text),
                child: Container(
                  width: 40, height: 40,
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
                  ),
                  child: const Icon(Icons.send,
                      color: Colors.black, size: 18),
                ),
              ),
            ],
          ),
        ),
      ],
    ),
  );

  Widget _bubble(Map<String, dynamic> msg, {bool typing = false}) {
    final isMentor = msg['role'] == 'mentor';
    final text     = msg['text'] as String;
    return Align(
      alignment: isMentor ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.only(bottom: AppSpacing.md),
        padding: const EdgeInsets.all(AppSpacing.md),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.78,
        ),
        decoration: BoxDecoration(
          color: isMentor ? AppColors.bgSecondary : AppColors.primary.withOpacity(0.15),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(AppSpacing.radiusLG),
            topRight: const Radius.circular(AppSpacing.radiusLG),
            bottomLeft: Radius.circular(isMentor ? 4 : AppSpacing.radiusLG),
            bottomRight: Radius.circular(isMentor ? AppSpacing.radiusLG : 4),
          ),
          border: Border.all(
            color: isMentor ? AppColors.border : AppColors.primary.withOpacity(0.3),
          ),
        ),
        child: typing
            ? Row(mainAxisSize: MainAxisSize.min, children: [
                _dot(0), _dot(150), _dot(300),
              ])
            : Text(text, style: AppTypography.bodyMD),
      ),
    );
  }

  Widget _dot(int delay) => TweenAnimationBuilder<double>(
    tween: Tween(begin: 0, end: 1),
    duration: const Duration(milliseconds: 600),
    curve: Curves.easeInOut,
    builder: (_, v, __) => Container(
      margin: const EdgeInsets.symmetric(horizontal: 3),
      width: 6, height: 6,
      decoration: BoxDecoration(
        color: AppColors.textMuted.withOpacity(v),
        shape: BoxShape.circle,
      ),
    ),
  );
}
