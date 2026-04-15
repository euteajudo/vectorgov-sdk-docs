"""
Exemplo 15: Pipeline RAG + Feedback

Demonstra o fluxo completo:
1. Buscar contexto no VectorGov
2. Gerar resposta com OpenAI (ou outro LLM)
3. Enviar feedback (like/dislike) usando o `query_id` da busca

> **Nota sobre `store_response()`**: a versão atual do SDK 0.19.5 expõe
> o método `vg.store_response()`, mas o endpoint correspondente no
> backend foi descontinuado. Para enviar feedback, use diretamente o
> `query_id` que vem do `vg.search()` — funciona sem precisar
> armazenar a resposta.

Requisitos:
    pip install vectorgov openai
"""

import os
import time
from vectorgov import VectorGov
from openai import OpenAI


def main():
    vg = VectorGov(api_key=os.environ.get("VECTORGOV_API_KEY"))
    openai_client = OpenAI()

    query = "O que é o Estudo Técnico Preliminar (ETP)?"
    print(f"Pergunta: {query}\n")

    # 1. Busca no VectorGov
    print("1. Buscando contexto no VectorGov...")
    start_search = time.time()
    results = vg.search(query, top_k=5)
    search_time = (time.time() - start_search) * 1000
    print(f"   Encontrados: {len(results)} documentos ({search_time:.0f}ms)")
    print(f"   query_id: {results.query_id}\n")

    # 2. Gera resposta com OpenAI
    print("2. Gerando resposta com OpenAI gpt-4o-mini...")
    start_gen = time.time()
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=results.to_messages(query),
        temperature=0.7,
        max_tokens=400,
    )
    gen_time = (time.time() - start_gen) * 1000
    answer = response.choices[0].message.content
    print(f"   Resposta gerada ({gen_time:.0f}ms)\n")
    print("-" * 60)
    print(answer)
    print("-" * 60 + "\n")

    # 3. Mostra as fontes (com citation jurídica — v0.19.4+)
    print("3. Fontes consultadas:")
    for i, hit in enumerate(results.hits[:3], 1):
        label = hit.citation or hit.source
        print(f"   [{i}] {label} (score={hit.score:.0%})")
    print()

    # 4. Envia feedback usando o query_id
    print("4. Enviando feedback positivo (like)...")
    feedback_ok = vg.feedback(results.query_id, like=True)
    if feedback_ok:
        print("   ✅ Feedback registrado com sucesso!")
    else:
        # O endpoint /sdk/feedback existe mas pode estar indisponível
        # temporariamente. Não é fatal — a resposta ao usuário já foi gerada.
        print("   ⚠️  Feedback não foi registrado (endpoint indisponível).")
        print("   O fluxo principal funcionou normalmente.")

    print("\n" + "=" * 60)
    print("Resumo:")
    print(f"  - Busca: {search_time:.0f}ms")
    print(f"  - Geração (OpenAI): {gen_time:.0f}ms")
    print(f"  - Total: {search_time + gen_time:.0f}ms")
    print(f"  - query_id (use em feedback): {results.query_id}")
    print("=" * 60)


if __name__ == "__main__":
    main()
