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

# Data a partir da qual a skill nova está em vigor. Edições anteriores são
# validadas em modo "lenient" (erros viram warnings), para não quebrar CI
# retroativamente em conteúdo gerado antes desta revisão.
STRICT_FROM = '2026-04-18'

CATEGORIES = {'sec','ai','cloud','devops','backend','frontend','db','lang','arqsw','arqsol'}
SEVERITIES = {'critical','high','medium','low'}
TOOL_KEYS = {'teams','notion','intellij','cursor','warp','mongocompass','dbeaver','postman','docker','structurizr','c4'}
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
_lenient = False  # definido por validate_edition conforme data

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
    if item.get('category') not in CATEGORIES:
        err(f"{label}: category inválida: {item.get('category')}")
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
    global _lenient
    ed = json.load(open(path, encoding='utf-8'))
    name = os.path.basename(path)
    # detecta legacy: edições anteriores ao cutoff viram warnings
    _lenient = (ed.get('date') or '') < STRICT_FROM
    for f in ('date','weekday','formatted_date','generated_at','hero_title','hero_description'):
        if f not in ed:
            err(f"{name}: campo raiz ausente: {f}")
    if 'top3' not in ed or not isinstance(ed['top3'], list):
        err(f"{name}: top3 ausente ou inválido")
    elif len(ed['top3']) != 3:
        warn(f"{name}: top3 com {len(ed['top3'])} itens (esperado 3)")
    if 'news' not in ed or not isinstance(ed.get('news'), list):
        err(f"{name}: news ausente")
    total = len(ed.get('top3') or []) + len(ed.get('news') or [])
    if total < 15:
        warn(f"{name}: total de notícias {total} < 15 (mínimo da skill)")
    cats = set()
    urls = []
    for i, it in enumerate(ed.get('top3') or []):
        check_item(it, f"{name}:top3[{i}]", require_star=True)
        cats.add(it.get('category'))
        urls.append(it.get('url'))
    # diversidade top3: ≥2 categorias distintas
    if len(cats) < 2:
        err(f"{name}: top3 precisa de ≥2 categorias distintas (tem {len(cats)})")
    for i, it in enumerate(ed.get('news') or []):
        check_item(it, f"{name}:news[{i}]")
        urls.append(it.get('url'))
    # duplicatas intra-edição
    dup = set([u for u in urls if urls.count(u) > 1 and u])
    for d in dup:
        err(f"{name}: URL duplicada intra-edição: {d}")

    # imagens no top3: meta 3/3 (WARN em qualquer modo)
    with_img = sum(1 for it in (ed.get('top3') or []) if it.get('image'))
    if with_img < 3:
        warn(f"{name}: {with_img}/3 itens do top3 têm imagem (meta: 3/3)")

    # imagens em news[]: meta ≥40% (strict)
    news_list = ed.get('news') or []
    if not _lenient and news_list:
        news_with_img = sum(1 for it in news_list if it.get('image'))
        ratio = news_with_img / len(news_list)
        if ratio < 0.4:
            warn(f"{name}: news[] com {news_with_img}/{len(news_list)} imagens (<40% — meta da skill)")

    # cobertura de categorias (strict)
    if not _lenient:
        cats_present = {it.get('category') for it in (ed.get('top3') or []) + (ed.get('news') or [])}
        missing_cats = CATEGORIES - cats_present
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
            if not tool_key:
                warn(f"{label}: tool_key ausente (novo campo obrigatório)")
            elif tool_key not in TOOL_KEYS:
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
        if len(tools) < 11:
            warn(f"{name}: tools[] com {len(tools)} itens (esperado 11, um por ferramenta)")
        missing_tools = TOOL_KEYS - tool_keys_seen
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
    idx = json.load(open(path, encoding='utf-8'))
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
