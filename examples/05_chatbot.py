"""
Exemplo 5: Chatbot Jurídico

Mostra como criar um chatbot que combina VectorGov + OpenAI.
Suporta dois modos:

- **Interativo** (default quando rodado em terminal): faz `input()` em loop
  até o usuário digitar 'sair'. Use para conversar de verdade no terminal.

- **Demo** (quando stdin não é TTY ou env CHATBOT_DEMO=1): roda 3 perguntas
  pré-definidas e encerra. Permite testar o fluxo sem terminal interativo.

Requisitos:
    pip install vectorgov openai
"""

import os
import sys
from vectorgov import VectorGov
from openai import OpenAI

VECTORGOV_KEY = os.getenv("VECTORGOV_API_KEY", "vg_xxx")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

DEMO_QUERIES = [
    "O que é ETP e quando deve ser elaborado?",
    "Quais os critérios de julgamento na licitação?",
    "Como funciona a dispensa de licitação?",
]


def is_interactive() -> bool:
    """Detecta se está rodando em terminal interativo."""
    if os.getenv("CHATBOT_DEMO") == "1":
        return False
    try:
        return sys.stdin.isatty()
    except (AttributeError, ValueError):
        return False


def get_query_for_turn(turn: int) -> str | None:
    """Pega a próxima query do usuário (interativo ou demo)."""
    if is_interactive():
        try:
            return input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            return None
    # Modo demo
    if turn >= len(DEMO_QUERIES):
        return None
    q = DEMO_QUERIES[turn]
    print(f"Você: {q}")
    return q


def create_chatbot():
    """Cria um chatbot com VectorGov + OpenAI."""
    vg = VectorGov(api_key=VECTORGOV_KEY)
    openai = OpenAI(api_key=OPENAI_KEY)

    # System prompt para o chatbot
    system_prompt = vg.get_system_prompt("chatbot")

    print("=" * 60)
    print("CHATBOT JURÍDICO - VectorGov")
    print("=" * 60)
    if is_interactive():
        print("Digite suas perguntas sobre licitações e contratos públicos.")
        print("Digite 'sair' para encerrar.\n")
    else:
        print(f"Modo demo — rodando {len(DEMO_QUERIES)} perguntas pré-definidas.\n")

    turn = 0
    while True:
        query = get_query_for_turn(turn)
        if query is None or query.lower() in ("sair", "exit", "quit"):
            print("\nAté logo!")
            break
        if not query:
            turn += 1
            continue

        # Buscar contexto (modo fast para chatbot)
        print("\n[Buscando...]")
        results = vg.search(query, mode="fast", top_k=3)

        # Gerar resposta
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=results.to_messages(query, system_prompt=system_prompt),
            temperature=0.5,
            max_tokens=500,
        )

        answer = response.choices[0].message.content
        print(f"\nAssistente: {answer}")

        # Mostra fontes — prefere citation (formato jurídico) sobre source
        sources = []
        for hit in results.hits[:3]:
            label = hit.citation or hit.source
            sources.append(label)
        print(f"\n[Fontes: {', '.join(sources)}]")
        print("-" * 60 + "\n")

        turn += 1


if __name__ == "__main__":
    create_chatbot()
