import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/constants/app_theme.dart';
import 'core/constants/app_colors.dart';
import 'core/router/app_router.dart';
import 'core/services/api_service.dart';
import 'core/services/storage_service.dart';
import 'core/providers/theme_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor:            Colors.transparent,
    statusBarIconBrightness:   Brightness.light,
    statusBarBrightness:       Brightness.dark,
    systemNavigationBarColor:  AppColors.bgPrimary,
    systemNavigationBarIconBrightness: Brightness.light,
  ));

  await StorageService().init();
  ApiService().init();

  runApp(const ProviderScope(child: GASApp()));
}

class GASApp extends ConsumerWidget {
  const GASApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router    = ref.watch(routerProvider);
    final themeMode = ref.watch(themeProvider);

    return MaterialApp.router(
      title:            'GAS Terminal',
      debugShowCheckedModeBanner: false,
      theme:            AppTheme.light,
      darkTheme:        AppTheme.dark,
      themeMode:        themeMode,
      routerConfig:     router,
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaler: TextScaler.noScaling,
          ),
          child: child!,
        );
      },
    );
  }
}
