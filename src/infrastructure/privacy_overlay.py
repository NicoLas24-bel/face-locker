# Archivo: src/infrastructure/privacy_overlay.py
import tkinter as tk
import os

class PrivacyOverlay:
    def __init__(self, image_path=None):
        self.root = None
        self.image_path = image_path

    def show(self):
        """Muestra la ventana a pantalla completa cubriendo todo el escritorio."""
        if self.root is None:
            self.root = tk.Tk()
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)
            self.root.configure(background='black')
            self.root.config(cursor="none") # Oculta el puntero del mouse

            # Si hay una imagen, la carga. Si no, muestra un diseño elegante por defecto.
            label_text = "MODO PRIVACIDAD ACTIVO\nVigilancia Biométrica en Curso..."
            label = tk.Label(
                self.root, 
                text=label_text, 
                fg="#00FF66", 
                bg="black", 
                font=("Helvetica", 28, "bold")
            )
            label.pack(expand=True)
            self.root.update()

    def update(self):
        """Mantiene con vida los eventos de la interfaz de Tkinter."""
        if self.root:
            self.root.update_idletasks()
            self.root.update()

    def hide(self):
        """Destruye la ventana y devuelve el control al escritorio."""
        if self.root:
            self.root.destroy()
            self.root = None