# VectorGov SDK — Single-Page LLM Reference

> **🤖 Para agentes LLM**: esta página consolida tudo que um agente precisa para usar o VectorGov SDK em uma única view. Ela é otimizada para `curl`/copy-paste em prompts. Para humanos, prefira o [README](https://github.com/euteajudo/vectorgov-sdk) ou a [Cheat Sheet](cheat-sheet.md).
>
> **Versão do SDK**: 0.19.5 · **Python**: 3.10+ · **Licença**: MIT

---

## TL;DR (30 segundos)

```bash
pip install vectorgov
export VECTORGOV_API_KEY=vg_...
```

```python
from vectorgov import VectorGov

vg = VectorGov()
result = vg.search("Quando o ETP pode ser dispensado?")

for hit in result:
    label = hit.citation or hit.source  # citation = formato jurídico
    print(f"[{hit.score:.0%}] {label}\n{hit.text[:200]}\n")
```

**Saída**:
```
[97%] Art. 18 da Lei 14.133/2021
Art. 18. A fase preparatória do processo licitatório é caracterizada pelo planejamento ...
```

---

## Os 23 métodos públicos

| Método | Custo | Retorna | Quando usar |
|---|---|---|---|
| `search(query, mode, top_k, ...)` | 💰 | `SearchResult` | Busca semântica padrão (3 modos) |
| `smart_search(query)` | 💰💰 | `SmartSearchResult` | Análise jurídica completa com Juiz LLM |
| `hybrid(query, hops)` | 💰 | `HybridResult` | Semântica + grafo de citações |
| `lookup(reference)` | 💰 | `LookupResult` | Resolve "Art. X da Lei Y" |
| `grep(query)` | 💰 | `GrepResult` | Busca textual literal (ripgrep) |
| `filesystem_search(query, mode)` | 💰 | `FilesystemResult` | Índice curado |
| `merged(query)` | 💰 | `MergedResult` | hybrid + filesystem via RRF |
| `read_canonical(doc_id, span_id)` | **free** | `CanonicalResult` | Texto canônico completo |
| `feedback(query_id, like)` | **free** | `bool` | Like/dislike (melhoria contínua) |
| `estimate_tokens(content, ...)` | **free** | `TokenStats` | Estima tokens antes do LLM |
| `store_response(query, answer, ...)` | **free** | `StoreResponseResult` | Armazena resposta de LLM externo |
| `get_system_prompt(style)` | **free** | `str` | Prompts pré-otimizados |
| `available_prompts` (property) | **free** | `list[str]` | Lista estilos disponíveis |
| `to_openai_tool()` | **free** | `dict` | Tool no formato OpenAI |
| `to_anthropic_tool()` | **free** | `dict` | Tool no formato Anthropic |
| `to_google_tool()` | **free** | `dict` | Tool no formato Google Gemini |
| `execute_tool_call(call)` | 💰 | `str` | Executa tool_call de qualquer LLM |
| `list_documents(page, limit)` | **free** | `DocumentsResponse` | Lista normas indexadas |
| `get_document(doc_id)` | **free** | `DocumentSummary` | Metadados de uma norma |
| `get_audit_logs(severity, ...)` | **free** | `AuditLogsResponse` | Logs de uso |
| `get_audit_stats(days)` | **free** | `AuditStats` | Estatísticas agregadas |
| `get_audit_event_types()` | **free** | `list[str]` | Tipos de evento disponíveis |
| `close()` | **free** | `None` | Libera recursos HTTP |

**Total**: 23 métodos. 8 de busca, 4 de function calling, 5 de tokens/feedback/prompts, 2 de documentos, 3 de auditoria, 1 utilitário.

---

## Decision tree: qual método de busca usar?

```
Pergunta:                                    Use:
─────────────────────────────────────────────────────────────
"Sei a referência exata"                     vg.lookup()
"Linguagem natural, simples"                 vg.search()
"Linguagem natural + análise jurídica"       vg.smart_search()  💰💰
"Linguagem natural + grafo de citações"      vg.hybrid()
"Máxima cobertura (multi-fonte)"             vg.merged()
"Texto literal (substring exata)"            vg.grep()
"Sigla/termo curado (ETP, PCA)"              vg.filesystem_search()
"Texto completo de uma lei/artigo"           vg.read_canonical()
```

### Tabela de comparação

| Método | Latência | Custo | Característica |
|---|---|---|---|
| `search` | 2-7s | 💰 | Busca semântica com refinamento |
| `smart_search` | 5-18s | 💰💰 | Pipeline de análise jurídica completo |
| `hybrid` | 3-10s | 💰 | Semântica + expansão por grafo de citações |
| `merged` | 2-5s | 💰 | hybrid + filesystem com RRF |
| `lookup` | < 1s | 💰 | Lookup determinístico de referência legal |
| `grep` | < 1s | 💰 | Busca textual exata |
| `filesystem_search` | < 1s | 💰 | Índice curado + busca textual |
| `read_canonical` | < 1s | **free** | Leitura direta do texto canônico |

---

## Modelos de dados

### `Hit` (retornado por `search`, `hybrid`, `smart_search`, `lookup`)

```python
hit.text              # str: texto do dispositivo
hit.score             # float: relevância (0.0 a 1.0)
hit.citation          # str|None: "Art. 75 da Lei 14.133/2021"  ← preferir
hit.source            # str: "Lei 14.133/2021, Art. 75" (formato legado)
hit.metadata          # Metadata: tipo, número, ano, artigo
hit.evidence_url      # str|None: URL para trecho destacado (30min)
hit.document_url      # str|None: URL para PDF original
hit.nota_especialista # str|None: nota do especialista (smart_search)
hit.jurisprudencia_tcu # str|None: jurisprudência TCU vinculada
hit.acordao_tcu_link  # str|None: link do acórdão
```

#### `hit.citation` — formato jurídico brasileiro (v0.19.4+)

| Tipo | Exemplo |
|---|---|
| Artigo (1-9) | `Art. 1º da Lei 14.133/2021` |
| Artigo (10+) | `Art. 75 da Lei 14.133/2021` |
| Parágrafo | `§ 2º do Art. 75 da Lei 14.133/2021` |
| Parágrafo único | `Parágrafo único do Art. 75 da Lei 14.133/2021` |
| Inciso | `Inc. III do § 2º do Art. 75 da Lei 14.133/2021` |
| Alínea | `Alínea "a" do Inc. III do § 2º do Art. 75 da Lei 14.133/2021` |

**Padrão idiomático** (sempre use):
```python
label = hit.citation or hit.source  # fallback defensivo
```

### `SearchResult`

```python
result.hits           # list[Hit]
result.total          # int
result.latency_ms     # float
result.cached         # bool
result.query_id       # str (use em vg.feedback)
result.mode           # str

# Métodos de formatação para LLMs
result.to_context(max_chars=4000)  # str
result.to_messages(query="...")    # list[dict] universal
result.to_prompt(query="...")      # str (Gemini-style)
```

### Outros Result types

- **`SmartSearchResult`** (estende SearchResult): + `confianca`, `raciocinio`, `tentativas`, `normas_presentes`
- **`HybridResult`**: + `graph_nodes: list[Hit]`, `stats`, `confidence`
- **`LookupResult`**: `match: Hit`, `parent: Hit`, `siblings: list[Hit]`, `children: list[Hit]`, `stitched_text`
- **`GrepResult`**: `matches: list[GrepMatch]` (com `citation`)
- **`FilesystemResult`**: `results: list[FilesystemHit]`, `mode_used`
- **`MergedResult`**: `results: list[MergedHit]` (com `sources: list[str]`), `mutual_count`
- **`CanonicalResult`**: `document_id`, `text`, `citation`, `breadcrumb`, `token_count`

---

## Padrões idiomáticos

### 1. Iterar com label legal
```python
for hit in result:
    label = hit.citation or hit.source
    print(f"[{hit.score:.0%}] {label}\n{hit.text[:200]}\n")
```

### 2. Filtrar por score mínimo
```python
relevant = [h for h in result.hits if h.score >= 0.5]
```

### 3. Filtrar por norma específica
```python
result = vg.search("credenciamento", document_id_filter="LEI-14133-2021")
```

### 4. Passar para qualquer LLM
```python
messages = result.to_messages(query="...")
# Funciona em OpenAI, Anthropic, Gemini, Ollama, LangChain
```

### 5. Limitar contexto por orçamento
```python
stats = vg.estimate_tokens(result, query="...", system_prompt=vg.get_system_prompt())
if stats.total_tokens > 100_000:
    context = result.to_context(max_chars=20_000)
```

### 6. Resolver referência exata
```python
r = vg.lookup("Art. 75 da Lei 14.133")
print(r.match.citation)         # 'Art. 75 da Lei 14.133/2021'
print(r.stitched_text)          # caput + parágrafos + incisos
```

### 7. Function calling (OpenAI)
```python
tools = [vg.to_openai_tool()]
response = openai.chat.completions.create(model="gpt-4o", messages=[...], tools=tools)
if response.choices[0].message.tool_calls:
    result_text = vg.execute_tool_call(response.choices[0].message.tool_calls[0])
```

### 8. Feedback
```python
result = vg.search("...")
vg.feedback(query_id=result.query_id, like=True)
```

### 9. Auditoria
```python
critical = vg.get_audit_logs(severity="critical", limit=100)
for log in critical.logs:
    print(f"{log.timestamp} [{log.event_type}] {log.action_taken}")
```

### 10. Context manager
```python
with VectorGov() as vg:
    result = vg.search("...")
# vg.close() é chamado automaticamente
```

---

## Erros comuns

| Erro | Causa | Fix |
|---|---|---|
| `AuthError` | Key inválida | API key deve começar com `vg_` |
| `RateLimitError` | Cota excedida | Aguarde ou faça upgrade |
| `hit.citation is None` | Cache legado | `label = hit.citation or hit.source` |
| `m.span_id == ""` em grep | IDs internos não expostos no response público | Use `m.citation or m.document_id` |
| `to_context()` com vírgula solta | SDK < 0.19.5 | `pip install -U vectorgov` |
| `ImportError langchain` | Extra não instalado | `pip install 'vectorgov[langchain]'` |
| `ValidationError` | Query < 3 chars | Mínimo 3 caracteres |
| `TimeoutError` em smart_search | Pipeline lento | `VectorGov(timeout=180.0)` |

---

## Exceções disponíveis

```python
from vectorgov import (
    VectorGovError,    # Base
    AuthError,         # 401
    ValidationError,   # 400
    RateLimitError,    # 429
    APIError,          # 5xx
    TimeoutError,      # timeout
)

try:
    result = vg.search("...")
except RateLimitError as e:
    print(f"Cota: {e.retry_after}s")
except AuthError:
    print("API key inválida")
except VectorGovError as e:
    print(f"Erro genérico: {e}")
```

---

## Integração com LLMs (cheat code)

### OpenAI
```python
from openai import OpenAI
result = vg.search("...")
response = OpenAI().chat.completions.create(
    model="gpt-4o-mini",
    messages=result.to_messages(query="..."),
)
```

### Anthropic Claude
```python
from anthropic import Anthropic
result = vg.search("...")
messages = result.to_messages(query="...")
response = Anthropic().messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=messages[0]["content"],  # system separado
    messages=[{"role": "user", "content": messages[1]["content"]}],
)
```

### Google Gemini
```python
import google.generativeai as genai
genai.configure()
result = vg.search("...")
messages = result.to_messages(query="...")
model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=messages[0]["content"])
response = model.generate_content(messages[1]["content"])
```

### Ollama (local, gratuito)
```python
from vectorgov.integrations.ollama import create_rag_pipeline
rag = create_rag_pipeline(vg, model="llama3:8b")
print(rag("..."))
```

### LangChain
```python
from vectorgov.integrations.langchain import VectorGovRetriever
retriever = VectorGovRetriever()  # lê VECTORGOV_API_KEY
docs = retriever.get_relevant_documents("...")
```

### MCP (Claude Desktop, Cursor)
```json
{
    "mcpServers": {
        "vectorgov": {
            "command": "uvx",
            "args": ["vectorgov-mcp"],
            "env": {"VECTORGOV_API_KEY": "vg_..."}
        }
    }
}
```

---

## Campos internos do response

Alguns IDs técnicos (`chunk_id`, `node_id`, `span_id`, `line_number`,
`char_offset`) podem vir vazios no response público — eles são usados
internamente para evidência mas não fazem parte do contrato público da
API.

**Sempre use `hit.citation`** como identificador legível para humanos e
LLMs. É o formato jurídico brasileiro pronto para exibição (`Art. 75 da
Lei 14.133/2021`) e nunca vem vazio quando o backend conhece o tipo do
documento.

```python
# Padrão idiomático defensivo
label = hit.citation or hit.source
```

---

## Versionamento e changelog

- **0.19.5** (atual) — `to_context()` e builders XML/markdown usam `citation`
- **0.19.4** — campo `citation` em todos os Result types
- **0.19.3** — fix: hybrid lê `evidence_url` em hits de grafo
- **0.19.2** — créditos em todos os 8 endpoints pagos
- **0.19.0** — IDs internos de implementação removidos do response público
- **0.18.x** — request_id em todos os Results

[Changelog completo](https://github.com/euteajudo/vectorgov-sdk-docs/blob/main/CHANGELOG.md)

---

## Links

- 📦 [PyPI](https://pypi.org/project/vectorgov/)
- 🐙 [GitHub](https://github.com/euteajudo/vectorgov-sdk)
- 📚 [Documentação completa](https://docs.vectorgov.io)
- 🧭 [Cheat Sheet (humanos)](cheat-sheet.md)
- 📖 [Reference técnica de métodos](api/methods.md)
- 🐛 [Issues](https://github.com/euteajudo/vectorgov-sdk/issues)
