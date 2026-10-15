# Archivo: src/services/monitoring_service.py
import cv2
import numpy as np
import time
from src.domain.face_recognizer import FaceRecognizer
from src.infrastructure.storage import LocalStorage
from src.infrastructure.lock_manager import LockManager
from src.infrastructure.privacy_overlay import PrivacyOverlay
from src.infrastructure.input_listener import InputListener

class MonitoringService:
    def __init__(self, threshold=0.85, check_interval_seconds=0.3):
        self.storage = LocalStorage()
        self.settings = self.storage.load_settings()
        
        self.camera_index = self.settings.get("camera_index", 0)
        self.master_profile = self.storage.load_profile()
        
        if self.master_profile is None:
            raise FileNotFoundError("No se encontró perfil facial. Completa el registro primero.")
            
        self.recognizer = FaceRecognizer()
        self.lock_manager = LockManager()
        self.overlay = PrivacyOverlay()
        
        self.unauthorized_input_detected = False
        self.input_listener = InputListener(on_input_detected_callback=self._trigger_hard_lock)
        
        self.threshold = threshold
        self.check_interval = check_interval_seconds
        self.running = False  # Bandera de control para detener desde la GUI

    def _trigger_hard_lock(self):
        self.unauthorized_input_detected = True

    def stop_monitoring(self):
        """Detiene el bucle de monitoreo de forma segura."""
        self.running = False

    def start_monitoring(self):
        self.running = True
        self.unauthorized_input_detected = False
        
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        last_check_time = 0
        is_privacy_active = False

        while self.running and cap.isOpened():
            if self.unauthorized_input_detected:
                print("\n[ALERTA] Interacción física detectada. Bloqueando SO...")
                self.input_listener.stop()
                self.overlay.hide()
                cap.release()
                self.running = False
                self.lock_manager.lock()
                break

            ret, frame = cap.read()
            if not ret:
                break

            current_time = time.time()

            if current_time - last_check_time >= self.check_interval:
                last_check_time = current_time
                current_embedding = self.recognizer.get_embedding(frame)

                is_authorized = False
                if current_embedding is not None:
                    distance = np.linalg.norm(self.master_profile - current_embedding)
                    is_authorized = distance < self.threshold

                if is_authorized:
                    if is_privacy_active:
                        self.overlay.hide()
                        self.input_listener.stop()
                        is_privacy_active = False
                else:
                    if not is_privacy_active:
                        self.overlay.show()
                        self.input_listener.start()
                        is_privacy_active = True

            if is_privacy_active:
                self.overlay.update()

            time.sleep(0.01)

        cap.release()
        self.overlay.hide()
        self.input_listener.stop()
        self.running = False