#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

# ─── 설정 ─────────────────────────────────────────────────────────
# 눈 감김 임계(초)
EYES_T_AND    = 2.0       # AND 조건용
EYES_T_OR     = 5.0       # OR 조건용

# CO2 임계(ppm)
CO2_T_AND     = 2000      # AND 조건용
CO2_T_OR      = 2500      # OR 조건용

CO2_POLL_SEC  = 5.0       # CO₂ 폴링 간격
STALE_SEC     = 12.0      # CO₂ 측정값 유효 기간
SERIAL_DEVICE = "/dev/serial0"
SERIAL_BAUD   = 9600
SERIAL_TO     = 2.5       # UART read timeout

# ─── 로깅 ─────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# ─── 부저 설정 (gpiozero) ────────────────────────────────────────
BUZZER_PIN = 18
BUZZ_FREQ  = 2000   # 초기 주파수(패턴 내에서 변경)
DUTY_CYCLE = 50     # %
