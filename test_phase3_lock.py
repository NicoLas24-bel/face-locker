# Archivo: test_phase3_lock.py
import time
from src.infrastructure.lock_manager import LockManager

def main():
    print("Iniciando prueba del Candado del Sistema...")
    locker = LockManager()
    
    print("\n¡ATENCIÓN! La pantalla se bloqueará en 5 segundos.")
    print("Asegúrate de saber tu contraseña de usuario para volver a entrar.")
    
    for i in range(5, 0, -1):
        print(f"Bloqueando en {i}...")
        time.sleep(1)
        
    # Llamamos a la función de bloqueo
    locker.lock()
    print("Prueba finalizada. Si estás leyendo esto sin haber puesto tu contraseña, el bloqueo falló.")

if __name__ == "__main__":
    main()