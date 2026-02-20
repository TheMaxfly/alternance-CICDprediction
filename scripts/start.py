"""
Lance l'API FastAPI (predictor) et l'interface Streamlit en parallele.

Usage:
    uv run python scripts/start.py
"""

import os
import signal
import subprocess
import sys
import time

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    procs = []

    # 1. Lancer l'API FastAPI
    api_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "briefml.api.predictor:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        cwd=PROJECT_DIR,
    )
    procs.append(api_proc)
    print(f"[start] API FastAPI lancee (PID {api_proc.pid}) sur http://localhost:8000")

    # 2. Lancer Streamlit
    st_proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "briefml/ui/app.py",
            "--server.port",
            "8501",
        ],
        cwd=PROJECT_DIR,
    )
    procs.append(st_proc)
    print(f"[start] Streamlit lance (PID {st_proc.pid}) sur http://localhost:8501")

    # 3. Gestion propre de l'arret (Ctrl+C)
    def shutdown(signum, frame):
        print("\n[start] Arret en cours...")
        for p in procs:
            p.terminate()
        for p in procs:
            p.wait()
        print("[start] Termine.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Attendre la fin d'un des deux processus
    try:
        while True:
            for p in procs:
                ret = p.poll()
                if ret is not None:
                    print(f"[start] Processus PID {p.pid} termine (code {ret})")
                    for other in procs:
                        if other.poll() is None:
                            other.terminate()
                            other.wait()
                    sys.exit(ret)
            time.sleep(0.5)
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
