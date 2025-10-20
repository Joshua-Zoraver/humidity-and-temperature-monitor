import subprocess
import time
import signal
import sys

#Keep track of processes
processes = []

def start_process(script_name):
    print(f"[runner] Launching {script_name}...")
    p = subprocess.Popen(["python3", script_name])
    processes.append(p)

def stop_processes():
    print("\n[runner] Stopping all processes...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    #Give them time to close
    time.sleep(2)
    for p in processes:
        if p.poll() is None:
            p.kill()
    print("[runner] All processes stopped.")

def main():
    try:
        #Start main.py
        start_process("main.py")

        #Wait 5 seconds before launching API
        time.sleep(5)

        #Start api.py
        start_process("api.py")

        #Keep script alive to monitor processes
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        stop_processes()
        sys.exit(0)

if __name__ == "__main__":
    main()
