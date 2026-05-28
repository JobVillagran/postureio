from collections import Counter


def generate_advice(readings):
    total = len(readings)

    if total == 0:
        return {
            "advice": "There is not enough data yet.",
            "risk_level": "unknown"
        }

    bad_count = sum(1 for item in readings if item.is_bad_posture)
    bad_percentage = (bad_count / total) * 100

    posture_counter = Counter(item.posture for item in readings)
    most_common_posture = posture_counter.most_common(1)[0][0]

    if bad_percentage >= 70:
        risk_level = "high"
        advice = f"Your posture needs attention. The most frequent issue is {most_common_posture}. Adjust your chair and take a short break."
    elif bad_percentage >= 40:
        risk_level = "medium"
        advice = f"Your posture can improve. You often sit in {most_common_posture}. Try to sit centered and keep your back supported."
    else:
        risk_level = "low"
        advice = "Your posture looks stable. Keep maintaining a balanced sitting position."

    return {
        "bad_posture_percentage": round(bad_percentage, 2),
        "most_common_posture": most_common_posture,
        "risk_level": risk_level,
        "advice": advice
    }