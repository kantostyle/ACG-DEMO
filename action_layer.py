def trigger_action(result, flags, log):

    status = result["status"]

    if status == "FALL" and not flags["fall"]:
        log("낙상 감지")
        flags["fall"] = True

    if status == "DANGER":
        if not flags["sms"]:
            log("보호자 문자 전송")
            flags["sms"] = True

        if not flags["call"]:
            log("보호자 전화 연결")
            flags["call"] = True

    if status == "EMERGENCY":

        if not flags["call_retry"]:
            log("보호자 전화 재시도")
            flags["call_retry"] = True

        if not flags["119"]:
            log("🚑 119 신고 + 의료 리포트 전송")
            flags["119"] = True
            flags["rescue"] = True

    return flags