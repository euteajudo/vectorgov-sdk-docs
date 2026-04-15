# Reference completa de métodos

> 22 métodos públicos do `VectorGov` cliente, organizados por categoria. Cada método segue o mesmo padrão: **propósito → quando usar → exemplo mínimo → parâmetros → retorno → exceções → exemplo avançado → veja também**.
>
> 💡 **Procurando um método específico?** Use a [Cheat Sheet](../cheat-sheet.md) para visão geral em 1 página, ou `Ctrl+F` aqui para buscar por nome.

---

## 🔍 Busca

### `search`

**Busca semântica simples** com 3 modos de performance.

#### Quando usar

- 80% dos casos de uso de busca em legislação
- Chat / RAG / autocomplete
- Quando você não precisa de análise jurídica completa nem de expansão por grafo
- Quando latência importa (mode `fast` retorna em ~2s)

#### Exemplo mínimo

```python
from vectorgov import VectorGov

vg = VectorGov()
result = vg.search("Quando o ETP pode ser dispensado?")

for hit in result:
    print(f"[{hit.score:.0%}] {hit.citation}")
    print(hit.text[:200])
```

#### Parâmetros

| Nome | Tipo | Default | Descrição |
|---|---|---|---|
| `query` | `str` | — (obrig.) | Pergunta em linguagem natural (≥ 3 caracteres) |
| `top_k` | `int` | `5` | Número de resultados (1-50) |
| `mode` | `"fast" \| "balanced" \| "precise"` | `"balanced"` | Trade-off latência/precisão (ver tabela abaixo) |
| `filters` | `dict` | `None` | Filtros estruturados (`tipo_documento`, `ano`, `orgao`) |
| `use_cache` | `bool` | `None` | Cache semântico (default do mode) |
| `document_id_filter` | `str` | `None` | Restringir a um documento específico |
| `trace_id` | `str` | `None` | ID externo para rastreamento |

**Modos de busca:**

| Mode | Latência | Quando usar |
|---|---|---|
| `fast` | ~2s | Autocomplete, busca rápida |
| `balanced` | ~5s | Default — chat, RAG (recomendado) |
| `precise` | ~15s | Análises críticas, queries ambíguas |

Os modos diferem em quantos estágios de refinamento o backend aplica.
`fast` retorna o resultado bruto da busca semântica, `balanced` aplica
re-ranking, `precise` aplica todos os refinamentos disponíveis.

#### Retorno

`SearchResult` com:

- `hits: list[Hit]` — resultados ordenados por relevância
- `total: int` — total de resultados encontrados
- `latency_ms: float`
- `query_id: str` — usar em `feedback()`
- `cached: bool`
- `mode: str`

Cada `Hit` tem `citation`, `source`, `text`, `score`, `metadata`, `evidence_url`, `document_url`. Veja [models.md#hit](models.md#hit).

#### Exceções

| Exceção | Causa |
|---|---|
| `ValidationError` | Query < 3 caracteres ou > 1000 |
| `AuthError` | API key inválida ou expirada |
| `RateLimitError` | Cota excedida |
| `APIError` | Erro genérico do backend (5xx) |

#### Exemplo avançado

```python
# Filtros estruturados
result = vg.search(
    "credenciamento",
    mode="precise",
    top_k=10,
    filters={
        "tipo_documento": "LEI",
        "ano": 2021,
    },
)

# Filtro por documento específico
result = vg.search(
    "dispensa de licitacao",
    document_id_filter="LEI-14133-2021",
)

# Iterar com fallback defensivo
for hit in result:
    label = hit.citation or hit.source
    print(f"[{label}] (score={hit.score:.2f})")
    print(hit.text)
    if hit.evidence_url:
        print(f"  Evidência: {hit.evidence_url}")
```

#### Veja também

- [`smart_search`](#smart_search) — quando você precisa de análise jurídica completa
- [`hybrid`](#hybrid) — quando precisa de expansão por grafo de citações
- [`merged`](#merged) — quando precisa de máxima cobertura (dual-path)
- [Guia: busca avançada](../guides/advanced-search.md)

---

### `smart_search`

**Análise jurídica completa** com Juiz LLM. Pipeline turnkey que decide tudo: chunks, expansão, validação.

#### Quando usar

- Quando você precisa de **resposta pronta com curadoria jurídica**
- Quando quer um Juiz LLM avaliando relevância e completude antes de entregar
- Quando aceita pagar mais (💰💰) por qualidade superior
- Quando latência ~10-18s é aceitável

#### Exemplo mínimo

```python
result = vg.smart_search("Quais os requisitos para dispensa de licitação?")

print(f"Confiança: {result.confianca}")
print(f"Raciocínio do Juiz: {result.raciocinio}")
print(f"Normas presentes: {result.normas_presentes}")

for hit in result.hits:
    print(f"\n[{hit.citation}]")
    print(hit.text)
    if hit.nota_especialista:
        print(f"💡 Nota: {hit.nota_especialista}")
    if hit.jurisprudencia_tcu:
        print(f"⚖️ TCU: {hit.jurisprudencia_tcu}")
```

#### Parâmetros

| Nome | Tipo | Default | Descrição |
|---|---|---|---|
| `query` | `str` | — | Query jurídica (3-1000 caracteres) |
| `use_cache` | `bool` | `False` | Cache semântico (privacidade off por padrão) |
| `trace_id` | `str` | `None` | ID externo |

#### Retorno

`SmartSearchResult` (estende `SearchResult`) com:

- `hits` — chunks aprovados pelo Juiz
- `confianca: str` — `"alta"`, `"media"`, `"baixa"`
- `raciocinio: str` — análise do Juiz LLM
- `tentativas: int` — quantas iterações do pipeline (1-2)
- `normas_presentes: list[str]` — normas que aparecem no resultado
- `quantidade_normas: int`
- `relacoes_count: int` — relações no grafo
- Hits incluem `nota_especialista` e `jurisprudencia_tcu` quando disponíveis

#### Exceções

| Exceção | Causa |
|---|---|
| `RateLimitError` | Plano free tem cota baixa para smart-search |
| `TimeoutError` | Pipeline excedeu 120s (raro) |
| `APIError` | Erro do backend |

#### Exemplo avançado

```python
result = vg.smart_search("É possível dispensar licitação para obras emergenciais?")

# Decisão baseada em confiança
if result.confianca == "alta":
    answer = "\n".join(h.text for h in result.hits)
elif result.confianca == "media":
    answer = "Resposta provável (revise):\n" + "\n".join(h.text for h in result.hits)
else:
    answer = f"Confiança baixa. Raciocínio: {result.raciocinio}"

# Passar para LLM para gerar resposta final
messages = result.to_messages(query="É possível dispensar licitação para obras emergenciais?")
```

#### Veja também

- [`search`](#search) — quando análise jurídica completa não é necessária
- [`hybrid`](#hybrid) — alternativa mais barata com expansão por grafo

---

### `hybrid`

**Busca semântica + expansão por grafo de citações**. Retorna chunks diretos **e** dispositivos relacionados.

#### Quando usar

- Quando precisa não só dos artigos mais relevantes, mas também dos **artigos citados/citantes**
- Para mostrar "cadeia regulatória" (ex: lei → decreto → IN)
- Para descobrir dispositivos relacionados que não apareceriam só por semântica

#### Exemplo mínimo

```python
result = vg.hybrid("dispensa de licitação")

print("=== Hits diretos ===")
for hit in result.hits:
    print(f"  [{hit.citation}] score={hit.score:.2f}")

print("\n=== Expansão por grafo ===")
for node in result.graph_nodes:
    print(f"  [{node.citation}] hop={node.hop}, freq={node.frequency}")
```

#### Parâmetros

| Nome | Tipo | Default | Descrição |
|---|---|---|---|
| `query` | `str` | — | Query jurídica |
| `top_k` | `int` | `10` | Hits diretos |
| `hops` | `int` | `1` | Profundidade do grafo (1 ou 2) |
| `graph_expansion` | `"bidirectional" \| "forward"` | `"bidirectional"` | Direção da expansão |
| `token_budget` | `int` | `6000` | Budget total de tokens |
| `use_cache` | `bool` | `None` |
| `trace_id` | `str` | `None` |

#### Retorno

`HybridResult` com:

- `hits: list[Hit]` — direct evidence (chunks diretos)
- `graph_nodes: list[Hit]` — chunks via expansão (com `hop`, `frequency`, `paths`, `relacao`)
- `stats: dict` — `seeds_count`, `graph_nodes_count`, `total_tokens`
- `confidence: float`
- `latency_ms: float`

#### Exemplo avançado

```python
# Expansão profunda (2 hops)
result = vg.hybrid("contratação direta", hops=2, top_k=5)

# Separar por tipo
print("\n📌 Diretos:")
for h in result.hits:
    print(f"  {h.citation}")

print("\n🕸️ Via grafo (1 hop):")
for n in result.graph_nodes:
    if n.hop == 1:
        print(f"  {n.citation} (relação: {n.relacao})")

print("\n🕸️ Via grafo (2 hops):")
for n in result.graph_nodes:
    if n.hop == 2:
        print(f"  {n.citation} (paths: {len(n.paths)})")

# Contexto pronto pra LLM (inclui ambos)
context = result.to_context(max_chars=4000)
```

#### Veja também

- [`merged`](#merged) — versão dual-path com filesystem
- [`search`](#search) — alternativa mais simples sem grafo
- [Guia: busca avançada](../guides/advanced-search.md)

---

### `lookup`

**Resolve referência legal exata** (`"Art. 75 da Lei 14.133"`) para o dispositivo correspondente. Sub-segundo.

#### Quando usar

- Quando o usuário ou seu agente já sabe a referência exata
- Para mostrar o texto consolidado de um artigo (caput + parágrafos + incisos)
- Para batch lookups (até 20 referências em uma chamada)

#### Exemplo mínimo

```python
r = vg.lookup("Art. 75 da Lei 14.133")

print(r.match.citation)   # 'Art. 75 da Lei 14.133/2021'
print(r.match.text)       # texto do artigo
print(r.stitched_text)    # caput + filhos consolidados
```

#### Parâmetros

| Nome | Tipo | Default | Descrição |
|---|---|---|---|
| `reference` | `str \| list[str]` | — | Referência (ou lista, batch máx 20) |
| `include_parent` | `bool` | `True` | Incluir artigo pai (para parágrafos/incisos) |
| `include_siblings` | `bool` | `True` | Incluir dispositivos irmãos |
| `trace_id` | `str` | `None` |

#### Retorno

`LookupResult` com:

- `status: str` — `"found"`, `"not_found"`, `"ambiguous"`, `"parse_failed"`
- `match: Hit | None` — dispositivo encontrado (com `citation`)
- `parent: Hit | None` — artigo pai (se aplicável)
- `siblings: list[Hit]` — dispositivos irmãos
- `children: list[Hit]` — dispositivos filhos (incisos do parágrafo, etc.)
- `stitched_text: str | None` — caput + filhos consolidados
- `candidates: list[LookupCandidate]` — quando `status="ambiguous"`
- `results: list[LookupResult] | None` — quando enviou batch

#### Exemplo avançado — batch

```python
refs = [
    "Art. 75 da Lei 14.133",
    "§ 2º do Art. 75 da Lei 14.133",
    "Inc. III do Art. 75 da Lei 14.133",
    "Art. 5 da IN 67/2021",
]
batch = vg.lookup(refs)

for r in batch.results:
    if r.status == "found":
        print(f"✅ {r.match.citation}")
        print(f"   {r.match.text[:100]}...")
    elif r.status == "ambiguous":
        print(f"⚠️  {r.reference} → {len(r.candidates)} candidatos")
    else:
        print(f"❌ {r.reference} → {r.status}: {r.message}")
```

#### Auto-split

Quando você passa uma string com múltiplas referências separadas por vírgula, ponto-e-vírgula ou "e", o backend faz split automático:

```python
# Vira batch automaticamente
r = vg.lookup("art. 6 da lei 14.133 e § 1 do art. 23 da lei 14.133")
# r.results tem 2 elementos
```

#### Veja também

- [`grep`](#grep) — para busca textual literal
- [`read_canonical`](#read_canonical) — para ler texto cru sem parser

---

### `grep`

**Busca textual literal** via ripgrep. Sub-segundo.

#### Quando usar

- Quando você sabe a forma exata do texto (`"dispensa de licitação"`)
- Para encontrar palavras-chave específicas
- Quando busca semântica retorna ruído mas você sabe o termo

#### Exemplo mínimo

```python
result = vg.grep("dispensa de licitacao", max_results=5)

for m in result:
    # Prefira citation a span_id (que pode vir vazio no response público)
    label = m.citation or m.document_id
    print(f"{label}: {m.matched_line}")
```

#### Parâmetros

| Nome | Tipo | Default | Descrição |
|---|---|---|---|
| `query` | `str` | — | Termo literal a buscar |
| `document_id` | `str` | `None` | Filtrar por documento |
| `max_results` | `int` | `20` | Máximo de matches (1-50) |
| `context_lines` | `int` | `3` | Linhas de contexto ao redor (0-10) |

#### Retorno

`GrepResult` com:

- `matches: list[GrepMatch]` — cada um com `text`, `matched_line`, `citation`, `document_id`
- `total: int`
- `files_searched: int`
- `latency_ms: float`

#### Campos internos em `GrepMatch`

Alguns IDs técnicos (`node_id`, `span_id`, `line_number`, `char_offset`) podem vir vazios no response público — eles são usados internamente para evidência mas não fazem parte do contrato público. Use `m.citation` (formato jurídico) como label visível para humanos e LLMs.

#### Exemplo avançado

```python
# Busca em documento específico
result = vg.grep("art. 75", document_id="LEI-14133-2021", context_lines=5)

# Filtrar por norma após busca
from collections import defaultdict
by_doc = defaultdict(list)
for m in vg.grep("dispensa", max_results=50):
    by_doc[m.document_id].append(m)

for doc, matches in by_doc.items():
    print(f"\n{doc}: {len(matches)} matches")
    for m in matches[:3]:
        print(f"  {m.citation or m.document_id}: {m.matched_line[:80]}")
```

#### Veja também

- [`filesystem_search`](#filesystem_search) — busca no índice curado (não literal)
- [`lookup`](#lookup) — para referência legal estruturada

---

### `filesystem_search`

**Índice curado** com modo `auto` que detecta se a query é referência legal (grep) ou semântica (index).

#### Quando usar

- Para siglas ou termos curados (`"ETP"`, `"PCA"`, `"PNCP"`)
- Para conceitos com aliases curados pelo especialista
- Quando quer combinar precisão + recall (modo `both`)

#### Exemplo mínimo

```python
result = vg.filesystem_search("ETP")

for hit in result:
    label = hit.citation or hit.document_id
    print(f"[{hit.source}] {label}")
    print(f"  {hit.breadcrumb}")
    if hit.text:
        print(f"  {hit.text[:100]}")
```

#### Parâmetros

| Nome | Tipo | Default | Descrição |
|---|---|---|---|
| `query` | `str` | — | Texto da busca |
| `document_id` | `str` | `None` | Filtrar por documento |
| `mode` | `"auto" \| "index" \| "grep" \| "both"` | `"auto"` | Modo de busca |
| `top_k` | `int` | `10` | Máximo de resultados (1-50) |
| `include_text` | `bool` | `True` | Incluir texto completo |

**Modos:**

| Mode | Quando usar |
|---|---|
| `auto` | Default — detecta automaticamente |
| `index` | Só índice curado (siglas, aliases) |
| `grep` | Só ripgrep (termo literal) |
| `both` | Combina os dois |

#### Retorno

`FilesystemResult` com `results: list[FilesystemHit]`, `total`, `mode_used`, `latency_ms`.

Cada `FilesystemHit` tem `text`, `source` (`"index"` ou `"grep"`), `breadcrumb`, `citation`.

#### Veja também

- [`merged`](#merged) — combina filesystem + hybrid via RRF
- [`grep`](#grep) — só busca textual literal

---

### `merged`

**Dual-path**: executa `hybrid` + `filesystem_search` em paralelo, deduplica e rankeia via RRF.

#### Quando usar

- Para **máxima cobertura** — combina o melhor dos dois mundos
- Quando você não sabe se a query é melhor para semântica ou índice curado
- Quando aceita um pouco mais de latência (~5s) para ter mais recall

#### Exemplo mínimo

```python
result = vg.merged("prazo para impugnação do edital")

print(f"Total: {result.total}")
print(f"Apenas hybrid: {result.hybrid_count}")
print(f"Apenas filesystem: {result.filesystem_count}")
print(f"Em ambas (mutual boost): {result.mutual_count}")

for hit in result:
    sources = ",".join(hit.sources)
    print(f"[{sources}] {hit.citation} (RRF={hit.score:.3f})")
```

#### Parâmetros

| Nome | Tipo | Default | Descrição |
|---|---|---|---|
| `query` | `str` | — | Query (2-1000 caracteres) |
| `document_id` | `str` | `None` | Filtrar por documento |
| `top_k` | `int` | `10` | Máximo de resultados (1-30) |
| `token_budget` | `int` | `6000` | Budget total de tokens |
| `enable_hybrid` | `bool` | `True` | Ligar busca híbrida |
| `enable_filesystem` | `bool` | `True` | Ligar busca filesystem |

#### Retorno

`MergedResult` com `results: list[MergedHit]`, `mutual_count`, `hybrid_count`, `filesystem_count`, etc.

Cada `MergedHit` tem `sources: list[str]` (`["hybrid"]`, `["filesystem"]`, ou ambas), `score` (RRF), `citation`.

#### Veja também

- [`hybrid`](#hybrid) — só semântica + grafo
- [`filesystem_search`](#filesystem_search) — só índice curado

---

### `read_canonical`

**Lê o texto canônico completo** de um documento (lei inteira) ou dispositivo específico (artigo). Determinístico, sub-segundo, **gratuito**.

#### Quando usar

- Para mostrar o texto completo de uma lei ou artigo
- Quando você já tem o `document_id` e (opcionalmente) `span_id`
- Para gerar contexto sem fazer busca semântica

#### Exemplo mínimo

```python
# Documento inteiro
doc = vg.read_canonical("LEI-14133-2021")
print(f"{doc.token_count} tokens, {doc.char_count} chars")
print(doc.text[:500])

# Dispositivo específico
art = vg.read_canonical("LEI-14133-2021", span_id="ART-075")
print(art.citation)   # 'Art. 75 da Lei 14.133/2021'
print(art.text)
```

#### Parâmetros

| Nome | Tipo | Default | Descrição |
|---|---|---|---|
| `document_id` | `str` | — | ID do documento (`LEI-14133-2021`, `IN-58-2022`, etc.) |
| `span_id` | `str` | `None` | ID do dispositivo (`ART-075`, `PAR-018-2`, `INC-005-III`) |

#### Retorno

`CanonicalResult` com:

- `document_id: str`
- `text: str` — texto completo
- `token_count: int`
- `char_count: int`
- `span_id: str | None` — quando solicitado
- `breadcrumb: str | None`
- `citation: str | None` — formato jurídico (quando span_id presente)
- `source: str`

#### Veja também

- [`lookup`](#lookup) — quando você tem a referência em texto, não o ID
- [`list_documents`](#list_documents) — para descobrir `document_id`

---

## 🤖 Function Calling (4 métodos)

### `to_openai_tool`

Retorna a ferramenta VectorGov no formato **OpenAI Function Calling**.

```python
from openai import OpenAI

client = OpenAI()
tools = [vg.to_openai_tool()]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Como funciona dispensa de licitação?"}],
    tools=tools,
)

# Se o LLM chamou a tool, executa
for call in response.choices[0].message.tool_calls or []:
    result_text = vg.execute_tool_call(call)
    print(result_text)
```

**Retorna**: `dict` no schema OpenAI Function Calling.
**Custo**: free (geração local).

---

### `to_anthropic_tool`

Retorna a ferramenta no formato **Anthropic Claude Tools**.

```python
from anthropic import Anthropic

client = Anthropic()
tools = [vg.to_anthropic_tool()]

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Critérios de julgamento?"}],
)

for block in response.content:
    if block.type == "tool_use":
        print(vg.execute_tool_call(block))
```

**Retorna**: `dict` no schema Anthropic Tools.
**Custo**: free.

---

### `to_google_tool`

Retorna a ferramenta no formato **Google Gemini Function Calling**.

```python
import google.generativeai as genai

genai.configure()
model = genai.GenerativeModel(
    "gemini-2.0-flash",
    tools=[vg.to_google_tool()],
)

chat = model.start_chat()
response = chat.send_message("Quando dispensar licitação?")

for part in response.parts:
    if part.function_call:
        print(vg.execute_tool_call(part.function_call))
```

**Retorna**: `dict` no schema Google Gemini.
**Custo**: free.

---

### `execute_tool_call`

**Executa uma chamada de tool** de qualquer LLM (OpenAI, Anthropic, Gemini) sem fazer parsing manual.

```python
result_text = vg.execute_tool_call(tool_call, mode="balanced")
```

**Parâmetros**:
- `tool_call`: o objeto retornado pelo LLM (formato OpenAI, Anthropic ou Gemini)
- `mode`: opcional, modo de busca (`"fast"`, `"balanced"`, `"precise"`)

**Retorna**: `str` — resultado formatado pronto para incluir na próxima mensagem do LLM.
**Custo**: 💰 (executa `search` internamente).

---

## 📊 Tokens & Feedback (2 métodos)

### `estimate_tokens`

**Estima quantos tokens** um texto ou resultado de busca consumiria. Use para planejar contexto antes de enviar ao LLM.

```python
# A partir de um SearchResult
result = vg.search("ETP")
stats = vg.estimate_tokens(
    result,
    query="O que é ETP?",
    system_prompt=vg.get_system_prompt("detailed"),
)

print(f"Context: {stats.context_tokens}")
print(f"System:  {stats.system_tokens}")
print(f"Query:   {stats.query_tokens}")
print(f"Total:   {stats.total_tokens}")
print(f"Hits incluídos: {stats.hits_count}")

if stats.total_tokens > 100_000:
    print("⚠️ Excede janela típica de modelos pequenos")
```

**Parâmetros**:
- `content`: `str` ou `SearchResult`
- `query`: opcional
- `system_prompt`: opcional

**Retorna**: `TokenStats` com `context_tokens`, `system_tokens`, `query_tokens`, `total_tokens`, `hits_count`, `char_count`, `encoding`.

**Custo**: free.

---

### `feedback`

**Envia like/dislike** sobre um resultado para melhoria contínua das buscas.

```python
result = vg.search("dispensa de licitacao")

# ... usuário aprovou os resultados ...
vg.feedback(query_id=result.query_id, like=True)

# ... ou rejeitou ...
vg.feedback(query_id=result.query_id, like=False)
```

**Parâmetros**:
- `query_id: str` — vem de `result.query_id`
- `like: bool` — `True` (positivo) ou `False` (negativo)

**Retorna**: `bool` — `True` se registrado.
**Custo**: free.

---

## 🎯 System Prompts (2)

### `get_system_prompt`

**Retorna prompt pré-otimizado** para passar ao LLM via `to_messages(system_prompt=...)`.

```python
result = vg.search("ETP")

# Prompt padrão
messages = result.to_messages(query="O que é ETP?")

# Prompt customizado
messages = result.to_messages(
    query="O que é ETP?",
    system_prompt=vg.get_system_prompt("detailed"),
)
```

**Estilos disponíveis**:

| Style | Tokens | Quando usar |
|---|---|---|
| `default` | ~150 | Uso geral, balanceado |
| `concise` | ~80 | Respostas curtas, economize tokens |
| `detailed` | ~300 | Análises completas, jurídicas |
| `chatbot` | ~200 | Conversa multi-turno |

**Custo**: free.

📖 [Guia: System Prompts](../guides/system-prompts.md)

---

### `available_prompts` (property)

**Lista os estilos disponíveis** (não é método — é property).

```python
print(vg.available_prompts)
# ['default', 'concise', 'detailed', 'chatbot']
```

---

## 📚 Documentos (2)

### `list_documents`

**Lista todas as normas indexadas** na base.

```python
docs = vg.list_documents(page=1, limit=20)

print(f"Total: {docs.total}")
for d in docs.documents:
    print(f"  {d.document_id} — {d.tipo_documento} {d.numero}/{d.ano}")
```

**Parâmetros**:
- `page: int = 1`
- `limit: int = 20`

**Retorna**: `DocumentsResponse` com `documents: list[DocumentSummary]`, `total`, `page`.
**Custo**: free.

---

### `get_document`

**Metadados de um documento específico**.

```python
doc = vg.get_document("LEI-14133-2021")
print(f"{doc.tipo_documento} {doc.numero}/{doc.ano}")
print(f"Título: {doc.titulo}")
print(f"Chunks: {doc.chunks_count}")
```

**Parâmetros**: `document_id: str`
**Retorna**: `DocumentSummary`
**Custo**: free.

---

## 🛡️ Auditoria & Compliance (3)

### `get_audit_logs`

**Logs de eventos de auditoria** (security, performance, validation).

```python
logs = vg.get_audit_logs(
    severity="warning",
    event_category="security",
    limit=50,
    start_date="2025-01-01",
)

for log in logs.logs:
    print(f"{log.timestamp} [{log.severity}] {log.event_type}: {log.action_taken}")
```

**Parâmetros**:
- `limit: int = 50`
- `page: int = 1`
- `severity: "info" | "warning" | "critical" | None`
- `event_type: str | None`
- `event_category: "security" | "performance" | "validation" | None`
- `start_date: str | None` (ISO 8601)
- `end_date: str | None`

**Retorna**: `AuditLogsResponse` com `logs: list[AuditLog]`, `total`, `page`.
**Custo**: free.

---

### `get_audit_stats`

**Estatísticas agregadas** dos últimos N dias.

```python
stats = vg.get_audit_stats(days=7)

print(f"Eventos:         {stats.total_events}")
print(f"Bloqueados:      {stats.blocked_count}")
print(f"Por categoria:   {stats.by_category}")
print(f"Por severidade:  {stats.by_severity}")
```

**Parâmetros**: `days: int = 30`
**Retorna**: `AuditStats`
**Custo**: free.

---

### `get_audit_event_types`

**Lista os tipos de evento disponíveis** para usar como filtro.

```python
types = vg.get_audit_event_types()
print(types)
# ['injection_blocked', 'pii_detected', 'rate_limited', ...]
```

**Retorna**: `list[str]`
**Custo**: free.

📖 [Guia: Auditoria & Compliance](../guides/observability-audit.md)

---

## 🛠️ Utilitário (1)

### `close`

**Libera conexões HTTP persistentes**. Use ou via context manager (recomendado) ou explicitamente.

```python
# Recomendado: context manager auto-close
with VectorGov() as vg:
    result = vg.search("ETP")

# Ou explícito
vg = VectorGov()
try:
    result = vg.search("ETP")
finally:
    vg.close()
```

**Custo**: free.

---

## Veja também

- 🧭 [Cheat Sheet](../cheat-sheet.md) — todos os métodos em 1 página + decision tree
- 🧱 [Modelos de dados](models.md) — `Hit`, `SearchResult`, etc.
- 🍳 [README com receitas](https://github.com/euteajudo/vectorgov-sdk#-receitas-comuns)
- 🔌 [Integrações](../integrations/index.md) — OpenAI, Claude, Gemini, LangChain, MCP
- 🐛 [Tratamento de erros](../guides/error-handling.md)
