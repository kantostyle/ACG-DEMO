import numpy as np
from collections import deque
import time

# -----------------------------
# 🔐 Zero Trust 보안
# -----------------------------
def encrypt_data(data):
    return f"ENC({data})"

def secure_decrypt(data, state):
    if state.get("status") == "EMERGENCY":
        return data.replace("ENC(", "").replace(")", "")
    return "LOCKED"

# -----------------------------
# 🔋 디바이스 상태 체크
# -----------------------------
def check_device_health(sensor, state):
    battery = sensor.get("battery", 100)
    network = sensor.get("network", True)

    if battery < 15:
        return "LOW_BATTERY"

    if not network:
        state["network_lost"] = state.get("network_lost", time.time())
        if time.time() - state["network_lost"] > 60:
            return "NETWORK_LOST"

    return None

# -----------------------------
# 🧍 낙상 (적응형)
# -----------------------------
def detect_fall(acc, state):
    hist = state.setdefault("acc_hist", deque(maxlen=30))
    hist.append(acc)
    avg = np.mean(hist)
    return acc > avg * 2

# -----------------------------
# ❤️ HR 변화량
# -----------------------------
def detect_hr_change(hr, state):
    hist = state.setdefault("hr_hist", deque(maxlen=20))
    hist.append(hr)

    if len(hist) < 10:
        return 0

    baseline = np.mean(list(hist)[:-1])
    return abs(hr - baseline)

# -----------------------------
# 🩸 SpO2 기울기 (30초)
# -----------------------------
def detect_spo2_drop(state):
    hist = state.setdefault("ox_hist", deque(maxlen=30))

    if len(hist) < 15:
        return None

    diff = hist[-1] - hist[0]

    if diff < -6:
        return "rapid"
    elif diff < -3:
        return "slow"

    return None

# -----------------------------
# 🔊 무반응 감지
# -----------------------------
def detect_unresponsive(acc, state):

    if "voice_time" not in state:
        return False

    if time.time() - state["voice_time"] < 10:
        return False

    acc_hist = state.get("acc_hist", [])

    if len(acc_hist) < 5:
        return False

    movement = max(acc_hist[-5:]) - min(acc_hist[-5:])

    return movement < 0.1

# -----------------------------
# 🧠 상태 안정화
# -----------------------------
def stabilize_status(new_status, state):
    hist = state.setdefault("status_hist", deque(maxlen=5))
    hist.append(new_status)
    return max(set(hist), key=hist.count)

# -----------------------------
# 🔁 히스테리시스
# -----------------------------
def apply_hysteresis(prev, curr):
    if prev == "EMERGENCY" and curr == "NORMAL":
        return "DANGER"
    if prev == "DANGER" and curr == "NORMAL":
        return "DANGER"
    return curr

# -----------------------------
# 📊 히스토리 요약
# -----------------------------
def summarize_history(state):
    hist = state.get("hist", [])

    if len(hist) < 5:
        return "데이터 부족"

    start = hist[0]
    end = hist[-1]

    return f"{start['hr']}→{end['hr']} / {start['ox']}→{end['ox']}"

# -----------------------------
# 📄 의료 리포트
# -----------------------------
def generate_report(state):

    disease = state.get("disease", "정보 없음")
    meds = state.get("meds", "정보 없음")

    summary = summarize_history(state)

    return f"""
[AI 응급 리포트]
- 상태: {state['status']}
- 활동: {state.get('activity')}
- 지속: {state.get('duration')}초
- 히스토리: {summary}
- 기저질환: {disease}
- 복용약: {meds}
"""

# -----------------------------
# 🩺 회복 분석
# -----------------------------
def analyze_recovery(state):

    hist = state.get("hist", [])

    if len(hist) < 10:
        return None

    last = hist[-1]

    if 60 < last["hr"] < 100 and last["ox"] > 95:
        return "회복 중"

    return None

# -----------------------------
# 🚀 메인 엔진
# -----------------------------
def run_engine(sensor, state):

    hr = sensor.get("hr")
    ox = sensor.get("oxygen")
    acc = sensor.get("acc", 1.0)
    activity = sensor.get("activity", "REST")

    state.setdefault("hist", []).append({"hr": hr, "ox": ox})
    state["activity"] = activity

    risk = 0
    status = "NORMAL"

    # 🔋 인프라 체크
    infra = check_device_health(sensor, state)
    if infra:
        return {"status": "DEVICE_ALERT", "risk": 0, "infra": infra}

    # 낙상
    if detect_fall(acc, state):
        risk += 40
        status = "FALL"

    # HR 변화
    if detect_hr_change(hr, state) > 40:
        risk += 30

    # SpO2
    trend = detect_spo2_drop(state)

    if ox < 90:
        risk += 50
    elif trend == "rapid":
        risk += 40
    elif trend == "slow":
        risk += 20

    # 활동 필터
    if activity == "ACTIVE" and hr > 120:
        risk -= 20

    # 상태 결정
    if risk >= 80:
        status = "EMERGENCY"
    elif risk >= 50:
        status = "DANGER"

    # 안정화 + 히스테리시스
    prev = state.get("prev_status", "NORMAL")
    status = stabilize_status(status, state)
    status = apply_hysteresis(prev, status)

    state["prev_status"] = status
    state["status"] = status

    # 지속시간
    if status in ["DANGER", "EMERGENCY"]:
        state["duration"] = state.get("duration", 0) + 1
    else:
        state["duration"] = 0

    # 음성 안내 트리거
    if status == "EMERGENCY" and "voice_time" not in state:
        state["voice_time"] = time.time()

    # 무반응
    unresponsive = detect_unresponsive(acc, state)

    report = generate_report(state) if status == "EMERGENCY" else None
    recovery = analyze_recovery(state)

    return {
        "status": status,
        "risk": min(risk, 100),
        "report": report,
        "recovery": recovery,
        "unresponsive": unresponsive
    }