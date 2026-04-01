# GAS Terminal — Flutter Mobile App

**Golden AI Strategy** trading platform mobile application.

## Requirements

- Flutter 3.16+ (Dart 3.2+)
- Android Studio / VS Code with Flutter plugin
- Android device or emulator (API 23+)

## Setup

```bash
# 1. Install Flutter (if not installed)
git clone https://github.com/flutter/flutter.git
export PATH="$PATH:$HOME/flutter/bin"

# 2. Navigate to app directory
cd gas-mobile-app

# 3. Install dependencies
flutter pub get

# 4. Run on device/emulator
flutter run

# 5. Build release APK
flutter build apk --release
```

## APK Location after build

```
gas-mobile-app/build/app/outputs/flutter-apk/app-release.apk
```

Transfer this file to your Android device via USB, ADB, or file sharing.

## API Configuration

Edit `lib/core/constants/app_constants.dart`:
```dart
static const String apiBase = 'https://YOUR_SERVER_IP_OR_DOMAIN';
static const String wsBase  = 'wss://YOUR_SERVER_IP_OR_DOMAIN';
```

For local development use your server IP, e.g. `http://192.168.1.x:8000`

## Architecture

```
lib/
├── main.dart                    # App entry point
├── core/
│   ├── constants/               # Colors, Typography, Theme, Spacing
│   ├── router/                  # GoRouter with ShellRoute
│   ├── services/                # API, WebSocket, Auth, Storage
│   └── models/                  # Data models
├── shared/
│   └── widgets/                 # Reusable UI components
└── features/                    # Feature screens
    ├── auth/                    # Splash, Login, Signup
    ├── dashboard/               # Main dashboard
    ├── markets/                 # Live prices
    ├── signal/                  # Trading signals
    ├── chart/                   # TradingView chart
    ├── calendar/                # Economic calendar
    ├── ai_features/             # 10 AI feature screens
    ├── risk/                    # Risk manager + Drawdown
    ├── journal/                 # Trading journal
    ├── backtest/                # Backtesting
    ├── scanner/                 # Market scanner
    ├── alerts/                  # Notifications
    ├── leaderboard/             # Leaderboard
    ├── profile/                 # User profile
    └── admin/                   # Admin panel (admin only)
```

## Admin Panel

The admin panel (`/admin`) is only accessible to users with `is_admin=true` or `role='admin'`.

Features:
- **Overview**: Total users, plan distribution, revenue stats, AI calls
- **Active Sessions**: Real-time count of currently logged-in users (refreshes every 30s)
- **Users**: Browse/search all users with online status indicators
- **Sessions**: Session statistics, peak users, login history

## Features

| Feature | Plan | Credits |
|---------|------|---------|
| Technical Analysis | Essential+ | Free |
| Signal | Essential+ | Free |
| Correlation | Plus+ | 2 |
| Fundamental | Plus+ | 2 |
| Calendar | Plus+ | 2 |
| Sentiment | Plus+ | 3 |
| Risk Manager | Plus+ | 2 |
| Hybrid System | Premium+ | 4 |
| Drawdown Recovery | Premium+ | 4 |
| Market Briefing | Premium+ | 5 |
| Psychology Coach | Premium+ | 5 |
| Journal | Premium+ | 3 |
| Prop Firm | Premium+ | 5 |
| Scanner | Ultimate | 15 |
| Backtesting | Ultimate | 20 |
| Mentor Mode | Ultimate | 10 |
