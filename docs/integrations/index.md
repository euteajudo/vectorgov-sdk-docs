# Integrações

VectorGov fornece chunks jurídicos prontos para alimentar **qualquer LLM ou framework de agentes**. O retorno do `vg.search()` (e dos demais métodos) tem um método universal `result.to_messages(query)` que serve OpenAI, Claude, Gemini, Ollama e outros sem adaptação.

## LLMs comerciais

| | | |
|---|---|---|
| 🤖 [**OpenAI GPT**](openai.md) | gpt-4o, gpt-4o-mini, gpt-4-turbo | `pip install openai` |
| 🟣 [**Anthropic Claude**](anthropic.md) | claude-sonnet-4, opus-4, haiku | `pip install anthropic` |
| 🔵 [**Google Gemini**](gemini.md) | gemini-2.0-flash, gemini-1.5-pro | `pip install google-generativeai` |

## LLMs locais (gratuitos)

| | | |
|---|---|---|
| 🦙 [**Ollama**](ollama.md) | llama3, mistral, qwen2.5 (recomendado) | nenhum extra |
| 🤗 [**HuggingFace Transformers**](transformers.md) | qualquer modelo do Hub | `pip install 'vectorgov[transformers]'` |

## Frameworks de agentes

| | | |
|---|---|---|
| 🦜 [**LangChain**](langchain.md) | `VectorGovRetriever` + `VectorGovTool` | `pip install 'vectorgov[langchain]'` |
| 📊 [**LangGraph**](langgraph.md) | ReAct agents + grafos RAG | `pip install 'vectorgov[langgraph]'` |
| 🅖 [**Google ADK**](google-adk.md) | toolset para Agent Dev Kit | `pip install 'vectorgov[google-adk]'` |

## Protocolos

| | | |
|---|---|---|
| 🔌 [**MCP Server**](mcp.md) | Claude Desktop, Cursor, Windsurf | `pip install 'vectorgov[mcp]'` |

## Instalação com extras

```bash
# Tudo de uma vez
pip install 'vectorgov[all]'

# Ou apenas o que você precisa
pip install 'vectorgov[langchain,langgraph]'
pip install 'vectorgov[mcp]'
```

## O padrão universal: `to_messages()`

Todas as integrações funcionam porque o `SearchResult` (e demais Results) expõem o método universal `to_messages(query)`:

```python
result = vg.search("...")
messages = result.to_messages(query="...")
# messages é uma list[dict] no formato {"role": "system|user|assistant", "content": "..."}
```

Esse formato funciona em:
- ✅ OpenAI Chat Completions
- ✅ Anthropic Messages
- ✅ Google Gemini (com adaptação leve para `system_instruction`)
- ✅ Ollama API
- ✅ LangChain (via `from_messages`)
- ✅ Praticamente qualquer LLM moderno
