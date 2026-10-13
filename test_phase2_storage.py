# Archivo: test_phase2_storage.py
import numpy as np
from src.infrastructure.storage import LocalStorage

def main():
    print("Iniciando prueba de Almacenamiento Local (Numpy + JSON)...")
    storage = LocalStorage()
    
    # 1. Probar el guardado del rostro
    vector_simulado = np.array([0.15, -0.42, 0.88, 3.14], dtype=np.float32)
    print("\n1. Guardando vector de perfil en 'data/master_profile.npy'...")
    storage.save_profile(vector_simulado)
    
    vector_recuperado = storage.load_profile()
    if vector_recuperado is not None:
        print(f"   ¡Éxito! Vector recuperado: {vector_recuperado}")
    
    # 2. Probar el guardado de configuración
    config_simulada = {"camera_index": 2, "tolerance": 0.7}
    print("\n2. Guardando configuraciones en 'data/settings.json'...")
    storage.save_settings(config_simulada)
    
    config_recuperada = storage.load_settings()
    if config_recuperada:
        print(f"   ¡Éxito! Configuración recuperada: {config_recuperada}")

if __name__ == "__main__":
    main()