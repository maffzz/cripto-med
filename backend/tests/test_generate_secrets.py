import base64
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_generate_env_replaces_sample_secrets_with_random_values(tmp_path):
    root = tmp_path / "project"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy(PROJECT_ROOT / "scripts/generate_secrets.py", scripts)
    example_path = PROJECT_ROOT / ".env.example"
    shutil.copy(example_path, root)
    example = dict(
        line.split("=", 1)
        for line in example_path.read_text().splitlines()
        if "=" in line and not line.startswith("#")
    )
    sample_keys = {
        base64.urlsafe_b64decode(entry.split(":", 1)[1] + "=" * (-len(entry.split(":", 1)[1]) % 4))
        for entry in example["ENC_KEYS"].split(",")
    }

    result = subprocess.run(
        [sys.executable, str(scripts / "generate_secrets.py"), "--generate-env"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )

    generated = dict(
        line.split("=", 1)
        for line in (root / ".env").read_text().splitlines()
        if "=" in line and not line.startswith("#")
    )
    key_entries = generated["ENC_KEYS"].split(",")

    assert [entry.split(":", 1)[0] for entry in key_entries] == ["v1", "v2"]
    for entry in key_entries:
        encoded_key = entry.split(":", 1)[1]
        decoded_key = base64.urlsafe_b64decode(encoded_key + "=" * (-len(encoded_key) % 4))
        assert len(decoded_key) == 32
        assert decoded_key not in sample_keys

    for name in (
        "POSTGRES_PASSWORD",
        "APP_DB_PASSWORD",
        "JWT_SECRET",
        "BACKUP_PASSPHRASE",
        "DEMO_PASSWORD_ADMIN",
        "DEMO_PASSWORD_DOCTOR",
        "DEMO_PASSWORD_ADMINISTRATIVO",
        "DEMO_PASSWORD_AUDITOR",
        "DEMO_PASSWORD_PACIENTE",
    ):
        assert "cambia-esto" not in generated[name]
        assert generated[name] not in result.stdout

    assert urlsplit(generated["DATABASE_URL"]).password == generated["POSTGRES_PASSWORD"]
    assert urlsplit(generated["OWNER_DATABASE_URL"]).password == generated["POSTGRES_PASSWORD"]

