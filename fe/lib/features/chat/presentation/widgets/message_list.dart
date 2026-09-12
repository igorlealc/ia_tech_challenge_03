import 'package:flutter/material.dart';

import '../../domain/entities/chat_message.dart';
import 'chat_message_bubble.dart';

class MessageList extends StatelessWidget {
  const MessageList({
    required this.messages,
    required this.isLoading,
    super.key,
  });

  final List<ChatMessage> messages;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    final itemCount = messages.length + (isLoading ? 1 : 0);
    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 16),
      itemCount: itemCount,
      itemBuilder: (context, index) {
        if (index >= messages.length) {
          return const _AssistantTypingIndicator();
        }

        return ChatMessageBubble(message: messages[index]);
      },
    );
  }
}

class _AssistantTypingIndicator extends StatelessWidget {
  const _AssistantTypingIndicator();

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 6),
        child: Chip(
          avatar: const SizedBox.square(
            dimension: 14,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          label: const Text('IA respondendo'),
          side: BorderSide.none,
        ),
      ),
    );
  }
}
