#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
from hailo_apps_infra.hailo_rpi_common import app_callback_class

# ─── 상태 ─────────────────────────────────────────────────────────
class DrowsyState(app_callback_class):
    def __init__(self):
        super().__init__()
        self.shut_start = None
        self.buzzer_on  = False
        # CO2 (단순 임계 비교 + 신선도 체크)
        self.co2_ppm    = None
        self.co2_ts     = 0.0

        self._lock      = threading.Lock()
        self._stop_ev   = threading.Event()

    def stop(self): self._stop_ev.set()
    def stopped(self): return self._stop_ev.is_set()
