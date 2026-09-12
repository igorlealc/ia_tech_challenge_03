import 'package:flutter_test/flutter_test.dart';
import 'package:medical_ai_chat/core/errors/app_exception.dart';
import 'package:medical_ai_chat/features/chat/domain/value_objects/message_content.dart';

void main() {
  test('rejects empty text', () {
    expect(() => MessageContent('   '), throwsA(isA<AppException>()));
  });

  test('keeps valid trimmed text', () {
    final content = MessageContent('  Febre ha dois dias  ');

    expect(content.value, 'Febre ha dois dias');
  });
}
