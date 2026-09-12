---
appliesTo: "**"
---

# Project Structure

Estrutura base esperada:

```text
lib/
  app/
  core/
  features/
    chat/
      data/
      domain/
      presentation/
  shared/
test/
docs/rules/
web/
```

- `app` contem bootstrap, app widget e router.
- `core` contem configuracao, HTTP, erros, logging e tema.
- `shared` contem widgets reutilizaveis sem regra de negocio.
- `features/chat` contem a experiencia principal da aplicacao.
- `prompt` pode manter arquivos de instrucao academica e nao faz parte do app.
