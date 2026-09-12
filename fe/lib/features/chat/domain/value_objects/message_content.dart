import '../../../../core/errors/api_error.dart';
import '../../../../core/errors/app_exception.dart';

class MessageContent {
  MessageContent(String value) : value = value.trim() {
    if (this.value.isEmpty) {
      throw const AppException(
        ApiError(
          code: 'EMPTY_MESSAGE',
          message: 'Digite uma mensagem antes de enviar.',
        ),
      );
    }

    if (this.value.length > maxLength) {
      throw const AppException(
        ApiError(
          code: 'MESSAGE_TOO_LONG',
          message: 'A mensagem deve ter ate 2000 caracteres.',
        ),
      );
    }
  }

  static const int maxLength = 2000;

  final String value;
}
