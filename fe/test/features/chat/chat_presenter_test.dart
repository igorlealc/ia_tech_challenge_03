import 'package:flutter_test/flutter_test.dart';
import 'package:medical_ai_chat/core/errors/api_error.dart';
import 'package:medical_ai_chat/core/errors/app_exception.dart';
import 'package:medical_ai_chat/features/chat/domain/entities/chat_message.dart';
import 'package:medical_ai_chat/features/chat/domain/entities/chat_transcript.dart';
import 'package:medical_ai_chat/features/chat/domain/repositories/medical_chat_repository.dart';
import 'package:medical_ai_chat/features/chat/domain/usecases/send_medical_chat_message.dart';
import 'package:medical_ai_chat/features/chat/domain/value_objects/message_content.dart';
import 'package:medical_ai_chat/features/chat/presentation/presenters/chat_presenter.dart';

void main() {
  test('adds doctor and assistant messages on success', () async {
    final presenter = ChatPresenter(
      sendMedicalChatMessage: SendMedicalChatMessage(
        repository: _SuccessfulMedicalChatRepository(),
      ),
    );

    await presenter.send('Febre e tosse.');

    expect(presenter.value.messages, hasLength(2));
    expect(presenter.value.isLoading, isFalse);
    expect(presenter.value.hasError, isFalse);
  });

  test('exposes error state when repository fails', () async {
    final presenter = ChatPresenter(
      sendMedicalChatMessage: SendMedicalChatMessage(
        repository: _FailingMedicalChatRepository(),
      ),
    );

    await presenter.send('Falhar');

    expect(presenter.value.messages, hasLength(1));
    expect(presenter.value.errorCode, 'FAKE_FAILURE');
    expect(presenter.value.isLoading, isFalse);
  });

  test('clears in-memory conversation', () async {
    final presenter = ChatPresenter(
      sendMedicalChatMessage: SendMedicalChatMessage(
        repository: _SuccessfulMedicalChatRepository(),
      ),
    );

    await presenter.send('Limpar depois');
    presenter.clearConversation();

    expect(presenter.value.messages, isEmpty);
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
      content: 'Resposta academica',
      createdAt: DateTime(2026),
    );
  }
}

class _FailingMedicalChatRepository implements MedicalChatRepository {
  @override
  Future<ChatMessage> sendMessage({
    required MessageContent message,
    required ChatTranscript transcript,
  }) async {
    throw const AppException(
      ApiError(
        code: 'FAKE_FAILURE',
        message: 'Falha simulada.',
      ),
    );
  }
}
