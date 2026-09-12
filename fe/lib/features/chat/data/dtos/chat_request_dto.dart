import 'chat_message_dto.dart';

class ChatRequestDto {
  const ChatRequestDto({
    required this.message,
    required this.conversation,
  });

  final String message;
  final List<ChatMessageDto> conversation;

  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'conversation': conversation.map((message) => message.toJson()).toList(),
    };
  }
}
