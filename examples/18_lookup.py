"""
Exemplo 18: Consulta Direta por Referência (Lookup)

Busca determinística de dispositivos legais por referência textual.
Retorna texto exato com contexto (pai, filhos, irmãos).

Latência: < 1 segundo. Ideal para citações exatas.
"""

import os
from vectorgov import VectorGov

API_KEY = os.getenv("VECTORGOV_API_KEY", "vg_sua_chave_aqui")


def main():
    vg = VectorGov(api_key=API_KEY)

    # --- Consulta única ---
    print("=== CONSULTA ÚNICA ===")
    ref = "Art. 75 da Lei 14.133/2021"
    print(f"Consultando: {ref}\n")

    result = vg.lookup(ref)

    # LookupResult tem `status` ("found", "not_found", "ambiguous")
    # e `match` (singular, um Hit)
    print(f"Status: {result.status}")

    if result.match:
        match = result.match
        # Prefira citation (formato jurídico) sobre source — v0.19.4+
        label = match.citation or match.source or "?"
        print(f"Citação: {label}")
        print(f"Texto: {match.text[:200]}...")
        print(f"Documento: {match.document_id}")

        # Evidence URLs (links para verificação) — atributos diretos no Hit
        if match.evidence_url:
            print(f"\nEvidência:")
            print(f"  Trecho destacado: {match.evidence_url}")
        if match.document_url:
            print(f"  PDF original:    {match.document_url}")

        # Pai e irmãos vêm direto no LookupResult, não no match
        if result.parent:
            parent_label = result.parent.citation or result.parent.source or "?"
            print(f"\nArtigo pai: {parent_label}")
        if result.siblings:
            print(f"Irmãos: {len(result.siblings)} dispositivos")
        if result.children:
            print(f"Filhos: {len(result.children)} dispositivos (incisos/parágrafos)")

        # Texto consolidado (caput + filhos)
        if result.stitched_text:
            print(f"\nTexto consolidado ({len(result.stitched_text)} chars):")
            print(result.stitched_text[:300] + "...")
    else:
        print(f"Não encontrado.")

    # --- Consulta em lote ---
    print("\n\n=== CONSULTA EM LOTE ===")
    refs = [
        "Art. 75 da Lei 14.133/2021",
        "Art. 6 da IN 65/2021",
        "Art. 3 do Decreto 10.947/2022",
    ]
    print(f"Consultando {len(refs)} referências...\n")

    batch = vg.lookup(refs)

    # Em batch, o LookupResult tem `results` (list de LookupResult)
    if batch.results:
        for sub in batch.results:
            if sub.match:
                label = sub.match.citation or sub.match.source or sub.match.document_id
                preview = (sub.match.text or "")[:80]
                print(f"  ✓ {label}: {preview}...")
            else:
                print(f"  ✗ {sub.reference}: não encontrado ({sub.status})")
    else:
        print("Nenhum resultado.")


if __name__ == "__main__":
    main()
