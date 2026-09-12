import '../../domain/entities/chat_author.dart';

class ChatMessageDto {
  const ChatMessageDto({
    required this.role,
    required this.content,
  });

  factory ChatMessageDto.fromJson(Map<String, dynamic> json) {
    return ChatMessageDto(
      role: json['role']?.toString() ?? ChatAuthor.assistant.name,
      content: json['content']?.toString() ?? '',
    );
  }

  final String role;
  final String content;

  Map<String, dynamic> toJson() {
    return {
      'role': role,
      'content': content,
    };
  }
}
