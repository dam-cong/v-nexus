#!/bin/bash
# Deploy an toàn cho server production — dùng cho MỌI lần deploy sau lần setup đầu tiên.
#
# Tại sao không dùng "docker-compose up -d --build --force-recreate":
#   docker-compose v1.29.2 (bản standalone, không phải plugin "docker compose" v2) có bug
#   KeyError: 'ContainerConfig' khi lệnh "recreate" container đã tồn tại (xảy ra với cả
#   --force-recreate lẫn "up -d" bình thường khi compose tự phát hiện image đổi và quyết
#   định "Recreating"). Cách né triệt để: LUÔN dừng + xoá container cũ trước bằng
#   "docker-compose down", để "up -d" sau đó chỉ còn việc CREATE (không bao giờ RECREATE).
#
# Script này cũng không cần lo schema DB lệch nữa: db/connector.py:init_db() tự chạy
# ALTER TABLE ADD COLUMN IF NOT EXISTS cho mọi cột mới mỗi khi gateway khởi động — nhưng
# CHỈ khi ai đó nhớ cập nhật danh sách đó khi thêm cột mới vào db/models.py (xem ghi chú
# cuối file này).

set -e

PROJECT_DIR="/opt/sourecode/v-nexus"
cd "$PROJECT_DIR"

echo "========================================="
echo "  V-NEXUS SCHOOL - Deploy"
echo "========================================="

echo "[1/5] Kéo code mới nhất..."
git pull

echo "[2/5] Build lại image (chỉ rebuild service có thay đổi, nhờ layer cache)..."
docker-compose build

echo "[3/5] Dừng và xoá container cũ (tránh bug 'ContainerConfig' của docker-compose khi recreate)..."
docker-compose down

echo "[4/5] Khởi động lại toàn bộ (chỉ CREATE, không RECREATE)..."
docker-compose up -d

echo "[5/5] Kiểm tra sức khỏe từng service..."
sleep 5

check_health() {
  local name="$1" url="$2" tries=10
  for i in $(seq 1 $tries); do
    if curl -sf "$url" > /dev/null 2>&1; then
      echo "  ✓ $name OK"
      return 0
    fi
    sleep 3
  done
  echo "  ✗ $name KHÔNG phản hồi sau $((tries * 3))s — xem log:"
  echo "      docker-compose logs --tail 50 $name"
  return 1
}

FAILED=0
check_health gateway  "http://localhost:8000/health" || FAILED=1
check_health frontend "http://localhost:8081/"        || FAILED=1

echo ""
docker-compose ps

echo ""
if [ "$FAILED" -eq 1 ]; then
  echo "========================================="
  echo "  DEPLOY CÓ LỖI — xem log ở trên trước khi báo đã xong."
  echo "========================================="
  exit 1
else
  echo "========================================="
  echo "  Deploy xong, mọi service khỏe mạnh."
  echo "========================================="
fi

echo ""
echo "  Nếu vẫn gặp lỗi 'column ... does not exist' trong log gateway:"
echo "  -> nghĩa là ai đó thêm cột mới vào db/models.py mà QUÊN thêm dòng"
echo "     'ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...' tương ứng vào"
echo "     hàm init_db() trong db/connector.py. Thêm dòng đó vào code (không phải"
echo "     chạy SQL tay trên server), commit, rồi deploy lại — để lần sau tự động,"
echo "     mọi môi trường (dev máy khác, production) đều tự vá khi gateway khởi động."
