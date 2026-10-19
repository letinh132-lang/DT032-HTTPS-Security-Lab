"""Ground-truth 4x2 positive/negative checks plus HTTP edge cases."""

import http.client
import pytest

from tools.dt032_audit import CHECKS, evaluate_target, http_request


@pytest.fixture(scope='module')
def evaluations():
    return {mode: evaluate_target(mode) for mode in ('vulnerable', 'hardened')}


@pytest.mark.parametrize('mode,check,should_flag', [
    (mode, check, mode == 'vulnerable')
    for mode in ('vulnerable', 'hardened')
    for check in CHECKS
])
def test_security_findings_match_seeded_ground_truth(evaluations, mode, check, should_flag):
    """A passing vulnerability test means a planted fault was correctly DETECTED."""
    assert evaluations[mode]['findings'][check] is should_flag


def test_http_hardened_hsts_is_not_trusted_on_http():
    response = http_request(5180)
    headers = {k.lower(): v for k, v in response['headers'].items()}
    assert response['status'] == 308
    assert 'strict-transport-security' not in headers


def test_redirect_does_not_trust_attacker_host():
    conn = http.client.HTTPConnection('127.0.0.1', 5180, timeout=5)
    try:
        conn.request('GET', '/?q=1', headers={'Host': 'wrong.example'})
        response = conn.getresponse()
        assert response.status == 308
        assert response.getheader('Location') == 'https://localhost:5543/?q=1'
        response.read()
    finally:
        conn.close()


@pytest.mark.parametrize('port', [5080, 5180])
def test_unknown_http_path_behavior(port):
    response = http_request(port, '/dt032_nonexistent_abc')
    # Vulnerable serves 404; Hardened redirects first, then secure server serves 404.
    assert response['status'] == (404 if port == 5080 else 308)
