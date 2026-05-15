"""
PROYECTO 3: Auditor de Contenido por IA
========================================
Compara un texto contra las "Directrices de Marca" de una empresa
y devuelve una auditoría con puntuación 0-100 y puntos de mejora.

Uso:
    python auditor.py --text "Tu texto aquí" --brand brand_template.json --key TU_API_KEY
    python auditor.py --input articulo.txt --key TU_API_KEY
    python auditor.py --input articulo.txt --brand mi_marca.json --key TU_API_KEY --save
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from google import genai

# ── CONFIG ─────────────────────────────────────────────────────────────────────
MODEL = "gemini-2.5-flash"

# ── Brand Guidelines por defecto ───────────────────────────────────────────────
DEFAULT_BRAND_GUIDELINES = {
    "brand_name": "AcmeCorp",
    "brand_description": "Empresa tecnológica B2B enfocada en soluciones de automatización para PYMES.",
    "tone_of_voice": {
        "desired": ["profesional", "cercano", "claro", "inspirador", "directo"],
        "avoid":   ["jerga informal", "lenguaje técnico excesivo", "tono condescendiente", "exageraciones"]
    },
    "writing_rules": [
        {"rule": "Oraciones cortas", "detail": "Máximo 25 palabras por oración."},
        {"rule": "Voz activa", "detail": "Usar voz activa en >80% de las oraciones."},
        {"rule": "Adjetivos controlados", "detail": "Máximo 2 adjetivos descriptivos por párrafo."},
        {"rule": "Sin superlativas vacías", "detail": "Prohibido: 'el mejor', 'increíble', 'revolucionario' sin evidencia."},
        {"rule": "Datos concretos", "detail": "Toda afirmación cuantificable debe incluir número o porcentaje."},
        {"rule": "Llamada a la acción clara", "detail": "Todo texto debe tener un CTA explícito al final."}
    ],
    "forbidden_words": ["literalmente", "básicamente", "obviamente", "simplemente", "fácilmente"],
    "required_elements": {
        "for_blog_posts": ["headline impactante", "al menos 1 dato estadístico", "CTA"],
        "for_linkedin":   ["hook en primera línea", "hashtags relevantes", "CTA"],
        "for_emails":     ["asunto personalizado", "nombre del destinatario", "1 solo CTA"]
    },
    "audience": "Dueños de PYMES y directores de operaciones de 35-55 años."
}

SYSTEM_PROMPT = """Eres un auditor experto en identidad de marca y comunicación estratégica.
Tu trabajo es evaluar textos con precisión quirúrgica contra directrices de marca específicas.

Debes ser:
- Objetivo y basado en evidencia textual concreta
- Constructivo: señalar problemas y ofrecer alternativas
- Consistente: misma regla, mismo criterio siempre

RESPONDE ÚNICAMENTE CON EL JSON SOLICITADO. Sin texto adicional, sin markdown."""

AUDIT_PROMPT = """Audita el siguiente TEXTO contra estas DIRECTRICES DE MARCA y devuelve exactamente este JSON:

{{
  "audit_summary": {{
    "brand_name": "{brand_name}",
    "audited_at": "{timestamp}",
    "word_count": <número entero>,
    "overall_score": <número entero 0-100>,
    "grade": "<A+|A|B+|B|C+|C|D|F>",
    "verdict": "<una frase de 10-15 palabras resumiendo el estado del texto>"
  }},
  "category_scores": {{
    "tone_of_voice":   {{"score": <0-100>, "weight": 30}},
    "writing_rules":   {{"score": <0-100>, "weight": 35}},
    "forbidden_words": {{"score": <0-100>, "weight": 15}},
    "audience_fit":    {{"score": <0-100>, "weight": 20}}
  }},
  "violations": [
    {{
      "rule": "<nombre de la regla violada>",
      "severity": "<critical|major|minor>",
      "quote": "<fragmento exacto del texto que viola la regla>",
      "explanation": "<por qué viola la regla>",
      "suggestion": "<reescritura concreta corregida>"
    }}
  ],
  "strengths": [
    {{
      "rule": "<nombre de la regla cumplida>",
      "evidence": "<fragmento del texto que la cumple>",
      "comment": "<por qué es un acierto>"
    }}
  ],
  "priority_improvements": [
    "<mejora concreta #1 con acción específica>",
    "<mejora concreta #2 con acción específica>",
    "<mejora concreta #3 con acción específica>"
  ],
  "rewritten_opening": "<reescritura del primer párrafo aplicando todas las correcciones>"
}}

DIRECTRICES DE MARCA:
{brand_json}

TEXTO A AUDITAR:
\"\"\"
{text}
\"\"\"

Responde SOLO con el JSON."""


# ── Core ───────────────────────────────────────────────────────────────────────

def run_audit(text: str, brand: dict, api_key: str | None = None) -> dict:
    """Ejecuta la auditoría de marca y retorna el resultado estructurado."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=key)

    prompt = AUDIT_PROMPT.format(
        brand_name=brand.get("brand_name", "Empresa"),
        timestamp=datetime.utcnow().isoformat() + "Z",
        brand_json=json.dumps(brand, ensure_ascii=False, indent=2),
        text=text.strip(),
    )

    print("🔍 Ejecutando auditoría…", end="", flush=True)

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={"system_instruction": SYSTEM_PROMPT},
    )

    print(" ✅")

    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


def print_report(result: dict) -> None:
    """Imprime el reporte de auditoría en la terminal."""
    s  = result["audit_summary"]
    cs = result["category_scores"]

    score = s["overall_score"]
    bar   = "█" * (score // 10) + "░" * (10 - score // 10)

    color_map = {"A+": "🏆", "A": "🥇", "B+": "🥈", "B": "🥉",
                 "C+": "🆗", "C": "⚠️",  "D": "❌",  "F": "🚨"}
    icon = color_map.get(s["grade"], "📋")

    print("\n" + "═"*62)
    print(f"  AUDITORÍA DE MARCA  ·  {s['brand_name'].upper()}")
    print("═"*62)
    print(f"\n  {icon}  PUNTUACIÓN GLOBAL: {score}/100  [{bar}]  Nota: {s['grade']}")
    print(f"  📝 {s['verdict']}")
    print(f"  📊 Palabras analizadas: {s['word_count']}")

    print(f"\n{'─'*62}")
    print("  DESGLOSE POR CATEGORÍA")
    for cat, data in cs.items():
        sc = data["score"]
        w  = data["weight"]
        b  = "█" * (sc // 10) + "░" * (10 - sc // 10)
        print(f"  {cat:<20} {b}  {sc:>3}/100  (peso {w}%)")

    violations = result.get("violations", [])
    if violations:
        print(f"\n{'─'*62}")
        print(f"  ⚠️  VIOLACIONES ({len(violations)})")
        sev_icon = {"critical": "🔴", "major": "🟡", "minor": "🔵"}
        for v in violations:
            ic = sev_icon.get(v["severity"], "⚪")
            print(f"\n  {ic} [{v['severity'].upper()}] {v['rule']}")
            print(f"     Texto:      «{v['quote'][:70]}»")
            print(f"     Problema:   {v['explanation']}")
            print(f"     Sugerencia: {v['suggestion']}")

    strengths = result.get("strengths", [])
    if strengths:
        print(f"\n{'─'*62}")
        print(f"  ✅ FORTALEZAS ({len(strengths)})")
        for st in strengths:
            print(f"\n  ✔ {st['rule']}")
            print(f"    {st['comment']}")

    print(f"\n{'─'*62}")
    print("  🚀 TOP 3 MEJORAS PRIORITARIAS")
    for i, imp in enumerate(result.get("priority_improvements", []), 1):
        print(f"  {i}. {imp}")

    print(f"\n{'─'*62}")
    print("  ✏️  REESCRITURA SUGERIDA (apertura)")
    print(f"\n  {result.get('rewritten_opening', '')}")
    print("\n" + "═"*62 + "\n")


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auditor de contenido por IA")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text",  "-t", help="Texto a auditar")
    group.add_argument("--input", "-i", help="Archivo .txt a auditar")
    parser.add_argument("--brand", "-b", help="JSON con directrices de marca (opcional)")
    parser.add_argument("--key",   "-k", help="Gemini API key (o usa GEMINI_API_KEY)")
    parser.add_argument("--save",  "-s", action="store_true", help="Guardar JSON resultado")
    args = parser.parse_args()

    # Texto
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = args.text

    # Brand guidelines
    if args.brand:
        brand = json.loads(Path(args.brand).read_text(encoding="utf-8"))
    else:
        brand = DEFAULT_BRAND_GUIDELINES
        print("ℹ️  Usando directrices de marca por defecto (AcmeCorp).")
        print("   Pasa --brand tu_marca.json para usar las tuyas.\n")

    result = run_audit(text, brand, api_key=args.key)
    print_report(result)

    if args.save:
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = Path(f"auditoria_{ts}.json")
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"💾 Guardado en: {path}\n")
