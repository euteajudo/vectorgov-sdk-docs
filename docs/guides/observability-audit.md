# Observabilidade e Auditoria

> **Monitore, rastreie e analise o uso da sua integração com VectorGov**

O VectorGov SDK oferece ferramentas completas de observabilidade e auditoria, permitindo que você monitore o uso da API, detecte problemas de segurança, atenda requisitos de compliance e debug de integrações.

---

## Segurança e Isolamento de Dados

### Por que seus logs são privados?

O VectorGov é uma plataforma **multi-tenant**, onde múltiplos clientes compartilham a mesma infraestrutura. Para garantir privacidade e segurança:

| Aspecto | Como Funciona |
|---------|---------------|
| **Isolamento** | Cada API Key só acessa seus próprios logs |
| **Filtro Automático** | O backend filtra por `api_key_id` automaticamente |
| **Sem Acesso Cruzado** | Impossível ver logs de outras organizações |
| **Dados Sensíveis** | Queries podem conter informações confidenciais |

### O que isso significa para você?

```python
from vectorgov import VectorGov

# Empresa A
vg_a = VectorGov(api_key="vg_empresa_a_xxx")
logs_a = vg_a.get_audit_logs()  # Só vê logs da Empresa A

# Empresa B
vg_b = VectorGov(api_key="vg_empresa_b_yyy")
logs_b = vg_b.get_audit_logs()  # Só vê logs da Empresa B

# Não há como a Empresa A acessar logs da Empresa B
```

---

## Por que usar Auditoria?

| Caso de Uso | Descrição |
|-------------|-----------|
| **Compliance** | Atenda requisitos de LGPD, auditoria interna e governança |
| **Segurança** | Detecte tentativas de injeção, vazamento de PII e uso suspeito |
| **Debugging** | Investigue problemas de integração e erros de validação |
| **Monitoramento** | Acompanhe métricas de uso, latência e padrões de queries |
| **Billing** | Entenda o consumo da API para planejamento de custos |

---

## Métodos Disponíveis

O SDK oferece 3 métodos para acessar dados de auditoria:

| Método | Função | Retorno |
|--------|--------|---------|
| `get_audit_logs()` | Lista eventos de auditoria com filtros | `AuditLogsResponse` |
| `get_audit_stats()` | Estatísticas agregadas de um período | `AuditStats` |
| `get_audit_event_types()` | Lista tipos de eventos disponíveis | `list[str]` |

> **IMPORTANTE**: Você só tem acesso aos seus próprios logs de auditoria. Logs de outros clientes não são visíveis.

---

## Importância de Cada Método

### `get_audit_logs()` - Investigação e Compliance

**Por que é importante:**

| Cenário | Como o Método Ajuda |
|---------|---------------------|
| **Investigação de Incidentes** | Veja exatamente o que aconteceu, quando e qual query causou o problema |
| **Compliance LGPD** | Prove que dados pessoais foram detectados e tratados adequadamente |
| **Debugging** | Identifique queries mal formadas ou que causam erros de validação |
| **Auditoria Interna** | Documente uso da API para relatórios de governança |

**O que cada campo retornado significa:**

| Campo | Significado | Ação Recomendada |
|-------|-------------|------------------|
| `event_type` | Tipo do evento (ex: `pii_detected`) | Filtre por tipos críticos |
| `severity` | Gravidade (`info`, `warning`, `critical`) | Monitore `critical` em tempo real |
| `risk_score` | Score de risco de 0.0 a 1.0 | Investigue scores > 0.7 |
| `action_taken` | O que o sistema fez (`logged`, `blocked`, `warned`) | Revise ações `blocked` |
| `query_text` | Query que gerou o evento (truncada) | Use para reproduzir problemas |
| `detection_types` | O que foi detectado (ex: `["cpf", "email"]`) | Identifique padrões de PII |

### `get_audit_stats()` - Visão Gerencial e Tendências

**Por que é importante:**

| Cenário | Como o Método Ajuda |
|---------|---------------------|
| **Dashboard Executivo** | Mostre métricas de segurança para stakeholders |
| **Identificação de Tendências** | Detecte aumento de tentativas de injection |
| **Planejamento de Capacidade** | Entenda volume de uso para sizing |
| **KPIs de Segurança** | Acompanhe taxa de bloqueios vs requisições totais |

**Métricas chave retornadas:**

| Campo | Significado | Meta Ideal |
|-------|-------------|------------|
| `total_events` | Total de eventos no período | Crescimento controlado |
| `blocked_count` | Requisições bloqueadas | Próximo de 0 |
| `warning_count` | Avisos gerados | Monitorar tendência |
| `events_by_type` | Distribuição por tipo | Maioria deve ser `search_completed` |
| `events_by_severity` | Distribuição por gravidade | Maioria deve ser `info` |

### `get_audit_event_types()` - Descoberta e Integração

**Por que é importante:**

| Cenário | Como o Método Ajuda |
|---------|---------------------|
| **Construir Interfaces** | Popular dropdowns de filtro dinamicamente |
| **Manter Compatibilidade** | Descobrir novos tipos de eventos adicionados |
| **Documentação** | Gerar docs automáticos dos eventos possíveis |
| **Validação** | Verificar se um tipo de evento existe antes de filtrar |

---

## `get_audit_logs()` - Listar Eventos

Lista eventos de auditoria com filtros avançados e paginação.

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `limit` | `int` | `50` | Quantidade por página (1-100) |
| `page` | `int` | `1` | Página de resultados |
| `severity` | `str` | `None` | Filtrar por severidade |
| `event_type` | `str` | `None` | Filtrar por tipo de evento |
| `event_category` | `str` | `None` | Filtrar por categoria |
| `start_date` | `str` | `None` | Data inicial (ISO 8601) |
| `end_date` | `str` | `None` | Data final (ISO 8601) |

### Exemplo Básico

```python
from vectorgov import VectorGov

vg = VectorGov(api_key="vg_xxx")

# Listar últimos 50 logs
logs = vg.get_audit_logs()
print(f"Total de eventos: {logs.total}")

for log in logs.logs:
    print(f"{log.created_at} | {log.event_type} | {log.severity}")
```

### Exemplo com Filtros

```python
# Apenas eventos de segurança com severidade warning ou critical
logs = vg.get_audit_logs(
    event_category="security",
    severity="warning",
    limit=100,
)

for log in logs.logs:
    print(f"⚠️ {log.event_type}: {log.query_text[:50] if log.query_text else 'N/A'}...")
    if log.action_taken:
        print(f"   Ação: {log.action_taken}")
```

### Exemplo com Período

```python
# Eventos da última semana
logs = vg.get_audit_logs(
    start_date="2025-01-12",
    end_date="2025-01-19",
    limit=100,
)

print(f"Eventos na semana: {logs.total}")
```

---

## `get_audit_stats()` - Estatísticas Agregadas

Obtém estatísticas resumidas de um período, ideal para dashboards e monitoramento.

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `days` | `int` | `30` | Período em dias (1-90) |

### Exemplo

```python
# Estatísticas dos últimos 30 dias
stats = vg.get_audit_stats(days=30)

print(f"📊 Resumo dos últimos {stats.period_days} dias:")
print(f"   Total de eventos: {stats.total_events}")
print(f"   Bloqueados: {stats.blocked_count}")
print(f"   Avisos: {stats.warning_count}")

print(f"\n📈 Por tipo:")
for event_type, count in stats.events_by_type.items():
    print(f"   {event_type}: {count}")

print(f"\n🚨 Por severidade:")
for severity, count in stats.events_by_severity.items():
    print(f"   {severity}: {count}")
```

### Saída Exemplo

```
📊 Resumo dos últimos 30 dias:
   Total de eventos: 1234
   Bloqueados: 12
   Avisos: 45

📈 Por tipo:
   search_completed: 1150
   pii_detected: 32
   injection_detected: 7
   rate_limit_exceeded: 45

🚨 Por severidade:
   info: 1150
   warning: 72
   critical: 12
```

---

## `get_audit_event_types()` - Tipos de Eventos

Lista todos os tipos de eventos de auditoria disponíveis no sistema.

### Exemplo

```python
types = vg.get_audit_event_types()
print("Tipos de eventos disponíveis:")
for event_type in types:
    print(f"  - {event_type}")
```

---

## Tipos de Eventos

| Tipo | Categoria | Descrição |
|------|-----------|-----------|
| `pii_detected` | security | Dados pessoais (CPF, email, telefone) detectados na query |
| `injection_detected` | security | Tentativa de prompt injection detectada |
| `injection_blocked` | security | Tentativa de prompt injection bloqueada |
| `rate_limit_exceeded` | performance | Rate limit da API excedido |
| `auth_failed` | security | Falha de autenticação (API key inválida) |
| `validation_error` | validation | Erro de validação de parâmetros |
| `low_relevance_query` | performance | Query com baixa relevância nos resultados |
| `search_completed` | performance | Busca concluída com sucesso |
| `feedback_received` | performance | Feedback (like/dislike) recebido |

---

## Severidades

| Severidade | Descrição | Ação do Sistema |
|------------|-----------|-----------------|
| `info` | Informativo | Apenas registrado |
| `warning` | Aviso | Registrado com alerta |
| `critical` | Crítico | Requisição pode ser bloqueada |

---

## Categorias

| Categoria | Eventos Típicos |
|-----------|-----------------|
| `security` | pii_detected, injection_detected, auth_failed |
| `performance` | rate_limit_exceeded, search_completed, low_relevance_query |
| `validation` | validation_error |

---

## Modelos de Dados

### `AuditLog`

Representa um evento individual de auditoria.

```python
@dataclass
class AuditLog:
    id: str                    # ID único do evento
    event_type: str            # Tipo do evento
    event_category: str        # Categoria (security, performance, validation)
    severity: str              # Severidade (info, warning, critical)
    query_text: str | None     # Query que gerou o evento
    detection_types: list[str] # Tipos de detecção ativados
    risk_score: float | None   # Score de risco (0.0 a 1.0)
    action_taken: str | None   # Ação tomada (logged, blocked, warned)
    endpoint: str | None       # Endpoint que gerou o evento
    client_ip: str | None      # IP do cliente (anonimizado)
    created_at: str | None     # Data/hora (ISO 8601)
    details: dict              # Detalhes adicionais
```

### `AuditLogsResponse`

Resposta paginada de listagem de logs.

```python
@dataclass
class AuditLogsResponse:
    logs: list[AuditLog]  # Lista de logs
    total: int            # Total de logs encontrados
    page: int             # Página atual
    pages: int            # Total de páginas
    limit: int            # Limite por página
```

### `AuditStats`

Estatísticas agregadas de auditoria.

```python
@dataclass
class AuditStats:
    total_events: int        # Total de eventos no período
    events_by_type: dict     # Contagem por tipo
    events_by_severity: dict # Contagem por severidade
    events_by_category: dict # Contagem por categoria
    blocked_count: int       # Quantidade bloqueada
    warning_count: int       # Quantidade de avisos
    period_days: int         # Período em dias
```

---

## Casos de Uso Práticos

### 1. Dashboard de Monitoramento

```python
from vectorgov import VectorGov
from datetime import datetime

vg = VectorGov(api_key="vg_xxx")

def gerar_relatorio_diario():
    """Gera relatório diário de uso da API."""
    stats = vg.get_audit_stats(days=1)

    print(f"=== Relatório {datetime.now().strftime('%Y-%m-%d')} ===")
    print(f"Total de requisições: {stats.total_events}")
    print(f"Problemas de segurança: {stats.blocked_count + stats.warning_count}")

    # Taxa de sucesso
    total = stats.total_events
    problemas = stats.blocked_count + stats.warning_count
    taxa_sucesso = ((total - problemas) / total * 100) if total > 0 else 100
    print(f"Taxa de sucesso: {taxa_sucesso:.1f}%")

    return stats

# Executar diariamente via cron/scheduler
relatorio = gerar_relatorio_diario()
```

### 2. Alertas de Segurança

```python
from vectorgov import VectorGov

vg = VectorGov(api_key="vg_xxx")

def verificar_alertas_seguranca():
    """Verifica eventos críticos de segurança."""
    logs = vg.get_audit_logs(
        event_category="security",
        severity="critical",
        limit=10,
    )

    if logs.total > 0:
        print(f"🚨 ALERTA: {logs.total} eventos críticos de segurança!")
        for log in logs.logs:
            print(f"  - {log.event_type}: {log.query_text[:50] if log.query_text else 'N/A'}...")
            print(f"    Risk Score: {log.risk_score}")
            print(f"    Ação: {log.action_taken}")
        return True

    print("✅ Nenhum evento crítico de segurança")
    return False

# Verificar periodicamente
verificar_alertas_seguranca()
```

### 3. Análise de PII (LGPD)

```python
from vectorgov import VectorGov

vg = VectorGov(api_key="vg_xxx")

def relatorio_pii(dias: int = 30):
    """Relatório de detecções de PII para compliance LGPD."""
    logs = vg.get_audit_logs(
        event_type="pii_detected",
        limit=100,
    )

    stats = vg.get_audit_stats(days=dias)
    pii_count = stats.events_by_type.get("pii_detected", 0)

    print(f"=== Relatório LGPD ({dias} dias) ===")
    print(f"Detecções de PII: {pii_count}")

    if logs.logs:
        print("\nÚltimas detecções:")
        for log in logs.logs[:5]:
            print(f"  - {log.created_at}: {log.details.get('pii_types', [])}")

    return pii_count

# Executar mensalmente para compliance
relatorio_pii(dias=30)
```

### 4. Debug de Integração

```python
from vectorgov import VectorGov

vg = VectorGov(api_key="vg_xxx")

def investigar_erros(dias: int = 7):
    """Investiga erros de validação para debug."""
    logs = vg.get_audit_logs(
        event_category="validation",
        limit=50,
    )

    if logs.total == 0:
        print("✅ Nenhum erro de validação encontrado")
        return

    print(f"⚠️ {logs.total} erros de validação:")

    # Agrupa por tipo
    erros_por_tipo = {}
    for log in logs.logs:
        tipo = log.details.get("field", "unknown")
        erros_por_tipo[tipo] = erros_por_tipo.get(tipo, 0) + 1

    print("\nErros por campo:")
    for campo, count in sorted(erros_por_tipo.items(), key=lambda x: -x[1]):
        print(f"  {campo}: {count}")

investigar_erros()
```

### 5. Monitoramento de Rate Limit

```python
from vectorgov import VectorGov

vg = VectorGov(api_key="vg_xxx")

def monitorar_rate_limit():
    """Monitora consumo de rate limit."""
    stats = vg.get_audit_stats(days=1)

    rate_limit_hits = stats.events_by_type.get("rate_limit_exceeded", 0)
    total_requests = stats.total_events

    if rate_limit_hits > 0:
        percentual = (rate_limit_hits / total_requests * 100) if total_requests > 0 else 0
        print(f"⚠️ Rate limit atingido {rate_limit_hits}x ({percentual:.1f}% das requisições)")
        print("   Considere aumentar seu limite ou otimizar o uso da API")
    else:
        print("✅ Rate limit: dentro do limite")

    return rate_limit_hits

monitorar_rate_limit()
```

---

## Boas Práticas

### ✅ Faça

1. **Monitore regularmente** - Configure verificações diárias de eventos críticos
2. **Armazene logs localmente** - Para análises históricas além do período disponível na API
3. **Configure alertas** - Para eventos de segurança com severidade `warning` ou `critical`
4. **Documente investigações** - Mantenha registro de incidentes e ações tomadas

### ❌ Evite

1. **Ignorar avisos de segurança** - Eventos `warning` podem indicar problemas crescentes
2. **Expor logs em interfaces públicas** - Logs podem conter informações sensíveis
3. **Polling excessivo** - Use intervalos razoáveis (ex: a cada 5 minutos)
4. **Descartar logs sem análise** - Revise padrões antes de arquivar

---

## Integração com Ferramentas Externas

### Exportar para JSON

```python
import json
from vectorgov import VectorGov

vg = VectorGov(api_key="vg_xxx")

logs = vg.get_audit_logs(limit=100)

# Exportar para arquivo
with open("audit_logs.json", "w") as f:
    json.dump([{
        "id": log.id,
        "event_type": log.event_type,
        "severity": log.severity,
        "created_at": log.created_at,
        "query_text": log.query_text,
        "details": log.details,
    } for log in logs.logs], f, indent=2)
```

### Enviar para Slack

```python
import requests
from vectorgov import VectorGov

vg = VectorGov(api_key="vg_xxx")
SLACK_WEBHOOK = "https://hooks.slack.com/services/xxx"

def alertar_slack():
    logs = vg.get_audit_logs(severity="critical", limit=5)

    if logs.total > 0:
        message = f"🚨 *{logs.total} eventos críticos no VectorGov*\n"
        for log in logs.logs:
            message += f"• `{log.event_type}`: {log.action_taken}\n"

        requests.post(SLACK_WEBHOOK, json={"text": message})
```

---

## Próximos Passos

- [System Prompts](./system-prompts.md) - Controle tokens e custos
- [Reference de métodos](../api/methods.md) - Documentação técnica completa
- [Modelos](../api/models.md) - Todos os modelos de dados
