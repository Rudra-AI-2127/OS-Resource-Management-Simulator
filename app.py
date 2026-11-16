"""
OS Resource Management Simulator Pro-Max — Unified Application Entry Point.
Launches the native high-performance zero-dependency web server (server.py)
or delegates to interactive terminal CLI mode (main.py).
Streamlit has been retired in favor of the Black & White Native Web Console.
"""

import argparse
from pathlib import Path
import subprocess
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OS Resource Management Simulator — Executive Unified Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                     # Starts native web server at http://127.0.0.1:8501/
  python app.py --port 8000         # Starts native web server at custom port 8000
  python app.py --cli               # Starts interactive terminal CLI interface
  python app.py --test              # Runs automated self-test verification
""",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface for native web server (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port for native web server (default: 8501)",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Launch interactive terminal CLI interface (main.py)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Execute automated server self-test verification and exit",
    )
    args = parser.parse_args()

    if args.cli:
        from main import main as cli_main
        cli_main()
    elif args.test:
        from server import run_self_test
        success = run_self_test()
        sys.exit(0 if success else 1)
    else:
        from server import run_server
        run_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
