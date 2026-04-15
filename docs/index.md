# VectorGov SDK

**Busca semântica em legislação brasileira** com chunks prontos para alimentar qualquer LLM.

```bash
pip install vectorgov
export VECTORGOV_API_KEY=vg_sua_chave
```

```python
from vectorgov import VectorGov

vg = VectorGov()
result = vg.search("Quando o ETP pode ser dispensado?")

for hit in result:
    print(f"[{hit.score:.0%}] {hit.citation}")
    print(hit.text[:200])
```

```
[97%] Art. 18 da Lei 14.133/2021
Art. 18. A fase preparatória do processo licitatório é caracterizada pelo planejamento ...
```

---

## 🚀 Por onde começar

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Quickstart**

    ---

    Do `pip install` ao primeiro resultado em 2 minutos.

    [:octicons-arrow-right-24: README](https://github.com/euteajudo/vectorgov-sdk#-quickstart-2-minutos)

-   :material-card-text-outline:{ .lg .middle } **Cheat Sheet**

    ---

    Os 23 métodos do SDK em uma única página, com decision tree.

    [:octicons-arrow-right-24: cheat-sheet.md](cheat-sheet.md)

-   :material-book-open-variant:{ .lg .middle } **Reference de métodos**

    ---

    Detalhe técnico de cada método: parâmetros, retorno, exceções, exemplos.

    [:octicons-arrow-right-24: api/methods.md](api/methods.md)

-   :material-robot:{ .lg .middle } **LLM Reference**

    ---

    Página single-page para alimentar agentes LLM via curl.

    [:octicons-arrow-right-24: llm-reference.md](llm-reference.md)

</div>

---

## 🔍 Os 8 métodos de busca

| Método | Latência | Custo | Pra que serve |
|---|---|---|---|
| [`search`](api/methods.md#search) | 2-7s | 💰 | Busca semântica simples — chat, RAG, autocomplete |
| [`smart_search`](api/methods.md#smart_search) | 5-18s | 💰💰 | Análise jurídica completa com Juiz LLM |
| [`hybrid`](api/methods.md#hybrid) | 3-10s | 💰 | Semântica + expansão por grafo de citações |
| [`merged`](api/methods.md#merged) | 2-5s | 💰 | Dual-path: hybrid + filesystem com RRF |
| [`lookup`](api/methods.md#lookup) | < 1s | 💰 | Resolve "Art. 75 da Lei 14.133" para o dispositivo |
| [`grep`](api/methods.md#grep) | < 1s | 💰 | Busca textual literal (ripgrep) |
| [`filesystem_search`](api/methods.md#filesystem_search) | < 1s | 💰 | Índice curado (siglas, termos técnicos) |
| [`read_canonical`](api/methods.md#read_canonical) | < 1s | **free** | Lê texto canônico completo |

> 🌳 **Qual usar?** Veja a [decision tree na cheat sheet](cheat-sheet.md#qual-metodo-de-busca-usar).

---

## 🍳 Receitas comuns

### Passar para o ChatGPT em 3 linhas

```python
from openai import OpenAI

result = vg.search("Critérios de julgamento")
response = OpenAI().chat.completions.create(
    model="gpt-4o-mini",
    messages=result.to_messages(query="Critérios de julgamento"),
)
print(response.choices[0].message.content)
```

### Resolver referência legal exata

```python
r = vg.lookup("Art. 75 da Lei 14.133")
print(r.match.citation)   # 'Art. 75 da Lei 14.133/2021'
print(r.stitched_text)    # caput + parágrafos + incisos consolidados
```

### Function calling (Claude)

```python
from anthropic import Anthropic

response = Anthropic().messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=[vg.to_anthropic_tool()],
    messages=[{"role": "user", "content": "Como funciona dispensa de licitação?"}],
)
for block in response.content:
    if block.type == "tool_use":
        print(vg.execute_tool_call(block))
```

> 🍳 **Mais receitas**: [README](https://github.com/euteajudo/vectorgov-sdk#-receitas-comuns) tem 7, [cheat-sheet](cheat-sheet.md#10-padroes-idiomaticos) tem 10.

---

## 📚 Categorias completas (23 métodos)

<div class="grid cards" markdown>

-   :material-magnify:{ .lg .middle } **🔍 Busca (8)**

    `search` · `smart_search` · `hybrid` · `merged` · `lookup` · `grep` · `filesystem_search` · `read_canonical`

    [:octicons-arrow-right-24: Detalhes](api/methods.md#busca)

-   :material-robot:{ .lg .middle } **🤖 Function Calling (4)**

    `to_openai_tool` · `to_anthropic_tool` · `to_google_tool` · `execute_tool_call`

    [:octicons-arrow-right-24: Detalhes](api/methods.md#function-calling-4-metodos)

-   :material-counter:{ .lg .middle } **📊 Tokens & Feedback (3)**

    `estimate_tokens` · `feedback` · `store_response`

    [:octicons-arrow-right-24: Detalhes](api/methods.md#tokens-feedback-3-metodos)

-   :material-format-quote-open:{ .lg .middle } **🎯 System Prompts (2)**

    `get_system_prompt` · `available_prompts`

    [:octicons-arrow-right-24: Detalhes](api/methods.md#system-prompts-2)

-   :material-file-document-multiple:{ .lg .middle } **📚 Documentos (2)**

    `list_documents` · `get_document`

    [:octicons-arrow-right-24: Detalhes](api/methods.md#documentos-2)

-   :material-shield-check:{ .lg .middle } **🛡️ Auditoria (3)**

    `get_audit_logs` · `get_audit_stats` · `get_audit_event_types`

    [:octicons-arrow-right-24: Detalhes](api/methods.md#auditoria-compliance-3)

</div>

---

## 🔌 Integrações

| | | | |
|---|---|---|---|
| [OpenAI](integrations/openai.md) | [Claude](integrations/anthropic.md) | [Gemini](integrations/gemini.md) | [Ollama](integrations/ollama.md) |
| [LangChain](integrations/langchain.md) | [LangGraph](integrations/langgraph.md) | [Google ADK](integrations/google-adk.md) | [Transformers](integrations/transformers.md) |
| [MCP Server](integrations/mcp.md) | | | |

---

## 📖 Guias temáticos

- 🧠 [Busca avançada](guides/advanced-search.md) — modos, filtros, dual-lane
- 🛡️ [Tratamento de erros](guides/error-handling.md) — exceções, retry
- 🎯 [System prompts](guides/system-prompts.md) — estilos e customização
- 📊 [Auditoria & compliance](guides/observability-audit.md) — logs, dashboards

---

## 🤝 Suporte

- 🐛 [GitHub Issues](https://github.com/euteajudo/vectorgov-sdk/issues)
- 📧 contato@vectorgov.io
- 📚 [Documentação completa](https://docs.vectorgov.io)
