import subprocess, sys, webbrowser, time
from pathlib import Path

def main():
    app = Path(__file__).parent / "app.py"
    p = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", str(app),
        "--server.headless=true",
        "--server.port=8501",
        "--browser.serverAddress=localhost",
    ])
    time.sleep(1.5)
    webbrowser.open("http://localhost:8501")
    p.wait()

if __name__ == "__main__":
    main()
