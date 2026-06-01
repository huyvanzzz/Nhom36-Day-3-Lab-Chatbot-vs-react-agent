import argparse
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from src.agent.agent import ReActAgent
from src.chatbot import ChatbotBaseline
from src.core.provider_factory import create_provider_from_env
from src.tools.travel_tools import get_travel_tools


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHAT_HTML = PROJECT_ROOT / "chat.html"


class ChatHandler(BaseHTTPRequestHandler):
    server_version = "TravelChat/0.1"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in {"/", "/chat.html"}:
            self._send_bytes(CHAT_HTML.read_bytes(), "text/html; charset=utf-8")
            return

        if path == "/api/health":
            self._send_json({"status": "ok"})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/chat":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        try:
            payload = self._read_json()
            query = str(payload.get("query", "")).strip()
            mode = str(payload.get("mode", "agent")).strip().lower()
            model = str(payload.get("model", "")).strip() or None
            max_steps = int(payload.get("max_steps", 5))

            if not query:
                self._send_json({"error": "query is required"}, status=HTTPStatus.BAD_REQUEST)
                return

            provider = create_provider_from_env(provider="openai", model=model)
            if mode == "chatbot":
                answer = ChatbotBaseline(provider).run(query)
            else:
                answer = ReActAgent(provider, get_travel_tools(), max_steps=max_steps).run(query)

            self._send_json(
                {
                    "answer": answer,
                    "mode": "chatbot" if mode == "chatbot" else "agent",
                    "model": provider.model_name,
                }
            )
        except Exception as exc:
            self._send_json(
                {
                    "error": type(exc).__name__,
                    "message": str(exc),
                },
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    def log_message(self, fmt: str, *args) -> None:
        try:
            sys.stderr.write("[web] " + fmt % args + "\n")
        except OSError:
            pass

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        if not body:
            return {}
        for encoding in ("utf-8", "utf-8-sig", "cp1258", "cp1252"):
            try:
                return json.loads(body.decode(encoding))
            except UnicodeDecodeError:
                continue
        return json.loads(body.decode("utf-8", errors="replace"))

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, body: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Travel Concierge web UI.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), ChatHandler)
    print(f"Serving chat UI at http://{args.host}:{args.port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
