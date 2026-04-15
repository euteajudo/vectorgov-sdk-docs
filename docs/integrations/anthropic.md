# Anthropic Claude

Integração com **Anthropic Claude** (claude-sonnet-4, claude-opus-4, claude-haiku).

## Pré-requisitos

```bash
pip install vectorgov anthropic
export VECTORGOV_API_KEY=vg_...
export ANTHROPIC_API_KEY=sk-ant-...
```

## Exemplo mínimo

```python
from vectorgov import VectorGov
from anthropic import Anthropic

vg = VectorGov()
result = vg.search("Quando o ETP pode ser dispensado?")

# Claude prefere system prompt separado
messages = result.to_messages(query="Quando o ETP pode ser dispensado?")

response = Anthropic().messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=messages[0]["content"],  # system separado
    messages=[{"role": "user", "content": messages[1]["content"]}],
)

print(response.content[0].text)
```

## Tool use (function calling)

Use `vg.to_anthropic_tool()` para registrar VectorGov como ferramenta nativa do Claude.

```python
client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=[vg.to_anthropic_tool()],
    messages=[{"role": "user", "content": "Como funciona dispensa de licitação?"}],
)

# Processar tool_use blocks
for block in response.content:
    if block.type == "tool_use":
        result_text = vg.execute_tool_call(block)
        print(result_text)
    elif block.type == "text":
        print(block.text)
```

## Streaming

```python
result = vg.search("Critérios de julgamento")
messages = result.to_messages(query="Critérios de julgamento")

with Anthropic().messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system=messages[0]["content"],
    messages=[{"role": "user", "content": messages[1]["content"]}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## Veja também

- [`to_anthropic_tool`](../api/methods.md#to_anthropic_tool)
- [`execute_tool_call`](../api/methods.md#execute_tool_call)
- [OpenAI GPT](openai.md)
- [Google Gemini](gemini.md)
