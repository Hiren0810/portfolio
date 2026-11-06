"""
Zero-dependency Real-Time Web Server and SSE Event Streamer.
Serves the web dashboard, REST control endpoints, and live Server-Sent Events (SSE).
Runs completely on Python standard library without requiring Flask, FastAPI, or Node.js.
"""

import http.server
import json
import logging
import os
import queue
import threading
import time
import urllib.parse
from typing import Dict, Any, List

logger = logging.getLogger("WebServer")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

class WebServer:
    def __init__(self, scanner_engine, host: str = "127.0.0.1", port: int = 8080):
        self.engine = scanner_engine
        self.host = host
        self.port = port
        self.clients: List[queue.Queue] = []
        self._lock = threading.Lock()
        self.server: Optional[http.server.ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None

        # Wire scanner engine callback to push SSE updates
        self.engine.state_callback = self.broadcast_state

    def broadcast_state(self, state: Dict[str, Any]):
        """Broadcast updated state to all connected SSE browser clients."""
        payload = f"data: {json.dumps(state)}\n\n"
        with self._lock:
            for q in list(self.clients):
                try:
                    q.put_nowait(payload)
                except Exception:
                    self.clients.remove(q)

    def start(self):
        """Start HTTP server in background thread."""
        handler_class = self._create_handler()
        self.server = http.server.ThreadingHTTPServer((self.host, self.port), handler_class)
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()
        logger.info(f"🌐 Trading Dashboard Live at: http://{self.host}:{self.port}")

    def stop(self):
        """Stop HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()

    def _create_handler(self):
        server_instance = self

        class TradingRequestHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Suppress verbose HTTP access logs in terminal
                pass

            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path

                if path == "/api/state":
                    self._send_json(server_instance.engine.get_state())
                elif path == "/api/stream":
                    self._handle_sse()
                elif path in ("/", "/index.html"):
                    self._serve_file(os.path.join(STATIC_DIR, "index.html"), "text/html")
                elif path.startswith("/static/"):
                    rel = path[len("/static/"):]
                    file_path = os.path.join(STATIC_DIR, rel)
                    content_type = "text/plain"
                    if file_path.endswith(".js"):
                        content_type = "application/javascript"
                    elif file_path.endswith(".css"):
                        content_type = "text/css"
                    elif file_path.endswith(".html"):
                        content_type = "text/html"
                    self._serve_file(file_path, content_type)
                else:
                    self.send_error(404, "Not Found")

            def do_POST(self):
                parsed = urllib.parse.urlparse(self.path)
                path = parsed.path
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
                data = json.loads(body) if body else {}

                if path == "/api/scan":
                    server_instance.engine.trigger_instant_scan()
                    self._send_json({"status": "SCAN_TRIGGERED"})
                elif path == "/api/toggle_pause":
                    server_instance.engine.is_running = not server_instance.engine.is_running
                    self._send_json({"status": "TOGGLED", "is_running": server_instance.engine.is_running})
                elif path == "/api/close_position":
                    pos_id = data.get("position_id")
                    if pos_id:
                        pos = server_instance.engine.broker.close_position(pos_id, reason="MANUAL_UI_CLOSE")
                        self._send_json({"status": "SUCCESS", "closed": pos.to_dict() if pos else None})
                    else:
                        self.send_error(400, "Missing position_id")
                elif path == "/api/close_all":
                    closed = server_instance.engine.broker.close_all_positions(reason="MANUAL_UI_EMERGENCY_CLOSE")
                    self._send_json({"status": "SUCCESS", "count": len(closed)})
                else:
                    self.send_error(404, "Not Found")

            def _send_json(self, data: dict):
                body = json.dumps(data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)

            def _serve_file(self, file_path: str, content_type: str):
                if not os.path.exists(file_path):
                    self.send_error(404, "File Not Found")
                    return
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)

            def _handle_sse(self):
                """Keep connection open and stream SSE packets."""
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                q = queue.Queue()
                with server_instance._lock:
                    server_instance.clients.append(q)

                # Send initial state immediately
                initial_state = f"data: {json.dumps(server_instance.engine.get_state())}\n\n"
                try:
                    self.wfile.write(initial_state.encode("utf-8"))
                    self.wfile.flush()

                    while True:
                        try:
                            msg = q.get(timeout=25.0)
                            self.wfile.write(msg.encode("utf-8"))
                            self.wfile.flush()
                        except queue.Empty:
                            # Send heartbeat comment to keep connection alive
                            self.wfile.write(b": heartbeat\n\n")
                            self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass
                finally:
                    with server_instance._lock:
                        if q in server_instance.clients:
                            server_instance.clients.remove(q)

        return TradingRequestHandler
