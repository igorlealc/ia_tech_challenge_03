import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';

import '../core/config/app_config.dart';
import '../core/http/api_client.dart';
import '../core/logging/app_logger.dart';
import '../features/chat/data/clients/http_medical_chat_api_client.dart';
import '../features/chat/data/clients/medical_chat_api_client.dart';
import '../features/chat/data/repositories/fake_medical_chat_repository.dart';
import '../features/chat/domain/repositories/medical_chat_repository.dart';
import '../features/chat/domain/usecases/send_medical_chat_message.dart';
import '../features/chat/presentation/presenters/chat_presenter.dart';
import 'router.dart';

class AppBootstrap {
  AppBootstrap({GetIt? serviceLocator})
      : _serviceLocator = serviceLocator ?? GetIt.instance;

  final GetIt _serviceLocator;

  GoRouter get router => _serviceLocator<GoRouter>();

  void configure() {
    if (_serviceLocator.isRegistered<GoRouter>()) {
      return;
    }

    AppLogger.configure();
    _registerCore();
    _registerChat();
    _serviceLocator.registerLazySingleton<GoRouter>(
      () => createAppRouter(_serviceLocator),
    );
  }

  void _registerCore() {
    _serviceLocator.registerLazySingleton<AppConfig>(AppConfig.fromEnvironment);
    _serviceLocator.registerLazySingleton<ApiClient>(
      () => ApiClient(config: _serviceLocator<AppConfig>()),
    );
  }

  void _registerChat() {
    _serviceLocator.registerLazySingleton<MedicalChatApiClient>(
      () => HttpMedicalChatApiClient(apiClient: _serviceLocator<ApiClient>()),
    );
    _serviceLocator.registerLazySingleton<MedicalChatRepository>(
      () => FakeMedicalChatRepository(
        client: _serviceLocator<MedicalChatApiClient>(),
      ),
    );
    _serviceLocator.registerFactory(
      () => SendMedicalChatMessage(
        repository: _serviceLocator<MedicalChatRepository>(),
      ),
    );
    _serviceLocator.registerFactory(
      () => ChatPresenter(
        sendMedicalChatMessage: _serviceLocator<SendMedicalChatMessage>(),
      ),
    );
  }
}
