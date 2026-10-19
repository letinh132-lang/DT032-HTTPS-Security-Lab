"""Record reproducibility metadata; only public-key certificate is hashed."""
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '06_Ket_qua_thuc_nghiem' / 'environment_manifest.json'


def cmd(args):
    if not shutil.which(args[0]):
        return 'not available'
    result = subprocess.run(args, capture_output=True, text=True, timeout=20)
    return (result.stdout or result.stderr).strip()[:400] or f'exit={result.returncode}'


def sha256(path):
    file = ROOT / path
    return hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else None


def main():
    report = {
        'recorded_utc': datetime.now(timezone.utc).isoformat(),
        'platform': platform.platform(),
        'python': sys.version,
        'docker': cmd(['docker', '--version']),
        'docker_compose': cmd(['docker', 'compose', 'version']),
        'webgoat_image': 'webgoat/webgoat:v2026.5',
        'webgoat_digest_local': cmd(['docker', 'image', 'inspect', 'webgoat/webgoat:v2026.5',
                                     '--format', '{{json .RepoDigests}}']),
        'webgoat_source': 'https://owasp.org/www-project-webgoat/',
        'webgoat_license': 'Check upstream repository license at experiment time',
        'checksum': {
            'public_test_certificate': sha256('certs/localhost.crt'),
            'lab_server': sha256('05_Source_code/https_lab/server.py'),
            'compose': sha256('docker-compose.yml'),
            'requirements': sha256('requirements-dt032.txt'),
        },
        'seed': 'N/A: deterministic synthetic configurations; no random sampling',
        'data_split': 'N/A: there is no ML training, validation or test split',
        'constraints': 'localhost-owned lab only; no unapproved scanning',
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Wrote', OUT)


if __name__ == '__main__':
    main()
