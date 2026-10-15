# Archivo: src/services/enrollment_service.py
import cv2
import numpy as np
import time
from src.domain.pose_estimator import PoseEstimator
from src.domain.face_recognizer import FaceRecognizer
from src.infrastructure.storage import LocalStorage

class EnrollmentService:
    def __init__(self, camera_index=0):
        print("[Servicio] Inicializando modelos de IA para registro...")
        self.pose_estimator = PoseEstimator()
        self.face_recognizer = FaceRecognizer()
        self.storage = LocalStorage()
        self.camera_index = camera_index

    def start_enrollment(self):
        cap = cv2.VideoCapture(self.camera_index)
        
        states = ["Frente", "Izquierda", "Derecha"]
        current_state_idx = 0
        
        collected_embeddings = []
        frames_needed_per_state = 5
        frames_collected = 0
        last_capture_time = 0  # Cooldown entre capturas (0.3 segundos)

        print("\n--- INICIANDO REGISTRO FACIAL ---")
        
        while cap.isOpened() and current_state_idx < len(states):
            ret, frame = cap.read()
            if not ret:
                break
                
            frame = cv2.flip(frame, 1)
            target_direction = states[current_state_idx]
            
            # 1. Obtener la pose actual
            pitch, yaw, direction = self.pose_estimator.get_pose(frame)
            display_frame = frame.copy()
            
            # 2. Diagnóstico visual en pantalla
            if pitch is not None:
                info_pose = f"Detectado: {direction} (Yaw: {int(yaw)} | Pitch: {int(pitch)})"
                cv2.putText(display_frame, info_pose, (20, 430), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # 3. Validar si la pose actual coincide con la solicitada
            if direction == target_direction:
                cv2.putText(display_frame, "¡POSICION CORRECTA! Extrayendo...", (20, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Cooldown de 300ms entre fotos para variar ligeramente la toma
                if time.time() - last_capture_time > 0.3:
                    embedding = self.face_recognizer.get_embedding(frame)
                    
                    if embedding is not None:
                        collected_embeddings.append(embedding)
                        frames_collected += 1
                        last_capture_time = time.time()
                        
                        # Si completó las 5 capturas de esta pose
                        if frames_collected >= frames_needed_per_state:
                            current_state_idx += 1
                            frames_collected = 0
            
            # Instrucción principal
            if current_state_idx < len(states):
                instruccion = f'Paso {current_state_idx + 1}/3: Mira a la {states[current_state_idx]}' if states[current_state_idx] != "Frente" else "Paso 1/3: Mira al Frente"
                cv2.putText(display_frame, instruccion, (20, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.putText(display_frame, f'Progreso: {frames_collected}/{frames_needed_per_state}', 
                            (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            cv2.imshow('Registro Biometrico', display_frame)
            
            if cv2.waitKey(10) & 0xFF == 27: # ESC para salir
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        # 4. Procesar y guardar el perfil final
        if len(collected_embeddings) == 15:
            master_profile = np.mean(collected_embeddings, axis=0)
            self.storage.save_profile(master_profile)
            print("\n¡Registro completado con éxito! Tu firma facial 3D ha sido guardada.")
            return True
        else:
            print("\nRegistro cancelado o incompleto.")
            return False