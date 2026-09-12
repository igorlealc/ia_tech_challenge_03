import '../../../../core/http/api_client.dart';
import '../dtos/chat_request_dto.dart';
import '../dtos/chat_response_dto.dart';
import 'medical_chat_api_client.dart';

class HttpMedicalChatApiClient implements MedicalChatApiClient {
  const HttpMedicalChatApiClient({
    required ApiClient apiClient,
  }) : _apiClient = apiClient;

  final ApiClient _apiClient;

  @override
  Future<ChatResponseDto> sendMessage(ChatRequestDto request) async {
    final json = await _apiClient.postJson(
      '/chat/messages',
      request.toJson(),
    );
    return ChatResponseDto.fromJson(json);
  }
}
