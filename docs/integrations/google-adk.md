# Google ADK

Integração com **Google Agent Development Kit** (ADK).

## Pré-requisitos

```bash
pip install 'vectorgov[google-adk]'
export VECTORGOV_API_KEY=vg_...
```

## Ferramenta de busca individual

```python
from vectorgov.integrations.google_adk import create_search_tool

# Cria ferramenta
search = create_search_tool(top_k=5)

# Testa diretamente (sem agente)
result = search("O que é ETP?")
print(result)
```

## Toolset completo (3 ferramentas)

```python
from vectorgov.integrations.google_adk import VectorGovToolset
from google.adk.agents import Agent

toolset = VectorGovToolset()

# Lista as ferramentas disponíveis
for tool in toolset.get_tools():
    print(f"- {tool.__name__}")
# - search_brazilian_legislation
# - list_legal_documents
# - get_article_text

# Usa com agente ADK
agent = Agent(
    name="legal_assistant",
    model="gemini-2.0-flash",
    tools=toolset.get_tools(),
)
```

## Agente pré-configurado

```python
from vectorgov.integrations.google_adk import create_legal_agent

agent = create_legal_agent()

response = agent.run("Quais os critérios de julgamento na licitação?")
print(response)
```

## Veja também

- [Gemini](gemini.md) — function calling direto sem ADK
- [LangGraph](langgraph.md) — alternativa com Python puro
