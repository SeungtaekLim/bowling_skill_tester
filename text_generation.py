import os
import json
from openai import OpenAI

# OpenAI API 키 설정
os.environ["OPENAI_API_KEY"] = "gpt 키 값 넣으센" 

# 각 지표별 평가 기준 (5단계 구간)
CRITERIA = {
    "shoulder_angle_diff": {
        "very_low": 0,
        "low": 15,
        "normal_min": 20,
        "normal_max": 25,
        "high": 30,
        "very_high": 100
    },
    "movement_distance": {
        "very_low": 0,
        "low": 0.1,
        "normal_min": 0.15,
        "normal_max": 0.3,
        "high": 0.5,
        "very_high": 2
    },
    "wrist_movement_total": {
        "very_low": 0,
        "low": 7,
        "normal_min": 10,
        "normal_max": 20,
        "high": 25,
        "very_high": 30
    },
    "ankle_switch_count": {
        "very_low": 0,
        "low": 1,
        "normal_min": 2,
        "normal_max": 4,
        "high": 6,
        "very_high": 7
    }
}

# 평가 결과에 따른 설명
INTERPRETATION_MESSAGES = {
    "매우 적음": "기준보다 많이 부족합니다. 동작이 너무 제한적일 수 있어요.",
    "적음": "기준보다 약간 부족합니다. 개선이 필요해요.",
    "적당함": "이상적인 범위입니다. 잘 유지되고 있어요.",
    "많음": "기준보다 약간 많습니다. 조금만 줄이면 더 좋을 수 있어요.",
    "매우 많음": "기준보다 많이 많습니다. 불안정하거나 과도할 수 있어요."
}

# 5단계 평가 함수
def interpret_value_v2(value, thresholds):
    if value < thresholds["low"]:
        return "매우 적음"
    elif value < thresholds["normal_min"]:
        return "적음"
    elif value <= thresholds["normal_max"]:
        return "적당함"
    elif value <= thresholds["high"]:
        return "많음"
    else:
        return "매우 많음"

# 메인 평가 함수
def evaluate_bowling_form(avg_shoulder_angle_diff, avg_movement, wrist_movement_total, ankle_switch_count):
    client = OpenAI()

    # 입력 값 정리
    values = {
        "shoulder_angle_diff": avg_shoulder_angle_diff,
        "movement_distance": avg_movement,
        "wrist_movement_total": wrist_movement_total,
        "ankle_switch_count": ankle_switch_count
    }

    # 해석 및 설명 추가
    interpretations = {}
    for key, value in values.items():
        thresholds = CRITERIA[key]
        interpretation = interpret_value_v2(value, thresholds)
        explanation = INTERPRETATION_MESSAGES[interpretation]
        interpretations[key] = f"{interpretation} - {explanation}"

    #GPT에게 보낼 메시지 구성
    prompt = f"""
제가 볼링 자세 평가를 완료했습니다. 결과는 아래와 같습니다:

- 평균 어깨 각도 차이 (90도에서): {avg_shoulder_angle_diff}도 ({interpretations["shoulder_angle_diff"]})
- 평균 이동 거리: {avg_movement} ({interpretations["movement_distance"]})
- 손목 이동 거리 총합: {wrist_movement_total} ({interpretations["wrist_movement_total"]})
- 발목 높이 변화 이벤트 수: {ankle_switch_count} ({interpretations["ankle_switch_count"]})

이 결과를 바탕으로 저의 볼링 자세에 대한 평가와 피드백을 주시고, 잘 된 점과 개선이 필요한 점을 알려주세요.
그리고 개선이 필요한 점이 크게 없다면, 개선이 필요한 점을 말할 때 잘하고 있지만 어떻게 더 했으면 좋겠다는 느낌으로 말해주세요.
또한, 다음 투구는 어떻게 하면 좋을지 추천해 주세요 이 또한 개선할 점이 많이 없다면 유지하라고 짧게 말하고 다음 자세를 추천해 주세요. 마지막으로 총 평가 점수를 0부터 100 사이 숫자로 제시해 주세요.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "당신은 볼링 자세에 대한 전문가입니다. 주어진 데이터를 바탕으로 자세 평가를 "
                    "4가지 항목으로 나눠서 제공하세요: "
                    "1) 잘한 점, 2) 개선이 필요한 점, 3) 다음 투구를 위한 추천, 4) 총 평가 점수 (0~100점 사이 숫자). "
                    "이동 거리나 수치적인 언급은 자제하고 대신 '크게', '적게', '많이' 등으로 표현해 주세요. "
                    "전체 피드백은 반드시 JSON 코드블럭 내에 반환해 주세요. 예:\n"
                    "```json\n"
                    "{\"잘한점\": \"...\", \"개선점\": \"...\", \"추천\": \"...\", \"점수\": 85}\n"
                    "```"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # 결과 파싱
    content = response.choices[0].message.content

    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {
            "잘한점": "결과를 파싱하는 데 문제가 발생했습니다.",
            "개선점": "형식이 올바르지 않아 개선점을 가져올 수 없습니다.",
            "추천": "다음 투구를 위한 추천을 확인할 수 없습니다.",
            "점수": 50
        }

    return result
