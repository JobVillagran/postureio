import os
from collections import Counter
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


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


def generate_local_ai_advice(summary):
    if summary["total_readings"] == 0:
        return {
            "source": "local_ai_rules",
            "risk_level": "unknown",
            "summary": summary,
            "advice": "There is not enough posture data yet to generate a recommendation."
        }

    bad_percentage = summary["bad_posture_percentage"]
    posture = summary["most_common_posture"]

    if bad_percentage >= 70:
        risk_level = "high"
        advice = (
            f"High posture risk detected. The most frequent issue is {posture}. "
            "Adjust your chair, sit centered, support your back, and take a short break."
        )
    elif bad_percentage >= 40:
        risk_level = "medium"
        advice = (
            f"Moderate posture risk detected. You often sit in {posture}. "
            "Try to balance your weight, keep both feet on the floor, and correct your back position."
        )
    else:
        risk_level = "low"
        advice = (
            "Posture behavior looks stable. Keep a balanced sitting position and continue taking regular breaks."
        )

    return {
        "source": "local_ai_rules",
        "risk_level": risk_level,
        "summary": summary,
        "advice": advice
    }


def generate_ai_advice(readings):
    summary = build_posture_summary(readings)

    if not GEMINI_API_KEY:
        return generate_local_ai_advice(summary)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
You are an ergonomic posture assistant for a university IoT project.

Analyze this posture summary and generate one short, practical recommendation.

Rules:
- Do not diagnose medical conditions.
- Do not mention that you are an AI.
- Use simple language.
- Keep the answer under 45 words.
- Focus on posture correction, breaks, and chair adjustment.

Data:
{summary}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        risk_level = "low"

        if summary["total_readings"] == 0:
            risk_level = "unknown"
        elif summary["bad_posture_percentage"] >= 70:
            risk_level = "high"
        elif summary["bad_posture_percentage"] >= 40:
            risk_level = "medium"

        return {
            "source": "gemini",
            "risk_level": risk_level,
            "summary": summary,
            "advice": response.text
        }

    except Exception as error:
        fallback = generate_local_ai_advice(summary)
        fallback["source"] = "local_ai_fallback"
        fallback["provider_error"] = str(error)

        return fallback