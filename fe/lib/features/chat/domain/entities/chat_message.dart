import '../value_objects/message_content.dart';
import 'chat_author.dart';

class ChatMessage {
  const ChatMessage({
    required this.id,
    required this.author,
    required this.content,
    required this.createdAt,
  });

  final String id;
  final ChatAuthor author;
  final String content;
  final DateTime createdAt;

  factory ChatMessage.doctor({
    required String id,
    required MessageContent content,
    required DateTime createdAt,
  }) {
    return ChatMessage(
      id: id,
      author: ChatAuthor.doctor,
      content: content.value,
      createdAt: createdAt,
    );
  }

  factory ChatMessage.assistant({
    required String id,
    required String content,
    required DateTime createdAt,
  }) {
    return ChatMessage(
      id: id,
      author: ChatAuthor.assistant,
      content: content.trim(),
      createdAt: createdAt,
    );
  }
}
