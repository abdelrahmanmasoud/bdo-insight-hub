"""English / German helpers. The web UI gets MAPS from /api/overview so labels are defined in one place."""

LANGS = ("en", "de")

TOPIC = {"delivery": "Lieferung", "price": "Preis", "support": "Support", "app": "App", "quality": "Qualität", "other": "Sonstiges"}
TOUCH = {"Onboarding": "Onboarding", "Delivery": "Lieferung", "Support": "Support", "Billing": "Abrechnung", "App": "App"}
SENTIMENT = {"positive": "positiv", "neutral": "neutral", "negative": "negativ"}
SEVERITY = {"error": "Fehler", "warning": "Warnung", "info": "Hinweis"}
SOURCE_EN = {"crm": "CRM", "finance": "Finance", "social": "Social media", "cx": "Customer experience", "compliance": "Compliance"}
SOURCE = {"crm": "CRM", "finance": "Finanzen", "social": "Social Media", "cx": "Customer Experience", "compliance": "Compliance"}
DEPT = {"crm": ("Sales", "Vertrieb"), "finance": ("Finance", "Finanzen"), "social": ("Marketing", "Marketing"),
        "cx": ("Customer Experience", "Customer Experience"), "compliance": ("Compliance", "Compliance")}
INDUSTRY = {"Photo & Retail": "Foto & Handel", "E-Commerce": "E-Commerce", "Industrial Manufacturing": "Industrielle Fertigung",
            "Automotive Supplier": "Automobilzulieferer", "Insurance & Pensions": "Versicherung & Altersvorsorge",
            "Renewable Energy": "Erneuerbare Energien"}
LOSS_REASON = {"price": "Preis", "timing": "Timing", "scope unclear": "Unklarer Umfang", "no data access": "Kein Datenzugang",
               "competitor": "Wettbewerber"}
WAVE = {1: ("Wave 1 (0-3 months)", "Welle 1 (0–3 Monate)"), 2: ("Wave 2 (3-6 months)", "Welle 2 (3–6 Monate)"),
        3: ("Wave 3 (6-12 months)", "Welle 3 (6–12 Monate)")}

MAPS = {"topic": TOPIC, "touch": TOUCH, "sentiment": SENTIMENT, "severity": SEVERITY, "source": SOURCE, "source_en": SOURCE_EN, "industry": INDUSTRY,
        "loss_reason": LOSS_REASON, "dept": {k: v[1] for k, v in DEPT.items()}, "dept_en": {k: v[0] for k, v in DEPT.items()},
        "wave": {str(k): v[1] for k, v in WAVE.items()}, "wave_en": {str(k): v[0] for k, v in WAVE.items()}}


def pick(lang, en, de):
    return de if lang == "de" else en


def tr(mapping, key, lang):
    """Translate a data value for German; English keeps the raw value."""
    return mapping.get(key, key) if lang == "de" else key


def num(n, lang="en"):
    """Whole number with thousands separators (1,234 in English, 1.234 in German)."""
    s = f"{n:,.0f}"
    return s.replace(",", ".") if lang == "de" else s


def eur(n, lang="en"):
    return f"{num(n, lang)} EUR"


def uc_name(u, lang="en"):
    return u.get("name_de", u["name"]) if lang == "de" else u["name"]


def wave(u, lang="en"):
    return WAVE[u["wave_n"]][1 if lang == "de" else 0]


def offer_field(o, key, lang="en"):
    """Offers are stored with German base keys; *_en holds the English text."""
    return o.get(f"{key}_en", o[key]) if lang == "en" else o[key]


def finding_text(i, lang="en"):
    return i.get("message_de", i["message"]) if lang == "de" else i["message"]
