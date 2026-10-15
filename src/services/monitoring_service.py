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
        print("[Monitoreo] Cargando servicio con Telón de Privacidad y Bloqueo por Entrada...")
        self.storage = LocalStorage()
        self.settings = self.storage.load_settings()
        
        self.camera_index = self.settings.get("camera_index", 0)
        self.master_profile = self.storage.load_profile()
        
        if self.master_profile is None:
            raise FileNotFoundError("No se encontró perfil facial. Ejecuta el registro primero.")
            
        self.recognizer = FaceRecognizer()
        self.lock_manager = LockManager()
        self.overlay = PrivacyOverlay()
        
        # Bandera para saber si un intruso tocó los periféricos
        self.unauthorized_input_detected = False
        
        # Iniciar escuchador de teclado/mouse
        self.input_listener = InputListener(on_input_detected_callback=self._trigger_hard_lock)
        
        self.threshold = threshold
        self.check_interval = check_interval_seconds

    def _trigger_hard_lock(self):
        """Se activa si alguien toca el mouse/teclado en modo privacidad."""
        self.unauthorized_input_detected = True

    def start_monitoring(self):
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        print("\n--- MONITOREO INTELIGENTE ACTIVO ---")
        last_check_time = 0
        is_privacy_active = False

        while cap.isOpened():
            # 1. Si alguien tocó el mouse/teclado mientras no estabas, BLOQUEO DURO INMEDIATO
            if self.unauthorized_input_detected:
                print("\n[ALERTA DE SEGURIDAD] ¡Interacción física detectada sin autorización! Bloqueando SO...")
                self.input_listener.stop()
                self.overlay.hide()
                cap.release()
                self.lock_manager.lock()
                break

            ret, frame = cap.read()
            if not ret:
                break

            current_time = time.time()

            # 2. Análisis de rostro cada 300ms
            if current_time - last_check_time >= self.check_interval:
                last_check_time = current_time
                current_embedding = self.recognizer.get_embedding(frame)

                is_authorized = False
                if current_embedding is not None:
                    distance = np.linalg.norm(self.master_profile - current_embedding)
                    is_authorized = distance < self.threshold

                # --- MÁQUINA DE ESTADOS ---
                if is_authorized:
                    # SI ERES TÚ: Quita el telón de privacidad si estaba puesto
                    if is_privacy_active:
                        print("[Seguridad] Rostro verificado. Desactivando modo privacidad...")
                        self.overlay.hide()
                        self.input_listener.stop()
                        is_privacy_active = False
                else:
                    # SI NO ERES TÚ O TE ALEJASTE: Muestra el telón de privacidad
                    if not is_privacy_active:
                        print("[Seguridad] Rostro ausente. Activando telón de privacidad...")
                        self.overlay.show()
                        self.input_listener.start()
                        is_privacy_active = True

            # Actualizar ventana de Tkinter si está activa
            if is_privacy_active:
                self.overlay.update()

            time.sleep(0.01)

        cap.release()
        self.overlay.hide()
        self.input_listener.stop()