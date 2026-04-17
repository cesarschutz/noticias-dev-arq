#!/usr/bin/env python3
"""Gera feed.xml (RSS 2.0) a partir de data/editions.json.

Uma entrada por edição diária, agrupando top3 como bullets no body.
"""
import html
import json
import os
import re
from datetime import datetime, timezone
from email.utils import format_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'feed.xml')

SITE_URL = os.environ.get('DEVPULSE_SITE_URL', 'https://cesarschutz.github.io/noticias-dev-arq/')
FEED_TITLE = 'DevPulse · Arquivo diário do arquiteto'
FEED_DESC = 'Curadoria diária de notícias técnicas para arquitetos de software e solução.'

def parse_iso(s):
    try:
        return datetime.fromisoformat(s.replace('Z','+00:00'))
    except Exception:
        return datetime.now(timezone.utc)

def build_item(edition, full):
    date = edition['date']
    link = f"{SITE_URL.rstrip('/')}/?d={date}"
    title = edition.get('summary') or full.get('hero_title') or f"Edição {date}"
    # body: resumo + 3 highlights
    body_parts = []
    if full.get('hero_description'):
        body_parts.append(f"<p>{html.escape(full['hero_description'])}</p>")
    if edition.get('highlights'):
        body_parts.append('<ul>')
        for h in edition['highlights']:
            body_parts.append(f'<li><a href="{html.escape(h.get("url",""))}">{html.escape(h.get("title",""))}</a></li>')
        body_parts.append('</ul>')
    description = ''.join(body_parts) or html.escape(title)
    # data de publicação: generated_at do dia se disponível
    dt = parse_iso(full.get('generated_at') or f"{date}T06:00:00-03:00")
    pub = format_datetime(dt)
    return f"""    <item>
      <title>{html.escape(title)}</title>
      <link>{html.escape(link)}</link>
      <guid isPermaLink="false">devpulse-{date}</guid>
      <pubDate>{pub}</pubDate>
      <description><![CDATA[{description}]]></description>
    </item>"""

def main():
    idx_path = os.path.join(DATA, 'editions.json')
    if not os.path.exists(idx_path):
        raise SystemExit('editions.json não encontrado')
    idx = json.load(open(idx_path, encoding='utf-8'))
    eds = idx.get('editions') or []
    items = []
    for e in eds[:30]:  # últimas 30
        date = e.get('date')
        p = os.path.join(DATA, date + '.json')
        if not os.path.exists(p):
            continue
        full = json.load(open(p, encoding='utf-8'))
        items.append(build_item(e, full))

    last_built = format_datetime(parse_iso(idx.get('last_generated') or datetime.now(timezone.utc).isoformat()))
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{html.escape(FEED_TITLE)}</title>
    <link>{html.escape(SITE_URL)}</link>
    <description>{html.escape(FEED_DESC)}</description>
    <language>pt-BR</language>
    <lastBuildDate>{last_built}</lastBuildDate>
    <atom:link href="{html.escape(SITE_URL.rstrip('/'))}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(xml)
    print(f"✓ feed.xml gerado com {len(items)} itens")

if __name__ == '__main__':
    main()
