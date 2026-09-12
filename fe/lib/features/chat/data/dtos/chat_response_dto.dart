import 'chat_message_dto.dart';

class ChatResponseDto {
  const ChatResponseDto({
    required this.message,
  });

  factory ChatResponseDto.fromJson(Map<String, dynamic> json) {
    final message = json['message'];
    return ChatResponseDto(
      message: ChatMessageDto.fromJson(
        message is Map<String, dynamic> ? message : <String, dynamic>{},
      ),
    );
  }

  final ChatMessageDto message;
}
