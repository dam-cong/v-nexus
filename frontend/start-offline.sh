#!/bin/sh
set -e

DIST_DIR=/app/dist

echo "[offline] Exporting data from ${GATEWAY_URL:-http://gateway:8000}..."

# Gateway có thể chưa sẵn sàng nhận request ngay khi container này khởi động
# (chỉ mới "started", chưa chắc app đã load xong route/DB pool) — thử lại vài
# lần thay vì chấp nhận thất bại ngay lần đầu, tránh /data trống vĩnh viễn cho
# tới khi ai đó restart container thủ công.
ATTEMPTS=6
DELAY=5
i=1
while [ "$i" -le "$ATTEMPTS" ]; do
  if node scripts/export-offline-data.cjs; then
    break
  fi
  if [ "$i" -eq "$ATTEMPTS" ]; then
    echo "[offline] WARN: data export failed after ${ATTEMPTS} attempts — /data not available"
  else
    echo "[offline] Export attempt ${i}/${ATTEMPTS} failed, retrying in ${DELAY}s..."
    sleep "$DELAY"
  fi
  i=$((i + 1))
done

echo "[offline] Starting preview server..."
exec npm run preview -- --host 0.0.0.0 --port 8501
