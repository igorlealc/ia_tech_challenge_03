---
appliesTo: "**/*.dart"
---

# Dart Coding Standards

- Use Dart null safety e mantenha tipos explicitos em APIs publicas.
- Use arquivos em `snake_case`, classes em `PascalCase` e membros em `camelCase`.
- Prefira objetos imutaveis, `const` e `final` sempre que isso mantiver clareza.
- Evite `print`; use `logging` para logs tecnicos.
- Mantenha funcoes e classes pequenas, com uma responsabilidade clara.
- Use `async` e `await` com tratamento de erro explicito.
- DTOs devem ficar na camada `data` e nao devem aparecer em widgets.
- Aplique Object Calisthenics de forma pragmatica, principalmente em dominio,
  use cases, presenters e mappers.
