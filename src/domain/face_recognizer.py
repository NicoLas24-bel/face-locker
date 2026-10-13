# Archivo: src/domain/face_recognizer.py
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
import cv2
from PIL import Image

class FaceRecognizer:
    def __init__(self):
        # Detectar si tienes tarjeta de video (GPU) o usar el procesador (CPU)
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        print(f"[IA] Cargando modelos en: {self.device}")

        # MTCNN: Para recortar la cara
        # keep_all=False porque solo queremos la cara principal
        self.mtcnn = MTCNN(keep_all=False, device=self.device)

        # FaceNet: Para generar el vector (embedding)
        # pretrained='vggface2' es el modelo pre-entrenado con millones de caras
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    def get_embedding(self, cv2_image):
        """
        Recibe un frame de OpenCV (cámara), recorta la cara y devuelve el vector.
        Si no hay cara, devuelve None.
        """
        # Convertir la imagen de BGR (OpenCV) a RGB (PIL) para PyTorch
        img_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        # 1. MTCNN recorta la cara y la estandariza
        face_tensor = self.mtcnn(img_pil)

        if face_tensor is None:
            return None # No detectó ninguna cara en la imagen

        # 2. PyTorch requiere que los tensores tengan una dimensión "batch" (lote)
        # Transformamos la forma de [3, 160, 160] a [1, 3, 160, 160]
        face_tensor = face_tensor.unsqueeze(0).to(self.device)

        # 3. FaceNet genera el vector matemático de 512 dimensiones
        with torch.no_grad(): # no_grad() ahorra memoria RAM porque no estamos entrenando
            embedding = self.resnet(face_tensor)

        # Convertimos el tensor de PyTorch a un array de Numpy para guardarlo fácil
        embedding_array = embedding.cpu().numpy()[0]
        
        return embedding_array