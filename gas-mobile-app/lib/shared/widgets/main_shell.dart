import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/app_colors.dart';
import '../../core/providers/theme_provider.dart';
import 'gas_drawer.dart';

class MainShell extends ConsumerStatefulWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  @override
  ConsumerState<MainShell> createState() => _MainShellState();
}

class _MainShellState extends ConsumerState<MainShell> {
  int _currentIndex(BuildContext context) {
    final loc = GoRouterState.of(context).matchedLocation;
    if (loc.startsWith('/markets'))  return 1;
    if (loc.startsWith('/signal'))   return 2;
    if (loc.startsWith('/calendar')) return 3;
    if (loc.startsWith('/profile'))  return 4;
    return 0;
  }

  void _onTap(BuildContext context, int i) {
    switch (i) {
      case 0: context.go('/dashboard'); break;
      case 1: context.go('/markets');   break;
      case 2: context.go('/signal');    break;
      case 3: context.go('/calendar');  break;
      case 4: context.go('/profile');   break;
    }
  }

  @override
  Widget build(BuildContext context) {
    final idx    = _currentIndex(context);
    final isDark = ref.watch(themeProvider) == ThemeMode.dark;
    final navBg  = isDark ? AppColors.bgPrimary : Colors.white;
    final topBorderColor = isDark
        ? AppColors.border
        : const Color(0xFFE0E0F0);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      drawer: GASDrawer(),
      body: Stack(
        children: [
          widget.child,
          // Floating theme toggle button above the bottom nav bar
          Positioned(
            right: 16,
            bottom: 72,
            child: GestureDetector(
              onTap: () => ref.read(themeProvider.notifier).toggle(),
              child: Container(
                width: 40, height: 40,
                decoration: BoxDecoration(
                  color: isDark ? AppColors.bgSurface : Colors.white,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isDark
                        ? AppColors.borderLight
                        : const Color(0xFFDDDDF0),
                    width: 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(isDark ? 0.3 : 0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Icon(
                  isDark
                      ? Icons.light_mode_outlined
                      : Icons.dark_mode_outlined,
                  size: 18,
                  color: isDark
                      ? AppColors.textSecondary
                      : const Color(0xFF66668A),
                ),
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: navBg,
          border: Border(top: BorderSide(color: topBorderColor)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(isDark ? 0.4 : 0.08),
              blurRadius: 12,
              offset: const Offset(0, -2),
            ),
          ],
        ),
        child: BottomNavigationBar(
          currentIndex: idx,
          onTap: (i) => _onTap(context, i),
          backgroundColor: Colors.transparent,
          elevation: 0,
          selectedItemColor:
              isDark ? AppColors.primary : const Color(0xFFB8860B),
          unselectedItemColor:
              isDark ? AppColors.textMuted : const Color(0xFF9999BB),
          type: BottomNavigationBarType.fixed,
          selectedLabelStyle:
              const TextStyle(fontSize: 10, fontWeight: FontWeight.w600),
          unselectedLabelStyle: const TextStyle(fontSize: 10),
          items: [
            _item(Icons.dashboard_outlined, Icons.dashboard,   'Dashboard'),
            _item(Icons.show_chart_outlined, Icons.show_chart, 'Markets'),
            _item(Icons.bolt_outlined, Icons.bolt,             'Signal'),
            _item(Icons.event_outlined, Icons.event,           'Calendar'),
            _item(Icons.person_outline, Icons.person,          'Profile'),
          ],
        ),
      ),
    );
  }

  BottomNavigationBarItem _item(
          IconData icon, IconData activeIcon, String label) =>
      BottomNavigationBarItem(
        icon: Icon(icon, size: 22),
        activeIcon: Icon(activeIcon, size: 22),
        label: label,
      );
}
