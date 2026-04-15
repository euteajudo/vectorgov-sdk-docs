"""
Exemplo 17: Busca Híbrida com Expansão por Grafo

Combina busca semântica com navegação por relações
normativas no grafo: CITA, REGULAMENTA, COMPLEMENTA, EXCEPCIONA.

Ideal para encontrar normas relacionadas e cadeias regulatórias.
"""

import os
from vectorgov import VectorGov

API_KEY = os.getenv("VECTORGOV_API_KEY", "vg_sua_chave_aqui")


def main():
    vg = VectorGov(api_key=API_KEY)

    query = "Quais os critérios de julgamento na licitação?"
    print(f"Hybrid Search: {query}\n")

    result = vg.hybrid(
        query,
        top_k=5,
        hops=2,                          # até 2 saltos no grafo
        graph_expansion="bidirectional",  # segue citações em ambas direções
        token_budget=3000,               # limite de tokens no contexto
    )

    # --- Evidências diretas (busca semântica) ---
    print(f"=== EVIDÊNCIAS DIRETAS ({len(result.hits)} resultados) ===")
    for i, hit in enumerate(result.hits, 1):
        # Prefira citation (formato jurídico) sobre source — v0.19.4+
        label = hit.citation or hit.source
        print(f"[{i}] {label} (score: {hit.score:.2%})")
        print(f"    {hit.text[:150]}...")

    # --- Expansão via grafo (artigos citados) ---
    # graph_nodes contém objetos Hit (não dicts), com atributos hop/frequency/etc
    print(f"\n=== EXPANSÃO VIA GRAFO ({len(result.graph_nodes)} nós) ===")
    for i, node in enumerate(result.graph_nodes, 1):
        label = node.citation or node.source or node.document_id or "?"
        text = (node.text or "")[:150]
        print(f"[G{i}] {label} (hop={node.hop}, citado {node.frequency}x)")
        print(f"     {text}...")

    # --- Estatísticas ---
    print(f"\n=== STATS ===")
    print(f"Seeds (busca semântica): {result.stats.get('seeds', result.stats.get('seeds_count', '?'))}")
    print(f"Graph nodes: {result.stats.get('graph_nodes', result.stats.get('nodes', '?'))}")
    print(f"Tokens usados: {result.stats.get('tokens', result.stats.get('total_tokens', '?'))}")
    print(f"Latência: {result.latency_ms}ms")

    # --- Contexto formatado para LLM ---
    print(f"\n=== CONTEXTO ===")
    print(result.to_context()[:400] + "...")


if __name__ == "__main__":
    main()
