import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class MessageComposer extends StatefulWidget {
  const MessageComposer({
    required this.isLoading,
    required this.onSend,
    super.key,
  });

  final bool isLoading;
  final ValueChanged<String> onSend;

  @override
  State<MessageComposer> createState() => _MessageComposerState();
}

class _MessageComposerState extends State<MessageComposer> {
  final TextEditingController _textController = TextEditingController();
  final FocusNode _focusNode = FocusNode();

  @override
  void didUpdateWidget(covariant MessageComposer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.isLoading && !widget.isLoading && mounted) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _focusNode.requestFocus();
        }
      });
    }
  }

  @override
  void dispose() {
    _focusNode.dispose();
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Expanded(
          child: TextField(
            key: ValueKey(widget.isLoading),
            controller: _textController,
            focusNode: _focusNode,
            readOnly: widget.isLoading,
            minLines: 1,
            maxLines: 5,
            textInputAction: TextInputAction.newline,
            decoration: const InputDecoration(
              hintText: 'Mensagem do medico',
            ),
            onSubmitted: _handleSubmitted,
          ),
        ),
        const SizedBox(width: 8),
        IconButton.filled(
          tooltip: 'Enviar mensagem',
          onPressed: widget.isLoading ? null : _send,
          icon: widget.isLoading
              ? const SizedBox.square(
                  dimension: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.send),
        ),
      ],
    );
  }

  void _handleSubmitted(String value) {
    if (widget.isLoading) {
      return;
    }

    if (!HardwareKeyboard.instance.isShiftPressed) {
      _send();
    }
  }

  void _send() {
    if (widget.isLoading) {
      return;
    }

    final text = _textController.text;
    if (text.trim().isEmpty) {
      return;
    }

    widget.onSend(text);
    _textController.clear();
    _focusNode.requestFocus();
  }
}
