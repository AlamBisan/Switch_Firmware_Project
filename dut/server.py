"""TCP management-interface server for the mock switch firmware.

Commands go in as plain CLI text (one per line), mirroring a real switch's
console/Telnet management interface. Responses come back as one JSON object
per line, so automation clients don't need to scrape human-formatted text.
"""
from __future__ import annotations

import json
import socketserver
import threading

from .firmware import SwitchFirmware


class _Handler(socketserver.StreamRequestHandler):
    def handle(self):
        firmware: SwitchFirmware = self.server.firmware
        while True:
            line = self.rfile.readline()
            if not line:
                break
            raw_cmd = line.decode("utf-8", errors="replace").rstrip("\r\n")
            if not raw_cmd:
                continue
            try:
                result = firmware.execute(raw_cmd)
                payload = {"ok": result.ok, "message": result.message, "data": result.data}
            except Exception as exc:
                # Transport-layer safety net: a single bad command must never
                # take down the whole management connection/server, even if
                # the firmware's own parser has a latent bug (see BUG-005).
                payload = {"ok": False, "message": f"ERROR: internal command failure ({exc.__class__.__name__})"}
            self.wfile.write((json.dumps(payload) + "\n").encode("utf-8"))


class SwitchServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, firmware: SwitchFirmware, host: str = "127.0.0.1", port: int = 0):
        super().__init__((host, port), _Handler)
        self.firmware = firmware

    @property
    def address(self):
        return self.server_address


def serve_in_background(server: SwitchServer) -> threading.Thread:
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    fw = SwitchFirmware()
    srv = SwitchServer(fw, port=9090)
    print(f"SwitchFW mock server listening on {srv.address[0]}:{srv.address[1]}")
    print("Try: printf 'show version\\n' | ncat 127.0.0.1 9090   (or use dut/client.py)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
