"""Smoke checks: run after `docker compose up -d`. No third-party libs."""

import http.client
import ssl
from pathlib import Path

CERT = Path(__file__).resolve().parents[1] / "certs" / "localhost.crt"


def test_http_redirect_policy():
    connection = http.client.HTTPConnection("localhost", 5080, timeout=5)
    connection.request("GET", "/")
    baseline = connection.getresponse()
    assert baseline.status == 200
    baseline.read()
    connection.close()

    connection = http.client.HTTPConnection("localhost", 5180, timeout=5)
    connection.request("GET", "/example?x=1")
    hardened = connection.getresponse()
    assert hardened.status == 308
    assert hardened.getheader("Location") == "https://localhost:5543/example?x=1"
    hardened.read()
    connection.close()


def get_https(port: int, tls_version: ssl.TLSVersion):
    ctx = ssl.create_default_context(cafile=str(CERT))
    ctx.minimum_version = tls_version
    ctx.maximum_version = tls_version
    conn = http.client.HTTPSConnection("localhost", port, context=ctx, timeout=5)
    try:
        conn.request("GET", "/")
        result = conn.getresponse()
        return result.status, dict(result.getheaders()), result.read().decode("utf-8")
    finally:
        conn.close()


def test_https_hsts_and_resource_scheme():
    code, headers, page = get_https(5443, ssl.TLSVersion.TLSv1_2)
    assert code == 200
    assert "strict-transport-security" not in headers
    assert 'src="http://localhost:5080/insecure.js"' in page

    code, headers, page = get_https(5543, ssl.TLSVersion.TLSv1_3)
    assert code == 200
    assert headers["Strict-Transport-Security"] == "max-age=31536000"
    assert 'src="/secure.js"' in page


def test_hardened_blocks_tls12():
    # In this lab, hardened is intentionally restricted to TLS 1.3 only.
    ctx = ssl.create_default_context(cafile=str(CERT))
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    conn = http.client.HTTPSConnection("localhost", 5543, context=ctx, timeout=5)
    try:
        try:
            conn.request("GET", "/")
            conn.getresponse()
        except ssl.SSLError:
            return
        assert False, "Hardened should refuse TLS 1.2 under the lab policy"
    finally:
        conn.close()
