import 'package:flutter_test/flutter_test.dart';
import 'package:medical_ai_chat/core/config/app_config.dart';

void main() {
  test('uses local API base URL by default', () {
    final config = AppConfig.fromEnvironment();

    expect(config.apiBaseUrl, 'http://localhost:8010');
  });
}
