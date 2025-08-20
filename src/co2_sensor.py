#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time, logging, serial
from .config import CO2_POLL_SEC, SERIAL_DEVICE, SERIAL_BAUD, SERIAL_TO
from .state import DrowsyState

# ─── CO₂ 프로토콜 ─────────────────────────────────────────────────
_READ_CMD = b"\xff\x01\x86\x00\x00\x00\x00\x00\x79"

def _rx_checksum_ok(b: bytes) -> bool:
    if len(b) != 9: return False
    return b[8] == ((0xFF - (sum(b[1:8]) % 256) + 1) & 0xFF)

def _read_co2_once(ser: serial.Serial) -> int | None:
    try:
        ser.reset_input_buffer()
        ser.write(_READ_CMD)
        r = ser.read(9)
        if len(r)==9 and r[0]==0xFF and r[1]==0x86 and _rx_checksum_ok(r):
            return r[2]*256 + r[3]
        return None
    except Exception:
        return None

# ─── CO₂ 폴링(5초마다 출력) ───────────────────────────────────────
def co2_poll_loop(user: DrowsyState):
    ser = None
    try:
        while not user.stopped():
            if ser is None:
                try:
                    ser = serial.Serial(SERIAL_DEVICE, baudrate=SERIAL_BAUD, timeout=SERIAL_TO)
                    logging.info("CO₂ UART open: %s @ %d", SERIAL_DEVICE, SERIAL_BAUD)
                except Exception as e:
                    logging.warning("CO₂ UART open 실패: %s", e)
                    time.sleep(1.0)
                    continue

            ppm = _read_co2_once(ser)
            now = time.time()

            with user._lock:
                if ppm is not None:
                    user.co2_ppm = ppm
                    user.co2_ts  = now

            # 5초마다 CO₂ 로그
            if ppm is not None:
                logging.info("CO₂=%d ppm", ppm)

            time.sleep(CO2_POLL_SEC)
    finally:
        try:
            if ser:
                ser.close()
        except Exception:
            pass
        logging.info("CO₂ 폴링 스레드 종료")
