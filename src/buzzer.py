#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, threading
from gpiozero import PWMOutputDevice
from .config import BUZZER_PIN, BUZZ_FREQ, DUTY_CYCLE

class BuzzerPlayer:
    """알람 ON 동안 '삐빅 삐빅 삐빅' 2톤 패턴 반복 재생 (gpiozero)"""
    def __init__(self, pin=BUZZER_PIN, freq=BUZZ_FREQ, duty=DUTY_CYCLE):
        self._dev = PWMOutputDevice(pin=pin, frequency=freq, initial_value=0.0)
        self._duty = duty / 100.0
        self._active = False
        self._stop_ev = threading.Event()
        self._lock = threading.Lock()
        self._th = threading.Thread(target=self._loop, daemon=True)
        self._th.start()

    def set_active(self, on: bool):
        with self._lock:
            self._active = on
            if not on:
                self._dev.value = 0.0

    def close(self):
        self.set_active(False)
        self._stop_ev.set()
        try:
            if self._th.is_alive(): self._th.join(timeout=1.0)
        except Exception:
            pass
        self._dev.close()

    def _tone(self, freq_hz: int, dur_sec: float):
        self._dev.frequency = freq_hz
        self._dev.value = self._duty
        time.sleep(dur_sec)
        self._dev.value = 0.0

    # 내부: 비동기 패턴 루프
    def _loop(self):
        HI = 2200; LO = 1300
        T_HI = 0.12; T_LO = 0.14
        GAP = 0.12
        PHRASE_GAP = 0.28

        while not self._stop_ev.is_set():
            if not self._active:
                time.sleep(0.03)
                continue

            for _ in range(3):  # '삐빅' 3회
                if not self._active: break
                self._tone(HI, T_HI)
                time.sleep(GAP)
                if not self._active: break
                self._tone(LO, T_LO)
                time.sleep(GAP)

            time.sleep(PHRASE_GAP)

# 전역 인스턴스 (원본과 동일 동작)
buzzer_player = BuzzerPlayer(pin=BUZZER_PIN, freq=BUZZ_FREQ, duty=DUTY_CYCLE)
