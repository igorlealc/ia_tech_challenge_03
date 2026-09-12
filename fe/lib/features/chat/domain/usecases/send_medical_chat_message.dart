import '../entities/chat_message.dart';
import '../entities/chat_transcript.dart';
import '../repositories/medical_chat_repository.dart';
import '../value_objects/message_content.dart';

class SendMedicalChatMessage {
  const SendMedicalChatMessage({
    required MedicalChatRepository repository,
  }) : _repository = repository;

  final MedicalChatRepository _repository;

  Future<ChatMessage> call({
    required String message,
    required ChatTranscript transcript,
  }) {
    return _repository.sendMessage(
      message: MessageContent(message),
      transcript: transcript,
    );
  }
}
