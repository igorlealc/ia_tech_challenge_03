---
appliesTo: "test/**/*.dart"
---

# Testing Standards

- Use `flutter_test` para testes unitarios e widget tests.
- Prefira fakes simples antes de mocks.
- Cubra value objects, DTOs, mappers, use cases, presenters e widgets.
- Testes de presenter devem validar loading, sucesso, erro e limpeza de estado.
- Widget tests devem validar estado vazio, carregamento e erro da tela de chat.
- Nao dependa de backend real nos testes desta primeira versao.
- Siga Arrange, Act, Assert para manter intencao clara.
