# MCP Server (Claude Desktop, Cursor, Windsurf)

Servidor **MCP (Model Context Protocol)** para integração direta com Claude Desktop, Cursor, Windsurf e outras ferramentas compatíveis.

## Pré-requisitos

```bash
pip install 'vectorgov[mcp]'
```

## Configuração no Claude Desktop

Edite o arquivo de configuração:

| OS | Caminho |
|---|---|
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` |

### Opção A — via `uvx` (recomendada, sem instalar)

```json
{
    "mcpServers": {
        "vectorgov": {
            "command": "uvx",
            "args": ["vectorgov-mcp"],
            "env": {
                "VECTORGOV_API_KEY": "vg_sua_chave_aqui"
            }
        }
    }
}
```

### Opção B — após instalar via pip

```json
{
    "mcpServers": {
        "vectorgov": {
            "command": "vectorgov-mcp",
            "env": {
                "VECTORGOV_API_KEY": "vg_sua_chave_aqui"
            }
        }
    }
}
```

Reinicie o Claude Desktop após editar.

## Configuração no Cursor

Adicione em `Settings → Features → MCP → Add MCP Server`:

```json
{
    "name": "vectorgov",
    "command": "uvx",
    "args": ["vectorgov-mcp"],
    "env": {
        "VECTORGOV_API_KEY": "vg_sua_chave"
    }
}
```

## Executar manualmente

```bash
# Via uvx (sem instalar)
uvx vectorgov-mcp

# Via pip (após instalar com [mcp])
vectorgov-mcp

# Via Python
python -m vectorgov.mcp
```

## Ferramentas expostas

O servidor MCP expõe 3 ferramentas que o Claude pode chamar:

| Ferramenta | Descrição |
|---|---|
| `search_legislation` | Busca semântica em legislação brasileira |
| `list_available_documents` | Lista normas indexadas na base |
| `get_article_text` | Texto completo de um artigo específico |

Após configurar, no Claude Desktop você pode pedir naturalmente:

> "Use o VectorGov para buscar o que diz a lei sobre dispensa de licitação"

E o Claude vai chamar `search_legislation` automaticamente.

## Veja também

- [Anthropic Claude (API direta)](anthropic.md) — alternativa via SDK Python
- [`to_anthropic_tool`](../api/methods.md#to_anthropic_tool) — tool sem MCP
