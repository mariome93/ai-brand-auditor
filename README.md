# 🎯 AI Brand Auditor — Auditor de Contenido por IA

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-4285F4?style=flat&logo=google&logoColor=white)
![JSON](https://img.shields.io/badge/Config-Brand_Guidelines_JSON-6366F1?style=flat)
![Score](https://img.shields.io/badge/Output-Score_0--100-22C55E?style=flat)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat)

> Herramienta que evalúa qué tan alineado está un texto con las **Directrices de Marca** de una empresa, devolviendo una puntuación 0-100 con violaciones concretas citando el texto exacto y sugiriendo reescrituras.

---

## ✨ ¿Qué genera?


Una auditoría estructurada en JSON con:

- 📊 **Puntuación global** (0-100) con nota tipo escolar (A+, B, C…)
- 📂 **Score por categoría** — tono, reglas de escritura, palabras prohibidas, fit de audiencia
- 🔴 **Violaciones** con severidad (critical / major / minor), cita exacta y sugerencia de corrección
- ✅ **Fortalezas** detectadas en el texto
- 🚀 **Top 3 mejoras prioritarias**
- ✏️ **Reescritura sugerida** del primer párrafo

---

## 🚀 Instalación paso a paso

### Paso 1 — Clona el repositorio

```bash
git clone https://github.com/mariome93/ai-brand-auditor.git
cd ai-brand-auditor
```

### Paso 2 — Crea un entorno virtual (recomendado)

**Mac / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Paso 3 — Instala las dependencias

```bash
pip install google-genai
```

### Paso 4 — Obtén tu API key de Gemini (gratis)

1. Ve a [aistudio.google.com](https://aistudio.google.com)
2. Inicia sesión con tu cuenta de Google
3. Clic en **"Get API key"** → **"Create API key"**
4. Copia la key (empieza con `AIza...`)

> No necesitas tarjeta de crédito. El plan gratuito incluye 1,500 requests/día.

### Paso 5 — Personaliza tus directrices de marca

Edita el archivo `brand_template.json` con las reglas de tu empresa:

```json
{
  "brand_name": "TuEmpresa",
  "brand_description": "Describe qué hace tu empresa.",
  "tone_of_voice": {
    "desired": ["profesional", "cercano", "claro"],
    "avoid":   ["jerga", "lenguaje pasivo", "exageraciones"]
  },
  "writing_rules": [
    {
      "rule": "Oraciones cortas",
      "detail": "Máximo 25 palabras por oración."
    },
    {
      "rule": "Voz activa",
      "detail": "Usar voz activa en más del 80% de las oraciones."
    },
    {
      "rule": "Sin superlativas sin evidencia",
      "detail": "No usar 'el mejor', 'increíble' sin datos que lo respalden."
    }
  ],
  "forbidden_words": ["básicamente", "literalmente", "obviamente"],
  "audience": "Describe a tu audiencia objetivo aquí."
}
```

> Si no defines un archivo de marca, el auditor usa unas directrices de ejemplo (AcmeCorp) incluidas en el código.

### Paso 6 — Corre la auditoría

**Con tu archivo de texto y directrices personalizadas:**
```bash
python auditor.py --input mi_texto.txt --brand brand_template.json --key TU_API_KEY
```

**Con texto directo y directrices por defecto:**
```bash
python auditor.py --text "Nuestro producto es literalmente el mejor del mercado." --key TU_API_KEY
```

**Guardando el reporte JSON en disco:**
```bash
python auditor.py --input mi_texto.txt --brand brand_template.json --key TU_API_KEY --save
```

También puedes exportar la key como variable de entorno:

**Mac / Linux:**
```bash
export GEMINI_API_KEY="TU_API_KEY"
python auditor.py --input mi_texto.txt --brand brand_template.json
```

**Windows:**
```bash
set GEMINI_API_KEY=TU_API_KEY
python auditor.py --input mi_texto.txt --brand brand_template.json
```

---

## 📤 Ejemplo de output en terminal

```
══════════════════════════════════════════════════════════════
  AUDITORÍA DE MARCA  ·  ACMECORP
══════════════════════════════════════════════════════════════

  ⚠️  PUNTUACIÓN GLOBAL: 61/100  [██████░░░░]  Nota: C+
  📝 El texto tiene buen tono pero viola reglas clave de escritura
  📊 Palabras analizadas: 42

  DESGLOSE POR CATEGORÍA
  tone_of_voice        ████████░░  78/100  (peso 30%)
  writing_rules        █████░░░░░  55/100  (peso 35%)
  forbidden_words      ████░░░░░░  40/100  (peso 15%)
  audience_fit         ████████░░  82/100  (peso 20%)

  ⚠️  VIOLACIONES (2)

  🔴 [CRITICAL] Palabras prohibidas
     Texto:      «nuestro producto es literalmente el mejor»
     Problema:   "literalmente" está en la lista de palabras prohibidas
     Sugerencia: «nuestro producto lidera su categoría con NPS de +72»

  🟡 [MAJOR] Sin superlativas sin evidencia
     Texto:      «el mejor del mercado»
     Problema:   afirmación cuantificable sin dato que la respalde
     Sugerencia: incluir métrica concreta o eliminar el superlativo

  🚀 TOP 3 MEJORAS PRIORITARIAS
  1. Reemplazar "literalmente" por dato concreto medible
  2. Acortar oraciones de más de 25 palabras
  3. Añadir un CTA explícito al final del texto
══════════════════════════════════════════════════════════════
```

---

## 📁 Estructura del proyecto

```
ai-brand-auditor/
├── auditor.py           ← Script principal
├── brand_template.json  ← Plantilla de directrices de marca (personalizable)
├── requirements.txt
└── README.md
```

---

## 📦 Dependencias

| Librería | Uso |
|---|---|
| `google-genai` | Llamadas a Gemini (SDK oficial nuevo) |

> ⚠️ Usa `google-genai` (SDK nuevo), **no** `google-generativeai` (deprecated).

---

## 💼 Caso de uso: consultoría de marca

Este auditor replica el flujo de una auditoría de contenido profesional:

1. El cliente define sus directrices en `brand_template.json`
2. Se pasan textos existentes (web, redes, emails) por el auditor
3. El reporte identifica inconsistencias con evidencia textual concreta
4. El equipo corrige basándose en sugerencias específicas y accionables

Tiempo de auditoría manual: 2-4 horas por texto. Con este tool: menos de 30 segundos.

---

## ⚠️ Límites del plan gratuito

| Modelo | Requests/día | Requests/minuto |
|---|---|---|
| gemini-2.0-flash | 1,500 | 15 |

Si ves un error `429 RESOURCE_EXHAUSTED`, espera unos minutos. El límite se resetea automáticamente.

---

## 🤝 Parte de mi portafolio AI

- 🔗 [ai-rag-agent](https://github.com/mariome93/ai-rag-agent) — Chatbot con RAG sobre PDFs
- 🔗 [ai-content-pipeline](https://github.com/mariome93/ai-content-pipeline) — Pipeline de automatización de contenido

---

*Desarrollado por [@mariome93](https://github.com/mariome93)*
