# Archivo: test_phase1.py
import cv2
from src.domain.pose_estimator import PoseEstimator

def find_available_cameras(max_tested=5):
    """
    Escanea los índices de video del sistema y devuelve una lista 
    con los índices de las cámaras que están enviando frames válidos.
    """
    print("Escaneando cámaras disponibles... (esto puede tomar unos segundos)")
    available_cameras = []
    
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Intentar leer un frame para confirmar que la cámara funciona
            ret, frame = cap.read()
            if ret and frame is not None:
                available_cameras.append(i)
        cap.release()
        
    return available_cameras

def main():
    cameras = find_available_cameras()
    
    if not cameras:
        print("Error: No se detectó ninguna cámara funcional.")
        return

    print("\n--- Cámaras detectadas ---")
    for cam_idx in cameras:
        print(f"Índice de cámara: {cam_idx}")
        
    # Si hay más de una, preguntamos al usuario. Si solo hay una, la tomamos directo.
    if len(cameras) > 1:
        while True:
            try:
                selected_idx = int(input("\nEscribe el índice de la cámara USB que deseas usar: "))
                if selected_idx in cameras:
                    break
                print("Por favor, elige un índice válido de la lista.")
            except ValueError:
                print("Entrada inválida. Ingresa un número.")
    else:
        selected_idx = cameras[0]
        print(f"\nUsando automáticamente la única cámara detectada (Índice {selected_idx})")

    print(f"\nIniciando cámara {selected_idx}... Presiona 'ESC' para salir.")
    cap = cv2.VideoCapture(selected_idx)
    estimator = PoseEstimator()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Se perdió la conexión con la cámara.")
            break
            
        frame = cv2.flip(frame, 1)

        pitch, yaw, direction = estimator.get_pose(frame)

        if pitch is not None and yaw is not None:
            cv2.putText(frame, f'Mirando a: {direction}', (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Yaw: {int(yaw)} | Pitch: {int(pitch)}', (20, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        else:
            cv2.putText(frame, 'Buscando rostro...', (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Prueba Fase 1 - Pose', frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()