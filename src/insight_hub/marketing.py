"""Marketingunterlagen: printable HTML one-pager (Ctrl+P -> PDF), generated from the offers + live stats. German or English."""
import html

from .i18n import offer_field, pick


def onepager(offers, stats, totals, lang="de"):
    t = lambda en, de: pick(lang, en, de)
    wr = {s["offer"]: s["win_rate"] for s in stats}
    cards = "".join(
        f"<div class='card'><h3>{html.escape(offer_field(o, 'offer', lang))}</h3><p class='q'>{html.escape(offer_field(o, 'problem', lang))}</p>"
        f"<p>{html.escape(offer_field(o, 'benefit', lang))}</p><p class='m'>{t('Win rate of recent offers', 'Win-Rate letzte Angebote')}: {wr.get(o['offer'], 0):.0%}</p></div>" for o in offers)
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>BDO Insight Hub – One-Pager</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;color:#12202f}}h1{{font-size:34px;margin:0}}.sub{{color:#5b6672;font-size:18px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:24px 0}}.card{{border:1px solid #ddd;border-radius:10px;padding:16px}}
.card h3{{margin:0 0 6px;color:#d3123a}}.q{{font-style:italic}}.m{{color:#5b6672;font-size:13px}}.stats{{display:flex;gap:32px}}
.stats b{{font-size:30px;display:block}}footer{{margin-top:24px;font-size:12px;color:#888}}@media print{{body{{margin:12mm}}}}</style></head><body>
<h1>{t('From data to AI strategy', 'Von Daten zur KI-Strategie')}</h1><p class="sub">Management Advisory: {t('AI &amp; Customer Experience', 'KI &amp; Customer Experience')}</p>
<div class="stats"><div><b>{totals['sources']}</b>{t('departments integrated', 'Fachbereiche integriert')}</div><div><b>{totals['posts']}</b>{t('social posts analysed', 'Social-Posts analysiert')}</div>
<div><b>{totals['reviews']}</b>{t('customer reviews evaluated', 'Kundenfeedbacks ausgewertet')}</div></div>
<div class="grid">{cards}</div><footer>[{t('Contact', 'Kontakt')}: recruiting@bdo.de]</footer></body></html>"""
