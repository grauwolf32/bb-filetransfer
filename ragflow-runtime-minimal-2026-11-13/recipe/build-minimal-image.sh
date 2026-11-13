#!/usr/bin/env bash
set -euo pipefail
umask 077
LAB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
IMAGE_TAG="localhost/ragflow-lab-minimal:v1.0.0-rc3-20261113"

# Send only this tiny context, never .env, credentials or the lab data.
# Squash inherited layers as well, so deleted Python/Vim files are not
# retained in the derivative image's lower layers. Keep the base for rollback.
exec "$LAB_DIR/lab.sh" podman build \
    --platform linux/arm64 --pull=never --network none \
    --layers=false --squash-all --format docker \
    --tag "$IMAGE_TAG" \
    --file "$LAB_DIR/config/minimal-image/Containerfile" \
    "$LAB_DIR/config/minimal-image"
