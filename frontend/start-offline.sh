#!/bin/sh
set -e

DIST_DIR=/app/dist

echo "[offline] Exporting data from ${GATEWAY_URL:-http://gateway:8000}..."
node scripts/export-offline-data.cjs || echo "[offline] WARN: data export failed — /data not available"

echo "[offline] Starting preview server..."
exec npm run preview -- --host 0.0.0.0 --port 8501
