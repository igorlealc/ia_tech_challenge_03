import '../../domain/entities/chat_message.dart';
import '../../domain/entities/chat_transcript.dart';

class ChatState {
  const ChatState({
    required this.transcript,
    required this.isLoading,
    required this.errorCode,
    required this.errorMessage,
  });

  const ChatState.empty()
      : transcript = const ChatTranscript.empty(),
        isLoading = false,
        errorCode = null,
        errorMessage = null;

  final ChatTranscript transcript;
  final bool isLoading;
  final String? errorCode;
  final String? errorMessage;

  List<ChatMessage> get messages => transcript.messages;

  bool get hasMessages => messages.isNotEmpty;

  bool get hasError => errorMessage != null;

  ChatState copyWith({
    ChatTranscript? transcript,
    bool? isLoading,
    String? errorCode,
    String? errorMessage,
    bool clearError = false,
  }) {
    return ChatState(
      transcript: transcript ?? this.transcript,
      isLoading: isLoading ?? this.isLoading,
      errorCode: clearError ? null : errorCode ?? this.errorCode,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
