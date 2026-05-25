import subprocess
import sys
import time
import os

def main():
    print("--- Starting SafetyGuard Project ---")
    
    backend_path = os.path.join(os.getcwd(), "backend")
    frontend_path = os.path.join(os.getcwd(), "frontend")

    print(f"[RUNNER] Starting Backend (Flask) in {backend_path}...")
    backend = subprocess.Popen(
        [sys.executable, "app.py"], 
        cwd=backend_path
    )
    
    print(f"[RUNNER] Starting Frontend (Vite) in {frontend_path}...")
    frontend = subprocess.Popen(
        "npm run dev", 
        cwd=frontend_path, 
        shell=True
    )
    
    print("[RUNNER] Services are running.")
    print("[RUNNER] Backend: http://localhost:5000")
    print("[RUNNER] Frontend: http://localhost:5173 (or next available port)")
    
    try:
        while True:
            time.sleep(1)
            if backend.poll() is not None:
                print("[RUNNER] Backend process has exited.")
                break
            if frontend.poll() is not None:
                print("[RUNNER] Frontend process has exited.")
                break
    except KeyboardInterrupt:
        print("\n[RUNNER] Stopping all services...")
    finally:
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main()
