import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../domain/entities/chat_author.dart';
import '../../domain/entities/chat_message.dart';

class ChatMessageBubble extends StatelessWidget {
  const ChatMessageBubble({
    required this.message,
    super.key,
  });

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final isDoctor = message.author == ChatAuthor.doctor;
    final scheme = Theme.of(context).colorScheme;
    final background = isDoctor
        ? scheme.primaryContainer
        : scheme.surfaceContainerHighest;
    final foreground = isDoctor
        ? scheme.onPrimaryContainer
        : scheme.onSurfaceVariant;

    return Align(
      alignment: isDoctor ? Alignment.centerRight : Alignment.centerLeft,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 680),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 6),
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: background,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          message.author.label,
                          style:
                              Theme.of(context).textTheme.labelMedium?.copyWith(
                                    color: foreground,
                                    fontWeight: FontWeight.w700,
                                  ),
                        ),
                      ),
                      if (!isDoctor)
                        IconButton(
                          tooltip: 'Copiar resposta',
                          visualDensity: VisualDensity.compact,
                          onPressed: () => _copyMessage(context),
                          icon: Icon(
                            Icons.copy,
                            size: 18,
                            color: foreground,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    message.content,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: foreground,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _copyMessage(BuildContext context) async {
    await Clipboard.setData(ClipboardData(text: message.content));
    if (!context.mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Resposta copiada'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
