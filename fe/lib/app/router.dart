import 'package:get_it/get_it.dart';
import 'package:go_router/go_router.dart';

import '../features/chat/presentation/pages/chat_page.dart';
import '../features/chat/presentation/presenters/chat_presenter.dart';

GoRouter createAppRouter(GetIt serviceLocator) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(
        path: '/',
        builder: (context, state) {
          return ChatPage(
            presenter: serviceLocator<ChatPresenter>(),
          );
        },
      ),
    ],
  );
}
