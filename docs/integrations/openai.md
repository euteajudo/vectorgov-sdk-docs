# OpenAI

Integração com **OpenAI GPT** (gpt-4o, gpt-4o-mini, gpt-4-turbo).

## Pré-requisitos

```bash
pip install vectorgov openai
export VECTORGOV_API_KEY=vg_...
export OPENAI_API_KEY=sk-...
```

## Exemplo mínimo (3 linhas)

```python
from vectorgov import VectorGov
from openai import OpenAI

vg = VectorGov()
result = vg.search("Quando o ETP pode ser dispensado?")

response = OpenAI().chat.completions.create(
    model="gpt-4o-mini",
    messages=result.to_messages(query="Quando o ETP pode ser dispensado?"),
)
print(response.choices[0].message.content)
```

`result.to_messages()` retorna `list[dict]` no formato `[{"role": "system", ...}, {"role": "user", ...}]` — universal de OpenAI/Anthropic/Gemini/Ollama.

## Function calling automático

Use `vg.to_openai_tool()` para registrar VectorGov como ferramenta. O LLM decide quando consultar legislação.

```python
client = OpenAI()

# Primeira chamada — GPT decide se precisa consultar legislação
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Quais os critérios de julgamento?"}],
    tools=[vg.to_openai_tool()],
)

# Se GPT chamou a tool, executa
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    result_text = vg.execute_tool_call(tool_call)

    # Segunda chamada com o resultado
    final = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Quais os critérios de julgamento?"},
            response.choices[0].message,
            {"role": "tool", "tool_call_id": tool_call.id, "content": result_text},
        ],
    )
    print(final.choices[0].message.content)
```

## Streaming

Streaming é configurado **no OpenAI** (VectorGov não gera tokens):

```python
result = vg.search("Critérios de julgamento")  # ~2s

stream = OpenAI().chat.completions.create(
    model="gpt-4o-mini",
    messages=result.to_messages(query="Critérios de julgamento"),
    stream=True,  # 👈 streaming aqui
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Veja também

- [`to_openai_tool`](../api/methods.md#to_openai_tool) — gera o schema da ferramenta
- [`execute_tool_call`](../api/methods.md#execute_tool_call) — executa qualquer tool_call
- [`get_system_prompt`](../api/methods.md#get_system_prompt) — prompts pré-otimizados
- [Anthropic Claude](anthropic.md)
- [Google Gemini](gemini.md)
