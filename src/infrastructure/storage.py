# Archivo: src/infrastructure/storage.py
import numpy as np
import json
import os

class LocalStorage:
    def __init__(self, data_dir="data"):
        # Forzar la ruta absoluta desde donde se está ejecutando el script
        self.base_path = os.path.abspath(os.getcwd())
        self.data_dir = os.path.join(self.base_path, data_dir)
        
        self.profile_path = os.path.join(self.data_dir, "master_profile.npy")
        self.settings_path = os.path.join(self.data_dir, "settings.json")
        
        # Crear la carpeta data si no existe
        os.makedirs(self.data_dir, exist_ok=True)
        print(f"[Storage] Directorio de datos apuntando a: {self.data_dir}")

    def save_profile(self, embedding_array):
        """Guarda el array matemático del rostro directamente en un archivo .npy"""
        np.save(self.profile_path, embedding_array)
        print(f"[Storage] Perfil guardado en: {self.profile_path}")

    def load_profile(self):
        """Carga el vector del rostro si existe, si no, devuelve None"""
        if os.path.exists(self.profile_path):
            return np.load(self.profile_path)
        return None

    def save_settings(self, settings_dict):
        """Guarda configuraciones como el índice de la cámara en un JSON"""
        with open(self.settings_path, 'w') as f:
            json.dump(settings_dict, f, indent=4)
        print(f"[Storage] Configuración guardada en: {self.settings_path}")

    def load_settings(self):
        """Carga las configuraciones. Devuelve un diccionario vacío si no existe."""
        if os.path.exists(self.settings_path):
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        return {}