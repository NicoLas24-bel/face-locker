# Archivo: main.py
from src.services.monitoring_service import MonitoringService

def main():
    try:
        # threshold=0.85 es la tolerancia (menor a 0.85 = autorizado)
        # max_unrecognized_seconds=3 da 3 segundos de tolerancia antes de bloquear
        monitor = MonitoringService(threshold=0.85, max_unrecognized_seconds=3)
        monitor.start_monitoring()
    except Exception as e:
        print(f"\n[Error] {e}")

if __name__ == "__main__":
    main()