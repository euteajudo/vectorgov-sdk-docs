# Ollama (LLMs locais)

Integração com **Ollama** — forma mais simples de rodar LLMs localmente, gratuita.

## Pré-requisitos

```bash
# 1. Instale o Ollama: https://ollama.ai/
# 2. Baixe um modelo
ollama pull llama3:8b

# 3. Instale o SDK (Ollama integration usa só stdlib)
pip install vectorgov
```

> ✨ A integração Ollama **não requer extras** — usa apenas a biblioteca padrão do Python.

## Pipeline RAG simples

```python
from vectorgov import VectorGov
from vectorgov.integrations.ollama import create_rag_pipeline

vg = VectorGov()

# Cria pipeline RAG com Ollama
rag = create_rag_pipeline(vg, model="llama3:8b")

# Usa como função
resposta = rag("Quais os critérios de julgamento na licitação?")
print(resposta)
```

## Classe `VectorGovOllama` (mais controle)

```python
from vectorgov.integrations.ollama import VectorGovOllama

rag = VectorGovOllama(vg, model="llama3:8b", top_k=5)

response = rag.ask("O que é ETP?")

print(response.answer)        # texto da resposta
print(response.sources)       # lista de fontes
print(response.latency_ms)    # latência total
print(response.model)         # modelo usado
```

## Chat com histórico

```python
rag = VectorGovOllama(vg, model="llama3:8b")

messages = [{"role": "user", "content": "O que é ETP?"}]
response = rag.chat(messages, use_rag=True)
print(response)

# Continua a conversa
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": "E quando pode ser dispensado?"})
response2 = rag.chat(messages, use_rag=True)
print(response2)
```

## Modelos recomendados

| Modelo | RAM | Qualidade | Português | Comando |
|---|---|---|---|---|
| `llama3.2:1b` | 1GB | Básica | Bom | `ollama pull llama3.2:1b` |
| `llama3.2:3b` | 4GB | Boa | Muito Bom | `ollama pull llama3.2:3b` |
| `llama3:8b` | 8GB | Muito Boa | **Excelente** | `ollama pull llama3:8b` |
| `mistral:7b` | 7GB | Muito Boa | Bom | `ollama pull mistral:7b` |
| `qwen2.5:7b` | 7GB | Excelente | Bom | `ollama pull qwen2.5:7b` |

```python
from vectorgov.integrations.ollama import list_models, get_recommended_models

# Lista modelos instalados localmente
print(list_models())

# Lista modelos recomendados
for name, info in get_recommended_models().items():
    print(f"{name}: {info['description']}")
```

## Veja também

- [HuggingFace Transformers](transformers.md) — alternativa local sem servidor
- [OpenAI GPT](openai.md) — LLM comercial
