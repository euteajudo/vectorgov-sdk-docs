# Google Gemini

Integração com **Google Gemini** (gemini-2.0-flash, gemini-1.5-pro).

## Pré-requisitos

```bash
pip install vectorgov google-generativeai
export VECTORGOV_API_KEY=vg_...
export GOOGLE_API_KEY=...
```

## Exemplo mínimo

```python
from vectorgov import VectorGov
import google.generativeai as genai

vg = VectorGov()
genai.configure()  # lê GOOGLE_API_KEY da env

result = vg.search("O que é ETP?")
messages = result.to_messages(query="O que é ETP?")

# Gemini usa system_instruction separado
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=messages[0]["content"],
)

response = model.generate_content(messages[1]["content"])
print(response.text)
```

## Function calling

```python
model = genai.GenerativeModel(
    "gemini-2.0-flash",
    tools=[vg.to_google_tool()],
)

chat = model.start_chat()
response = chat.send_message("Quando dispensar licitação?")

# Processar function_call se houver
for part in response.parts:
    if part.function_call:
        result_text = vg.execute_tool_call(part.function_call)
        # Continuar a conversa com o resultado
        followup = chat.send_message([
            genai.protos.Content(
                parts=[genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=part.function_call.name,
                        response={"result": result_text},
                    )
                )]
            )
        ])
        print(followup.text)
```

## Streaming

```python
result = vg.search("Critérios de julgamento")
messages = result.to_messages(query="Critérios de julgamento")

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=messages[0]["content"],
)

response = model.generate_content(messages[1]["content"], stream=True)
for chunk in response:
    print(chunk.text, end="", flush=True)
```

## Veja também

- [`to_google_tool`](../api/methods.md#to_google_tool)
- [`execute_tool_call`](../api/methods.md#execute_tool_call)
- [Google ADK](google-adk.md)
- [OpenAI GPT](openai.md)
