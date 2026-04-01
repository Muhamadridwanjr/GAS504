import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/auth/screens/splash_screen.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/signup_screen.dart';
import '../../features/auth/screens/ios_coming_soon_screen.dart';
import '../../features/dashboard/dashboard_screen.dart';
import '../../features/markets/markets_screen.dart';
import '../../features/signal/signal_screen.dart';
import '../../features/chart/chart_screen.dart';
import '../../features/profile/profile_screen.dart';
import '../../features/calendar/calendar_screen.dart';
import '../../features/ai_features/technical_screen.dart';
import '../../features/ai_features/correlation_screen.dart';
import '../../features/ai_features/fundamental_screen.dart';
import '../../features/ai_features/sentiment_screen.dart';
import '../../features/ai_features/session_screen.dart';
import '../../features/ai_features/hybrid_screen.dart';
import '../../features/ai_features/briefing_screen.dart';
import '../../features/ai_features/psychology_screen.dart';
import '../../features/ai_features/mentor_screen.dart';
import '../../features/ai_features/propfirm_screen.dart';
import '../../features/risk/risk_screen.dart';
import '../../features/risk/drawdown_screen.dart';
import '../../features/journal/journal_screen.dart';
import '../../features/backtest/backtest_screen.dart';
import '../../features/scanner/scanner_screen.dart';
import '../../features/alerts/alerts_screen.dart';
import '../../features/leaderboard/leaderboard_screen.dart';
import '../../features/admin/admin_screen.dart';
import '../services/auth_service.dart';
import '../../shared/widgets/main_shell.dart';

final _authService = AuthService();

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/splash',
    redirect: (context, state) {
      final isAuth = _authService.isLoggedIn;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');
      final isSplash    = state.matchedLocation == '/splash';

      if (isSplash) return null;
      if (!isAuth && !isAuthRoute) return '/auth/login';
      if (isAuth  &&  isAuthRoute) return '/dashboard';
      return null;
    },
    routes: [
      // ── Splash ─────────────────────────────────────────────────────────
      GoRoute(
        path: '/splash',
        builder: (ctx, s) => const SplashScreen(),
      ),

      // ── Auth ───────────────────────────────────────────────────────────
      GoRoute(
        path: '/auth/login',
        builder: (ctx, s) => const LoginScreen(),
      ),
      GoRoute(
        path: '/auth/signup',
        builder: (ctx, s) => const SignupScreen(),
      ),
      GoRoute(
        path: '/auth/ios-coming-soon',
        builder: (ctx, s) => const IosComingSoonScreen(),
      ),

      // ── Main Shell (bottom nav) ────────────────────────────────────────
      ShellRoute(
        builder: (ctx, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/dashboard',
            builder: (ctx, s) => const DashboardScreen(),
          ),
          GoRoute(
            path: '/markets',
            builder: (ctx, s) => const MarketsScreen(),
            routes: [
              GoRoute(
                path: 'chart/:symbol',
                builder: (ctx, s) => ChartScreen(
                  symbol: s.pathParameters['symbol'] ?? 'XAUUSD',
                  timeframe: s.uri.queryParameters['tf'] ?? '1h',
                ),
              ),
            ],
          ),
          GoRoute(
            path: '/signal',
            builder: (ctx, s) => SignalScreen(
              pair: s.uri.queryParameters['pair'] ?? 'XAUUSD',
            ),
          ),
          GoRoute(
            path: '/calendar',
            builder: (ctx, s) => const CalendarScreen(),
          ),
          GoRoute(
            path: '/profile',
            builder: (ctx, s) => const ProfileScreen(),
          ),
        ],
      ),

      // ── AI Features (no shell — full screen) ──────────────────────────
      GoRoute(
        path: '/ai/technical',
        builder: (ctx, s) => TechnicalScreen(
          pair: s.uri.queryParameters['pair'] ?? 'XAUUSD',
        ),
      ),
      GoRoute(
        path: '/ai/correlation',
        builder: (ctx, s) => const CorrelationScreen(),
      ),
      GoRoute(
        path: '/ai/fundamental',
        builder: (ctx, s) => FundamentalScreen(
          pair: s.uri.queryParameters['pair'] ?? 'XAUUSD',
        ),
      ),
      GoRoute(
        path: '/ai/sentiment',
        builder: (ctx, s) => SentimentScreen(
          pair: s.uri.queryParameters['pair'] ?? 'XAUUSD',
        ),
      ),
      GoRoute(
        path: '/ai/session',
        builder: (ctx, s) => const SessionScreen(),
      ),
      GoRoute(
        path: '/ai/hybrid',
        builder: (ctx, s) => HybridScreen(
          pair: s.uri.queryParameters['pair'] ?? 'XAUUSD',
        ),
      ),
      GoRoute(
        path: '/ai/briefing',
        builder: (ctx, s) => const BriefingScreen(),
      ),
      GoRoute(
        path: '/ai/psychology',
        builder: (ctx, s) => const PsychologyScreen(),
      ),
      GoRoute(
        path: '/ai/mentor',
        builder: (ctx, s) => const MentorScreen(),
      ),
      GoRoute(
        path: '/ai/propfirm',
        builder: (ctx, s) => const PropFirmScreen(),
      ),
      GoRoute(
        path: '/risk',
        builder: (ctx, s) => const RiskScreen(),
      ),
      GoRoute(
        path: '/drawdown',
        builder: (ctx, s) => const DrawdownScreen(),
      ),
      GoRoute(
        path: '/journal',
        builder: (ctx, s) => const JournalScreen(),
      ),
      GoRoute(
        path: '/backtest',
        builder: (ctx, s) => const BacktestScreen(),
      ),
      GoRoute(
        path: '/scanner',
        builder: (ctx, s) => const ScannerScreen(),
      ),
      GoRoute(
        path: '/alerts',
        builder: (ctx, s) => const AlertsScreen(),
      ),
      GoRoute(
        path: '/leaderboard',
        builder: (ctx, s) => const LeaderboardScreen(),
      ),
      GoRoute(
        path: '/admin',
        redirect: (ctx, s) => _authService.isAdmin ? null : '/dashboard',
        builder: (ctx, s) => const AdminScreen(),
      ),
    ],

    errorBuilder: (ctx, state) => Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline,
                color: Color(0xFFFF1744), size: 48),
            const SizedBox(height: 16),
            Text('Page not found: ${state.matchedLocation}',
                style: const TextStyle(color: Colors.white)),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => ctx.go('/dashboard'),
              child: const Text('Go to Dashboard'),
            ),
          ],
        ),
      ),
    ),
  );
});
