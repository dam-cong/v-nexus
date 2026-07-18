#!/bin/bash
set -e

echo "========================================="
echo "  V-Nexus Tutor - Server Setup Script"
echo "========================================="

PROJECT_DIR="/opt/sourecode/v-nexus"

# 1. Check if project exists, if not create directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo "[1/5] Creating project directory..."
    mkdir -p $PROJECT_DIR
else
    echo "[1/5] Project directory exists."
fi

cd $PROJECT_DIR

# 2. Create docs/data directory (required by Dockerfile)
echo "[2/5] Ensuring docs/data/ directory exists..."
mkdir -p docs/data

# 3. Check if JSON files exist, if not warn user
MISSING=0
for f in question-bank.json placement-test.json survey-results.json knowledge-graph.json; do
    if [ ! -f "docs/data/$f" ]; then
        echo "  WARNING: docs/data/$f not found!"
        MISSING=1
    fi
done

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "  Please copy the following files to $PROJECT_DIR/docs/data/:"
    echo "    - question-bank.json"
    echo "    - placement-test.json"
    echo "    - survey-results.json"
    echo "    - knowledge-graph.json"
    echo ""
    echo "  You can use rsync from local:"
    echo "    rsync -avz /home/hiendc/Documents/VAIC-2026/v-nexus/docs/data/ root@<server-ip>:$PROJECT_DIR/docs/data/"
    echo ""
    read -p "  Press Enter after copying files, or type 'skip' to continue without them: " USER_INPUT
    if [ "$USER_INPUT" != "skip" ]; then
        echo "  Resuming..."
    fi
fi

# 4. Stop old containers
echo "[3/5] Stopping old containers..."
docker-compose down 2>/dev/null || true

# 5. Build and start
echo "[4/5] Building and starting containers..."
docker-compose build
docker-compose up -d

# 6. Show status
echo "[5/5] Container status:"
docker-compose ps

echo ""
echo "========================================="
echo "  Setup complete!"
echo "========================================="
echo ""
echo "  Frontend:    http://localhost:8081"
echo "  Gateway API: http://localhost:8000"
echo "  MCP Server:  http://localhost:8500"
echo "  Database:    localhost:5434"
echo ""
echo "  Login: admin@vnexus.vn / 123456"
echo ""
echo "  To rebuild:  docker-compose build && docker-compose up -d"
echo "  To stop:     docker-compose down"
echo "  To view logs: docker-compose logs -f"
echo ""
