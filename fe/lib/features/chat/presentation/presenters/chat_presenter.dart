import 'package:flutter/foundation.dart';

import '../../../../core/errors/app_exception.dart';
import '../../domain/entities/chat_message.dart';
import '../../domain/usecases/send_medical_chat_message.dart';
import '../../domain/value_objects/message_content.dart';
import 'chat_state.dart';

class ChatPresenter extends ValueNotifier<ChatState> {
  ChatPresenter({
    required SendMedicalChatMessage sendMedicalChatMessage,
  })  : _sendMedicalChatMessage = sendMedicalChatMessage,
        super(const ChatState.empty());

  final SendMedicalChatMessage _sendMedicalChatMessage;

  Future<void> send(String text) async {
    if (value.isLoading) {
      return;
    }

    try {
      final content = MessageContent(text);
      final doctorMessage = ChatMessage.doctor(
        id: 'doctor-${DateTime.now().microsecondsSinceEpoch}',
        content: content,
        createdAt: DateTime.now(),
      );
      final transcript = value.transcript.add(doctorMessage);
      value = value.copyWith(
        transcript: transcript,
        isLoading: true,
        clearError: true,
      );
      final assistantMessage = await _sendMedicalChatMessage(
        message: content.value,
        transcript: transcript,
      );
      value = value.copyWith(
        transcript: value.transcript.add(assistantMessage),
        isLoading: false,
        clearError: true,
      );
    } on AppException catch (exception) {
      value = value.copyWith(
        isLoading: false,
        errorCode: exception.error.code,
        errorMessage: exception.error.message,
      );
    } catch (_) {
      value = value.copyWith(
        isLoading: false,
        errorCode: 'UNEXPECTED_ERROR',
        errorMessage: 'Nao foi possivel obter resposta da IA.',
      );
    }
  }

  void clearConversation() {
    value = const ChatState.empty();
  }
}
