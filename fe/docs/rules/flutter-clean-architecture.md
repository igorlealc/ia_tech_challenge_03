---
appliesTo: "lib/features/**"
---

# Flutter Clean Architecture

- Organize codigo por feature com `data`, `domain` e `presentation`.
- `domain` contem entidades, value objects, repositories abstratos e use cases.
- `data` contem clients, DTOs, mappers e repositories concretos.
- `presentation` contem pages, presenters, estados e widgets da feature.
- Widgets nao podem chamar HTTP, DTOs ou repositories diretamente.
- Use cases dependem apenas de contratos de dominio.
- A feature principal deste projeto e `chat`, com conversa medico-IA em memoria.
