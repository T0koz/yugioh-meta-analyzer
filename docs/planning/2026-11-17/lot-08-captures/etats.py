"""Planche des états des composants d'interaction (lot 8).

Charge une page du site (pour sa feuille de style réelle), remplace le contenu de <main>
par toutes les variantes de `.ctl`, puis force les pseudo-classes par CDP
(CSS.forcePseudoState) : une section par état, une capture par largeur.
Mesure aussi les animations en cours en mouvement réduit.
"""
import sys
from playwright.sync_api import sync_playwright
base, out = sys.argv[1], sys.argv[2]

ROW = """
<a class="ctl ctl-primary" href="#">Principal</a>
<button class="ctl ctl-secondary" type="button">Secondaire</button>
<button class="ctl ctl-ghost" type="button">Discret</button>
<button class="ctl ctl-secondary ctl-sm" type="button">Petit</button>
<button class="ctl ctl-pill" type="button" aria-pressed="false">Pill</button>
<button class="ctl ctl-pill" type="button" aria-pressed="true">Pill active</button>
<nav class="ctl-rail"><a class="ctl ctl-tab" href="#">Onglet</a><a class="ctl ctl-tab" href="#" aria-current="page">Onglet actif</a></nav>
"""
STATES = [("repos", []), ("survol", ["hover"]), ("appui", ["hover", "active"]), ("focus", ["focus-visible"]), ("désactivé", None)]

def build(page):
    page.evaluate("""([row, states]) => {
      const main = document.querySelector('main');
      main.innerHTML = '';
      main.style.paddingTop = '32px';
      for (const name of states) {
        const s = document.createElement('section');
        s.dataset.state = name;
        s.style.cssText = 'margin-bottom:28px';
        s.innerHTML = `<p style="font:500 12px var(--font-jetbrains-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted-text);margin-bottom:12px">${name}</p>`
          + `<div style="display:flex;flex-wrap:wrap;gap:14px;align-items:center">${row}</div>`;
        if (name === 'désactivé') s.querySelectorAll('.ctl').forEach(el => { el.setAttribute('aria-disabled','true'); if (el.tagName==='BUTTON') el.disabled = true; });
        main.appendChild(s);
      }
    }""", [ROW, [n for n, _ in STATES]])

def force(page, cdp):
    cdp.send("DOM.enable"); cdp.send("CSS.enable")
    root = cdp.send("DOM.getDocument", {"depth": 0})["root"]["nodeId"]
    for name, pseudo in STATES:
        if not pseudo: continue
        ids = cdp.send("DOM.querySelectorAll", {"nodeId": root, "selector": f'section[data-state="{name}"] .ctl'})["nodeIds"]
        for i in ids:
            cdp.send("CSS.forcePseudoState", {"nodeId": i, "forcedPseudoClasses": pseudo})

with sync_playwright() as p:
    b = p.chromium.launch()
    for width in (375, 768, 1440):
        ctx = b.new_context(viewport={"width": width, "height": 900}, device_scale_factor=2)
        page = ctx.new_page()
        page.goto(base + "/ban?tab=simulateur", wait_until="networkidle")
        build(page)
        force(page, ctx.new_cdp_session(page))
        page.wait_for_timeout(600)
        page.locator("main").screenshot(path=f"{out}/etats-{width}.png")
        ctx.close()

    # Mouvement réduit : aucune animation ni transition en cours, aucune transformation.
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    page = ctx.new_page()
    page.goto(base + "/ban?tab=simulateur", wait_until="networkidle")
    build(page)
    force(page, ctx.new_cdp_session(page))
    r = page.evaluate("""() => ({
      animations: document.getAnimations().length,
      transformes: [...document.querySelectorAll('main .ctl')].filter(e => !['none','matrix(1, 0, 0, 1, 0, 0)'].includes(getComputedStyle(e).transform)).length,
      controles: document.querySelectorAll('main .ctl').length })""")
    print("mouvement réduit, états forcés :", r)
    # Et en interaction réelle : survol puis appui maintenu sur un bouton.
    btn = page.locator('section[data-state="repos"] .ctl-primary')
    btn.hover(); page.mouse.down()
    r2 = page.evaluate("""() => { const e = document.querySelector('section[data-state="repos"] .ctl-primary');
      return { animations: document.getAnimations().length, transform: getComputedStyle(e).transform, active: e.matches(':active') } }""")
    page.mouse.up()
    print("mouvement réduit, appui réel :", r2)
    ctx.close()

    # Témoin : mouvement autorisé, l'appui réel anime bien.
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    page.goto(base + "/ban?tab=simulateur", wait_until="networkidle")
    build(page)
    btn = page.locator('section[data-state="repos"] .ctl-primary')
    btn.hover(); page.mouse.down()
    n = page.evaluate("document.getAnimations().length")
    page.wait_for_timeout(400)
    t = page.evaluate("""getComputedStyle(document.querySelector('section[data-state="repos"] .ctl-primary')).transform""")
    page.mouse.up()
    print("témoin mouvement autorisé : animations pendant l'appui =", n, "; transform enfoncé =", t)
    b.close()
