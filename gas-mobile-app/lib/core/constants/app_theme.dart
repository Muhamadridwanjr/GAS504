import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'app_colors.dart';
import 'app_typography.dart';
import 'app_spacing.dart';

class AppTheme {
  AppTheme._();

  // ── Dark theme ──────────────────────────────────────────────────────────────
  static ThemeData get dark => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    scaffoldBackgroundColor: AppColors.bgPrimary,
    colorScheme: const ColorScheme.dark(
      primary:      AppColors.primary,
      secondary:    AppColors.accent,
      surface:      AppColors.bgSecondary,
      onPrimary:    AppColors.bgDeep,
      onSecondary:  AppColors.bgDeep,
      onSurface:    AppColors.textPrimary,
      error:        AppColors.error,
      onError:      Colors.white,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor:  AppColors.bgPrimary,
      foregroundColor:  AppColors.textPrimary,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: AppTypography.h3,
      systemOverlayStyle: SystemUiOverlayStyle(
        statusBarColor:            Colors.transparent,
        statusBarIconBrightness:   Brightness.light,
        statusBarBrightness:       Brightness.dark,
      ),
    ),
    cardTheme: CardTheme(
      color: AppColors.bgSecondary,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLG),
        side: const BorderSide(color: AppColors.border, width: 1),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: AppColors.bgTertiary,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.lg, vertical: AppSpacing.md,
      ),
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
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        borderSide: const BorderSide(color: AppColors.error),
      ),
      hintStyle: AppTypography.bodyMD.copyWith(color: AppColors.textMuted),
      labelStyle: AppTypography.labelLG,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor:     AppColors.primary,
        foregroundColor:     AppColors.bgDeep,
        minimumSize:         const Size(double.infinity, 52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        ),
        textStyle: AppTypography.btnLG,
        elevation: 0,
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: AppColors.primary,
        textStyle: AppTypography.btnMD,
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.textPrimary,
        side: const BorderSide(color: AppColors.border),
        minimumSize: const Size(double.infinity, 48),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        ),
        textStyle: AppTypography.btnMD,
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: AppColors.bgTertiary,
      selectedColor:   AppColors.primary.withOpacity(0.15),
      labelStyle: AppTypography.labelMD.copyWith(color: AppColors.textSecondary),
      side: const BorderSide(color: AppColors.border),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
      ),
    ),
    dividerTheme: const DividerThemeData(
      color: AppColors.border,
      thickness: 1,
      space: 1,
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor:     AppColors.bgPrimary,
      selectedItemColor:   AppColors.primary,
      unselectedItemColor: AppColors.textMuted,
      type: BottomNavigationBarType.fixed,
      elevation: 0,
      selectedLabelStyle:   TextStyle(fontSize: 10, fontWeight: FontWeight.w600),
      unselectedLabelStyle: TextStyle(fontSize: 10),
    ),
    dialogTheme: DialogTheme(
      backgroundColor: AppColors.bgModal,
      elevation: 24,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusXL),
        side: const BorderSide(color: AppColors.border),
      ),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: AppColors.bgSurface,
      contentTextStyle: AppTypography.bodyMD,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
      ),
      behavior: SnackBarBehavior.floating,
    ),
    scrollbarTheme: ScrollbarThemeData(
      thumbColor: WidgetStateProperty.all(AppColors.border),
      trackColor: WidgetStateProperty.all(AppColors.bgSecondary),
      radius: const Radius.circular(AppSpacing.radiusFull),
      thickness: WidgetStateProperty.all(3),
    ),
    textTheme: const TextTheme(
      displayLarge:   AppTypography.h1,
      displayMedium:  AppTypography.h2,
      displaySmall:   AppTypography.h3,
      headlineMedium: AppTypography.h4,
      bodyLarge:      AppTypography.bodyLG,
      bodyMedium:     AppTypography.bodyMD,
      bodySmall:      AppTypography.bodySM,
      labelLarge:     AppTypography.btnMD,
      labelMedium:    AppTypography.labelMD,
      labelSmall:     AppTypography.labelSM,
    ),
  );

  // ── Light theme ─────────────────────────────────────────────────────────────
  static const Color _lightBg       = Color(0xFFF4F4F9);
  static const Color _lightSurface  = Color(0xFFFFFFFF);
  static const Color _lightCard     = Color(0xFFFFFFFF);
  static const Color _lightBorder   = Color(0xFFDDDDF0);
  static const Color _lightText     = Color(0xFF1A1A2E);
  static const Color _lightSub      = Color(0xFF555577);
  static const Color _lightMuted    = Color(0xFF9999BB);
  static const Color _lightGold     = Color(0xFFB8860B); // dark amber readable on white
  static const Color _lightInput    = Color(0xFFF0F0F8);

  static ThemeData get light => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    scaffoldBackgroundColor: _lightBg,
    colorScheme: const ColorScheme.light(
      primary:     AppColors.primary,   // gold stays gold (buttons)
      secondary:   Color(0xFF0097A7),
      surface:     _lightSurface,
      onPrimary:   Colors.black,
      onSecondary: Colors.white,
      onSurface:   _lightText,
      error:       Color(0xFFD32F2F),
      onError:     Colors.white,
    ),
    appBarTheme: const AppBarTheme(
      backgroundColor: _lightSurface,
      foregroundColor: _lightText,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: TextStyle(
        fontFamily: 'Roboto',
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: _lightText,
      ),
      systemOverlayStyle: SystemUiOverlayStyle(
        statusBarColor:            Colors.transparent,
        statusBarIconBrightness:   Brightness.dark,
        statusBarBrightness:       Brightness.light,
      ),
    ),
    cardTheme: CardTheme(
      color: _lightCard,
      elevation: 0,
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusLG),
        side: const BorderSide(color: _lightBorder, width: 1),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: _lightInput,
      contentPadding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.lg, vertical: AppSpacing.md,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        borderSide: const BorderSide(color: _lightBorder),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        borderSide: const BorderSide(color: _lightBorder),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        borderSide: const BorderSide(color: Color(0xFFD32F2F)),
      ),
      hintStyle: const TextStyle(color: _lightMuted),
      labelStyle: const TextStyle(
        fontSize: 13, fontWeight: FontWeight.w600,
        color: Color(0xFF66668A), letterSpacing: 0.8,
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor:     AppColors.primary,
        foregroundColor:     Colors.black,
        minimumSize:         const Size(double.infinity, 52),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        ),
        textStyle: AppTypography.btnLG,
        elevation: 0,
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: _lightGold,
        textStyle: AppTypography.btnMD,
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: _lightText,
        side: const BorderSide(color: _lightBorder),
        minimumSize: const Size(double.infinity, 48),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
        ),
        textStyle: AppTypography.btnMD,
      ),
    ),
    chipTheme: ChipThemeData(
      backgroundColor: _lightInput,
      selectedColor:   AppColors.primary.withOpacity(0.15),
      labelStyle: const TextStyle(
        fontFamily: 'Roboto', fontSize: 11, fontWeight: FontWeight.w600,
        color: Color(0xFF66668A),
      ),
      side: const BorderSide(color: _lightBorder),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusFull),
      ),
    ),
    dividerTheme: const DividerThemeData(
      color: _lightBorder,
      thickness: 1,
      space: 1,
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor:     _lightSurface,
      selectedItemColor:   _lightGold,
      unselectedItemColor: _lightMuted,
      type: BottomNavigationBarType.fixed,
      elevation: 0,
      selectedLabelStyle:   TextStyle(fontSize: 10, fontWeight: FontWeight.w600),
      unselectedLabelStyle: TextStyle(fontSize: 10),
    ),
    dialogTheme: DialogTheme(
      backgroundColor: _lightSurface,
      elevation: 8,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusXL),
        side: const BorderSide(color: _lightBorder),
      ),
    ),
    snackBarTheme: SnackBarThemeData(
      backgroundColor: _lightText,
      contentTextStyle: const TextStyle(color: Colors.white),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.radiusMD),
      ),
      behavior: SnackBarBehavior.floating,
    ),
    scrollbarTheme: ScrollbarThemeData(
      thumbColor: WidgetStateProperty.all(_lightBorder),
      trackColor: WidgetStateProperty.all(_lightInput),
      radius: const Radius.circular(AppSpacing.radiusFull),
      thickness: WidgetStateProperty.all(3),
    ),
    textTheme: const TextTheme(
      displayLarge:   TextStyle(fontFamily: 'Roboto', fontSize: 28, fontWeight: FontWeight.w700, color: _lightText, letterSpacing: -0.5),
      displayMedium:  TextStyle(fontFamily: 'Roboto', fontSize: 22, fontWeight: FontWeight.w700, color: _lightText, letterSpacing: -0.3),
      displaySmall:   TextStyle(fontFamily: 'Roboto', fontSize: 18, fontWeight: FontWeight.w600, color: _lightText),
      headlineMedium: TextStyle(fontFamily: 'Roboto', fontSize: 16, fontWeight: FontWeight.w600, color: _lightText),
      bodyLarge:      TextStyle(fontFamily: 'Roboto', fontSize: 16, fontWeight: FontWeight.w400, color: _lightText, height: 1.5),
      bodyMedium:     TextStyle(fontFamily: 'Roboto', fontSize: 14, fontWeight: FontWeight.w400, color: _lightText, height: 1.5),
      bodySmall:      TextStyle(fontFamily: 'Roboto', fontSize: 12, fontWeight: FontWeight.w400, color: Color(0xFF66668A), height: 1.4),
      labelLarge:     TextStyle(fontFamily: 'Roboto', fontSize: 14, fontWeight: FontWeight.w600),
      labelMedium:    TextStyle(fontFamily: 'Roboto', fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF66668A), letterSpacing: 1.0),
      labelSmall:     TextStyle(fontFamily: 'Roboto', fontSize: 10, fontWeight: FontWeight.w600, color: _lightMuted, letterSpacing: 1.2),
    ),
  );
}
