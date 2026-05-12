# TaskFlow — Project

A production-grade **Task Manager** built with Python Flask, demonstrating a complete DevOps workflow: development → version control → containerization → CI/CD → Infrastructure as Code.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Developer Machine                    │
│                                                         │
│  ┌──────────┐    git push    ┌──────────────────────┐  │
│  │  VS Code  │ ─────────────▶│   GitHub Repository   │  │
│  └──────────┘                └──────────┬───────────┘  │
│                                         │               │
│                               GitHub Actions CI/CD      │
│                               ┌─────────▼───────────┐  │
│                               │ 1. Lint (flake8)     │  │
│                               │ 2. Test (pytest)     │  │
│                               │ 3. Build (Docker)    │  │
│                               │ 4. Push (GHCR)       │  │
│                               │ 5. Deploy            │  │
│                               └─────────┬───────────┘  │
│                                         │               │
│  ┌──────────────────────────────────────▼───────────┐  │
│  │              Docker Container                     │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Flask App (Gunicorn, 2 workers)           │  │  │
│  │  │  ├── /          → HTML UI                  │  │  │
│  │  │  ├── /api/tasks → REST API (CRUD)          │  │  │
│  │  │  └── /api/stats → Dashboard stats          │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  │  SQLite DB (persisted via Docker Volume)          │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Option A — Run Directly

```bash
# Clone and install
git clone https://github.com/youruser/taskflow.git
cd taskflow
pip install -r requirements.txt

# Run
python run.py

# Open browser
open http://localhost:5000
```

### Option B — Docker

```bash
# Build and run
docker build -t taskflow .
docker run -d -p 5000:5000 -v taskflow-data:/data taskflow

# Or with Docker Compose
docker compose up -d
```

### Option C — Terraform (Infrastructure as Code)

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## Project Structure

```
taskflow/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── models.py          # SQLAlchemy models
│   ├── api.py             # REST API blueprint (/api/*)
│   ├── routes.py          # Main routes
│   └── templates/
│       └── index.html     # Single-page UI
│
├── tests/
│   ├── conftest.py
│   └── test_api.py        # 20+ pytest unit tests
│
├── terraform/
│   ├── main.tf            # IaC — Docker-based infrastructure
│   └── terraform.tfvars
│
├── ansible/
│   ├── playbook.yml       # Server provisioning playbook
│   └── inventory.yml
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml      # GitHub Actions pipeline
│
├── Dockerfile             # Multi-stage production build
├── docker-compose.yml     # Local orchestration
├── pipeline.sh            # Shell-based local pipeline
├── requirements.txt
└── run.py                 # Entry point
```

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks (filterable) |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/:id` | Get single task |
| PUT | `/api/tasks/:id` | Update task |
| DELETE | `/api/tasks/:id` | Delete task |
| PATCH | `/api/tasks/:id/toggle` | Toggle completed |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/health` | Health check |

### Example — Create a task

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write project report",
    "priority": "high",
    "category": "school",
    "due_date": "2025-12-01T23:59:00"
  }'
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## CI/CD Pipeline

### GitHub Actions (automated)

Triggered on every `git push`:

1. **Lint** — flake8 style check + bandit security scan  
2. **Test** — pytest with coverage report  
3. **Build** — Docker multi-stage image build  
4. **Smoke Test** — Container health + API validation  
5. **Push** — Push image to GitHub Container Registry  
6. **Deploy** — Rolling deploy to production  

### Shell Pipeline (local)

```bash
chmod +x pipeline.sh
./pipeline.sh
```

---

## Infrastructure as Code

### Terraform

```bash
cd terraform
terraform init      # Download providers
terraform plan      # Preview changes
terraform apply     # Apply infrastructure
terraform destroy   # Tear down
```

Resources created:
- Docker network (isolated)
- Docker volume (persistent data)
- Docker container (app)
- Local `.env` file (generated secrets)

### Ansible

```bash
cd ansible
ansible-playbook -i inventory.yml playbook.yml
```

Handles: Docker install, user setup, app deployment, systemd service, firewall rules, log rotation.

---

## Tools Used

| Tool | Purpose |
|------|---------|
| Python / Flask | Web framework |
| SQLAlchemy | ORM + database |
| Gunicorn | Production WSGI server |
| Git / GitHub | Version control |
| Docker | Containerization |
| GitHub Actions | CI/CD automation |
| Terraform | Infrastructure as Code |
| Ansible | Configuration management |
| pytest | Unit testing |
| flake8 / bandit | Lint & security |

---

## Git Workflow

```bash
# Feature branches
git checkout -b feature/add-due-dates
# ... develop ...
git commit -m "feat: add due date support to task model"
git push origin feature/add-due-dates
# Open PR → CI runs → merge to main → auto deploy
```

---


