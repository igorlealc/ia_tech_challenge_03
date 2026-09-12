import '../dtos/chat_message_dto.dart';
import '../dtos/chat_request_dto.dart';
import '../dtos/chat_response_dto.dart';
import 'medical_chat_api_client.dart';

class FakeMedicalChatApiClient implements MedicalChatApiClient {
  @override
  Future<ChatResponseDto> sendMessage(ChatRequestDto request) async {
    await Future<void>.delayed(const Duration(milliseconds: 450));
    return ChatResponseDto(
      message: ChatMessageDto(
        role: 'assistant',
        content: _buildResponse(request.message),
      ),
    );
  }

  String _buildResponse(String message) {
    return 'Resposta simulada para fins academicos: revisei a mensagem '
        '"$message". Considere correlacionar os achados clinicos, historico, '
        'exame fisico e exames complementares antes de qualquer decisao.';
  }
}
