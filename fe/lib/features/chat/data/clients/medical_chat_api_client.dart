import '../dtos/chat_request_dto.dart';
import '../dtos/chat_response_dto.dart';

abstract interface class MedicalChatApiClient {
  Future<ChatResponseDto> sendMessage(ChatRequestDto request);
}
