# Archivo: test_phase4_enroll.py
from src.services.enrollment_service import EnrollmentService
from src.infrastructure.storage import LocalStorage

def main():
    # 1. Guardar tu cámara preferida en las configuraciones para futuros usos
    storage = LocalStorage()
    indice_camara_usb = 2 
    storage.save_settings({"camera_index": indice_camara_usb, "tolerance": 0.7})
    
    # 2. Iniciar el registro dinámico
    enrollment = EnrollmentService(camera_index=indice_camara_usb)
    enrollment.start_enrollment()

if __name__ == "__main__":
    main()