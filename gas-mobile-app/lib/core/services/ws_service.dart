import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../constants/app_constants.dart';
import 'storage_service.dart';

class WsService {
  static final WsService _instance = WsService._internal();
  factory WsService() => _instance;
  WsService._internal();

  final _storage = StorageService();

  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>>? _tickController;
  bool _reconnecting = false;
  Timer? _pingTimer;
  Timer? _reconnectTimer;

  Stream<Map<String, dynamic>> get tickStream =>
      (_tickController ??= StreamController.broadcast()).stream;

  Future<void> connect() async {
    if (_channel != null) return;
    _tickController ??= StreamController.broadcast();

    final token = await _storage.getToken();
    final uri = Uri.parse(
      '${AppConstants.terminalWs}${token != null ? '?token=$token' : ''}',
    );

    try {
      _channel = WebSocketChannel.connect(uri);
      _channel!.stream.listen(
        _onMessage,
        onDone: _onDisconnect,
        onError: _onError,
        cancelOnError: false,
      );
      _startPing();
    } catch (e) {
      _scheduleReconnect();
    }
  }

  void _onMessage(dynamic raw) {
    try {
      final data = jsonDecode(raw as String) as Map<String, dynamic>;
      _tickController?.add(data);
    } catch (_) {}
  }

  void _onDisconnect() {
    _channel = null;
    _pingTimer?.cancel();
    if (!_reconnecting) _scheduleReconnect();
  }

  void _onError(dynamic error) {
    _channel = null;
    _pingTimer?.cancel();
    if (!_reconnecting) _scheduleReconnect();
  }

  void _startPing() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      try { _channel?.sink.add('ping'); } catch (_) {}
    });
  }

  void _scheduleReconnect() {
    if (_reconnecting) return;
    _reconnecting = true;
    _reconnectTimer = Timer(const Duration(seconds: 5), () {
      _reconnecting = false;
      connect();
    });
  }

  void subscribe(List<String> symbols) {
    try {
      _channel?.sink.add(jsonEncode({
        'action': 'subscribe',
        'symbols': symbols,
      }));
    } catch (_) {}
  }

  void disconnect() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
  }

  void dispose() {
    disconnect();
    _tickController?.close();
    _tickController = null;
  }
}
