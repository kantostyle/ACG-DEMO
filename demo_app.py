import streamlit as st
import pandas as pd
import time
import datetime

st.set_page_config(layout="centered")

# -----------------------------
# 초기 상태
# -----------------------------
if "scenario" not in st.session_state:

    st.session_state.scenario = None
    st.session_state.step = 0
   
    #전체 그래프
    st.session_state.hr = []
    st.session_state.ox = []

    # 회복 그래프
    st.session_state.recovery_hr = []
    st.session_state.recovery_ox = []

   # 로그
    st.session_state.log = []

    #상태 플래그
    st.session_state.flags = {
        "fall": False,
        "danger": False,
        "call_retry": False,
        "119": False,
        "rescue": False
    }

    st.session_state.finished = False
    st.session_state.recovery_triggered = False
    st.session_state.unresponsive_count = 0

# -----------------------------
# trigger
# -----------------------------
def trigger(action):
    st.session_state["_action"] = action

    st.session_state.scenario = None
    st.session_state.step = 0

    st.session_state.hr = []
    st.session_state.ox = []

    st.session_state.recovery_hr = []
    st.session_state.recovery_ox = []

    st.session_state.log = []

    st.session_state.flags = {
        "fall": False,
        "danger": False,
        "call_retry": False,
        "119": False,
        "rescue": False
    }

    st.session_state.finished = False
    st.session_state.recovery_triggered = False
    st.session_state.unresponsive_count = 0

    st.rerun()
    st.stop()

# -----------------------------
# reset
# -----------------------------
def reset_demo():

    st.session_state.scenario = None
    st.session_state.step = 0

    st.session_state.hr = []
    st.session_state.ox = []

    st.session_state.recovery_hr = []
    st.session_state.recovery_ox = []

    st.session_state.log = []

    st.session_state.flags = {
        "fall": False,
        "danger": False,
        "call_retry": False,
        "119": False,
        "rescue": False
    }

    st.session_state.finished = False
    st.session_state.recovery_triggered = False
    st.session_state.unresponsive_count = 0

    st.rerun()
    st.stop()

# -----------------------------
# action 처리
# -----------------------------
if "_action" in st.session_state:

    st.session_state.scenario = st.session_state["_action"]

    del st.session_state["_action"]

    st.rerun()
    st.stop()

# -----------------------------
# 상태 아이콘
# -----------------------------
status_icon = {
    "NORMAL": "✅",
    "ACTIVE": "🏃",
    "FALL": "🧍",
    "DANGER": "⚠️",
    "EMERGENCY": "🚨",
    "RECOVERY": "🩺",
    "NOT_WORN": "❌",
    "END": "🏁"
}

# -----------------------------
# 위험 점수
# -----------------------------
def calculate_risk(status, hr, ox):
    risk = 0

    if hr and (hr > 120 or hr < 50):
        risk += 30

    if ox:
        if ox < 90:
            risk += 40
        elif ox < 94:
            risk += 20

    if status == "FALL": risk += 40
    if status == "DANGER": risk += 70
    if status == "EMERGENCY": risk += 90

    return min(risk, 100)

# -----------------------------
# 로그
# -----------------------------
def log(msg, status, hr=None, ox=None, risk=None):

    now = datetime.datetime.now().strftime("%H:%M:%S")

    text = f"{now} | {status} | {msg}"

    if hr: text += f" | ❤️ {hr}"
    if ox: text += f" | 🩸 {ox}"
    if risk: text += f" | ⚠️ {risk}"

    if st.session_state.log and st.session_state.log[-1] == text:
        return

    st.session_state.log.append(text)

# -----------------------------
# 시나리오
# -----------------------------
def get_state(s, step):

    # -------------------------
    # 🏠 일상
    # -------------------------
    if s == "daily":
        if step < 3: return "NORMAL", 75, 98
        elif step < 5: return "FALL", 60, 94
        elif step < 8: return "DANGER", 120, 92
        elif step < 12: return "EMERGENCY", 130, 88
        # RECOVERY
        elif step == 12: return "RECOVERY", 120, 90
        elif step == 13: return "RECOVERY", 110, 92
        elif step == 14: return "RECOVERY", 100, 94
        elif step == 15: return "RECOVERY", 90, 96
        else: return "END", 80, 98

    # -------------------------
    # 🚶 보행
    # -------------------------
    if s == "walking":
        if step < 4: return "NORMAL", 80, 97
        elif step < 6: return "FALL", 55, 94
        elif step < 9: return "DANGER", 60, 93
        elif step < 13: return "EMERGENCY", 50, 90
        # RECOVERY
        elif step == 13: return "RECOVERY", 58, 91
        elif step == 14: return "RECOVERY", 63, 92
        elif step == 15: return "RECOVERY", 68, 94
        elif step == 16: return "RECOVERY", 73, 96
        else: return "END", 80, 98

    # -------------------------
    # 🏃 운동
    # -------------------------
    if s == "exercise":
        if step < 2: return "NORMAL", 90, 98
        elif step < 5: return "ACTIVE", 140, 98
        elif step < 7: return "FALL", 60, 94
        elif step < 10: return "DANGER", 120, 92
        elif step < 14: return "EMERGENCY", 130, 88
        # RECOVERY
        elif step == 14: return "RECOVERY", 125, 89
        elif step == 15: return "RECOVERY", 115, 91
        elif step == 16: return "RECOVERY", 105, 93
        elif step == 17: return "RECOVERY", 95, 95
        elif step == 18: return "RECOVERY", 85, 97
        else: return "END", 80, 98

    # -------------------------
    # 🧍 정적 이상
    # -------------------------
    if s == "silent":
        if step < 4: return "NORMAL", 70, 98
        elif step < 7: return "DANGER", 45, 90
        elif step < 12: return "EMERGENCY", 40, 85
        # RECOVERY
        elif step == 12: return "RECOVERY", 45, 87
        elif step == 13: return "RECOVERY", 52, 89
        elif step == 14: return "RECOVERY", 60, 92
        elif step == 15: return "RECOVERY", 66, 95
        else: return "END", 75, 98

    # -------------------------
    # ❌ 미착용
    # -------------------------
    if s == "not_worn":
        return "NOT_WORN", None, None

    return "NORMAL", 70, 98

# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:

    st.title("🚨 대응 흐름")

    f = st.session_state.flags

    if f["fall"]: st.warning("🧍 낙상 감지")

    if f["danger"]:
        st.warning("📩 보호자 문자 전송")
        st.error("📞 보호자 전화 연결")

    if f["call_retry"]: st.warning("📞 전화 재시도")

    if f["119"]: st.success("🚑 119 신고")

    if f["rescue"]: st.info("🚑 구조대 출발")

    st.divider()
    st.subheader("📋 이벤트 로그")

    for l in st.session_state.log[-10:]:
        st.write(l)

# -----------------------------
# 버튼
# -----------------------------
c0, c1, c2, c3, c4, c5 = st.columns(6)

# 초기화 버튼 (맨 앞)
if c0.button("🔄 초기화"):
    reset_demo()

# 시나리오 버튼
if c1.button("🏠 일상"):
    trigger("daily")

if c2.button("🚶 보행"):
    trigger("walking")

if c3.button("🏃 운동"):
    trigger("exercise")

if c4.button("🧍 정적"):
    trigger("silent")

if c5.button("❌ 미착용"):
    trigger("not_worn")

# -----------------------------
# 실행
# -----------------------------
if st.session_state.scenario:

    status, hr, ox = get_state(
        st.session_state.scenario,
        st.session_state.step
    )

    icon = status_icon.get(status, "❓")

    st.markdown(f"## {icon} 상태: {status}")

    # -------------------------
    # 미착용
    # -------------------------
    if status == "NOT_WORN":

        st.warning("❌ 기기 미착용 상태")

        log("❌ 미착용 감지", status)
        st.stop()
    # -------------------------
    # 위험 점수
    # -------------------------
    risk = calculate_risk(status, hr, ox)

    st.metric("⚠️ 위험 점수", risk)
    st.progress(risk / 100)

    # 실시간 바이탈 표시
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "❤️ 심박수 (HR)",
            f"{hr} bpm"
        )

    with col2:
        st.metric(
            "🩸 산소포화도 (SpO2)",
            f"{ox}%"
        )

    # UX
    if status in ["DANGER", "EMERGENCY"]:
        st.warning("🔊 괜찮으신가요?")

    f = st.session_state.flags

    if status == "FALL" and not f["fall"]:
        log("🧍 낙상 감지", status, hr, ox, risk)
        f["fall"] = True

    if status == "DANGER" and not f["danger"]:
        log("📩 보호자 문자 전송", status, hr, ox, risk)
        log("📞 보호자 전화 연결", status, hr, ox, risk)
        f["danger"] = True

    if status == "EMERGENCY":

        if not f["call_retry"]:
            log("📞 전화 재시도", status, hr, ox, risk)
            f["call_retry"] = True

        if not f["119"]:
            log("🚑 119 신고", status, hr, ox, risk)
            f["119"] = True

        if not f["rescue"]:
            time.sleep(2)
            log("🚑 구조대 출발", status, hr, ox, risk)
            f["rescue"] = True

    if status == "RECOVERY" and not st.session_state.recovery_triggered:

        st.session_state.log = []
        st.session_state.flags = {
            "fall": False,
            "danger": False,
            "call_retry": False,
            "119": False,
            "rescue": False
        }

        st.session_state.recovery_triggered = True

    # -------------------------
    # 전체 그래프 저장
    # -------------------------
    if hr is not None:
        st.session_state.hr.append(hr)

    if ox is not None:
        st.session_state.ox.append(ox)

    # -------------------------
    # 회복 그래프 저장
    # -------------------------
    if status == "RECOVERY":

        st.session_state.recovery_hr.append(hr)
        st.session_state.recovery_ox.append(ox)

    # -------------------------
    # 전체 그래프
    # -------------------------
    st.subheader("📊 생체 데이터 흐름")

    st.line_chart(pd.DataFrame({
        "HR": st.session_state.hr,
        "SpO2": st.session_state.ox
    }))

    # -------------------------
    # 회복 그래프
    # -------------------------
    if len(st.session_state.recovery_hr) > 0:

        st.subheader("📈 회복 곡선")

        st.line_chart(pd.DataFrame({
            "Recovery HR": st.session_state.recovery_hr,
            "Recovery SpO2": st.session_state.recovery_ox
        }))

    # -------------------------
    # 위치
    # -------------------------
    st.subheader("📍 현재 위치")

    st.map(pd.DataFrame({
        "lat": [37.4828],
        "lon": [127.0360]
    }))

    # -------------------------
    # 종료
    # -------------------------
    if status == "END":

        st.success("🏁 상황 종료")

    else:

        st.session_state.step += 1

        time.sleep(1)

        st.rerun()

else:

    st.info("👆 시나리오를 선택하세요")