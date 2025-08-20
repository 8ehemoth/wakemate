#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading, logging, sys
from hailo_apps_infra.detection_pipeline_simple import GStreamerDetectionApp
from .state import DrowsyState
from .co2_sensor import co2_poll_loop
from .callbacks import app_callback
from .buzzer import buzzer_player  # 종료시 close()
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels-json", default="/home/pi/hailo-rpi5-examples/resources/eyes-labels.json")
    parser.add_argument("--hef-path", default="/usr/share/hailo-models/eyes.hef")
    parser.add_argument("--input", default="libcamerasrc")
    return parser.parse_args()

# (추가) 커맨드라인 인자가 하나도 없을 때만 기본 인자 주입
if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv += [
            "--labels-json", "/home/pi/hailo-rpi5-examples/resources/eyes-labels.json",
            "--hef-path", "/usr/share/hailo-models/eyes.hef",
            "--input", "libcamerasrc",
        ]

    user = DrowsyState()
    th = None
    try:
        th = threading.Thread(target=co2_poll_loop, args=(user,), daemon=True)
        th.start()

        app = GStreamerDetectionApp(app_callback, user)
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            user.stop()
            if th and th.is_alive(): th.join(timeout=2.0)
        except Exception:
            pass
        try:
            buzzer_player.close()
        finally:
            logging.info("정상 종료")
