# LangGraph

Integração com **LangGraph** para grafos RAG e agentes ReAct.

## Pré-requisitos

```bash
pip install 'vectorgov[langgraph]'
```

## ReAct Agent

```python
from vectorgov.integrations.langgraph import create_vectorgov_tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# Cria ferramenta VectorGov
tool = create_vectorgov_tool(top_k=5)  # lê VECTORGOV_API_KEY

# Cria agente ReAct
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools=[tool])

# Executa
result = agent.invoke({"messages": [("user", "O que é ETP?")]})
print(result["messages"][-1].content)
```

## Grafo RAG customizado

```python
from vectorgov.integrations.langgraph import create_retrieval_node, VectorGovState
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# Nó de retrieval VectorGov
retrieval_node = create_retrieval_node(top_k=5)

# Nó de geração
def generate(state: VectorGovState) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini")
    context = state.get("context", "")
    query = state.get("query", "")
    response = llm.invoke(f"Contexto: {context}\n\nPergunta: {query}")
    return {"response": response.content}

# Constrói grafo
builder = StateGraph(dict)
builder.add_node("retrieve", retrieval_node)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

graph = builder.compile()

# Executa
result = graph.invoke({"query": "Quando o ETP pode ser dispensado?"})
print(result["response"])
```

## Grafo RAG pré-configurado

```python
from vectorgov.integrations.langgraph import create_legal_rag_graph
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
graph = create_legal_rag_graph(llm=llm)

result = graph.invoke({"query": "Quais os critérios de julgamento?"})
print(result["response"])
```

## Veja também

- [LangChain](langchain.md) — versão sem grafo
- [Google ADK](google-adk.md) — alternativa multi-agent do Google
