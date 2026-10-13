# Archivo: src/infrastructure/lock_manager.py
import subprocess
import platform

class LockManager:
    def __init__(self):
        self.os_type = platform.system()
        print(f"[LockManager] Sistema operativo detectado: {self.os_type}")

    def lock(self):
        """Bloquea la sesión del sistema operativo."""
        print("[LockManager] ¡Rostro no detectado/No autorizado! Bloqueando sistema...")
        
        try:
            if self.os_type == "Linux":
                # Lista de comandos de bloqueo para diferentes entornos (GNOME, KDE, XFCE, genéricos)
                comandos_linux = [
                    ['xdg-screensaver', 'lock'],
                    ['gnome-screensaver-command', '-l'],
                    ['dbus-send', '--type=method_call', '--dest=org.gnome.ScreenSaver', '/org/gnome/ScreenSaver', 'org.gnome.ScreenSaver.Lock'],
                    ['loginctl', 'lock-session']
                ]
                
                bloqueado = False
                for cmd in comandos_linux:
                    try:
                        # Ejecutamos el comando ocultando la salida de error en la terminal
                        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"[LockManager] Bloqueo exitoso utilizando: {cmd[0]}")
                        bloqueado = True
                        break # Si funciona, salimos del bucle
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue # Si falla o no existe el comando, intenta el siguiente
                
                if not bloqueado:
                    print("[LockManager] Error: Ningún comando de bloqueo funcionó en tu entorno de Linux.")

            elif self.os_type == "Windows":
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            else:
                print("[LockManager] Sistema operativo no soportado para bloqueo automático.")
                
        except Exception as e:
            print(f"[LockManager] Error crítico al intentar bloquear: {e}")