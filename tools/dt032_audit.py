"""DT032 evidence-driven, local-only HTTP/TLS configuration audit.

The TLS-1.3-only check is a *course lab policy*, NOT a finding that all TLS 1.2 is insecure.
Only targets fixed at localhost are scanned; no external URLs are accepted.
"""

import argparse
import csv
import hashlib
import html.parser
import http.client
import json
import platform
import re
import ssl
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CERT = ROOT / 'certs' / 'localhost.crt'
OUTPUT = ROOT / '06_Ket_qua_thuc_nghiem' / 'security_audit'
MIN_HSTS_SECONDS = 31536000  # Project policy, not a universal browser requirement.
CHECKS = (
    'redirect_missing',
    'hsts_missing_or_short',
    'http_script_on_https_page',
    'tls13_only_policy_violation',
)
TARGETS = {
    'vulnerable': {'http_port': 5080, 'https_port': 5443},
    'hardened': {'http_port': 5180, 'https_port': 5543},
}
# Ground truth planted in our OWN test lab. Do not extrapolate to websites.
GROUND_TRUTH = {mode: {name: mode == 'vulnerable' for name in CHECKS}
                for mode in TARGETS}


class ScriptSrcParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'script':
            a = dict(attrs)
            if a.get('src'):
                self.scripts.append(a['src'])


def _context(cert, tls_version):
    ctx = ssl.create_default_context(cafile=str(cert))
    ctx.minimum_version = tls_version
    ctx.maximum_version = tls_version
    return ctx


def http_request(port, path='/?dt032=1'):
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=6)
    try:
        conn.request('GET', path)
        resp = conn.getresponse()
        return {'status': resp.status, 'headers': dict(resp.getheaders()),
                'body': resp.read().decode('utf-8', errors='replace')}
    finally:
        conn.close()


def tls_probe(port, cert, version):
    """Return successful handshake or a deliberate TLS negotiation rejection.

    Timeouts, certificate failures, refused connections and other runtime errors
    must abort the audit rather than being scored as a secure rejection.
    """
    ctx = _context(cert, version)
    conn = http.client.HTTPSConnection('localhost', port, context=ctx, timeout=6)
    try:
        conn.request('GET', '/')
        response = conn.getresponse()
        response.read()
        return {'accepted': True, 'protocol': version.name, 'http_status': response.status}
    except ssl.SSLCertVerificationError:
        raise
    except ssl.SSLError as exc:
        message = str(exc)
        # Restrict classification to TLS handshake negotiation failures.
        expected_failure = any(term in message.lower() for term in (
            'protocol version', 'unsupported protocol', 'alert handshake failure',
            'handshake failure', 'no protocols available', 'tlsv1 alert',
        ))
        if not expected_failure:
            raise
        return {'accepted': False, 'protocol': version.name, 'reason': message[:200]}
    finally:
        conn.close()


def https_request(port, cert, version):
    conn = http.client.HTTPSConnection('localhost', port,
                                      context=_context(cert, version), timeout=6)
    try:
        conn.request('GET', '/')
        resp = conn.getresponse()
        return {'status': resp.status,
                'headers': {k.lower(): v for k, v in resp.getheaders()},
                'body': resp.read().decode('utf-8', errors='replace')}
    finally:
        conn.close()


def parse_max_age(header):
    match = re.search(r'(?:^|;)\s*max-age\s*=\s*(\d+)(?:\s*;|\s*$)', header, re.I)
    return int(match.group(1)) if match else None


def evaluate_target(mode, cert=DEFAULT_CERT):
    if mode not in TARGETS:
        raise ValueError('Audit target must be vulnerable or hardened')
    if not cert.is_file():
        raise FileNotFoundError(f'Local CA certificate is missing: {cert}')
    t0 = time.perf_counter()
    ports = TARGETS[mode]
    http = http_request(ports['http_port'])
    loc = http['headers'].get('Location', http['headers'].get('location', ''))
    expected_location = f'https://localhost:{ports["https_port"]}/?dt032=1'
    redirects = http['status'] in (301, 308) and loc == expected_location
    tls12 = tls_probe(ports['https_port'], cert, ssl.TLSVersion.TLSv1_2)
    tls13 = tls_probe(ports['https_port'], cert, ssl.TLSVersion.TLSv1_3)
    if not tls12['accepted'] and not tls13['accepted']:
        raise RuntimeError(f'No negotiated TLS version for {mode}')
    supported = ssl.TLSVersion.TLSv1_3 if tls13['accepted'] else ssl.TLSVersion.TLSv1_2
    https = https_request(ports['https_port'], cert, supported)
    if https['status'] != 200:
        raise RuntimeError(f'{mode} HTTPS returned unexpected status {https["status"]}')
    hsts_header = https['headers'].get('strict-transport-security', '')
    max_age = parse_max_age(hsts_header)
    hsts_ok = max_age is not None and max_age >= MIN_HSTS_SECONDS
    parser = ScriptSrcParser()
    parser.feed(https['body'])
    http_scripts = [src for src in parser.scripts if urlsplit(src).scheme.lower() == 'http']
    findings = {
        'redirect_missing': not redirects,
        'hsts_missing_or_short': not hsts_ok,
        'http_script_on_https_page': bool(http_scripts),
        'tls13_only_policy_violation': tls12['accepted'] or not tls13['accepted'],
    }
    elapsed = time.perf_counter() - t0
    return {
        'mode': mode, 'duration_sec': round(elapsed, 4),
        'findings': findings,
        'observations': {
            'http_status': http['status'], 'redirect_location': loc,
            'expected_redirect_location': expected_location,
            'hsts_header': hsts_header, 'hsts_max_age': max_age,
            'script_sources': parser.scripts, 'http_script_sources': http_scripts,
            'tls12': tls12, 'tls13': tls13,
            'https_status': https['status'],
        },
    }


def metrics_for(targets):
    counts = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}
    for result in targets:
        mode = result['mode']
        for key, predicted in result['findings'].items():
            actual = GROUND_TRUTH[mode][key]
            key = ('TP' if actual and predicted else
                   'FN' if actual and not predicted else
                   'FP' if not actual and predicted else 'TN')
            counts[key] += 1
    n_pos = counts['TP'] + counts['FN']
    n_neg = counts['TN'] + counts['FP']
    precision_den = counts['TP'] + counts['FP']
    counts['detection_rate'] = round(counts['TP'] / n_pos, 4) if n_pos else None
    counts['false_positive_rate'] = round(counts['FP'] / n_neg, 4) if n_neg else None
    counts['precision'] = round(counts['TP'] / precision_den, 4) if precision_den else None
    counts['coverage'] = round(len(targets) * len(CHECKS) / (2 * len(CHECKS)), 4)
    counts['checked_cases'] = len(targets) * len(CHECKS)
    return counts


def audit_once(cert=DEFAULT_CERT):
    start = time.perf_counter()
    results = [evaluate_target(mode, cert) for mode in TARGETS]
    return {'date_utc': datetime.now(timezone.utc).isoformat(),
            'results': results, 'metrics': metrics_for(results),
            'total_duration_sec': round(time.perf_counter() - start, 4)}


def run_experiment(repeats=3, cert=DEFAULT_CERT, output=OUTPUT):
    output.mkdir(parents=True, exist_ok=True)
    runs = []
    for i in range(1, repeats + 1):
        run = audit_once(cert)
        run['iteration'] = i
        (output / f'run_{i:02d}.json').write_text(
            json.dumps(run, ensure_ascii=False, indent=2), encoding='utf-8')
        runs.append(run)
        print(f'Run {i}/{repeats}: TP={run["metrics"]["TP"]} '
              f'FN={run["metrics"]["FN"]} FP={run["metrics"]["FP"]} '
              f'runtime={run["total_duration_sec"]:.3f}s', flush=True)

    durations = [r['total_duration_sec'] for r in runs]
    summary = {
        'experiment': 'DT032 local HTTPS lab',
        'security_policy': f'HSTS >= {MIN_HSTS_SECONDS}s; TLS 1.3-only',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'host': {'python': sys.version.split()[0], 'platform': platform.platform()},
        'certificate_sha256': hashlib.sha256(cert.read_bytes()).hexdigest(),
        'repetitions': repeats,
        'mean_runtime_sec': round(statistics.mean(durations), 4),
        'std_runtime_sec': round(statistics.stdev(durations), 4) if repeats > 1 else 0.0,
        'all_runs': [{'iteration': r['iteration'], 'duration_sec': r['total_duration_sec'],
                      'metrics': r['metrics']} for r in runs],
    }
    (output / 'summary.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    with (output / 'results.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'mode', 'check', 'ground_truth_misconfiguration',
                         'detected_misconfiguration', 'correct', 'run_duration_sec'])
        for run in runs:
            for target in run['results']:
                for check in CHECKS:
                    actual = GROUND_TRUTH[target['mode']][check]
                    detected = target['findings'][check]
                    writer.writerow([run['iteration'], target['mode'], check,
                                     int(actual), int(detected), int(actual == detected),
                                     run['total_duration_sec']])
    return summary


def main():
    parser = argparse.ArgumentParser(description='DT032 authorized localhost-only experiment')
    parser.add_argument('--repeat', type=int, default=3, help='Number of controlled repetitions')
    parser.add_argument('--gate', action='store_true',
                        help='Exit nonzero when hardened has findings or seeded faults are missed')
    args = parser.parse_args()
    if not 1 <= args.repeat <= 100:
        parser.error('--repeat must be between 1 and 100')
    summary = run_experiment(args.repeat)
    print(f'Reports: {OUTPUT}')
    print('Mean runtime:', summary['mean_runtime_sec'], 'seconds')
    print('Std runtime:', summary['std_runtime_sec'], 'seconds')
    if args.gate:
        bad = [r for r in summary['all_runs'] if
               r['metrics']['FN'] or r['metrics']['FP'] or r['metrics']['coverage'] != 1]
        if bad:
            print('SECURITY GATE: FAIL', file=sys.stderr)
            return 1
        print('SECURITY GATE: PASS (on the supplied lab ground truth only)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
