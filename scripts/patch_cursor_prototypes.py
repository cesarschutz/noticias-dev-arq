#!/usr/bin/env python3
"""One-off patcher: inject expanded renderAbout + theme markers into cursor-index-*.html"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Inline SVG mascots (robot architect) — one pose per prototype
MASCOT_SVGS = {
    1: """<svg viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg" class="csr-mascot"><defs><linearGradient id="g1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#38bdf8"/><stop offset="100%" stop-color="#a78bfa"/></linearGradient></defs><ellipse cx="60" cy="128" rx="40" ry="8" fill="rgba(0,0,0,.2)"/><rect x="28" y="32" width="64" height="72" rx="14" fill="url(#g1)" stroke="#0f172a" stroke-width="2"/><rect x="38" y="48" width="44" height="12" rx="3" fill="#0f172a" opacity=".85"/><circle cx="48" cy="86" r="6" fill="#f8fafc"/><circle cx="72" cy="86" r="6" fill="#f8fafc"/><path d="M52 102 Q60 108 68 102" stroke="#0f172a" stroke-width="2" fill="none"/><rect x="54" y="18" width="12" height="18" rx="2" fill="#64748b"/><path d="M90 56 L118 40 L116 52 L96 60 Z" fill="#f59e0b" stroke="#0f172a" stroke-width="1.5"/><rect x="22" y="96" width="10" height="28" rx="4" fill="#475569"/><rect x="88" y="96" width="10" height="28" rx="4" fill="#475569"/></svg>""",
    2: """<svg viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg" class="csr-mascot"><ellipse cx="60" cy="128" rx="40" ry="8" fill="rgba(0,0,0,.15)"/><rect x="30" y="36" width="60" height="68" rx="16" fill="#1e293b" stroke="#94a3b8" stroke-width="2"/><circle cx="50" cy="72" r="7" fill="#38bdf8"/><circle cx="70" cy="72" r="7" fill="#38bdf8"/><rect x="44" y="88" width="32" height="4" rx="2" fill="#94a3b8"/><path d="M24 104 L8 120 L14 124 L28 108 Z" fill="#64748b"/><path d="M96 104 L112 120 L106 124 L92 108 Z" fill="#64748b"/></svg>""",
    3: """<svg viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg" class="csr-mascot"><ellipse cx="60" cy="128" rx="42" ry="8" fill="rgba(0,0,0,.12)"/><rect x="26" y="28" width="68" height="78" rx="12" fill="#fef3c7" stroke="#0f172a" stroke-width="3"/><rect x="34" y="40" width="52" height="36" rx="4" fill="#fff" stroke="#0f172a"/><circle cx="48" cy="94" r="5" fill="#0f172a"/><circle cx="72" cy="94" r="5" fill="#0f172a"/><path d="M50 108 h20" stroke="#0f172a" stroke-width="3"/><rect x="48" y="8" width="24" height="22" rx="3" fill="#ef4444" stroke="#0f172a" stroke-width="2"/></svg>""",
    4: """<svg viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg" class="csr-mascot"><defs><pattern id="grid" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M8 0H0V8" fill="none" stroke="#0ea5e9" stroke-opacity=".4"/></pattern></defs><rect x="0" y="0" width="120" height="140" fill="url(#grid)" opacity=".3"/><ellipse cx="60" cy="128" rx="38" ry="7" fill="rgba(14,165,233,.25)"/><rect x="32" y="34" width="56" height="70" rx="8" fill="none" stroke="#0ea5e9" stroke-width="2.5"/><rect x="40" y="48" width="40" height="24" stroke="#0ea5e9" fill="none"/><circle cx="52" cy="88" r="4" fill="#0ea5e9"/><circle cx="68" cy="88" r="4" fill="#0ea5e9"/><line x1="44" y1="108" x2="76" y2="108" stroke="#0ea5e9"/><line x1="60" y1="20" x2="60" y2="34" stroke="#0ea5e9"/></svg>""",
    5: """<svg viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg" class="csr-mascot"><ellipse cx="60" cy="128" rx="36" ry="7" fill="#000"/><rect x="36" y="40" width="48" height="64" rx="0" fill="#fff" stroke="#000" stroke-width="4"/><rect x="44" y="54" width="32" height="8" fill="#000"/><circle cx="52" cy="82" r="5" fill="#000"/><circle cx="68" cy="82" r="5" fill="#000"/><rect x="52" y="96" width="16" height="3" fill="#000"/><circle cx="60" cy="22" r="10" fill="#e11d48" stroke="#000" stroke-width="3"/></svg>""",
}

NEW_RENDER_ABOUT = r'''function renderAbout(){
  const el = $('main-inner');
  const totalEditions = STATE.editionsIndex?.editions?.length || 0;
  const nTopics = TOOLS.length;

  function secHd(iconPaths, label){
    return `<div class="ab-section-hd">
      <span class="ab-section-hd-icon">${iconSvg(iconPaths, 16)}</span>
      <span class="ab-section-title">${label}</span>
      <span class="ab-section-rule"></span>
    </div>`;
  }

  const catCards = Object.entries(CAT).map(([key, cat]) => `
    <div class="ab-cat-card" style="--k:var(--cat-${key})" onclick="setView('cat:${key}')">
      <div class="ab-cat-icon">${iconSvg(CAT_ICONS[key] || '', 20)}</div>
      <div class="ab-cat-name">${cat.lf}</div>
      <div class="ab-cat-rule">min 1 · max 3 / edição (news+pilares)</div>
    </div>`).join('');

  const toolGroups = Object.entries(TOOL_GROUPS).map(([gk, g]) => {
    const tiles = TOOLS.filter(t => t.group === gk).map(t => {
      const domain = (() => { try { return new URL(t.url||'https://example.com').hostname; } catch(e){ return 'example.com'; } })();
      const fb = `https://www.google.com/s2/favicons?domain=${domain}&sz=64`;
      return `<div class="ab-tool-tile" style="--k:var(--cat-${t.category})" onclick="setView('tool:${t.key}')" title="${escAttr(t.name)}">
        <img class="ab-tool-logo" src="${escAttr(t.logo)}" onerror="this.src='${fb}'" alt="${escAttr(t.name)}">
        <span class="ab-tool-name">${esc(t.name)}</span>
      </div>`;
    }).join('');
    return `<div class="ab-group">
      <div class="ab-group-hd" style="color:${g.color}">${iconSvg(CAT_ICONS[g.icon]||'',12)} ${g.label}</div>
      <div class="ab-tool-grid">${tiles}</div>
    </div>`;
  }).join('');

  const mascotSlot = `<div class="ab-mascot-svg" aria-hidden="true"><!-- MASCOT_SVG --></div>`;

  el.innerHTML = `<div class="about-page about-page--expanded">

    <div class="ab-hero">
      <div class="ab-hero-top">
        ${mascotSlot}
        <div class="ab-hero-text">
          <div class="ab-hero-prompt">$ cat manual/operacao.md · CsR News</div>
          <h1 class="ab-hero-title">CsR News — aprendizado técnico diário</h1>
          <p class="ab-hero-sub">Curadoria automática + regras editoriais explícitas. Uma edição por dia (alvo 6h BRT), pensada para arquitetos de software e solução que precisam de sinal sem ruído.</p>
          <div class="ab-hero-actions">
            <button type="button" class="ab-btn-primary" onclick="setView('home')">Abrir edição mais recente</button>
            <button type="button" class="ab-btn-ghost" onclick="window.open('https://github.com/cesarschutz/noticias-dev-arq','_blank')">Código no GitHub</button>
          </div>
        </div>
      </div>
      <div class="ab-stats">
        <div class="ab-stat"><span class="ab-stat-n">${totalEditions || '—'}</span><span class="ab-stat-l">edições no índice</span></div>
        <div class="ab-stat"><span class="ab-stat-n">13</span><span class="ab-stat-l">categorias editoriais</span></div>
        <div class="ab-stat"><span class="ab-stat-n">${nTopics}</span><span class="ab-stat-l">assuntos monitorados</span></div>
        <div class="ab-stat"><span class="ab-stat-n">6h</span><span class="ab-stat-l">BRT · rotina diária</span></div>
        <div class="ab-stat"><span class="ab-stat-n">5</span><span class="ab-stat-l">frases / edição</span></div>
      </div>
    </div>

    <section class="ab-section">
      ${secHd(CAT_ICONS.distarch, 'Taxonomia: o que é cada coisa')}
      <div class="ab-3col">
        <div class="ab-explain-box ab-tax">
          <h3>Categoria</h3>
          <p>Tema editorial <strong>amplo</strong> (ex.: segurança, dados, DevOps). Aparece no feed como <code>news[]</code> + pilares. Cobertura por edição: <strong>mínimo 1 e máximo 3 itens</strong> por categoria (contando <code>news[]</code> e <code>pillars[]</code> juntos).</p>
        </div>
        <div class="ab-explain-box ab-tax">
          <h3>Tópico (rail: Tópicos)</h3>
          <p>Conceito de domínio <strong>específico</strong> (API-First, DDD, OWASP…). Monitorado em <code>tools[]</code> com <code>tool_key</code>. <strong>Obrigatório 1 item por tópico por edição</strong> — se não houver novidade, entra evergreen, sem repetir URL das últimas 7 edições.</p>
        </div>
        <div class="ab-explain-box ab-tax">
          <h3>Ferramenta &amp; linguagem</h3>
          <p>No rail, <strong>Ferramentas</strong> são produtos (K8s, Postgres, IDEs…). <strong>Linguagens</strong> (Java, JS/TS, Python) seguem a mesma obrigatoriedade de 1/dia e ainda têm painel de <strong>versões</strong> (JEP / PEP / ECMA) quando aplicável.</p>
        </div>
      </div>
      <p class="ab-note">Tags em <code>tags[]</code> são detalhes dentro de uma notícia — não são “tópicos” com compromisso diário.</p>
    </section>

    <section class="ab-section">
      ${secHd(CAT_ICONS.obs, 'Como a atualização diária funciona')}
      <div class="ab-2col">
        <div class="ab-explain-box">
          <h3>Janela de busca</h3>
          <p>No modo normal, a skill usa <code>last_generated</code> em <code>data/editions.json</code> como piso temporal: tudo publicado depois disso entra na janela (sem limite artificial de dias).</p>
        </div>
        <div class="ab-explain-box">
          <h3>Volume mínimo por atraso</h3>
          <p>Regra dinâmica: ≤24h → ≥1 por categoria / ≥15 notícias; até 72h → ≥2 por categoria / ≥25; acima → ≥3 por categoria / ≥35 (podendo gerar mais de uma edição se atraso &gt; 5 dias).</p>
        </div>
      </div>
      <div class="ab-explain-box">
        <h3>Blocklist</h3>
        <p>URLs já usadas nas <strong>últimas 7 edições</strong> são proibidas. Headlines quase idênticas também são descartadas — evita eco e força diversidade.</p>
      </div>
    </section>

    <section class="ab-section">
      ${secHd(CAT_ICONS.enterprise, 'Mapa de fontes (skill csr-news-daily)')}
      <p class="ab-lede">Lista resumida de <strong>subáreas</strong> e sites preferidos para busca — quando não houver matéria na fonte preferida, vale qualquer fonte sólida (changelog, blog de engenharia, paper). Qualidade &gt; checklist.</p>
      <div class="ab-atlas">
        <details><summary>Segurança &amp; IAM — CVEs, IAM, supply chain</summary>
          <ul>
            <li><strong>CVE / threat intel:</strong> <a href="https://thehackernews.com" target="_blank" rel="noopener">The Hacker News</a>, <a href="https://www.bleepingcomputer.com" target="_blank" rel="noopener">BleepingComputer</a>, <a href="https://www.cisa.gov/news-events/cybersecurity-advisories" target="_blank" rel="noopener">CISA</a>, <a href="https://nvd.nist.gov" target="_blank" rel="noopener">NVD</a></li>
            <li><strong>Supply chain:</strong> <a href="https://snyk.io/blog" target="_blank" rel="noopener">Snyk</a>, <a href="https://blog.aquasec.com" target="_blank" rel="noopener">Aqua</a>, <a href="https://krebsonsecurity.com" target="_blank" rel="noopener">Krebs</a></li>
            <li><strong>Identity:</strong> <a href="https://auth0.com/blog" target="_blank" rel="noopener">Auth0</a>, <a href="https://developer.okta.com/blog/" target="_blank" rel="noopener">Okta</a></li>
          </ul>
        </details>
        <details><summary>IA &amp; LLMs — modelos, agents, coding</summary>
          <ul>
            <li><a href="https://simonwillison.net" target="_blank" rel="noopener">Simon Willison</a>, <a href="https://openai.com/blog" target="_blank" rel="noopener">OpenAI</a>, <a href="https://www.anthropic.com/news" target="_blank" rel="noopener">Anthropic</a>, <a href="https://huggingface.co/blog" target="_blank" rel="noopener">Hugging Face</a></li>
            <li><strong>IDEs:</strong> <a href="https://cursor.com/changelog" target="_blank" rel="noopener">Cursor changelog</a></li>
          </ul>
        </details>
        <details><summary>AWS — serviços e arquitetura</summary>
          <ul>
            <li><a href="https://aws.amazon.com/new/" target="_blank" rel="noopener">What's New</a>, <a href="https://aws.amazon.com/blogs/architecture/" target="_blank" rel="noopener">Architecture Blog</a>, <a href="https://lastweekinaws.com" target="_blank" rel="noopener">Last Week in AWS</a></li>
          </ul>
        </details>
        <details><summary>DevOps / dados / integração / backend / observabilidade</summary>
          <ul>
            <li><strong>K8s / CNCF:</strong> <a href="https://kubernetes.io/blog/" target="_blank" rel="noopener">Kubernetes Blog</a>, <a href="https://www.cncf.io/blog/" target="_blank" rel="noopener">CNCF</a></li>
            <li><strong>Git / CI:</strong> <a href="https://github.blog/changelog/" target="_blank" rel="noopener">GitHub Changelog</a>, <a href="https://blog.argoproj.io" target="_blank" rel="noopener">Argo</a></li>
            <li><strong>Dados:</strong> <a href="https://www.postgresql.org/about/newsarchive/" target="_blank" rel="noopener">PostgreSQL</a>, <a href="https://redis.io/blog/" target="_blank" rel="noopener">Redis</a>, <a href="https://www.confluent.io/blog/" target="_blank" rel="noopener">Confluent</a></li>
            <li><strong>Obs:</strong> <a href="https://grafana.com/blog/" target="_blank" rel="noopener">Grafana</a>, <a href="https://opentelemetry.io/blog/" target="_blank" rel="noopener">OpenTelemetry</a></li>
          </ul>
        </details>
        <details><summary>Arquitetura / design / enterprise / distarch / fintech / testes</summary>
          <ul>
            <li><strong>Design:</strong> <a href="https://martinfowler.com" target="_blank" rel="noopener">Martin Fowler</a>, <a href="https://www.infoq.com" target="_blank" rel="noopener">InfoQ</a>, <a href="https://structurizr.com" target="_blank" rel="noopener">Structurizr</a></li>
            <li><strong>Enterprise:</strong> <a href="https://architectelevator.com" target="_blank" rel="noopener">Architect Elevator</a>, <a href="https://www.finops.org/blog/" target="_blank" rel="noopener">FinOps</a></li>
            <li><strong>Fintech BR:</strong> <a href="https://www.bcb.gov.br" target="_blank" rel="noopener">BCB</a>, <a href="https://www.stripe.com/blog/engineering" target="_blank" rel="noopener">Stripe Eng</a></li>
            <li><strong>Testes:</strong> <a href="https://playwright.dev/blog" target="_blank" rel="noopener">Playwright</a>, <a href="https://docs.pact.io/blog/" target="_blank" rel="noopener">Pact</a></li>
          </ul>
        </details>
      </div>
    </section>

    <section class="ab-section">
      ${secHd(CAT_ICONS.enterprise, 'Categorias — atalho para o arquivo histórico')}
      <div class="ab-2col" style="margin-bottom:18px">
        <div class="ab-explain-box">
          <h3>Função na UI</h3>
          <p>Cada categoria abre uma visão <code>cat:&lt;chave&gt;</code> com todas as notícias daquele tema ao longo das edições carregadas.</p>
        </div>
        <div class="ab-explain-box">
          <h3>Regra editorial</h3>
          <p>Entre 1 e 3 itens por categoria por dia (pilares + feed). Subtópicos (ex.: SAML dentro de segurança) aparecem quando há notícia — sem promessa diária por sub-tópico.</p>
        </div>
      </div>
      <div class="ab-cat-grid">${catCards}</div>
    </section>

    <section class="ab-section">
      ${secHd(CAT_ICONS.devops, 'Assuntos monitorados — tópicos, ferramentas e linguagens')}
      <div class="ab-2col" style="margin-bottom:18px">
        <div class="ab-explain-box">
          <h3>Cobertura mínima</h3>
          <p><strong>${nTopics} entradas</strong> no mapa — cada uma com exatamente 1 item na edição (via <code>tools[]</code>). Falhou a novidade? Evergreen autorizado, desde que URL não esteja na blocklist.</p>
        </div>
        <div class="ab-explain-box">
          <h3>Linguagens</h3>
          <p>Java, JavaScript/TS e Python abrem também o painel de <strong>versões</strong> (arquivos em <code>data/java-versions</code>, <code>python-versions</code>, <code>js-versions</code>) com JEPs, PEPs ou features ECMA.</p>
        </div>
      </div>
      ${toolGroups}
    </section>

    <section class="ab-section">
      ${secHd(CAT_ICONS.ai, 'Frases &amp; versículos')}
      <div class="ab-2col">
        <div class="ab-explain-box">
          <h3>Frases</h3>
          <p>Cinco citações por edição, rotacionando no painel lateral em ciclo longo. Clique no bloco leva à fonte quando houver URL.</p>
        </div>
        <div class="ab-explain-box">
          <h3>Versículos</h3>
          <p>Palavras de Jesus (Evangelhos), rodapé fixo, link para leitura online.</p>
        </div>
      </div>
    </section>

    <section class="ab-section ab-assets">
      ${secHd(CAT_ICONS.design, 'Placeholders de imagem &amp; prompts (opcional)')}
      <div class="ab-placeholder-grid">
        <div class="ab-ph"><span>01</span><small>Logo CsR</small></div>
        <div class="ab-ph"><span>02</span><small>Mascote · hero</small></div>
        <div class="ab-ph"><span>03</span><small>Mascote · categorias</small></div>
        <div class="ab-ph"><span>04</span><small>Mascote · ferramentas</small></div>
        <div class="ab-ph"><span>05</span><small>Mascote · versões</small></div>
      </div>
      <details class="ab-prompts">
        <summary>Prompts sugeridos (cole no gerador de imagem)</summary>
        <ol>
          <li><strong>Logo:</strong> “Minimal wordmark CsR News, architect + developer, monoline, vector, dark background, amber and cyan accent, no photorealism.”</li>
          <li><strong>Mascote hero:</strong> “Friendly robot architect with blueprints, pointing to a holographic dashboard, isometric, soft light, professional editorial illustration.”</li>
          <li><strong>Categorias:</strong> “Same robot studying a wall of labeled folders (security, cloud, data), flat illustration, consistent character.”</li>
          <li><strong>Ferramentas:</strong> “Same robot carrying a toolbox with Kubernetes/docker icons, dynamic pose, tech noir palette.”</li>
          <li><strong>Versões:</strong> “Same robot in front of a giant version timeline (Java/Python/JS), calm pose, infographic style.”</li>
        </ol>
      </details>
    </section>

  </div>`;
}'''

def replace_render_about(html: str, variant: int) -> str:
    start = html.find("function renderAbout(){")
    if start < 0:
        raise ValueError("renderAbout not found")
    end = html.find("\n\nfunction renderReadLater(){", start)
    if end < 0:
        raise ValueError("renderReadLater anchor not found")
    body = NEW_RENDER_ABOUT.strip().replace("<!-- MASCOT_SVG -->", MASCOT_SVGS[variant])
    return html[:start] + body + html[end:]


def main():
    for n in range(1, 6):
        path = ROOT / f"cursor-index-{n}.html"
        text = path.read_text(encoding="utf-8")
        text = replace_render_about(text, n)
        path.write_text(text, encoding="utf-8")
        print("patched", path.name)


if __name__ == "__main__":
    main()
