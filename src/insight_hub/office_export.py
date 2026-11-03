"""MS-Office outputs: PowerPoint sales deck, Word technical appendix, Excel analysis workbook."""


def sales_deck(c, path):
    from .i18n import INDUSTRY, TOPIC, TOUCH
    from pptx import Presentation
    from pptx.util import Inches, Pt
    prs = Presentation()

    def bullets(title, items):
        s = prs.slides.add_slide(prs.slide_layouts[1]); s.shapes.title.text = title
        tf = s.placeholders[1].text_frame; tf.text = items[0]
        for t in items[1:]:
            tf.add_paragraph().text = t
        for p in tf.paragraphs:
            p.font.size = Pt(20)
    t = prs.slides.add_slide(prs.slide_layouts[0])
    t.shapes.title.text = "KI- & CX-Strategie"; t.placeholders[1].text = f"{c['client']['name']} · Beispielanalyse"
    bullets("Ausgangslage", [f"Branche: {INDUSTRY.get(c['client']['industry'], c['client']['industry'])}", f"Offene Pipeline: {c['client']['pipeline_eur']:,.0f} EUR", f"NPS: {c['nps']}"])
    bullets("Erkenntnisse", [f"Größter Churn-Treiber: {TOUCH.get(c['drivers'][0]['touchpoint'], c['drivers'][0]['touchpoint'])}" if c["drivers"] else "–",
                             f"Frühwarnsignal: {TOPIC.get(c['emerging'][0]['topic'], c['emerging'][0]['topic'])}" if c["emerging"] else "Keine akuten Social-Themen"])
    s = prs.slides.add_slide(prs.slide_layouts[5]); s.shapes.title.text = "Roadmap"
    rows = c["strategy"][:5]  # German sales deck
    tb = s.shapes.add_table(len(rows) + 1, 3, Inches(0.5), Inches(1.6), Inches(9), Inches(3)).table
    for i, h in enumerate(["Use Case", "Score", "Welle"]):
        tb.cell(0, i).text = h
    for r, u in enumerate(rows, 1):
        tb.cell(r, 0).text, tb.cell(r, 1).text, tb.cell(r, 2).text = u["name_de"], str(u["score"]), u["wave"].replace("Wave", "Welle").replace("months", "Monate")
    bullets("Empfohlene Angebote", [f"{o['offer']} – {o.get('why_de', o['why'])}" for o in c["offers"]] or ["–"])
    prs.save(path)


def technical_doc(c, path):
    from docx import Document
    d = Document(); d.add_heading(f"Technical appendix – {c['client']['name']}", 1)
    d.add_heading("Source coverage", 2)
    t = d.add_table(rows=1, cols=2); t.rows[0].cells[0].text, t.rows[0].cells[1].text = "Source", "Records"
    for s, n in c["client"]["records"].items():
        row = t.add_row().cells; row[0].text, row[1].text = s, str(n)
    d.add_heading("Data quality", 2)
    for i in c["dq"] or [{"severity": "ok", "message": "no issues"}]:
        d.add_paragraph(f"{i['severity']}: {i['message']}", style="List Bullet")
    d.save(path)


def workbook(all_ctx, stats, path):
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "unified_view"
    ws.append(["client_id", "name", "industry", "pipeline_eur", "budget_eur", "spent_eur", "nps"])
    for c in all_ctx:
        v = c["client"]; ws.append([v["client_id"], v["name"], v["industry"], v["pipeline_eur"], v["budget_eur"], v["spent_eur"], c["nps"]])
    w2 = wb.create_sheet("strategy"); w2.append(["client_id", "use_case", "score", "wave"])
    for c in all_ctx:
        for u in c["strategy"]:
            w2.append([c["client"]["client_id"], u["name"], u["score"], u["wave"]])
    w3 = wb.create_sheet("offer_feedback"); w3.append(["offer", "n", "win_rate", "action"])
    for s in stats:
        w3.append([s["offer"], s["n"], s["win_rate"], s["action"]])
    wb.save(path)


def audience_deck(slides, target):
    """Render deck specs from decks.py to PowerPoint. `target` is a path or a file-like object."""
    from pptx import Presentation
    from pptx.util import Inches, Pt
    prs = Presentation()
    for i, sp in enumerate(slides):
        if i == 0:
            s = prs.slides.add_slide(prs.slide_layouts[0]); s.shapes.title.text = sp["title"]; s.placeholders[1].text = sp.get("subtitle", "")
        elif "table" in sp:
            s = prs.slides.add_slide(prs.slide_layouts[5]); s.shapes.title.text = sp["title"]
            rows = sp["table"]
            tb = s.shapes.add_table(len(rows), len(rows[0]), Inches(0.5), Inches(1.6), Inches(9), Inches(0.5 * len(rows))).table
            for r, row in enumerate(rows):
                for k, val in enumerate(row):
                    tb.cell(r, k).text = val
                    tb.cell(r, k).text_frame.paragraphs[0].font.size = Pt(14)
        else:
            s = prs.slides.add_slide(prs.slide_layouts[1]); s.shapes.title.text = sp["title"]
            tf = s.placeholders[1].text_frame; tf.text = sp["bullets"][0]
            for b in sp["bullets"][1:]:
                tf.add_paragraph().text = b
            for p in tf.paragraphs:
                p.font.size = Pt(22)
        if sp.get("notes"):
            s.notes_slide.notes_text_frame.text = sp["notes"]
    prs.save(target)
