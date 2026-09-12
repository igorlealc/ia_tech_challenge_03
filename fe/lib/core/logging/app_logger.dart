import 'package:logging/logging.dart';

class AppLogger {
  const AppLogger._();

  static void configure() {
    Logger.root.level = Level.INFO;
  }
}
