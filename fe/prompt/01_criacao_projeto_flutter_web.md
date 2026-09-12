# Prompt 01 - Criacao do Projeto Frontend Flutter Web

## Contexto

Antes de qualquer acao, use obrigatoriamente a skill:

```text
$flutter_project_creator
```

Atue como um Arquiteto de Software e Desenvolvedor Flutter Senior especialista em Flutter Web, Dart, Clean Architecture, MVP, Object Calisthenics, `go_router`, `get_it`, consumo de APIs REST, acessibilidade, responsividade, testes automatizados e apps web desacoplados.

Crie o projeto frontend Flutter Web em `trabalho3/fe`.

O frontend deve ser uma aplicacao funcional, nao uma landing page. A aplicacao sera um terminal de chat entre medico e IA para fins academicos. Nao implemente persistencia local ou remota de conversas nesta primeira versao. A conversa pode existir apenas em memoria durante a sessao aberta no navegador.

Caso ainda nao exista backend ou contrato REST definitivo, implemente a infraestrutura para consumo de API com contratos isolados, um fake de desenvolvimento para respostas da IA e TODOs tecnicos claros para os pontos pendentes.

## Objetivo

Criar a primeira versao do frontend com:

1. Projeto Flutter Web inicializado em `trabalho3/fe`.
2. Uma unica experiencia principal: tela de chat medico-IA na rota `/`.
3. Clean Architecture por feature.
4. MVP na camada de apresentacao.
5. Estado com `ValueNotifier<TState>` e `ValueListenableBuilder`.
6. DI por construtor com `get_it` no composition root.
7. Rotas web com `go_router`.
8. Client REST configuravel por `API_BASE_URL`.
9. Tema Material 3 centralizado.
10. Layout responsivo para desktop e mobile web.
11. Tratamento padronizado de loading, vazio, erro e sucesso.
12. Testes unitarios e widget tests iniciais.
13. Documentacao inicial e regras do projeto em `docs/rules`.

## Local de criacao

Crie ou evolua o projeto em:

```text
trabalho3/fe/
```

Nao remova pastas existentes do repositorio.

Se `trabalho3/fe/` ja existir, leia o estado real antes de alterar, preserve mudancas existentes e aplique a evolucao incrementalmente.

## Escopo funcional

O sistema deve representar um terminal de chat semelhante a experiencia do ChatGPT, adaptado ao contexto academico de suporte medico.

### Tela unica de chat

Ao abrir `/`, o usuario deve ver diretamente a tela de conversa, sem home operacional, landing page, dashboard, settings ou fluxo de cadastro/login.

A tela deve conter:

- cabecalho compacto com nome da aplicacao e status simples da IA;
- area de mensagens com rolagem;
- estado inicial vazio com orientacao curta para iniciar a conversa;
- bolhas ou linhas de mensagem distinguindo medico e IA;
- campo de texto multiline para o medico digitar;
- botao de envio com icone;
- suporte a envio por teclado quando fizer sentido na web;
- indicador visual enquanto a IA esta "respondendo";
- tratamento de erro quando a chamada de API ou fake falhar;
- acao discreta para limpar a conversa em memoria;
- layout responsivo que funcione bem em desktop e mobile.

Como o trabalho e academico, exiba uma nota curta e discreta na interface informando que as respostas sao simuladas ou experimentais e nao substituem avaliacao clinica real.

### Comportamento esperado

- Mensagens do medico devem ser adicionadas imediatamente ao estado em memoria.
- Enquanto a IA responde, o input pode ficar temporariamente desabilitado ou sinalizar carregamento.
- A resposta da IA deve ser obtida por um use case.
- O use case deve depender de um contrato de repository.
- O repository pode usar um client REST real ou um fake de desenvolvimento.
- Nao persistir mensagens em banco, arquivo, localStorage, IndexedDB ou cookies.
- Nao implementar autenticacao nesta primeira versao.
- Nao criar telas extras de settings, diagnostico ou historico, salvo se indispensavel para inicializacao tecnica do Flutter.

## Stack obrigatoria

- Flutter Web.
- Dart com null safety.
- `flutter_lints`.
- Material 3.
- Clean Architecture por feature.
- MVP na camada de apresentacao.
- Object Calisthenics como orientacao de design de codigo.
- API REST JSON.
- Configuracao de URL do backend por `--dart-define`.
- Testes unitarios e widget tests.

## Dependencias sugeridas

Antes de adicionar dependencias, verifique se ja existem no `pubspec.yaml`.

Use defaults simples e estaveis:

- `go_router`: roteamento web/deep links.
- `get_it`: DI simples e explicita.
- `dio`: client REST.
- `logging`: logs estruturados, sem `print` em producao.

Evite adicionar BLoC, Riverpod, `provider`, `injectable`, `freezed`, `build_runner` ou code generation nesta primeira versao, salvo se o projeto ja usar esse padrao.

## Regras de arquitetura

Seguir os padroes definidos pela skill `$flutter_project_creator` e aplicar:

- Clean Architecture por feature.
- MVP na camada de apresentacao.
- `ValueNotifier<TState>` e `ValueListenableBuilder` para estado.
- DI por construtor com `get_it` no composition root.
- Rotas com `go_router`.
- API HTTP isolada em `lib/core/http`.
- Configuracao em `lib/core/config`.
- Erros padronizados em `lib/core/errors`.
- Tema centralizado em `lib/core/theme`.
- Widgets compartilhados sem regra de negocio em `lib/shared/widgets`.
- Nao misturar regra de apresentacao em clients HTTP.
- Nao colocar regra de negocio diretamente em widgets.
- DTOs nao devem vazar para a camada de `presentation`.
- Presenters devem coordenar eventos da view, estado de UI e chamadas aos use cases.
- Criar testes em `test/features`, `test/core` ou estrutura equivalente seguindo `docs/rules`.

Estrutura sugerida:

```text
trabalho3/fe/
  lib/
    main.dart
    app/
      app.dart
      bootstrap.dart
      router.dart
    core/
      config/
      errors/
      http/
      logging/
      theme/
      widgets/
    features/
      chat/
        data/
          clients/
          dtos/
          mappers/
          repositories/
        domain/
          entities/
          repositories/
          usecases/
          value_objects/
        presentation/
          pages/
          presenters/
          widgets/
    shared/
      widgets/
  test/
    core/
    features/
      chat/
  integration_test/
  assets/
  docs/
    rules/
```

Adapte a estrutura se o Flutter gerar pastas adicionais, mas preserve a separacao entre `presentation`, `domain`, `data`, `core` e `shared`.

## Modelo de dominio sugerido

Crie modelos simples e imutaveis para representar a conversa em memoria:

- `ChatMessage`: entidade de mensagem com identificador local, autor, conteudo e horario.
- `ChatAuthor`: enum ou objeto que diferencie `doctor` e `assistant`.
- `ChatTranscript`: colecao encapsulada de mensagens quando houver comportamento util.
- `MessageContent`: value object para validar texto nao vazio e limites razoaveis de tamanho.
- `SendMedicalChatMessage`: use case para enviar a mensagem do medico e obter a resposta da IA.
- `MedicalChatRepository`: contrato de dominio para solicitar resposta da IA.

Nao modele paciente real, prontuario, diagnostico definitivo, CID, prescricao ou dados sensiveis nesta primeira versao. A interface deve ser uma demonstracao academica de interacao textual.

## Contrato REST sugerido

Prepare o frontend para consumir um endpoint futuro:

```http
POST /chat/messages
Content-Type: application/json
```

Request:

```json
{
  "message": "Texto enviado pelo medico.",
  "conversation": [
    {
      "role": "doctor",
      "content": "Mensagem anterior."
    },
    {
      "role": "assistant",
      "content": "Resposta anterior."
    }
  ]
}
```

Response:

```json
{
  "message": {
    "role": "assistant",
    "content": "Resposta simulada da IA."
  }
}
```

Enquanto o backend nao existir, use um fake local na camada `data` que retorne respostas simuladas e deixe TODO tecnico indicando onde trocar pelo client REST real.

## Configuracao de ambiente

Criar configuracao para base URL:

```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8080
```

Default local aceitavel:

```text
http://localhost:8080
```

Nao hardcodar URL de producao, segredo, chave de API ou credencial no Flutter.

Se a primeira versao usar fake local, mantenha `API_BASE_URL` configurada e coberta por teste mesmo que ainda nao seja chamada pela tela.

## Client REST

Criar infraestrutura HTTP reutilizavel:

- client configurado a partir de `API_BASE_URL`;
- parsing de respostas JSON;
- timeout razoavel;
- logs tecnicos via `logging`;
- mapeamento de erro padronizado `{ code, message }`;
- ponto unico para adicionar headers comuns;
- sem chamadas HTTP diretamente em widgets.

Modelo de erro esperado:

```json
{
  "code": "INVALID_REQUEST",
  "message": "Parametro invalido."
}
```

## Interface

A interface deve priorizar uso repetido e clareza:

- nada de hero de marketing;
- nada de cards decorativos em excesso;
- conteudo principal deve ser o terminal de conversa;
- altura da area de mensagens deve se adaptar ao viewport;
- o campo de envio deve permanecer acessivel;
- textos devem caber em desktop e mobile sem sobreposicao;
- usar icones em botoes quando houver icone Material/Lucide equivalente disponivel no projeto;
- estados de loading, erro e vazio devem ser visiveis sem bloquear leitura das mensagens anteriores.

## Regras oficiais Flutter/Dart

Considere o guia oficial:

```text
https://raw.githubusercontent.com/flutter/flutter/refs/heads/master/docs/rules/rules.md
```

Se nao conseguir acessar o link, use `analysis_options.yaml`, `flutter_lints` e Effective Dart como base.

Alinhe o projeto a estas diretrizes:

- usar `dart format`;
- respeitar lints;
- nomes descritivos;
- arquivos em `snake_case`;
- classes em `PascalCase`;
- membros em `camelCase`;
- widgets imutaveis;
- usar `const` sempre que possivel;
- separar UI, estado, dominio e dados;
- aplicar Object Calisthenics em dominio, use cases, presenters e DTOs/mappers quando fizer sentido;
- evitar chamadas de rede dentro de `build`;
- preferir composicao de widgets;
- quebrar `build` grande em widgets menores;
- usar `go_router` para navegacao web;
- usar `Future`, `async` e `await` com tratamento de erro;
- usar `logging` ou `dart:developer`, nunca `print` em producao.

## Object Calisthenics

Use Object Calisthenics como guia de design para manter o codigo pequeno, coeso e expressivo:

- prefira objetos de dominio e value objects a tipos primitivos soltos quando houver regra associada;
- encapsule colecoes em classes quando elas tiverem comportamento ou validacao propria;
- mantenha classes e metodos pequenos, com uma responsabilidade clara;
- evite `else` quando early return ou polimorfismo tornar o fluxo mais simples;
- evite encadeamento excessivo de getters e chamadas;
- reduza abreviacoes e nomes genericos;
- preserve imutabilidade nos estados e modelos sempre que possivel;
- nao aplique a tecnica mecanicamente quando ela piorar a clareza ou contrariar padroes consolidados do Flutter.

## Regras do projeto obrigatorias

Crie exatamente estes arquivos no frontend:

```text
docs/rules/dart-coding-standards.md
docs/rules/flutter-clean-architecture.md
docs/rules/dependency-injection.md
docs/rules/state-management.md
docs/rules/project-structure.md
docs/rules/testing-standards.md
docs/rules/commits-and-language.md
```

As regras devem refletir o estado real criado no projeto e reforcar:

- Clean Architecture por feature.
- MVP com presenters baseados em `ValueNotifier<TState>`.
- Object Calisthenics aplicado de forma pragmatica.
- DI por construtor e `get_it` apenas no composition root.
- HTTP centralizado em `core/http`.
- DTOs restritos a `data`.
- Widgets sem regra de negocio.
- Testes com fakes simples antes de mocks.
- Conversas de chat mantidas apenas em memoria nesta primeira versao.
- Idioma padrao do codigo e commits conforme convencao documentada.

## Testes obrigatorios

Crie testes iniciais para:

- leitura de `API_BASE_URL` com default local;
- parsing de erros padronizados;
- DTOs e mappers do contrato de chat;
- repository fake de chat medico-IA;
- use case `SendMedicalChatMessage` com repository fake;
- validacao de `MessageContent` para texto vazio e texto valido;
- presenter baseado em `ValueNotifier`, incluindo envio, loading, sucesso, erro e limpar conversa;
- widget test da tela de chat com estado vazio;
- widget test da tela de chat durante resposta da IA;
- widget test da tela de chat exibindo mensagem de erro.

Use fakes simples antes de mocks.

## Validacao obrigatoria

Ao final, execute quando disponivel:

```bash
cd trabalho3/fe
flutter pub get
dart format .
flutter analyze
flutter test
```

Se algum comando nao puder ser executado por falta de Flutter/Dart no ambiente, informe claramente.

## Entregaveis esperados

1. Projeto Flutter Web criado ou evoluido em `trabalho3/fe`.
2. `analysis_options.yaml` configurado com lints adequadas.
3. App funcional com tela unica de chat medico-IA na rota `/`.
4. Tema Material 3 centralizado.
5. Configuracao de `API_BASE_URL` por `--dart-define`.
6. Infraestrutura HTTP isolada em `lib/core/http`.
7. Tratamento de erro padronizado `{ code, message }`.
8. Feature `chat` organizada por `data`, `domain` e `presentation`.
9. Presenters baseados em `ValueNotifier<TState>`.
10. Composition root com `get_it`.
11. Fake de desenvolvimento para resposta da IA quando nao houver backend.
12. Testes unitarios e widget tests iniciais.
13. Documentacao inicial do frontend.
14. Arquivos de regras criados em `docs/rules`.
15. Validacoes executadas ou bloqueios registrados.

## Criterios de aceite

- A skill `$flutter_project_creator` foi usada antes da implementacao.
- O projeto existe em `trabalho3/fe`.
- Ao abrir `/`, o usuario ve uma tela de chat funcional, nao uma landing page.
- O layout funciona em desktop e mobile web.
- A conversa ocorre apenas em memoria e nao e persistida.
- O medico consegue enviar mensagens e visualizar respostas simuladas ou reais da IA.
- O estado vazio, loading, erro e sucesso da conversa sao tratados.
- `API_BASE_URL` pode ser configurada por `--dart-define`.
- O client HTTP nao fica acoplado a widgets.
- Erros padronizados sao mapeados e exibidos corretamente.
- Clean Architecture por feature esta aplicada.
- DI usa construtores e `get_it` no composition root.
- Presentation usa MVP com presenters baseados em `ValueNotifier<TState>`.
- Object Calisthenics foi aplicado de forma pragmatica nas classes criadas.
- Nao ha uso de `provider`, BLoC, Riverpod ou code generation sem justificativa tecnica.
- `docs/rules/*.md` existem e refletem o estado real do projeto.
- `flutter analyze` e `flutter test` passam ou os bloqueios estao documentados.

## Resumo final esperado

Responda com:

- confirmacao de uso da skill `$flutter_project_creator`;
- arquivos principais criados;
- dependencias usadas;
- padrao de DI;
- padrao de state management;
- aplicacao de MVP e Object Calisthenics;
- rotas criadas;
- estrategia de configuracao por `--dart-define`;
- comportamento de chat em memoria;
- existencia ou nao de backend real para IA;
- comandos executados;
- resultados de `flutter analyze` e `flutter test`;
- TODOs tecnicos;
- appliesTo definidos nas regras do projeto;
- fonte usada para as regras:
  - skill `$flutter_project_creator`;
  - guia oficial Flutter/Dart, se acessado.
