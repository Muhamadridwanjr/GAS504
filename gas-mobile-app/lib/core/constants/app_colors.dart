import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // ── Brand ──────────────────────────────────────────────────────────────────
  static const Color primary       = Color(0xFFFFD700); // Gold
  static const Color primaryDark   = Color(0xFFB8860B);
  static const Color primaryLight  = Color(0xFFFFF176);
  static const Color accent        = Color(0xFF00E5FF); // Cyan accent

  // ── Background ─────────────────────────────────────────────────────────────
  static const Color bgDeep        = Color(0xFF050508); // deepest black
  static const Color bgPrimary     = Color(0xFF0A0A0F); // main bg
  static const Color bgSecondary   = Color(0xFF0F0F18); // card bg
  static const Color bgTertiary    = Color(0xFF151525); // elevated card
  static const Color bgSurface     = Color(0xFF1A1A2E); // surface
  static const Color bgModal       = Color(0xFF12121F); // modal bg

  // ── Border ─────────────────────────────────────────────────────────────────
  static const Color border        = Color(0xFF1E1E3A);
  static const Color borderLight   = Color(0xFF252545);
  static const Color borderGold    = Color(0xFF3D3010);
  static const Color borderFocus   = Color(0xFF4A4060);

  // ── Text ───────────────────────────────────────────────────────────────────
  static const Color textPrimary   = Color(0xFFEEEEFF);
  static const Color textSecondary = Color(0xFF8888AA);
  static const Color textMuted     = Color(0xFF555577);
  static const Color textGold      = Color(0xFFFFD700);
  static const Color textCyan      = Color(0xFF00E5FF);

  // ── Semantic ───────────────────────────────────────────────────────────────
  static const Color bullish       = Color(0xFF00E676); // green
  static const Color bearish       = Color(0xFFFF1744); // red
  static const Color neutral       = Color(0xFF8888AA);
  static const Color warning       = Color(0xFFFFC107);
  static const Color info          = Color(0xFF29B6F6);
  static const Color success       = Color(0xFF00E676);
  static const Color error         = Color(0xFFFF1744);

  // ── Signal confidence ──────────────────────────────────────────────────────
  static const Color conf90        = Color(0xFF00E676); // >= 90%
  static const Color conf75        = Color(0xFF69F0AE); // 75-90%
  static const Color conf60        = Color(0xFFFFC107); // 60-75%
  static const Color conf50        = Color(0xFFFF7043); // < 60%

  // ── Plan colors ────────────────────────────────────────────────────────────
  static const Color planEssential = Color(0xFF78909C);
  static const Color planPlus      = Color(0xFF42A5F5);
  static const Color planPremium   = Color(0xFFAB47BC);
  static const Color planUltimate  = Color(0xFFFFD700);

  // ── Market session ─────────────────────────────────────────────────────────
  static const Color sessionSydney    = Color(0xFF4FC3F7);
  static const Color sessionTokyo     = Color(0xFFE91E63);
  static const Color sessionLondon    = Color(0xFF26C6DA);
  static const Color sessionNewYork   = Color(0xFF7E57C2);
  static const Color sessionClosed    = Color(0xFF424242);

  // ── Chart palette ──────────────────────────────────────────────────────────
  static const List<Color> chartPalette = [
    Color(0xFFFFD700),
    Color(0xFF00E5FF),
    Color(0xFF00E676),
    Color(0xFFFF4081),
    Color(0xFFAA00FF),
    Color(0xFFFF6D00),
    Color(0xFF29B6F6),
    Color(0xFF76FF03),
  ];

  // ── Gradients ──────────────────────────────────────────────────────────────
  static const LinearGradient goldGradient = LinearGradient(
    colors: [Color(0xFFFFD700), Color(0xFFB8860B)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient bgGradient = LinearGradient(
    colors: [Color(0xFF0A0A0F), Color(0xFF0F0F20)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xFF151525), Color(0xFF0F0F18)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient bullishGradient = LinearGradient(
    colors: [Color(0xFF00E676), Color(0xFF00897B)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient bearishGradient = LinearGradient(
    colors: [Color(0xFFFF1744), Color(0xFFC62828)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
