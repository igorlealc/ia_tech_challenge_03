import '../../domain/entities/chat_author.dart';
import '../../domain/entities/chat_message.dart';
import '../dtos/chat_message_dto.dart';

class ChatMessageMapper {
  const ChatMessageMapper();

  ChatMessageDto toDto(ChatMessage message) {
    return ChatMessageDto(
      role: message.author.name,
      content: message.content,
    );
  }

  ChatMessage toEntity(ChatMessageDto dto) {
    return ChatMessage(
      id: 'assistant-${DateTime.now().microsecondsSinceEpoch}',
      author: _authorFromRole(dto.role),
      content: dto.content,
      createdAt: DateTime.now(),
    );
  }

  ChatAuthor _authorFromRole(String role) {
    if (role == ChatAuthor.doctor.name) {
      return ChatAuthor.doctor;
    }

    return ChatAuthor.assistant;
  }
}
