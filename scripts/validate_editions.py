#!/usr/bin/env python3
"""Valida estrutura de data/editions.json e data/YYYY-MM-DD.json.

Uso:
  python3 scripts/validate_editions.py            # valida tudo
  python3 scripts/validate_editions.py 2026-04-17 # valida uma data

Saída:
- Exit 0 se tudo ok.
- Exit 1 em qualquer erro estrutural.
- Avisos (WARN) em stderr não quebram o build.

Taxonomia única — o arquivo não mantém histórico de versões. Se a taxonomia
evoluir, atualize os conjuntos `CATEGORIES` e `TOOL_KEYS` abaixo.
"""
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

# ── Taxonomia única ─────────────────────────────────────────────────────────
CATEGORIES = {
    # Transversal
    'ai', 'aiops', 'sec',
    # Plataforma & Infraestrutura
    'cloud', 'devops', 'obs',
    # Desenvolvimento
    'backend', 'data', 'integ', 'testing', 'frontend',
    # Arquitetura
    'design', 'distarch', 'enterprise',
    # Fundação
    'fundamentals',
    # Domínio
    'fintech',
}

TOOL_KEYS = {
    # Linguagens
    'java', 'javascript', 'python',
    # AI & IDEs
    'claudecode', 'cursor', 'intellij', 'vscode',
    # Git & CI/CD
    'argocd', 'ghactions', 'github',
    # Containers & IaC
    'docker', 'kubernetes', 'terraform',
    # Mesh, Proxies & Edge
    'istio', 'nginx', 'cloudflare',
    # Dados & Streaming
    'databricks', 'postgres', 'redis', 'kafka',
    # Obs & Segurança
    'dynatrace', 'datadog', 'keycloak', 'vault',
    # Backend & Build
    'gradle', 'maven', 'springboot',
    # Design & Docs (docs-as-code)
    'structurizr', 'plantuml', 'mermaid',
}

SEVERITIES = {'critical', 'high', 'medium', 'low'}
KINDS = {'release', 'news', 'tip', 'tutorial', 'curiosity'}

# URLs genéricas proibidas (padrões)
GENERIC_URL_PATTERNS = [
    re.compile(r'https?://[^/]+/new/?$'),
    re.compile(r'https?://[^/]+/news/?$'),
    re.compile(r'https?://[^/]+/blog/?$'),
    re.compile(r'https?://[^/]+/releases/?$'),
    re.compile(r'https?://[^/]+/changelog/?$'),
    re.compile(r'https?://[^/]+/?$'),  # homepage pura
]

errors = []
warnings = []


def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)


def check_url(url, label):
    if not url or not isinstance(url, str):
        err(f"{label}: url ausente")
        return
    try:
        parsed = urlparse(url)
    except Exception:
        err(f"{label}: url inválida: {url}")
        return
    if parsed.scheme not in ('http', 'https'):
        err(f"{label}: esquema inesperado: {url}")
    for pat in GENERIC_URL_PATTERNS:
        if pat.match(url.rstrip('/') + ('/' if pat.pattern.endswith('/?$') else '')):
            warn(f"{label}: url genérica suspeita: {url}")
            break


def check_image_url(url, label):
    if not url or not isinstance(url, str):
        return
    if not url.startswith('https://'):
        warn(f"{label}: image deve ser https://: {url}")


def check_item(item, label):
    required = ['category', 'category_label', 'category_icon',
                'headline', 'summary', 'source', 'url', 'read_time']
    for f in required:
        if f not in item or item[f] in (None, ''):
            err(f"{label}: campo obrigatório ausente: {f}")
    # why_it_matters é novo campo da v1 — warn (não err) para não quebrar items legados
    if not item.get('why_it_matters'):
        warn(f"{label}: why_it_matters ausente (recomendado)")
    cat = item.get('category')
    if cat and cat not in CATEGORIES:
        err(f"{label}: category inválida: {cat}")
    sev = item.get('severity')
    if sev is not None and sev not in SEVERITIES:
        err(f"{label}: severity inválida: {sev}")
    if 'read_time' in item and not isinstance(item['read_time'], (int, float)):
        err(f"{label}: read_time deve ser numérico")
    for flag in ('urgent', 'breaking'):
        if flag in item and not isinstance(item[flag], bool):
            err(f"{label}: {flag} deve ser boolean")
    if 'cves' in item:
        if not isinstance(item['cves'], list):
            err(f"{label}: cves deve ser array")
        else:
            for c in item['cves']:
                if not re.match(r'^CVE-\d{4}-\d{4,}$', c):
                    warn(f"{label}: CVE em formato incomum: {c}")
    if 'tags' in item:
        if not isinstance(item['tags'], list):
            err(f"{label}: tags deve ser array")
    if 'published_at' in item:
        try:
            datetime.fromisoformat(item['published_at'].replace('Z', '+00:00'))
        except Exception:
            warn(f"{label}: published_at não é ISO 8601: {item['published_at']}")
    check_url(item.get('url'), label)
    if item.get('image'):
        check_image_url(item['image'], label)


def validate_edition(path):
    with open(path, encoding='utf-8') as f:
        ed = json.load(f)
    name = os.path.basename(path)
    for f in ('date', 'weekday', 'formatted_date', 'generated_at', 'hero_title', 'hero_description'):
        if f not in ed:
            err(f"{name}: campo raiz ausente: {f}")

    if 'news' not in ed or not isinstance(ed.get('news'), list):
        err(f"{name}: news ausente")

    urls = []
    news_list = ed.get('news') or []
    for i, it in enumerate(news_list):
        check_item(it, f"{name}:news[{i}]")
        urls.append(it.get('url'))

    # duplicatas intra-edição
    dup = set([u for u in urls if urls.count(u) > 1 and u])
    for d in dup:
        err(f"{name}: URL duplicada intra-edição: {d}")

    # imagens em news[]: meta ≥80%
    if news_list:
        news_with_img = sum(1 for it in news_list if it.get('image'))
        ratio = news_with_img / len(news_list)
        if ratio < 0.8:
            warn(f"{name}: news[] com {news_with_img}/{len(news_list)} imagens (<80% — usar Google favicon como fallback)")

    # cobertura de categorias: v1 flexível — warn só se >50% das categorias vazias
    cats_present = {it.get('category') for it in news_list if it.get('category')}
    missing_cats = CATEGORIES - cats_present
    if len(missing_cats) > len(CATEGORIES) // 2:
        warn(f"{name}: {len(missing_cats)} de {len(CATEGORIES)} categorias sem itens (>50% vazias): {sorted(missing_cats)}")

    # volume mínimo news[]: 15 itens (janela ≤24h)
    if len(news_list) < 15:
        warn(f"{name}: news[] com {len(news_list)} itens (<15 — volume baixo para a janela)")

    # highlights[] — top 3 meritocráticos do dia (opcional dentro da edição,
    # obrigatório em editions.json)
    hl = ed.get('highlights')
    if hl is not None:
        if not isinstance(hl, list):
            err(f"{name}: highlights deve ser array")
        elif len(hl) != 3:
            warn(f"{name}: highlights com {len(hl)} itens (esperado 3)")

    # tools[] — validação
    tools = ed.get('tools') or []
    tool_keys_seen = set()
    for i, t in enumerate(tools):
        label = f"{name}:tools[{i}]"
        for f in ('name', 'url'):
            if not t.get(f):
                err(f"{label}: campo ausente: {f}")
        check_url(t.get('url'), label)
        if t.get('image'):
            check_image_url(t['image'], label)
        tool_key = t.get('tool_key')
        if not tool_key:
            err(f"{label}: tool_key ausente")
        elif tool_key not in TOOL_KEYS:
            err(f"{label}: tool_key inválido: {tool_key}")
        else:
            tool_keys_seen.add(tool_key)
        kind = t.get('kind')
        if not kind:
            err(f"{label}: kind ausente (release|news|tip|tutorial|curiosity)")
        elif kind not in KINDS:
            err(f"{label}: kind inválido: {kind}")
        if kind == 'release' and not t.get('version'):
            warn(f"{label}: kind=release sem version")
        if not t.get('headline'):
            warn(f"{label}: headline ausente (recomendado)")
        if not t.get('source'):
            warn(f"{label}: source ausente (recomendado)")

    # rotação dinâmica v1: mínimo 10 tools/dia (não 1 por tool_key)
    if len(tools) < 10:
        warn(f"{name}: tools[] com {len(tools)} itens (<10 — rotação v1 exige mínimo 10/dia)")

    # quotes[] — opcional
    q = ed.get('quotes')
    if q is not None:
        if not isinstance(q, list):
            err(f"{name}: quotes deve ser array")
        else:
            if len(q) != 5:
                warn(f"{name}: quotes com {len(q)} itens (esperado 5)")
            for i, qi in enumerate(q):
                for f in ('text', 'author', 'related_to'):
                    if not qi.get(f):
                        err(f"{name}:quotes[{i}]: campo ausente: {f}")
                rel = qi.get('related_to', '')
                if rel != 'general' and not (rel.startswith('cat:') or rel.startswith('tool:')):
                    warn(f"{name}:quotes[{i}]: related_to inesperado: {rel}")
    else:
        warn(f"{name}: quotes[] ausente (esperado 5 itens por edição)")


def validate_index(path):
    with open(path, encoding='utf-8') as f:
        idx = json.load(f)
    eds = idx.get('editions') or []
    lg = idx.get('last_generated')
    # last_generated só é obrigatório quando já há edições (skill preenche ao rodar pela 1ª vez)
    if eds and not lg:
        err('editions.json: last_generated ausente')
    if lg:
        try:
            datetime.fromisoformat(str(lg).replace('Z', '+00:00'))
        except Exception:
            warn(f"editions.json: last_generated não é ISO 8601: {lg}")
    if not eds:
        warn('editions.json: editions vazio (primeira execução)')
        return
    dates = [e.get('date') for e in eds]
    if dates != sorted(dates, reverse=True):
        warn('editions.json: editions[] não ordenadas desc por data')
    for e in eds:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', e.get('date', '')):
            err(f"editions.json: date inválida: {e.get('date')}")
        hl = e.get('highlights') or []
        if len(hl) != 3:
            warn(f"editions.json: {e.get('date')} com {len(hl)} highlights (esperado 3)")
        if 'counts_by_category' not in e:
            warn(f"editions.json: {e.get('date')} sem counts_by_category (SPA usa lazy-load otimizado)")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    idx_path = os.path.join(DATA, 'editions.json')
    if os.path.exists(idx_path):
        validate_index(idx_path)
    else:
        err('editions.json não encontrado')

    if target:
        p = os.path.join(DATA, target + '.json')
        if not os.path.exists(p):
            err(f"{target}.json não encontrado")
        else:
            validate_edition(p)
    else:
        for f in sorted(os.listdir(DATA)):
            if re.match(r'^\d{4}-\d{2}-\d{2}\.json$', f):
                validate_edition(os.path.join(DATA, f))

    for w in warnings:
        sys.stderr.write(f"WARN: {w}\n")
    for e in errors:
        sys.stderr.write(f"ERROR: {e}\n")
    if errors:
        sys.stderr.write(f"\n✗ {len(errors)} erro(s), {len(warnings)} aviso(s)\n")
        sys.exit(1)
    sys.stdout.write(f"✓ validação ok · {len(warnings)} aviso(s)\n")


if __name__ == '__main__':
    main()
