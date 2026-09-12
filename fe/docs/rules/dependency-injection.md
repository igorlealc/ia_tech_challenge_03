---
appliesTo: "lib/app/bootstrap.dart"
---

# Dependency Injection

- Use DI por construtor em todas as classes com dependencias.
- Use `get_it` apenas no composition root em `lib/app/bootstrap.dart`.
- Registre configuracao, clients, repositories, use cases e factories de
  presenters no bootstrap.
- Widgets recebem presenters por construtor.
- Nao acessar `GetIt.instance` diretamente dentro de widgets, use cases,
  repositories ou clients.
