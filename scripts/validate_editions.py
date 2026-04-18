#!/usr/bin/env python3
"""Valida estrutura de data/editions.json e data/YYYY-MM-DD.json.

Uso:
  python3 scripts/validate_editions.py            # valida tudo
  python3 scripts/validate_editions.py 2026-04-17 # valida uma data

Saída:
- Exit 0 se tudo ok.
- Exit 1 em qualquer erro estrutural.
- Avisos (WARN) em stderr não quebram o build.
"""
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')

# Cutoffs de strictness:
# STRICT_FROM    — v1 da skill (tools com kind/tool_key, imagens, quotes).
# STRICT_FROM_V2 — v2 da taxonomia (arqsw/arqsol ainda válidos, 36 tools).
# STRICT_FROM_V3 — v3 da taxonomia (design/enterprise/distarch; 37 tools, sem dbeaver/mongocompass/whimsical/plantuml).
# STRICT_FROM_V4 — v4 da taxonomia (rebrand CsR News; +categoria testing; 13 categorias).
# STRICT_FROM_V5 — v5 da taxonomia (+eventdriven/apifirst/resiliency/springcloud/quarkus/lambda/dynamodb; -warp/-postman; 42 tools).
STRICT_FROM    = '2026-04-18'
STRICT_FROM_V2 = '2026-04-17'
STRICT_FROM_V3 = '2026-04-19'
STRICT_FROM_V4 = '2026-04-19'
STRICT_FROM_V5 = '2026-04-19'

# Taxonomia v1 (legacy — aceita como warning em strict_v2/v3)
CATEGORIES_V1 = {'sec','ai','cloud','devops','backend','frontend','db','lang','arqsw','arqsol','obs','data','integ'}
TOOL_KEYS_V1  = {'teams','notion','intellij','cursor','warp','mongocompass','dbeaver','postman','docker','structurizr','c4','whimsical','plantuml'}

# Taxonomia v2 (válida de 2026-04-17 até 2026-04-18)
CATEGORIES_V2 = {'sec','ai','aws','devops','obs','data','integ','backend','arqsw','arqsol','fintech'}
TOOL_KEYS_V2  = {
  'structurizr','whimsical','plantuml',
  'cursor','claudecode','chatgpt','vscode','warp',
  'cve','keycloak','owasp',
  'git','github','docker','kubernetes','terraform','helm','ghactions',
  'dynatrace','grafana',
  'postgres','mysql','mongocompass','dbeaver','databricks','redis',
  'kafka','postman','openapi',
  'java','javascript','python',
  'intellij','springboot','gradle','maven'
}

# Taxonomia v3 (exigida a partir de STRICT_FROM_V3)
CATEGORIES_V3 = {'sec','ai','aws','devops','obs','data','integ','backend','design','enterprise','distarch','fintech'}
TOOL_KEYS_V3  = {
  'structurizr',
  'cursor','claudecode','chatgpt','vscode','warp',
  'cve','keycloak','owasp',
  'git','github','docker','kubernetes','terraform','helm','ghactions',
  'argocd','istio',
  'dynatrace','grafana',
  'postgres','mysql','databricks','redis',
  'kafka','postman','openapi',
  'java','javascript','python',
  'intellij','springboot','gradle','maven',
  'microservices','ddd','cloudnative'
}

# Taxonomia v4 — CsR News rebrand + categoria testing (a partir de STRICT_FROM_V4)
CATEGORIES_V4 = CATEGORIES_V3 | {'testing'}
TOOL_KEYS_V4  = TOOL_KEYS_V3  # tool_keys não mudaram nesta versão

# Taxonomia v5 — +eventdriven/apifirst/resiliency/springcloud/quarkus/lambda/dynamodb; -warp/-postman
CATEGORIES_V5 = CATEGORIES_V4  # categorias inalteradas
TOOL_KEYS_V5  = (TOOL_KEYS_V4 - {'warp','postman'}) | {
  'eventdriven','apifirst','resiliency',
  'springcloud','quarkus',
  'lambda','dynamodb',
}

# União: aceita tudo (validator decide por data)
CATEGORIES = CATEGORIES_V1 | CATEGORIES_V2 | CATEGORIES_V3 | CATEGORIES_V4 | CATEGORIES_V5
TOOL_KEYS  = TOOL_KEYS_V1  | TOOL_KEYS_V2  | TOOL_KEYS_V3  | TOOL_KEYS_V4  | TOOL_KEYS_V5

SEVERITIES = {'critical','high','medium','low'}
KINDS = {'release','news','tip','tutorial','curiosity'}

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
_lenient    = False  # definido por validate_edition conforme data
_strict_v2  = False  # True para edições >= STRICT_FROM_V2
_strict_v3  = False  # True para edições >= STRICT_FROM_V3
_strict_v4  = False  # True para edições >= STRICT_FROM_V4 (testing category)
_strict_v5  = False  # True para edições >= STRICT_FROM_V5 (+42 topics, -warp/-postman)

def err(msg):
    if _lenient: warnings.append('(legacy) ' + msg)
    else: errors.append(msg)
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
    if parsed.scheme not in ('http','https'):
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

def check_item(item, label, require_star=False):
    required = ['category','category_label','category_icon','headline','summary','source','url','read_time']
    for f in required:
        if f not in item or item[f] in (None, ''):
            err(f"{label}: campo obrigatório ausente: {f}")
    cat = item.get('category')
    if _strict_v5:
        valid_cats = CATEGORIES_V5
    elif _strict_v4:
        valid_cats = CATEGORIES_V4
    elif _strict_v3:
        valid_cats = CATEGORIES_V3
    elif _strict_v2:
        valid_cats = CATEGORIES_V2
    else:
        valid_cats = CATEGORIES
    if cat not in valid_cats:
        if (_strict_v4 or _strict_v3) and cat in CATEGORIES_V2 and cat not in CATEGORIES_V3:
            err(f"{label}: category '{cat}' pertence à taxonomia v2 — use a equivalente v3 (arqsw→design, arqsol→enterprise)")
        elif _strict_v2 and cat in CATEGORIES_V1:
            err(f"{label}: category '{cat}' pertence à taxonomia v1 — use a equivalente v2 (data→data, lang→backend, frontend→obs/integ/backend)")
        else:
            err(f"{label}: category inválida: {cat}")
    sev = item.get('severity')
    if sev is not None and sev not in SEVERITIES:
        err(f"{label}: severity inválida: {sev}")
    if require_star and not item.get('star'):
        err(f"{label}: top3 requer star:true")
    if 'read_time' in item and not isinstance(item['read_time'], (int,float)):
        err(f"{label}: read_time deve ser numérico")
    for flag in ('urgent','star','breaking','new'):  # 'new' mantido só pra validar tipo em legacy
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
            datetime.fromisoformat(item['published_at'].replace('Z','+00:00'))
        except Exception:
            warn(f"{label}: published_at não é ISO 8601: {item['published_at']}")
    check_url(item.get('url'), label)
    if item.get('image'):
        check_image_url(item['image'], label)

def validate_edition(path):
    global _lenient, _strict_v2, _strict_v3, _strict_v4, _strict_v5
    with open(path, encoding='utf-8') as f:
        ed = json.load(f)
    name = os.path.basename(path)
    edition_date = ed.get('date') or ''
    # detecta legacy: edições anteriores ao cutoff viram warnings
    _lenient   = edition_date < STRICT_FROM
    _strict_v2 = edition_date >= STRICT_FROM_V2
    _strict_v3 = edition_date >= STRICT_FROM_V3
    _strict_v4 = edition_date >= STRICT_FROM_V4
    _strict_v5 = edition_date >= STRICT_FROM_V5
    for f in ('date','weekday','formatted_date','generated_at','hero_title','hero_description'):
        if f not in ed:
            err(f"{name}: campo raiz ausente: {f}")
    # pillars[] — novo campo obrigatório (aceita top3 legado)
    pillars = ed.get('pillars') or ed.get('top3') or []
    pillars_key = 'pillars' if 'pillars' in ed else ('top3' if 'top3' in ed else 'pillars')
    if not pillars or not isinstance(pillars, list):
        err(f"{name}: pillars ausente ou inválido")
    elif len(pillars) != 3:
        warn(f"{name}: pillars com {len(pillars)} itens (esperado 3)")
    if 'news' not in ed or not isinstance(ed.get('news'), list):
        err(f"{name}: news ausente")
    total = len(pillars) + len(ed.get('news') or [])
    if total < 15:
        warn(f"{name}: total de notícias {total} < 15 (mínimo da skill)")
    pillar_keys_seen = set()
    urls = []
    for i, it in enumerate(pillars):
        label = f"{name}:{pillars_key}[{i}]"
        check_item(it, label, require_star=False)
        # valida campo pillar (obrigatório em edições >= STRICT_FROM_V2)
        pk = it.get('pillar')
        if _strict_v2:
            if not pk:
                err(f"{label}: campo 'pillar' ausente (java|aws|distarch)")
            elif pk not in ('java', 'aws', 'distarch'):
                err(f"{label}: pillar inválido '{pk}' (esperado java|aws|distarch)")
            else:
                pillar_keys_seen.add(pk)
        urls.append(it.get('url'))
    # todos os 3 pilares devem estar presentes (strict_v2)
    if _strict_v2 and len(pillar_keys_seen) < 3:
        missing_p = {'java','aws','distarch'} - pillar_keys_seen
        err(f"{name}: pilares faltando em pillars[]: {sorted(missing_p)}")
    for i, it in enumerate(ed.get('news') or []):
        check_item(it, f"{name}:news[{i}]")
        urls.append(it.get('url'))
    # duplicatas intra-edição
    dup = set([u for u in urls if urls.count(u) > 1 and u])
    for d in dup:
        err(f"{name}: URL duplicada intra-edição: {d}")

    # imagens nos pillars: meta 3/3 (WARN em qualquer modo)
    with_img = sum(1 for it in pillars if it.get('image'))
    if with_img < 3:
        warn(f"{name}: {with_img}/3 pillars têm imagem (meta: 3/3)")

    # imagens em news[]: meta ≥80% (strict) — cascata com Google favicon garante
    news_list = ed.get('news') or []
    if not _lenient and news_list:
        news_with_img = sum(1 for it in news_list if it.get('image'))
        ratio = news_with_img / len(news_list)
        if ratio < 0.8:
            warn(f"{name}: news[] com {news_with_img}/{len(news_list)} imagens (<80% — meta da skill; usar Google favicon como fallback)")

    # cobertura de categorias (strict)
    if not _lenient:
        top_items = ed.get('pillars') if (_strict_v2 or _strict_v3 or _strict_v4 or _strict_v5) else (ed.get('top3') or [])
        cats_present = {it.get('category') for it in (top_items or []) + (ed.get('news') or [])}
        if _strict_v5:
            expected_cats = CATEGORIES_V5
        elif _strict_v4:
            expected_cats = CATEGORIES_V4
        elif _strict_v3:
            expected_cats = CATEGORIES_V3
        elif _strict_v2:
            expected_cats = CATEGORIES_V2
        else:
            expected_cats = CATEGORIES_V1
        missing_cats = expected_cats - cats_present
        if missing_cats:
            warn(f"{name}: categorias sem itens: {sorted(missing_cats)}")

    # tools[] — validação expandida
    tools = ed.get('tools') or []
    tool_keys_seen = set()
    for i, t in enumerate(tools):
        label = f"{name}:tools[{i}]"
        # campos mínimos sempre exigidos
        for f in ('name','url'):
            if not t.get(f):
                err(f"{label}: campo ausente: {f}")
        check_url(t.get('url'), label)
        if t.get('image'):
            check_image_url(t['image'], label)
        # campos novos (strict)
        if not _lenient:
            tool_key = t.get('tool_key')
            if _strict_v5:
                valid_keys = TOOL_KEYS_V5
            elif _strict_v4:
                valid_keys = TOOL_KEYS_V4
            elif _strict_v3:
                valid_keys = TOOL_KEYS_V3
            elif _strict_v2:
                valid_keys = TOOL_KEYS_V2
            else:
                valid_keys = TOOL_KEYS
            if not tool_key:
                warn(f"{label}: tool_key ausente (novo campo obrigatório)")
            elif tool_key not in valid_keys:
                if (_strict_v3 or _strict_v2) and tool_key in TOOL_KEYS_V1:
                    err(f"{label}: tool_key '{tool_key}' pertence à taxonomia v1 — use a equivalente atual")
                else:
                    err(f"{label}: tool_key inválido: {tool_key}")
            else:
                tool_keys_seen.add(tool_key)
            kind = t.get('kind')
            if not kind:
                warn(f"{label}: kind ausente (release|news|tip|tutorial|curiosity)")
            elif kind not in KINDS:
                err(f"{label}: kind inválido: {kind}")
            if kind == 'release' and not t.get('version'):
                warn(f"{label}: kind=release sem version")
            if not t.get('headline'):
                warn(f"{label}: headline ausente (recomendado)")
            if not t.get('source'):
                warn(f"{label}: source ausente (recomendado)")

    # cobertura de ferramentas (strict)
    if not _lenient:
        if _strict_v5:
            expected = TOOL_KEYS_V5
        elif _strict_v4:
            expected = TOOL_KEYS_V4
        elif _strict_v3:
            expected = TOOL_KEYS_V3
        elif _strict_v2:
            expected = TOOL_KEYS_V2
        else:
            expected = TOOL_KEYS_V1
        if len(tools) < len(expected):
            warn(f"{name}: tools[] com {len(tools)} itens (esperado {len(expected)}, um por ferramenta)")
        missing_tools = expected - tool_keys_seen
        if missing_tools:
            warn(f"{name}: ferramentas sem item em tools[]: {sorted(missing_tools)}")

    # quotes[] — opcional, mas validado se presente
    q = ed.get('quotes')
    if q is not None:
        if not isinstance(q, list):
            err(f"{name}: quotes deve ser array")
        else:
            if len(q) != 5:
                warn(f"{name}: quotes com {len(q)} itens (esperado 5)")
            valid_rel_prefix = ('cat:', 'tool:', 'general')
            for i, qi in enumerate(q):
                for f in ('text','author','related_to'):
                    if not qi.get(f):
                        err(f"{name}:quotes[{i}]: campo ausente: {f}")
                rel = qi.get('related_to','')
                if rel != 'general' and not (rel.startswith('cat:') or rel.startswith('tool:')):
                    warn(f"{name}:quotes[{i}]: related_to inesperado: {rel}")
    elif not _lenient:
        warn(f"{name}: quotes[] ausente (esperado 5 itens por edição)")

def validate_index(path):
    with open(path, encoding='utf-8') as f:
        idx = json.load(f)
    if 'last_generated' not in idx:
        err('editions.json: last_generated ausente')
    else:
        try:
            datetime.fromisoformat(idx['last_generated'].replace('Z','+00:00'))
        except Exception:
            warn(f"editions.json: last_generated não é ISO 8601: {idx['last_generated']}")
    eds = idx.get('editions') or []
    if not eds:
        err('editions.json: editions vazio')
    dates = [e.get('date') for e in eds]
    if dates != sorted(dates, reverse=True):
        warn('editions.json: editions[] não ordenadas desc por data')
    for e in eds:
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', e.get('date','')):
            err(f"editions.json: date inválida: {e.get('date')}")
        hl = e.get('highlights') or []
        if len(hl) != 3:
            warn(f"editions.json: {e.get('date')} com {len(hl)} highlights (esperado 3)")
        # counts_by_category / counts_by_tool são opcionais mas recomendados
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
