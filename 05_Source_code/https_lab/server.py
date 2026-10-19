"""DT032: local-only HTTPS misconfiguration lab (educational)."""

import html
import os
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import urlsplit

MODE = os.environ.get("LAB_MODE", "vulnerable").lower()
if MODE not in {"vulnerable", "hardened"}:
    raise ValueError("LAB_MODE must be 'vulnerable' or 'hardened'")

HTTP_PORT = int(os.environ.get("LISTEN_HTTP_PORT", "5080"))
HTTPS_PORT = int(os.environ.get("LISTEN_HTTPS_PORT", "5443"))
PUBLIC_HTTP_PORT = int(os.environ.get("PUBLIC_HTTP_PORT", str(HTTP_PORT)))
PUBLIC_HTTPS_PORT = int(os.environ.get("PUBLIC_HTTPS_PORT", str(HTTPS_PORT)))
CERT_FILE = os.environ.get("LAB_CERT_FILE", "/certs/localhost.crt")
KEY_FILE = os.environ.get("LAB_KEY_FILE", "/certs/localhost.key")


class LabServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, handler, *, https: bool):
        super().__init__(address, handler)
        self.is_https = https


class Handler(BaseHTTPRequestHandler):
    server_version = "DT032Lab/1.0"
    protocol_version = "HTTP/1.1"

    def do_HEAD(self):
        self.handle_request(send_body=False)

    def do_GET(self):
        self.handle_request(send_body=True)

    def handle_request(self, *, send_body: bool):
        # Never put the unsanitized Host header into a redirect Location.
        if not self.server.is_https and MODE == "hardened":
            target = f"https://localhost:{PUBLIC_HTTPS_PORT}{self.path}"
            self.send_response(308)
            self.send_header("Location", target)
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return

        path = urlsplit(self.path).path
        if path in {"/insecure.js", "/secure.js"}:
            status = 200
            content_type = "text/javascript; charset=utf-8"
            content = (
                "document.getElementById('resource-status').textContent = "
                "'JavaScript loaded';\n"
            ).encode("utf-8")
        elif path == "/":
            status = 200
            content_type = "text/html; charset=utf-8"
            if MODE == "vulnerable":
                script_src = f"http://localhost:{PUBLIC_HTTP_PORT}/insecure.js"
                info = "Baseline: HTTP served, no HSTS, HTTP script reference, TLS 1.2"
            else:
                script_src = "/secure.js"
                info = "Hardened: redirect, HSTS, HTTPS resources, TLS 1.3"
            content = f"""<!doctype html>
<html lang="vi">
<head><meta charset="utf-8"><title>DT032 HTTPS Lab - {MODE}</title></head>
<body>
  <h1>DT032 HTTPS Security Lab</h1>
  <p id="mode">Mode: {MODE}</p>
  <p id="description">{html.escape(info)}</p>
  <p id="resource-status">JavaScript not loaded yet</p>
  <script src="{html.escape(script_src, quote=True)}"></script>
</body>
</html>
""".encode("utf-8")
        else:
            status = 404
            content_type = "text/plain; charset=utf-8"
            content = b"Not found\n"

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        # HSTS is only meaningful on HTTPS responses.
        if self.server.is_https and MODE == "hardened":
            self.send_header("Strict-Transport-Security", "max-age=31536000")
        self.end_headers()
        if send_body:
            self.wfile.write(content)


def main():
    httpd = LabServer(("0.0.0.0", HTTP_PORT), Handler, https=False)
    httpsd = LabServer(("0.0.0.0", HTTPS_PORT), Handler, https=True)
    tls = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    if MODE == "hardened":
        tls.minimum_version = ssl.TLSVersion.TLSv1_3
        tls.maximum_version = ssl.TLSVersion.TLSv1_3
    else:
        # TLS 1.2 is acceptable in many real deployments, but is
        # deliberately below the lab's STRICT TLS-1.3-only policy.
        tls.minimum_version = ssl.TLSVersion.TLSv1_2
        tls.maximum_version = ssl.TLSVersion.TLSv1_2
    tls.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    httpsd.socket = tls.wrap_socket(httpsd.socket, server_side=True)
    Thread(target=httpd.serve_forever, daemon=True).start()
    print(
        f"DT032 {MODE} ready: HTTP {HTTP_PORT}, HTTPS {HTTPS_PORT}, "
        f"published HTTP {PUBLIC_HTTP_PORT}, HTTPS {PUBLIC_HTTPS_PORT}",
        flush=True,
    )
    httpsd.serve_forever()


if __name__ == "__main__":
    main()
