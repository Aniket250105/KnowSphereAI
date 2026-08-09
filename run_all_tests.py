import subprocess
import time
import sys

def run_tests():
    print("Starting FastAPI server in background...")
    server_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "127.0.0.1", "--port", "8000"])
    
    # Wait for server to start
    time.sleep(3)
    
    scripts = [
        "scripts/test_phase5_5.py",
        "scripts/test_phase6a.py",
        "scripts/test_phase6b.py",
        "scripts/test_phase6c.py"
    ]
    
    for script in scripts:
        print(f"\n====================================")
        print(f"Running {script}")
        print(f"====================================")
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"Test {script} failed.")
    
    print("\nTerminating FastAPI server...")
    server_proc.terminate()
    server_proc.wait()
    print("Done.")

if __name__ == "__main__":
    run_tests()
