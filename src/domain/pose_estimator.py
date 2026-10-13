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
            [0.0, 0.0, 0.0],            
            [0.0, -330.0, -65.0],       
            [-225.0, 170.0, -135.0],    
            [225.0, 170.0, -135.0],     
            [-150.0, -150.0, -125.0],   
            [150.0, -150.0, -125.0]     
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
        
        pitch = angles[0] * 360
        yaw = angles[1] * 360

        direction = "Frente"
        if yaw < -12:
            direction = "Izquierda"
        elif yaw > 12:
            direction = "Derecha"
        elif pitch < -10:
            direction = "Abajo"
        elif pitch > 15:
            direction = "Arriba"

        return pitch, yaw, direction