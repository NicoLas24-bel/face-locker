# Archivo: src/domain/pose_estimator.py
import cv2
import mediapipe as mp
import numpy as np

class PoseEstimator:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
        
        # Coordenadas 3D genéricas de un rostro humano
        self.face_3d = np.array([
            [0.0, 0.0, 0.0],            # Punta de la nariz
            [0.0, -330.0, -65.0],       # Barbilla
            [-225.0, 170.0, -135.0],    # Esquina ojo izquierdo
            [225.0, 170.0, -135.0],     # Esquina ojo derecho
            [-150.0, -150.0, -125.0],   # Comisura boca izquierda
            [150.0, -150.0, -125.0]     # Comisura boca derecha
        ], dtype=np.float64)

    def get_pose(self, image):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)
        
        if not results.multi_face_landmarks:
            return None, None, "No detectado"

        img_h, img_w, _ = image.shape
        face_2d = []

        face_landmarks = results.multi_face_landmarks[0]
        
        for idx in [1, 152, 226, 446, 57, 287]:
            pos = face_landmarks.landmark[idx]
            x, y = int(pos.x * img_w), int(pos.y * img_h)
            face_2d.append([x, y])
            
        face_2d = np.array(face_2d, dtype=np.float64)

        focal_length = 1 * img_w
        cam_matrix = np.array([
            [focal_length, 0, img_h / 2],
            [0, focal_length, img_w / 2],
            [0, 0, 1]
        ])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)

        success, rot_vec, trans_vec = cv2.solvePnP(self.face_3d, face_2d, cam_matrix, dist_matrix)
        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        
        # RQDecomp3x3 entrega los ángulos en grados directo (rango normal aprox. -180 a 180)
        pitch = angles[0]
        yaw = angles[1]

        # Umbrales ajustados para detectar la posición de la cabeza
        direction = "Frente"
        if yaw < -10:
            direction = "Izquierda"
        elif yaw > 10:
            direction = "Derecha"

        return pitch, yaw, direction