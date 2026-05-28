from collections import Counter


def generate_advice(readings):
    total = len(readings)

    if total == 0:
        return {
            "advice": "There is not enough data yet.",
            "risk_level": "unknown",
            "recommended_action": "collect_more_data"
        }

    bad_count = sum(1 for item in readings if item.is_bad_posture)
    bad_percentage = (bad_count / total) * 100

    posture_counter = Counter(item.posture for item in readings)
    most_common_posture = posture_counter.most_common(1)[0][0]

    if bad_percentage >= 70:
        risk_level = "high"
        recommended_action = "trigger_alert"
        advice = f"High posture risk detected. The most frequent issue is {most_common_posture}. Adjust the chair position and take a short break."
    elif bad_percentage >= 40:
        risk_level = "medium"
        recommended_action = "show_warning"
        advice = f"Moderate posture risk detected. The most frequent posture is {most_common_posture}. Try to sit centered and support your back."
    else:
        risk_level = "low"
        recommended_action = "no_action"
        advice = "Posture behavior looks stable. Keep a balanced sitting position."

    return {
        "bad_posture_percentage": round(bad_percentage, 2),
        "most_common_posture": most_common_posture,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "advice": advice
    }