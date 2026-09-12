import 'api_error.dart';

class AppException implements Exception {
  const AppException(this.error);

  factory AppException.unexpected() {
    return const AppException(
      ApiError(
        code: 'UNEXPECTED_ERROR',
        message: 'Nao foi possivel concluir a operacao.',
      ),
    );
  }

  final ApiError error;

  @override
  String toString() => '${error.code}: ${error.message}';
}
