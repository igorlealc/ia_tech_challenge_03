import 'package:dio/dio.dart';
import 'package:logging/logging.dart';

import '../config/app_config.dart';
import '../errors/api_error.dart';
import '../errors/app_exception.dart';

class ApiClient {
  static const _requestTimeout = Duration(seconds: 360);

  ApiClient({
    required AppConfig config,
    Dio? dio,
    Logger? logger,
  })  : _dio = dio ?? Dio(),
        _logger = logger ?? Logger('ApiClient') {
    _dio.options = BaseOptions(
      baseUrl: config.apiBaseUrl,
      connectTimeout: _requestTimeout,
      sendTimeout: _requestTimeout,
      receiveTimeout: _requestTimeout,
      headers: {'Accept': 'application/json'},
    );
  }

  final Dio _dio;
  final Logger _logger;

  Future<Map<String, dynamic>> postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(path, data: body);
      return response.data ?? <String, dynamic>{};
    } on DioException catch (exception, stackTrace) {
      _logger.warning('HTTP request failed', exception, stackTrace);
      throw _mapDioException(exception);
    } catch (exception, stackTrace) {
      _logger.severe('Unexpected HTTP failure', exception, stackTrace);
      throw AppException.unexpected();
    }
  }

  AppException _mapDioException(DioException exception) {
    final data = exception.response?.data;
    if (data is Map<String, dynamic>) {
      return AppException(ApiError.fromJson(data));
    }

    return const AppException(
      ApiError(
        code: 'NETWORK_ERROR',
        message: 'Nao foi possivel comunicar com o servidor.',
      ),
    );
  }
}
