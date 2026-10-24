
import threading
import time
import subprocess
import sys

from health_server import start_health_server


def main():
    while True:
        print("Starting Shrutix Music Bot...", flush=True)

        process = subprocess.Popen(
            [sys.executable, "-u", "-m", "ShrutixMusic"]
        )

        try:
            exit_code = process.wait()
        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            raise

        print(
            f"Music bot exited with code {exit_code}. "
            "Restarting in 5 seconds...",
            flush=True,
        )
        time.sleep(5)


if __name__ == "__main__":
    start_health_server()
    main()
    
