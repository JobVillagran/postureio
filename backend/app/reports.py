from collections import Counter


def generate_summary(readings):
    total = len(readings)

    if total == 0:
        return {
            "total_readings": 0,
            "good_posture_percentage": 0,
            "bad_posture_percentage": 0,
            "most_common_posture": None
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