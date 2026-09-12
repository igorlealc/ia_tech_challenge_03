import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:medical_ai_chat/core/errors/api_error.dart';
import 'package:medical_ai_chat/core/errors/app_exception.dart';
import 'package:medical_ai_chat/features/chat/domain/entities/chat_message.dart';
import 'package:medical_ai_chat/features/chat/domain/entities/chat_transcript.dart';
import 'package:medical_ai_chat/features/chat/domain/repositories/medical_chat_repository.dart';
import 'package:medical_ai_chat/features/chat/domain/usecases/send_medical_chat_message.dart';
import 'package:medical_ai_chat/features/chat/domain/value_objects/message_content.dart';
import 'package:medical_ai_chat/features/chat/presentation/pages/chat_page.dart';
import 'package:medical_ai_chat/features/chat/presentation/presenters/chat_presenter.dart';

void main() {
  testWidgets('shows empty chat state', (tester) async {
    await tester.pumpWidget(_buildPage(_SuccessfulMedicalChatRepository()));

    expect(find.text('Inicie a conversa clinica academica'), findsOneWidget);
    expect(find.text('Mensagem do medico'), findsOneWidget);
  });

  testWidgets('shows loading while assistant answers', (tester) async {
    await tester.pumpWidget(_buildPage(_SlowMedicalChatRepository()));

    await tester.enterText(find.byType(TextField), 'Conduta academica?');
    await tester.tap(find.byIcon(Icons.send));
    await tester.pump();

    expect(find.text('IA respondendo'), findsWidgets);
  });

  testWidgets('shows error message when assistant fails', (tester) async {
    await tester.pumpWidget(_buildPage(_FailingMedicalChatRepository()));

    await tester.enterText(find.byType(TextField), 'Falhar');
    await tester.tap(find.byIcon(Icons.send));
    await tester.pumpAndSettle();

    expect(find.textContaining('Falha simulada.'), findsOneWidget);
  });
}

Widget _buildPage(MedicalChatRepository repository) {
  return MaterialApp(
    home: ChatPage(
      presenter: ChatPresenter(
        sendMedicalChatMessage: SendMedicalChatMessage(
          repository: repository,
        ),
      ),
    ),
  );
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

class _SlowMedicalChatRepository implements MedicalChatRepository {
  @override
  Future<ChatMessage> sendMessage({
    required MessageContent message,
    required ChatTranscript transcript,
  }) {
    return Future<ChatMessage>.delayed(
      const Duration(seconds: 1),
      () => ChatMessage.assistant(
        id: 'assistant-test',
        content: 'Resposta academica lenta',
        createdAt: DateTime(2026),
      ),
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
