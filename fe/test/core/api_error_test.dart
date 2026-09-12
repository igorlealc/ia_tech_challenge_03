import 'package:flutter_test/flutter_test.dart';
import 'package:medical_ai_chat/core/errors/api_error.dart';

void main() {
  test('parses standardized API error', () {
    final error = ApiError.fromJson({
      'code': 'INVALID_REQUEST',
      'message': 'Parametro invalido.',
    });

    expect(error.code, 'INVALID_REQUEST');
    expect(error.message, 'Parametro invalido.');
  });
}
