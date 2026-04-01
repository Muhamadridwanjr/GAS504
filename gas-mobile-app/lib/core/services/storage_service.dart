import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/app_constants.dart';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  final _secure = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );

  SharedPreferences? _prefs;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // ── Secure ─────────────────────────────────────────────────────────────────
  Future<void> setToken(String token) =>
      _secure.write(key: AppConstants.keyToken, value: token);

  Future<String?> getToken() =>
      _secure.read(key: AppConstants.keyToken);

  Future<void> setRefreshToken(String token) =>
      _secure.write(key: AppConstants.keyRefresh, value: token);

  Future<String?> getRefreshToken() =>
      _secure.read(key: AppConstants.keyRefresh);

  Future<void> clearTokens() async {
    await _secure.delete(key: AppConstants.keyToken);
    await _secure.delete(key: AppConstants.keyRefresh);
  }

  // ── User cache ─────────────────────────────────────────────────────────────
  Future<void> saveUser(Map<String, dynamic> user) async {
    _prefs?.setString(AppConstants.keyUser, jsonEncode(user));
  }

  Map<String, dynamic>? getUser() {
    final raw = _prefs?.getString(AppConstants.keyUser);
    if (raw == null) return null;
    try { return jsonDecode(raw) as Map<String, dynamic>; }
    catch (_) { return null; }
  }

  Future<void> clearUser() async {
    await _prefs?.remove(AppConstants.keyUser);
  }

  // ── Biometric ──────────────────────────────────────────────────────────────
  Future<void> setBiometricEnabled(bool val) async {
    await _prefs?.setBool(AppConstants.keyBiometric, val);
  }

  bool get biometricEnabled =>
      _prefs?.getBool(AppConstants.keyBiometric) ?? false;

  // ── Generic prefs ─────────────────────────────────────────────────────────
  Future<void> setBool(String key, bool val) async =>
      _prefs?.setBool(key, val);

  bool? getBool(String key) => _prefs?.getBool(key);

  Future<void> setString(String key, String val) async =>
      _prefs?.setString(key, val);

  String? getString(String key) => _prefs?.getString(key);

  // ── Clear all ─────────────────────────────────────────────────────────────
  Future<void> clearAll() async {
    await clearTokens();
    await clearUser();
    await _prefs?.clear();
  }
}
