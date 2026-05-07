"""
CLI helper to run common tasks during refactor.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def run_backend():
    subprocess.run([sys.executable, "-m", "uvicorn", "src.backend.app:app", "--reload", "--port", "8000"], check=True)

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('cmd', choices=['backend'])
    args = p.parse_args()
    if args.cmd == 'backend':
        run_backend()
