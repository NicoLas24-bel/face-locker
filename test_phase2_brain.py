# Archivo: test_phase2_brain.py
import cv2
from src.domain.face_recognizer import FaceRecognizer

def main():
    print("Iniciando carga de modelos de IA... (esto puede tardar unos segundos la primera vez)")
    recognizer = FaceRecognizer()
    
    # IMPORTANTE: Cambia el "2" por el índice de tu cámara USB que vimos antes
    camera_index = 2 
    cap = cv2.VideoCapture(camera_index)
    
    print("\nModelos listos. ¡Sonríe a la cámara!")
    print("Presiona la barra espaciadora ('SPACE') para capturar tu rostro.")
    print("Presiona 'ESC' para salir.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        
        # Clonar el frame para dibujar encima sin afectar la imagen que va a la IA
        display_frame = frame.copy()
        cv2.putText(display_frame, "Presiona ESPACIO para extraer vector", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.imshow('Prueba Fase 2 - Cerebro IA', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Si presiona ESPACIO (código 32)
        if key == 32:
            print("\nProcesando imagen con MTCNN y FaceNet...")
            vector = recognizer.get_embedding(frame)
            
            if vector is not None:
                print(f"¡Éxito! Cara detectada.")
                print(f"Dimensión del vector: {vector.shape} (debería ser 512)")
                print(f"Primeros 5 números de tu firma facial: {vector[:5]}")
            else:
                print("No se detectó ninguna cara en la imagen. Intenta de nuevo.")
                
        # Si presiona ESC (código 27)
        elif key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()