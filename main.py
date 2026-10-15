# Archivo: main.py
from src.services.monitoring_service import MonitoringService

def main():
    try:
        # Inicializamos el servicio con el nuevo flujo de Privacidad + Bloqueo por entrada
        monitor = MonitoringService(
            threshold=0.85,              # Tolerancia de reconocimiento facial
            check_interval_seconds=0.3   # Evaluación de IA cada 300 ms (eficiente)
        )
        monitor.start_monitoring()
    except Exception as e:
        print(f"\n[Error] {e}")

if __name__ == "__main__":
    main()