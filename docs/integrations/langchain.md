# LangChain

Integração com **LangChain** via `VectorGovRetriever` e `VectorGovTool`.

## Pré-requisitos

```bash
pip install 'vectorgov[langchain]'
```

## VectorGovRetriever (RetrievalQA)

```python
from vectorgov.integrations.langchain import VectorGovRetriever
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

retriever = VectorGovRetriever(top_k=5)  # lê VECTORGOV_API_KEY da env

qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4o-mini"),
    retriever=retriever,
)

answer = qa.invoke("Quando o ETP pode ser dispensado?")
print(answer["result"])
```

## LCEL (LangChain Expression Language)

```python
from vectorgov.integrations.langchain import VectorGovRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

retriever = VectorGovRetriever()
llm = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_template("""
Contexto: {context}

Pergunta: {question}
""")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("O que é ETP?")
print(answer)
```

## VectorGovTool (Agentes)

```python
from vectorgov.integrations.langchain import VectorGovTool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

tool = VectorGovTool()
llm = ChatOpenAI(model="gpt-4o")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente jurídico que usa VectorGov para consultar legislação."),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_openai_tools_agent(llm, [tool], prompt)
executor = AgentExecutor(agent=agent, tools=[tool])

result = executor.invoke({"input": "O que diz a lei sobre ETP?"})
print(result["output"])
```

## Veja também

- [LangGraph](langgraph.md) — para grafos RAG mais complexos
- [`to_openai_tool`](../api/methods.md#to_openai_tool) — alternativa direta sem LangChain
