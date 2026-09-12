---
appliesTo: "lib/features/**/presentation/**"
---

# State Management

- Use MVP na camada de apresentacao.
- Presenters coordenam eventos da view, validacoes de UI e chamadas a use cases.
- Presenters devem estender ou encapsular `ValueNotifier<TState>`.
- Views observam estado com `ValueListenableBuilder`.
- Estados devem ser imutaveis e explicitamente tipados.
- O chat deve representar vazio, loading, sucesso e erro.
- Conversas sao mantidas apenas em memoria e podem ser limpas pelo presenter.
- Nao usar BLoC, Riverpod, Provider ou code generation nesta primeira versao.
