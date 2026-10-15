# Archivo: src/infrastructure/input_listener.py
from pynput import keyboard, mouse

class InputListener:
    def __init__(self, on_input_detected_callback):
        self.on_input_detected = on_input_detected_callback
        self.k_listener = None
        self.m_listener = None
        self.is_listening = False

    def start(self):
        """Inicia la escucha de eventos de mouse y teclado."""
        if not self.is_listening:
            self.k_listener = keyboard.Listener(on_press=self._on_action)
            self.m_listener = mouse.Listener(on_move=self._on_action, on_click=self._on_action)
            self.k_listener.start()
            self.m_listener.start()
            self.is_listening = True

    def stop(self):
        """Detiene la escucha para no consumir recursos cuando estás trabajando normal."""
        if self.is_listening:
            if self.k_listener:
                self.k_listener.stop()
            if self.m_listener:
                self.m_listener.stop()
            self.is_listening = False

    def _on_action(self, *args):
        """Callback ejecutado al tocar cualquier periférico."""
        if self.is_listening:
            self.on_input_detected()