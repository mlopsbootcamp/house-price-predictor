#!/usr/bin/env python3
"""Resolve the AWS region for the Terraform AWS provider."""

import json
import os
import subprocess
import sys

region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
if not region:
    try:
        result = subprocess.run(
            ["aws", "configure", "get", "region"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print("AWS CLI is required to resolve the configured region", file=sys.stderr)
        sys.exit(1)
    if result.returncode not in (0, 1):
        print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    region = result.stdout.strip() or "us-east-1"

print(json.dumps({"region": region}))
