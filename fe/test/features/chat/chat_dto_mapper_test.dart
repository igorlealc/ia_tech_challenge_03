import 'package:flutter_test/flutter_test.dart';
import 'package:medical_ai_chat/features/chat/data/dtos/chat_response_dto.dart';
import 'package:medical_ai_chat/features/chat/data/mappers/chat_message_mapper.dart';
import 'package:medical_ai_chat/features/chat/domain/entities/chat_author.dart';

void main() {
  test('parses chat response DTO and maps assistant message', () {
    final response = ChatResponseDto.fromJson({
      'message': {
        'role': 'assistant',
        'content': 'Resposta simulada.',
      },
    });

    final entity = const ChatMessageMapper().toEntity(response.message);

    expect(entity.author, ChatAuthor.assistant);
    expect(entity.content, 'Resposta simulada.');
  });
}
