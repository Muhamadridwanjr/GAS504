import 'api_service.dart';
import 'storage_service.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final _api     = ApiService();
  final _storage = StorageService();

  bool _isLoggedIn = false;
  Map<String, dynamic>? _currentUser;

  bool get isLoggedIn => _isLoggedIn;
  Map<String, dynamic>? get currentUser => _currentUser;
  bool get isAdmin =>
      _currentUser?['role'] == 'admin' || _currentUser?['is_admin'] == true;

  Future<bool> restoreSession() async {
    final token = await _storage.getToken();
    if (token == null) return false;
    try {
      final user = await _api.getProfile();
      _currentUser = user;
      await _storage.saveUser(user);
      _isLoggedIn = true;
      return true;
    } catch (_) {
      final cached = _storage.getUser();
      if (cached != null) {
        _currentUser = cached;
        _isLoggedIn  = true;
        return true;
      }
      await _storage.clearTokens();
      return false;
    }
  }

  // Login — accepts email or username
  Future<Map<String, dynamic>> login(String usernameOrEmail, String password) async {
    final resp = await _api.login(usernameOrEmail, password);
    final token = resp['access_token'] as String?;
    if (token == null) throw Exception(resp['detail'] ?? 'Login gagal');
    await _storage.setToken(token);
    if (resp['refresh_token'] != null) {
      await _storage.setRefreshToken(resp['refresh_token'] as String);
    }
    final user = resp['user'] as Map<String, dynamic>? ?? await _api.getProfile();
    _currentUser = user;
    await _storage.saveUser(user);
    _isLoggedIn = true;
    return user;
  }

  // Step 1: send OTP to email
  Future<void> sendOtp(String email, String username) async {
    await _api.sendOtp(email, username);
  }

  // Step 2: register with OTP
  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    required String otp,
    String fullName = '',
  }) async {
    final resp = await _api.register(
      username: username,
      email:    email,
      password: password,
      otp:      otp,
      fullName: fullName,
    );
    final token = resp['access_token'] as String?;
    if (token == null) throw Exception(resp['detail'] ?? 'Registrasi gagal');
    await _storage.setToken(token);
    if (resp['refresh_token'] != null) {
      await _storage.setRefreshToken(resp['refresh_token'] as String);
    }
    final user = resp['user'] as Map<String, dynamic>? ?? await _api.getProfile();
    _currentUser = user;
    await _storage.saveUser(user);
    _isLoggedIn = true;
    return user;
  }

  Future<void> logout() async {
    _isLoggedIn  = false;
    _currentUser = null;
    await _storage.clearAll();
  }

  Future<Map<String, dynamic>> updateProfile(Map<String, dynamic> data) async {
    final updated = await _api.updateProfile(data);
    _currentUser = {...?_currentUser, ...updated};
    await _storage.saveUser(_currentUser!);
    return _currentUser!;
  }

  void updateUserField(String key, dynamic value) {
    if (_currentUser != null) {
      _currentUser![key] = value;
      _storage.saveUser(_currentUser!);
    }
  }
}
