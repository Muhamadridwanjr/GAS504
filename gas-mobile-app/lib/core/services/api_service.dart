import 'package:dio/dio.dart';
import '../constants/app_constants.dart';
import 'storage_service.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  late final Dio _dio;
  final _storage = StorageService();

  void init() {
    _dio = Dio(BaseOptions(
      baseUrl: AppConstants.apiBase,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 20),
      headers: {
        'Content-Type': 'application/json',
        'Accept':       'application/json',
      },
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          final refreshed = await _refreshToken();
          if (refreshed) {
            final token = await _storage.getToken();
            error.requestOptions.headers['Authorization'] = 'Bearer $token';
            final retry = await _dio.request(
              error.requestOptions.path,
              options: Options(
                method: error.requestOptions.method,
                headers: error.requestOptions.headers,
              ),
              data: error.requestOptions.data,
              queryParameters: error.requestOptions.queryParameters,
            );
            return handler.resolve(retry);
          }
        }
        handler.next(error);
      },
    ));
  }

  Future<bool> _refreshToken() async {
    try {
      final refresh = await _storage.getRefreshToken();
      if (refresh == null) return false;
      final resp = await Dio().post(
        '${AppConstants.apiBase}/auth/v1/auth/refresh',
        data: {'refresh_token': refresh},
      );
      final newToken = resp.data['access_token'];
      if (newToken != null) {
        await _storage.setToken(newToken);
        return true;
      }
    } catch (_) {}
    return false;
  }

  // ── Auth ────────────────────────────────────────────────────────────────────
  // Login — backend accepts username OR email in the "username" field
  Future<Map<String, dynamic>> login(String usernameOrEmail, String password) async {
    final r = await _dio.post('/auth/v1/auth/login', data: {
      'username': usernameOrEmail,
      'password': password,
    });
    return r.data as Map<String, dynamic>;
  }

  // Step 1 of register — send OTP to email
  Future<void> sendOtp(String email, String username) async {
    await _dio.post('/auth/v1/auth/send-otp', data: {
      'email':    email,
      'username': username,
    });
  }

  // Step 2 of register — submit form + OTP code
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String otp,
    String fullName = '',
  }) async {
    final r = await _dio.post('/auth/v1/auth/register', data: {
      'username':  username,
      'email':     email,
      'password':  password,
      'full_name': fullName,
      'otp':       otp,
    });
    return r.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getProfile() async {
    final r = await _dio.get('/auth/v1/auth/user');
    return r.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> data) async {
    final r = await _dio.patch('/auth/v1/auth/profile', data: data);
    return r.data as Map<String, dynamic>;
  }

  // No backend logout endpoint — just clear local tokens
  Future<void> logout() async {}

  // ── Overview / Dashboard ────────────────────────────────────────────────────
  Future<Map<String, dynamic>> getOverview() async {
    final r = await _dio.get('/terminal/overview');
    return r.data as Map<String, dynamic>;
  }

  // ── Signal ──────────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> getSignal(String pair) async {
    final r = await _dio.get('/terminal/signal/latest',
        queryParameters: {'pair': pair});
    return r.data as Map<String, dynamic>;
  }

  // ── News ────────────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> getNews() async {
    final r = await _dio.get('/terminal/news');
    return r.data as Map<String, dynamic>;
  }

  // ── Calendar ────────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> getCalendar() async {
    final r = await _dio.get('/terminal/calendar');
    return r.data as Map<String, dynamic>;
  }

  // ── Markets (Binance) ───────────────────────────────────────────────────────
  Future<Map<String, dynamic>> getBinanceTicker(String pair) async {
    final encoded = Uri.encodeComponent(pair);
    final r = await _dio.get('/terminal/binance/ticker/$encoded');
    return r.data as Map<String, dynamic>;
  }

  Future<List<dynamic>> getBinanceTickers() async {
    final r = await _dio.get('/terminal/binance/tickers');
    return r.data as List<dynamic>;
  }

  Future<List<dynamic>> getOHLCV(String pair, String timeframe, {int limit = 200}) async {
    final encoded = Uri.encodeComponent(pair);
    final r = await _dio.get(
      '/terminal/binance/ohlcv/$encoded',
      queryParameters: {'timeframe': timeframe, 'limit': limit},
    );
    return r.data as List<dynamic>;
  }

  // ── AI Features ─────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> callAIFeature(
      String feature, Map<String, dynamic> params) async {
    final r = await _dio.post('/web/api/v1/analysis/$feature', data: params);
    return r.data as Map<String, dynamic>;
  }

  // ── Plan / Credits ──────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> getPlanStatus() async {
    final r = await _dio.get('/web/api/v1/billing/status');
    return r.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getFeatures() async {
    final r = await _dio.get('/web/api/v1/plan/features');
    return r.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getUserLevel() async {
    final r = await _dio.get('/web/api/v1/level/my-level');
    return r.data as Map<String, dynamic>;
  }

  // ── Journal ─────────────────────────────────────────────────────────────────
  Future<List<dynamic>> getJournal() async {
    final r = await _dio.get('/web/api/v1/journal');
    return r.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> createJournalEntry(Map<String, dynamic> data) async {
    final r = await _dio.post('/web/api/v1/journal', data: data);
    return r.data as Map<String, dynamic>;
  }

  Future<void> deleteJournalEntry(String id) async {
    await _dio.delete('/web/api/v1/journal/$id');
  }

  // ── Alerts ──────────────────────────────────────────────────────────────────
  Future<List<dynamic>> getAlerts() async {
    final r = await _dio.get('/web/api/v1/notifications');
    return r.data as List<dynamic>;
  }

  // ── Leaderboard ─────────────────────────────────────────────────────────────
  Future<List<dynamic>> getLeaderboard() async {
    final r = await _dio.get('/web/api/v1/leaderboard');
    return r.data as List<dynamic>;
  }

  // ── Admin ───────────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> getAdminStats() async {
    final r = await _dio.get('/web/api/v1/admin/stats');
    return r.data as Map<String, dynamic>;
  }

  Future<List<dynamic>> getAdminUsers({int page = 1, int limit = 50, String? search}) async {
    final r = await _dio.get('/web/api/v1/admin/users', queryParameters: {
      'page': page, 'limit': limit,
      if (search != null) 'search': search,
    });
    return r.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> getActiveSessionsCount() async {
    final r = await _dio.get('/web/api/v1/admin/active-sessions');
    return r.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> adminUpdateUser(String userId, Map<String, dynamic> data) async {
    final r = await _dio.patch('/web/api/v1/admin/users/$userId', data: data);
    return r.data as Map<String, dynamic>;
  }

  // ── Booster packs ───────────────────────────────────────────────────────────
  Future<List<dynamic>> getBoosterPacks() async {
    final r = await _dio.get('/web/api/v1/booster/packs');
    return r.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> purchaseBooster(String packId) async {
    final r = await _dio.post('/web/api/v1/booster/purchase', data: {'pack_id': packId});
    return r.data as Map<String, dynamic>;
  }

  // ── IDX ─────────────────────────────────────────────────────────────────────
  Future<Map<String, dynamic>> getIHSG() async {
    final r = await _dio.get('/terminal/idx/ihsg');
    return r.data as Map<String, dynamic>;
  }

  Future<List<dynamic>> getIDXTickers(List<String> symbols) async {
    final r = await _dio.get('/terminal/idx/tickers',
        queryParameters: {'symbols': symbols.join(',')});
    return r.data as List<dynamic>;
  }

  // ── Health ──────────────────────────────────────────────────────────────────
  Future<bool> healthCheck() async {
    try {
      final r = await _dio.get('/web/api/v1/health',
          options: Options(receiveTimeout: const Duration(seconds: 5)));
      return r.statusCode == 200;
    } catch (_) { return false; }
  }
}
