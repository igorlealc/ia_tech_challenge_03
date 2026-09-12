import 'package:flutter_test/flutter_test.dart';
import 'package:medical_ai_chat/features/chat/domain/entities/chat_message.dart';
import 'package:medical_ai_chat/features/chat/domain/entities/chat_transcript.dart';
import 'package:medical_ai_chat/features/chat/domain/repositories/medical_chat_repository.dart';
import 'package:medical_ai_chat/features/chat/domain/usecases/send_medical_chat_message.dart';
import 'package:medical_ai_chat/features/chat/domain/value_objects/message_content.dart';

void main() {
  test('returns assistant response through repository contract', () async {
    final useCase = SendMedicalChatMessage(
      repository: _SuccessfulMedicalChatRepository(),
    );

    final response = await useCase(
      message: 'Paciente com dor toracica.',
      transcript: const ChatTranscript.empty(),
    );

    expect(response.content, contains('Resposta academica'));
  });
}

class _SuccessfulMedicalChatRepository implements MedicalChatRepository {
  @override
  Future<ChatMessage> sendMessage({
    required MessageContent message,
    required ChatTranscript transcript,
  }) async {
    return ChatMessage.assistant(
      id: 'assistant-test',
      content: 'Resposta academica para ${message.value}',
      createdAt: DateTime(2026),
    );
  }
}
