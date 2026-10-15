# Archivo: src/ui/app_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import cv2
import os

from src.infrastructure.storage import LocalStorage
from src.services.enrollment_service import EnrollmentService
from src.services.monitoring_service import MonitoringService

class AppGUI:
    def __init__(self):
        self.storage = LocalStorage()
        self.monitoring_service = None
        self.monitor_thread = None

        self.root = tk.Tk()
        self.root.title("FaceLocker - Seguridad Biométrica")
        self.root.geometry("450x400")
        self.root.resizable(False, False)

        # Configurar estilos modernos
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.container = ttk.Frame(self.root, padding=20)
        self.container.pack(fill="both", expand=True)

        # Verificar si el usuario ya está configurado
        if self._is_configured():
            self.show_dashboard_view()
        else:
            self.show_setup_view()

    def _is_configured(self):
        """Revisa si existen las configuraciones y el perfil de rostro guardado."""
        profile_exists = self.storage.load_profile() is not None
        settings = self.storage.load_settings()
        return profile_exists and "camera_index" in settings

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- PANTALLA 1: CONFIGURACIÓN E INICIALIZACIÓN ---
    def show_setup_view(self):
        self.clear_container()

        title = ttk.Label(self.container, text="Configuración Inicial", font=("Helvetica", 16, "bold"))
        title.pack(pady=(0, 15))

        desc = ttk.Label(self.container, text="Selecciona tu cámara y realiza el registro facial de tu rostro.", wraplength=400)
        desc.pack(pady=(0, 15))

        # Selector de Cámara
        cam_frame = ttk.LabelFrame(self.container, text=" Configuración de Cámara ", padding=10)
        cam_frame.pack(fill="x", pady=10)

        ttk.Label(cam_frame, text="Cámara Detectada:").pack(anchor="w")
        
        self.cam_combo = ttk.Combobox(cam_frame, state="readonly")
        self.cam_combo.pack(fill="x", pady=5)
        
        btn_scan = ttk.Button(cam_frame, text="Buscar Cámaras", command=self._scan_cameras)
        btn_scan.pack(pady=5)

        self._scan_cameras() # Escaneo inicial

        # Botón para Registrar Rostro
        btn_enroll = ttk.Button(self.container, text="Iniciar Registro Facial (3D)", command=self._start_enrollment)
        btn_enroll.pack(fill="x", pady=20)

    def _scan_cameras(self):
        """Escanea puertos de video disponibles."""
        available = []
        for i in range(4):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append(f"Cámara {i}")
            cap.release()

        if available:
            self.cam_combo['values'] = available
            self.cam_combo.current(0)
        else:
            self.cam_combo['values'] = ["No se detectaron cámaras"]
            self.cam_combo.current(0)

    def _start_enrollment(self):
        selected = self.cam_combo.get()
        if "Cámara" not in selected:
            messagebox.showerror("Error", "Por favor selecciona una cámara válida.")
            return

        cam_idx = int(selected.split()[1])
        # Guardar cámara seleccionada
        self.storage.save_settings({"camera_index": cam_idx, "tolerance": 0.85})

        # Ocultar ventana mientras corre el asistente de registro
        self.root.withdraw()
        enrollment = EnrollmentService(camera_index=cam_idx)
        success = enrollment.start_enrollment()
        self.root.deiconify()

        if success:
            messagebox.showinfo("Éxito", "¡Registro facial completado correctamente!")
            self.show_dashboard_view()
        else:
            messagebox.showwarning("Incompleto", "El registro fue cancelado. Inténtalo de nuevo.")

    # --- PANTALLA 2: PANEL DE CONTROL Y MONITOREO ---
    def show_dashboard_view(self):
        self.clear_container()

        title = ttk.Label(self.container, text="Panel de Control", font=("Helvetica", 16, "bold"))
        title.pack(pady=(0, 10))

        # Indicador de Estado
        self.status_frame = tk.Frame(self.container, bg="#FFCCCC", padx=15, pady=15)
        self.status_frame.pack(fill="x", pady=15)

        self.status_label = tk.Label(self.status_frame, text="ESTADO: INACTIVO", font=("Helvetica", 12, "bold"), bg="#FFCCCC", fg="#990000")
        self.status_label.pack()

        # Botón Principal ON/OFF
        self.btn_toggle = ttk.Button(self.container, text="ACTIVAR MONITOREO", command=self._toggle_monitoring)
        self.btn_toggle.pack(fill="x", ipady=10, pady=10)

        # Opciones secundarias
        btn_reconfig = ttk.Button(self.container, text=" Re-registrar Rostro / Cambiar Cámara", command=self.show_setup_view)
        btn_reconfig.pack(fill="x", pady=5)

    def _toggle_monitoring(self):
        if self.monitoring_service and self.monitoring_service.running:
            # Detener Monitoreo
            self.monitoring_service.stop_monitoring()
            self.status_frame.config(bg="#FFCCCC")
            self.status_label.config(text="ESTADO: INACTIVO", bg="#FFCCCC", fg="#990000")
            self.btn_toggle.config(text="ACTIVAR MONITOREO")
        else:
            # Iniciar Monitoreo en hilo secundario
            try:
                self.monitoring_service = MonitoringService()
                self.monitor_thread = threading.Thread(target=self.monitoring_service.start_monitoring, daemon=True)
                self.monitor_thread.start()

                self.status_frame.config(bg="#CCFFCC")
                self.status_label.config(text="ESTADO: VIGILANDO EN SEGUNDO PLANO", bg="#CCFFCC", fg="#006600")
                self.btn_toggle.config(text="DETENER MONITOREO")
            except Exception as e:
                messagebox.showerror("Error al iniciar", str(e))

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if self.monitoring_service and self.monitoring_service.running:
            self.monitoring_service.stop_monitoring()
        self.root.destroy()