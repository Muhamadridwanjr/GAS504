import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_typography.dart';

class ConfidenceRing extends StatelessWidget {
  final double value; // 0.0 – 1.0
  final double size;
  final double strokeWidth;
  final bool showLabel;

  const ConfidenceRing({
    super.key,
    required this.value,
    this.size = 48,
    this.strokeWidth = 4,
    this.showLabel = true,
  });

  Color get _color {
    if (value >= 0.90) return AppColors.conf90;
    if (value >= 0.75) return AppColors.conf75;
    if (value >= 0.60) return AppColors.conf60;
    return AppColors.conf50;
  }

  @override
  Widget build(BuildContext context) {
    final pct = (value * 100).round();
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          CustomPaint(
            size: Size(size, size),
            painter: _RingPainter(
              value: value,
              color: _color,
              strokeWidth: strokeWidth,
            ),
          ),
          if (showLabel)
            Text('$pct',
                style: AppTypography.priceXS.copyWith(
                    color: _color,
                    fontSize: size * 0.25,
                    fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  final double value;
  final Color color;
  final double strokeWidth;

  _RingPainter({
    required this.value,
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final r  = (size.width - strokeWidth) / 2;
    final rect = Rect.fromCircle(center: Offset(cx, cy), radius: r);

    // Background ring
    canvas.drawArc(
      rect,
      -math.pi / 2,
      math.pi * 2,
      false,
      Paint()
        ..color = color.withOpacity(0.15)
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth,
    );

    // Progress arc
    canvas.drawArc(
      rect,
      -math.pi / 2,
      math.pi * 2 * value,
      false,
      Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(_RingPainter old) =>
      old.value != value || old.color != color;
}
