import sys
import argparse
from ai_chat_module import (
    generate_lorri_response,
    generate_lorri_response_with_history,
)

BANNER = r"""
╔══════════════════════════════════════════════════════════════════╗
║  L O R R I . A I                                                 ║
║  Next-Generation Global Freight Intelligence Grid                ║
║  ── Optimization Engines  ·  Sustainability Intelligence ──      ║
║  Backend : DialoGPT-small  (117M, fully local)                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ─── CLI MODE ─────────────────────────────────────────────────────────────────

def run_cli():
    print(BANNER)
    print("  LORRI Intelligence Grid — ONLINE")
    print("  Type your freight query. ('exit' to quit)\n")
    print("─" * 66)

    history_ids = None

    while True:
        try:
            user_input = input("\n  YOU   ▸  ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  LORRI ▸  Session terminated. Freight grid standing by.")
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "bye"}:
            print("\n  LORRI ▸  Session closed. Your optimised lanes remain saved.")
            break

        print("\n  LORRI ▸  ", end="", flush=True)
        response, history_ids = generate_lorri_response_with_history(
            user_input, history_ids
        )
        print(response)
        print("\n" + "─" * 66)


# ─── HTTP SERVER MODE ─────────────────────────────────────────────────────────

def run_server(port: int = 5050):
    """
    POST /chat        { "message": "...", "session_id": "abc" }
                      → { "response": "...", "session_id": "abc" }
    POST /chat/reset  { "session_id": "abc" }  → clears history
    GET  /health      → { "status": "ok", "model": "DialoGPT-small" }
    """
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
    except ImportError:
        print("[LORRI] Missing deps. Run: pip install flask flask-cors")
        sys.exit(1)

    app = Flask(__name__)
    CORS(app)

    _sessions: dict = {}   # session_id -> torch history tensor

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "agent": "LORRI.AI",
                        "model": "microsoft/DialoGPT-small"})

    @app.route("/chat", methods=["POST"])
    def chat():
        data       = request.get_json(silent=True) or {}
        msg        = (data.get("message") or "").strip()
        session_id = data.get("session_id", "default")
        if not msg:
            return jsonify({"error": "No message provided"}), 400
        try:
            response, updated_ids = generate_lorri_response_with_history(
                msg, _sessions.get(session_id)
            )
            _sessions[session_id] = updated_ids
            return jsonify({"response": response, "session_id": session_id})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @app.route("/chat/reset", methods=["POST"])
    def reset():
        data       = request.get_json(silent=True) or {}
        session_id = data.get("session_id", "default")
        _sessions.pop(session_id, None)
        return jsonify({"status": "reset", "session_id": session_id})

    print(BANNER)
    print(f"  HTTP Agent — http://0.0.0.0:{port}")
    print(f"  POST  http://localhost:{port}/chat")
    print(f"  GET   http://localhost:{port}/health\n")
    print("  NOTE: DialoGPT-small downloads ~350 MB on first run, then runs offline.\n")
    app.run(host="0.0.0.0", port=port, debug=False)


# ─── DEMO MODE ────────────────────────────────────────────────────────────────

DEMO_QUERIES = [
    "I have 20 containers in Shanghai. Optimize my lane to Rotterdam, "
    "avoiding congestion and maximizing sustainability.",
    "What is the cheapest route from Singapore to Los Angeles?",
    "Give me LORRI's optimization capabilities summary.",
]


def run_demo():
    print(BANNER)
    print("  DEMO MODE — 3 sample queries\n" + "─" * 66)
    for i, q in enumerate(DEMO_QUERIES, 1):
        print(f"\n  DEMO {i}  ▸  {q}")
        print("\n  LORRI   ▸  ", end="", flush=True)
        print(generate_lorri_response(q))
        print("\n" + "─" * 66)


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LORRI.AI — DialoGPT-small Agent")
    parser.add_argument("--server", action="store_true", help="Run as HTTP server")
    parser.add_argument("--port",   type=int, default=5050)
    parser.add_argument("--demo",   action="store_true", help="Run demo queries")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    elif args.server:
        run_server(args.port)
    else:
        run_cli()