import 'chat_message.dart';

class ChatTranscript {
  const ChatTranscript(List<ChatMessage> messages)
      : _messages = messages;

  const ChatTranscript.empty() : _messages = const [];

  final List<ChatMessage> _messages;

  List<ChatMessage> get messages => List.unmodifiable(_messages);

  bool get isEmpty => _messages.isEmpty;

  ChatTranscript add(ChatMessage message) {
    return ChatTranscript([..._messages, message]);
  }

  ChatTranscript addAll(List<ChatMessage> messages) {
    return ChatTranscript([..._messages, ...messages]);
  }
}
