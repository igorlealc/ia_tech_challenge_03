import 'package:flutter/material.dart';

import '../../../../shared/widgets/error_banner.dart';
import '../presenters/chat_presenter.dart';
import '../presenters/chat_state.dart';
import '../widgets/chat_header.dart';
import '../widgets/empty_chat_view.dart';
import '../widgets/message_composer.dart';
import '../widgets/message_list.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({
    required this.presenter,
    super.key,
  });

  final ChatPresenter presenter;

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  @override
  void dispose() {
    widget.presenter.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: ValueListenableBuilder<ChatState>(
          valueListenable: widget.presenter,
          builder: (context, state, child) {
            return _ChatLayout(
              state: state,
              onSend: widget.presenter.send,
              onClear: widget.presenter.clearConversation,
            );
          },
        ),
      ),
    );
  }
}

class _ChatLayout extends StatelessWidget {
  const _ChatLayout({
    required this.state,
    required this.onSend,
    required this.onClear,
  });

  final ChatState state;
  final ValueChanged<String> onSend;
  final VoidCallback onClear;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ChatHeader(
          isLoading: state.isLoading,
          canClear: state.hasMessages,
          onClear: onClear,
        ),
        Expanded(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 960),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: state.hasMessages
                  ? MessageList(
                      messages: state.messages,
                      isLoading: state.isLoading,
                    )
                  : const EmptyChatView(),
            ),
          ),
        ),
        _ChatFooter(
          state: state,
          onSend: onSend,
        ),
      ],
    );
  }
}

class _ChatFooter extends StatelessWidget {
  const _ChatFooter({
    required this.state,
    required this.onSend,
  });

  final ChatState state;
  final ValueChanged<String> onSend;

  @override
  Widget build(BuildContext context) {
    return ColoredBox(
      color: Theme.of(context).colorScheme.surface,
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 960),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (state.hasError)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: ErrorBanner(
                      message: state.errorMessage!,
                      code: state.errorCode ?? 'UNKNOWN_ERROR',
                    ),
                  ),
                MessageComposer(
                  isLoading: state.isLoading,
                  onSend: onSend,
                ),
                const SizedBox(height: 8),
                Text(
                  'Uso academico: respostas simuladas ou experimentais nao '
                  'substituem avaliacao clinica real.',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
