# HuggingFace Transformers

Integração com modelos do **HuggingFace Hub** rodando localmente via `transformers`.

## Pré-requisitos

```bash
pip install 'vectorgov[transformers]'
# ou explicitamente:
pip install vectorgov transformers torch accelerate
```

## Pipeline RAG simples

```python
from vectorgov import VectorGov
from vectorgov.integrations.transformers import create_rag_pipeline

vg = VectorGov()

# Inicializa pipeline com modelo do Hub
rag = create_rag_pipeline(
    vg,
    model_name="meta-llama/Llama-3.2-3B-Instruct",
    top_k=5,
)

# Usa como função
resposta = rag("O que é ETP?")
print(resposta.answer)
print(resposta.sources)
```

## Modelos recomendados

| Modelo | Tamanho | Quantização | Qualidade |
|---|---|---|---|
| `meta-llama/Llama-3.2-1B-Instruct` | 1B | fp16 | Básica |
| `meta-llama/Llama-3.2-3B-Instruct` | 3B | fp16 | Boa |
| `meta-llama/Llama-3.1-8B-Instruct` | 8B | int4 (4GB VRAM) | Muito Boa |
| `Qwen/Qwen2.5-7B-Instruct` | 7B | int4 | Excelente |

## CPU-only (sem GPU)

```python
from vectorgov.integrations.transformers import VectorGovTransformers

rag = VectorGovTransformers(
    vg,
    model_name="meta-llama/Llama-3.2-1B-Instruct",
    device="cpu",  # 👈 força CPU
)

response = rag.ask("O que é ETP?")
print(response.answer)
```

## Quantização 4-bit (economia de VRAM)

```python
rag = VectorGovTransformers(
    vg,
    model_name="meta-llama/Llama-3.1-8B-Instruct",
    quantization="4bit",  # ~4GB VRAM para modelo 7B
    device="cuda",
)
```

## Veja também

- [Ollama](ollama.md) — alternativa mais simples para rodar LLMs locais
- [OpenAI GPT](openai.md) — LLM comercial
