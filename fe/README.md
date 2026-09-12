# Medical AI Chat

Aplicacao Flutter Web academica para simular um terminal de chat entre medico e IA.

## Executar

```bash
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8010
```

## Docker

```bash
docker build -t medical-ai-chat-fe .
docker run -p 8080:80 medical-ai-chat-fe
```

Com URL de API diferente:

```bash
docker build -t medical-ai-chat-fe --build-arg API_BASE_URL=http://localhost:8010 .
docker run -p 8080:80 medical-ai-chat-fe
```

Acesse em `http://localhost:8080`.

## Escopo

- Tela unica de chat na rota `/`.
- Conversas mantidas apenas em memoria durante a sessao.
- Sem login, historico, banco, `localStorage`, `IndexedDB` ou cookies.
- Integracao HTTP com o backend local em `POST /chat/messages`.

## Validacao

```bash
dart format .
flutter analyze
flutter test
```
