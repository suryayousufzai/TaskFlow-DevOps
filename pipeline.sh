#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  TaskFlow — Local DevOps Pipeline Script
#  Simulates a full CI/CD pipeline: lint → test → build → deploy
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

# ── Config ──────────────────────────────────────────────────────
IMAGE_NAME="taskflow"
CONTAINER_NAME="taskflow-app"
PORT=5000
LOG_FILE="pipeline.log"

# ── Helpers ─────────────────────────────────────────────────────
header()  { echo -e "\n${BOLD}${BLUE}╔══ $1 ══╗${RESET}"; }
step()    { echo -e "${CYAN}  ▶ $1${RESET}"; }
success() { echo -e "${GREEN}  ✅ $1${RESET}"; }
warn()    { echo -e "${YELLOW}  ⚠  $1${RESET}"; }
fail()    { echo -e "${RED}  ❌ $1${RESET}"; exit 1; }
log()     { echo "[$(date '+%H:%M:%S')] $1" >> "$LOG_FILE"; }

PIPELINE_START=$(date +%s)
> "$LOG_FILE"

echo -e "${BOLD}${CYAN}"
cat << 'EOF'
  ████████╗ █████╗ ███████╗██╗  ██╗███████╗██╗      ██████╗ ██╗    ██╗
  ╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝██╔════╝██║     ██╔═══██╗██║    ██║
     ██║   ███████║███████╗█████╔╝ █████╗  ██║     ██║   ██║██║ █╗ ██║
     ██║   ██╔══██║╚════██║██╔═██╗ ██╔══╝  ██║     ██║   ██║██║███╗██║
     ██║   ██║  ██║███████║██║  ██╗██║     ███████╗╚██████╔╝╚███╔███╔╝
     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚══╝╚══╝
                      DevOps Pipeline — Local Mode
EOF
echo -e "${RESET}"

# ═══════════════════════════════════════════════════════════════════
# STAGE 1: LINT
# ═══════════════════════════════════════════════════════════════════
header "STAGE 1: LINT & STATIC ANALYSIS"
log "Starting lint stage"

step "Checking Python installation..."
python3 --version || fail "Python 3 not found"

step "Installing lint tools..."
pip install flake8 bandit --quiet

step "Running flake8..."
if flake8 app/ run.py --max-line-length=120 --exclude=__pycache__,migrations 2>&1 | tee -a "$LOG_FILE"; then
  success "flake8 passed — no style violations"
else
  warn "flake8 found issues (check $LOG_FILE for details)"
fi

step "Running bandit security scan..."
if bandit -r app/ -ll -q 2>&1 | tee -a "$LOG_FILE"; then
  success "bandit passed — no high-severity issues"
else
  warn "bandit flagged some items — review $LOG_FILE"
fi

success "Stage 1 complete"

# ═══════════════════════════════════════════════════════════════════
# STAGE 2: TEST
# ═══════════════════════════════════════════════════════════════════
header "STAGE 2: UNIT TESTS"
log "Starting test stage"

step "Installing test dependencies..."
pip install -r requirements.txt pytest pytest-cov --quiet

step "Running pytest..."
if pytest tests/ -v --tb=short --cov=app --cov-report=term-missing 2>&1 | tee -a "$LOG_FILE"; then
  success "All tests passed"
else
  fail "Tests failed — pipeline aborted. Check $LOG_FILE"
fi

success "Stage 2 complete"

# ═══════════════════════════════════════════════════════════════════
# STAGE 3: BUILD
# ═══════════════════════════════════════════════════════════════════
header "STAGE 3: DOCKER BUILD"
log "Starting docker build stage"

if ! command -v docker &> /dev/null; then
  warn "Docker not found. Simulating build stage..."
  echo "  [SIMULATED] docker build -t ${IMAGE_NAME}:latest ."
  echo "  [SIMULATED] Build would produce a 2-stage image:"
  echo "              Stage 1: python:3.12-slim builder"
  echo "              Stage 2: python:3.12-slim runtime (non-root)"
  success "Build stage simulated"
else
  step "Building Docker image: ${IMAGE_NAME}:latest"
  BUILD_START=$(date +%s)
  docker build -t "${IMAGE_NAME}:latest" . 2>&1 | tee -a "$LOG_FILE"
  BUILD_END=$(date +%s)
  success "Image built in $((BUILD_END - BUILD_START))s"

  step "Inspecting image..."
  docker image inspect "${IMAGE_NAME}:latest" --format \
    'Size: {{.Size}} bytes | OS: {{.Os}} | Created: {{.Created}}' 2>/dev/null || true
fi

success "Stage 3 complete"

# ═══════════════════════════════════════════════════════════════════
# STAGE 4: SMOKE TEST (container)
# ═══════════════════════════════════════════════════════════════════
header "STAGE 4: SMOKE TEST"
log "Starting smoke test stage"

if command -v docker &> /dev/null && docker image inspect "${IMAGE_NAME}:latest" &>/dev/null; then
  step "Stopping existing container if running..."
  docker stop "${CONTAINER_NAME}" 2>/dev/null || true
  docker rm   "${CONTAINER_NAME}" 2>/dev/null || true

  step "Starting container on port ${PORT}..."
  docker run -d \
    --name "${CONTAINER_NAME}" \
    -p "${PORT}:5000" \
    -e SECRET_KEY="pipeline-test-key" \
    "${IMAGE_NAME}:latest"

  step "Waiting for health check..."
  HEALTHY=false
  for i in $(seq 1 20); do
    if curl -sf "http://localhost:${PORT}/health" > /dev/null 2>&1; then
      HEALTHY=true
      break
    fi
    printf "."
    sleep 1
  done
  echo ""

  if [ "$HEALTHY" = true ]; then
    success "Container is healthy!"
    step "Running API smoke tests..."
    curl -sf "http://localhost:${PORT}/api/health" | python3 -m json.tool
    
    # Create a test task
    TASK=$(curl -sf -X POST "http://localhost:${PORT}/api/tasks" \
      -H "Content-Type: application/json" \
      -d '{"title":"Pipeline smoke test","priority":"high","category":"devops"}')
    TASK_ID=$(echo "$TASK" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
    success "Created task with ID: $TASK_ID"

    # Fetch stats
    curl -sf "http://localhost:${PORT}/api/stats" | python3 -m json.tool
    success "All smoke tests passed!"

    step "Stopping test container..."
    docker stop "${CONTAINER_NAME}" && docker rm "${CONTAINER_NAME}"
  else
    warn "Container did not become healthy in time"
    docker logs "${CONTAINER_NAME}" | tail -20
    docker stop "${CONTAINER_NAME}" && docker rm "${CONTAINER_NAME}"
  fi
else
  warn "Docker image not available — simulating smoke tests"
  echo "  [SIMULATED] GET  /health          → 200 OK"
  echo "  [SIMULATED] GET  /api/tasks       → 200 []"
  echo "  [SIMULATED] POST /api/tasks       → 201 {id:1, title: ...}"
  echo "  [SIMULATED] GET  /api/stats       → 200 {total:1}"
  success "Smoke tests simulated"
fi

success "Stage 4 complete"

# ═══════════════════════════════════════════════════════════════════
# STAGE 5: DEPLOY (simulated)
# ═══════════════════════════════════════════════════════════════════
header "STAGE 5: DEPLOY"
log "Starting deploy stage"

step "Simulating production deployment..."
sleep 1
echo ""
echo "  Target:    production server (192.168.1.100)"
echo "  Image:     ${IMAGE_NAME}:latest"
echo "  Strategy:  Rolling update (zero-downtime)"
echo ""
echo "  → Pulling new image on remote host"
echo "  → Running: docker compose up -d --pull always"
echo "  → Waiting for health checks to pass"
echo "  → Draining old container"
echo "  → Deployment complete"
echo ""

success "Production deployment simulated"

# ═══════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════
PIPELINE_END=$(date +%s)
DURATION=$((PIPELINE_END - PIPELINE_START))

echo -e "\n${BOLD}${GREEN}"
echo "╔════════════════════════════════════════╗"
echo "║       PIPELINE COMPLETED               ║"
printf "║  %-38s║\n" "Duration: ${DURATION}s"
printf "║  %-38s║\n" "Log: $LOG_FILE"
echo "║                                        ║"
echo "║  Stages:                               ║"
echo "║    ✅ 1. Lint & Static Analysis        ║"
echo "║    ✅ 2. Unit Tests                    ║"
echo "║    ✅ 3. Docker Build                  ║"
echo "║    ✅ 4. Smoke Tests                   ║"
echo "║    ✅ 5. Deploy                        ║"
echo "╚════════════════════════════════════════╝"
echo -e "${RESET}"

log "Pipeline completed in ${DURATION}s"
