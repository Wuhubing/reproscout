"""Configure Inspect's Docker provider; keep the model outside the container."""

from pathlib import Path

import yaml

from .tasks import IMAGE


def compose_file(run: Path, image: str = IMAGE) -> Path:
    path = run / "compose.yaml"
    config = {
        "services": {
            "default": {
                "image": image,
                "platform": "linux/amd64",
                "init": True,
                "command": ["bash", "-c", "sleep infinity"],
                "working_dir": "/code",
                "network_mode": "none",
                "cap_drop": ["ALL"],
                "security_opt": ["no-new-privileges:true"],
                "pids_limit": 128,
                "mem_limit": "2g",
                "cpus": 2,
                "environment": {
                    "OPENBLAS_NUM_THREADS": "1",
                    "OMP_NUM_THREADS": "1",
                    "PYTHONIOENCODING": "utf-8",
                },
            }
        }
    }
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path


SETUP = """#!/bin/bash
set -euo pipefail
rm -rf /results /code /data
mkdir -p /results /code /data
tar -xf /tmp/reproscout-input.tar -C /
rm /tmp/reproscout-input.tar
"""
