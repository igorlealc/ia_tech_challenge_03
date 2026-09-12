import '../../domain/entities/chat_message.dart';
import '../../domain/entities/chat_transcript.dart';
import '../../domain/repositories/medical_chat_repository.dart';
import '../../domain/value_objects/message_content.dart';
import '../clients/medical_chat_api_client.dart';
import '../dtos/chat_request_dto.dart';
import '../mappers/chat_message_mapper.dart';

class FakeMedicalChatRepository implements MedicalChatRepository {
  const FakeMedicalChatRepository({
    required MedicalChatApiClient client,
    ChatMessageMapper mapper = const ChatMessageMapper(),
  })  : _client = client,
        _mapper = mapper;

  final MedicalChatApiClient _client;
  final ChatMessageMapper _mapper;

  @override
  Future<ChatMessage> sendMessage({
    required MessageContent message,
    required ChatTranscript transcript,
  }) async {
    // TODO: trocar por HttpMedicalChatApiClient quando o backend existir.
    final response = await _client.sendMessage(
      ChatRequestDto(
        message: message.value,
        conversation: transcript.messages.map(_mapper.toDto).toList(),
      ),
    );
    return _mapper.toEntity(response.message);
  }
}
