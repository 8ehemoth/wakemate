#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, logging, gi, hailo
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from .config import (
    EYES_T_AND, EYES_T_OR,
    CO2_T_AND, CO2_T_OR,
    STALE_SEC
)
from .state import DrowsyState
from .buzzer import buzzer_player

# ─── PadProbe ─────────────────────────────────────────────────────
def app_callback(pad, info, user: DrowsyState):
    buf = info.get_buffer()
    if buf is None:
        return Gst.PadProbeReturn.OK

    # 눈 감김 여부 추출
    eyes_closed = any(
        det.get_label() == "close" and det.get_confidence() > 0.5
        for det in hailo.get_roi_from_buffer(buf).get_objects_typed(hailo.HAILO_DETECTION)
    )

    now = time.time()

    # 상태 업데이트
    if eyes_closed:
        if user.shut_start is None:
            user.shut_start = now
    else:
        user.shut_start = None

    # 눈 감김 지속시간 계산
    eyes_dur = (now - user.shut_start) if user.shut_start is not None else 0.0
    eyes_ge_and = eyes_dur >= EYES_T_AND   # ≥ 2s
    eyes_ge_or  = eyes_dur >= EYES_T_OR    # ≥ 5s

    # 최신 CO₂ 값 읽기
    with user._lock:
        co2_ppm = user.co2_ppm
        co2_ts  = user.co2_ts

    co2_fresh  = (co2_ppm is not None) and ((now - co2_ts) <= STALE_SEC)
    co2_ge_and = co2_fresh and (co2_ppm >= CO2_T_AND)   # ≥ 2000ppm
    co2_ge_or  = co2_fresh and (co2_ppm >= CO2_T_OR)    # ≥ 2500ppm

    # ── 최종 알람 조건 ────────────────────────────────────────────
    # (A) (eyes ≥ 2s) AND (CO2 ≥ 2000)   OR
    # (B) (eyes ≥ 5s)                     OR
    # (C) (CO2 ≥ 2500)
    alarm = (eyes_ge_and and co2_ge_and) or eyes_ge_or or co2_ge_or

    # 로그용 이유 문자열
    reason_parts = []
    if eyes_ge_and and co2_ge_and:
        reason_parts.append(f"AND(eyes≥{EYES_T_AND:.1f}s & CO₂≥{CO2_T_AND})")
    if eyes_ge_or:
        reason_parts.append(f"OR(eyes≥{EYES_T_OR:.1f}s)")
    if co2_ge_or:
        reason_parts.append(f"OR(CO₂≥{CO2_T_OR})")
    reason = " | ".join(reason_parts) if reason_parts else "조건 불충족"

    if alarm and not user.buzzer_on:
        buzzer_player.set_active(True); user.buzzer_on = True
        logging.info("부저 ON(패턴) | %s | CO₂=%s", reason, co2_ppm)
    elif (not alarm) and user.buzzer_on:
        buzzer_player.set_active(False); user.buzzer_on = False
        logging.info("부저 OFF | %s | CO₂=%s", reason, co2_ppm)

    return Gst.PadProbeReturn.OK
