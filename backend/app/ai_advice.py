import os
from collections import Counter
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def normalize_language(lang: str = "en"):
    return "es" if lang == "es" else "en"


def build_posture_summary(readings):
    total = len(readings)

    if total == 0:
        return {
            "total_readings": 0,
            "message": "No posture data available"
        }

    bad_count = sum(1 for item in readings if item.is_bad_posture)
    good_count = total - bad_count

    posture_counter = Counter(item.posture for item in readings)
    most_common_posture = posture_counter.most_common(1)[0][0]

    return {
        "total_readings": total,
        "good_posture_percentage": round((good_count / total) * 100, 2),
        "bad_posture_percentage": round((bad_count / total) * 100, 2),
        "most_common_posture": most_common_posture
    }


def get_risk_level(summary):
    if summary["total_readings"] == 0:
        return "unknown"

    bad_percentage = summary["bad_posture_percentage"]

    if bad_percentage >= 70:
        return "high"

    if bad_percentage >= 40:
        return "medium"

    return "low"


def format_posture_for_language(posture, lang):
    posture_names = {
        "en": {
            "correct": "correct",
            "leaning_left": "leaning left",
            "leaning_right": "leaning right",
            "leaning_forward": "leaning forward",
            "leaning_back": "leaning back",
            "slouched": "slouched",
            "not_sitting": "not sitting"
        },
        "es": {
            "correct": "correcta",
            "leaning_left": "inclinado a la izquierda",
            "leaning_right": "inclinado a la derecha",
            "leaning_forward": "inclinado hacia adelante",
            "leaning_back": "inclinado hacia atrás",
            "slouched": "encorvado",
            "not_sitting": "sin persona sentada"
        }
    }

    return posture_names[lang].get(posture, posture)


def generate_local_ai_advice(summary, lang: str = "en"):
    lang = normalize_language(lang)
    risk_level = get_risk_level(summary)

    if summary["total_readings"] == 0:
        advice = (
            "There is not enough posture data yet to generate a recommendation."
            if lang == "en"
            else "Aún no hay suficientes lecturas de postura para generar una recomendación."
        )

        return {
            "source": "local_ai_rules",
            "language": lang,
            "risk_level": "unknown",
            "summary": summary,
            "advice": advice
        }

    bad_percentage = summary["bad_posture_percentage"]
    posture = format_posture_for_language(summary["most_common_posture"], lang)

    if lang == "es":
        if bad_percentage >= 70:
            advice = (
                f"Riesgo postural alto detectado. La postura más frecuente es {posture}. "
                "Ajustá tu silla, sentate centrado, apoyá la espalda y tomá una pausa corta."
            )
        elif bad_percentage >= 40:
            advice = (
                f"Riesgo postural moderado detectado. Frecuentemente estás en postura {posture}. "
                "Intentá balancear tu peso, mantener ambos pies en el suelo y corregir tu espalda."
            )
        else:
            advice = (
                "El comportamiento postural se ve estable. Mantené una posición balanceada "
                "y seguí tomando pausas regulares."
            )
    else:
        if bad_percentage >= 70:
            advice = (
                f"High posture risk detected. The most frequent issue is {posture}. "
                "Adjust your chair, sit centered, support your back, and take a short break."
            )
        elif bad_percentage >= 40:
            advice = (
                f"Moderate posture risk detected. You often sit in {posture}. "
                "Try to balance your weight, keep both feet on the floor, and correct your back position."
            )
        else:
            advice = (
                "Posture behavior looks stable. Keep a balanced sitting position and continue taking regular breaks."
            )

    return {
        "source": "local_ai_rules",
        "language": lang,
        "risk_level": risk_level,
        "summary": summary,
        "advice": advice
    }


def generate_ai_advice(readings, lang: str = "en"):
    lang = normalize_language(lang)
    summary = build_posture_summary(readings)

    if not GEMINI_API_KEY:
        return generate_local_ai_advice(summary, lang)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        language_instruction = (
            "Write the final recommendation only in Spanish."
            if lang == "es"
            else "Write the final recommendation only in English."
        )

        prompt = f"""
You are an ergonomic posture assistant for a university IoT project.

Analyze this posture summary and generate one short, practical recommendation.

Rules:
- {language_instruction}
- Do not diagnose medical conditions.
- Do not mention that you are an AI.
- Use simple language.
- Keep the answer under 45 words.
- Focus on posture correction, short breaks, chair position, and sitting balance.
- Do not repeat raw JSON field names unless needed.

Data:
{summary}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return {
            "source": "gemini",
            "language": lang,
            "risk_level": get_risk_level(summary),
            "summary": summary,
            "advice": response.text
        }

    except Exception as error:
        fallback = generate_local_ai_advice(summary, lang)
        fallback["source"] = "local_ai_fallback"
        fallback["provider_error"] = str(error)

        return fallback