import 'package:flutter/material.dart';

import 'app/app.dart';
import 'app/bootstrap.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final bootstrap = AppBootstrap();
  bootstrap.configure();
  runApp(MedicalAiChatApp(router: bootstrap.router));
}
