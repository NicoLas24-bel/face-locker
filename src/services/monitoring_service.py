# Archivo: src/services/monitoring_service.py
import cv2
import numpy as np
import time
from src.domain.face_recognizer import FaceRecognizer
from src.infrastructure.storage import LocalStorage
from src.infrastructure.lock_manager import LockManager

class MonitoringService:
    def __init__(self, threshold=0.85, max_unrecognized_seconds=3):
        print("[Monitoreo] Cargando servicio de vigilancia...")
        self.storage = LocalStorage()
        self.settings = self.storage.load_settings()
        
        self.camera_index = self.settings.get("camera_index", 0)
        self.master_profile = self.storage.load_profile()
        
        if self.master_profile is None:
            raise FileNotFoundError("No se encontró 'master_profile.npy'. Completa el registro (Fase 4) primero.")
            
        self.recognizer = FaceRecognizer()
        self.lock_manager = LockManager()
        self.threshold = threshold
        self.max_unrecognized_seconds = max_unrecognized_seconds

    def start_monitoring(self):
        cap = cv2.VideoCapture(self.camera_index)
        print(f"\n--- MONITOREO ACTIVO (Cámara {self.camera_index}) ---")
        print("El sistema vigilará tu rostro. Presiona 'ESC' en la ventana para salir.")

        unrecognized_start_time = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error al leer la cámara.")
                break

            frame = cv2.flip(frame, 1)
            display_frame = frame.copy()

            # Extraer el vector del rostro actual
            current_embedding = self.recognizer.get_embedding(frame)

            if current_embedding is not None:
                # Calcular la distancia euclidiana entre el rostro actual y tu perfil guardado
                distance = np.linalg.norm(self.master_profile - current_embedding)
                is_authorized = distance < self.threshold

                if is_authorized:
                    unrecognized_start_time = None
                    color = (0, 255, 0) # Verde
                    status = f"AUTORIZADO (Distancia: {distance:.2f})"
                else:
                    color = (0, 0, 255) # Rojo
                    status = f"DESCONOCIDO (Distancia: {distance:.2f})"
                    if unrecognized_start_time is None:
                        unrecognized_start_time = time.time()
            else:
                color = (0, 0, 255)
                status = "NO SE DETECTA ROSTRO"
                if unrecognized_start_time is None:
                    unrecognized_start_time = time.time()

            # Lógica del temporizador de bloqueo
            if unrecognized_start_time is not None:
                elapsed = time.time() - unrecognized_start_time
                time_left = max(0.0, self.max_unrecognized_seconds - elapsed)
                
                cv2.putText(display_frame, f"ALERTA: Bloqueando en {time_left:.1f}s", (20, 90), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if elapsed >= self.max_unrecognized_seconds:
                    print("\n[ALERTA] Usuario no reconocido o ausente. Ejecutando bloqueo...")
                    cv2.destroyAllWindows()
                    cap.release()
                    self.lock_manager.lock()
                    break

            cv2.putText(display_frame, status, (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.imshow('Vigilancia de Seguridad', display_frame)

            if cv2.waitKey(100) & 0xFF == 27: # ESC para salir voluntariamente
                break

        cap.release()
        cv2.destroyAllWindows()