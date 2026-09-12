import '../entities/chat_message.dart';
import '../entities/chat_transcript.dart';
import '../value_objects/message_content.dart';

abstract interface class MedicalChatRepository {
  Future<ChatMessage> sendMessage({
    required MessageContent message,
    required ChatTranscript transcript,
  });
}
