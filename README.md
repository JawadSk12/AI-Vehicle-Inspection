# CAPVIA AI — Automated Vehicle Quality Inspection System

<div align="center">

![CAPVIA AI Banner](https://img.shields.io/badge/CAPVIA_AI-Production_Ready-2563EB?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIi8+PC9zdmc+)

**Enterprise-grade AI-powered paint defect detection and damage assessment for automotive vehicles.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![RT-DETR v2](https://img.shields.io/badge/AI_Model-RT--DETR_v2_Large-FF6B35)](https://github.com/lyuwenyu/RT-DETR)

</div>

---

## 🚗 Overview

CAPVIA AI is a **production-ready, full-stack enterprise SaaS platform** that uses state-of-the-art computer vision to automatically detect paint defects on vehicle surfaces. Built as a final-year engineering capstone project, it demonstrates a complete AI/ML pipeline from raw data to actionable business insights — complete with cost estimation in Indian Rupees, PDF report generation, and a stunning dark-mode SaaS UI.

### 🎯 Key Capabilities

| Feature | Details |
|---|---|
| **AI Detection** | RT-DETR v2 Large (Real-Time DEtection TRansformer) — outperforms YOLO on detection accuracy |
| **Glare Filtering** | Intelligent glare/reflection suppression to eliminate false positives |
| **Measurement Engine** | Sub-millimetre defect size, area, perimeter calculation from pixel coordinates |
| **Severity Scoring** | 5-tier AI severity engine (Minor → Critical) based on area, count, confidence, class |
| **Cost Estimation** | Repair cost in ₹ INR with range, estimated value, and time required |
| **PDF Reports** | Professional branded PDF reports with QR codes, images, findings table |
| **JWT Auth** | Secure role-based authentication with access + refresh tokens |
| **Full REST API** | OpenAPI-documented FastAPI backend with async SQLAlchemy ORM |
| **Dark SaaS UI** | React + TypeScript + TailwindCSS premium glassmorphism design |
| **One-Click Deploy** | Docker Compose with PostgreSQL, Backend, Frontend, Nginx reverse proxy |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CAPVIA AI                             │
│              Automated Vehicle Quality Inspection            │
└─────────────────────────────────────────────────────────────┘

Input: Vehicle Image (JPG/PNG/WEBP)
           │
           ▼
   ┌───────────────┐     ┌──────────────────┐
   │  FastAPI REST │────▶│  Preprocessing   │
   │   Backend     │     │  (OpenCV resize) │
   └───────────────┘     └────────┬─────────┘
           │                      │
           │              ┌───────▼───────────┐
           │              │  RT-DETR v2 Large │
           │              │  Object Detection │
           │              │  (Ultralytics)    │
           │              └───────┬───────────┘
           │                      │
           │              ┌───────▼───────────┐
           │              │  Glare Filter     │
           │              │  (HSV + texture)  │
           │              └───────┬───────────┘
           │                      │
           │              ┌───────▼───────────┐
           │              │  Measurement      │
           │              │  Engine (mm²)     │
           │              └───────┬───────────┘
           │                      │
           │              ┌───────▼───────────┐
           │              │  Severity Engine  │
           │              │  + Cost Estimator │
           │              └───────┬───────────┘
           │                      │
           ▼                      ▼
   ┌───────────────┐     ┌──────────────────┐
   │  PostgreSQL   │     │  PDF Report      │
   │  Database     │     │  (ReportLab+QR)  │
   └───────────────┘     └──────────────────┘
           │
           ▼
   ┌───────────────┐
   │  React + Vite │
   │  TypeScript   │
   │  TailwindCSS  │
   └───────────────┘
```

---

## 📁 Project Structure

```
Paint_defect/
├── backend/                          # FastAPI Python backend
│   ├── app/
│   │   ├── config.py                 # Pydantic Settings
│   │   ├── database.py               # Async SQLAlchemy engine
│   │   ├── main.py                   # FastAPI app + lifespan
│   │   ├── models/                   # ORM models (User, Inspection, Report)
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── routes/                   # API routes (auth, predict, inspections, reports, dashboard)
│   │   ├── services/                 # Business logic (auth, severity, cost, predict)
│   │   ├── utils/                    # Image utils, glare filter, measurement, calibration
│   │   └── reports/                  # ReportLab PDF generator
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                         # React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── types/                    # TypeScript interfaces
│   │   ├── lib/                      # API client, auth context, utils
│   │   ├── components/Layout/        # Sidebar, Header, Layout
│   │   └── pages/                    # Dashboard, NewInspection, ResultPage, History, Profile
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── Dockerfile
├── ai_model/
│   ├── train_rtdetr.py               # RT-DETR v2 training script
│   ├── predict.py                    # Standalone inference
│   ├── dataset.yaml                  # Dataset config for Ultralytics
│   └── weights/                      # Trained model weights
├── dataset/
│   └── audit_dataset.py              # Dataset quality audit tool
├── car-scratches-1/                  # Dataset (train/valid/test)
│   ├── train/ valid/ test/
│   └── data.yaml
├── tests/                            # Pytest test suite (20+ tests)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_api.py
│   ├── test_severity.py
│   ├── test_measurement.py
│   └── test_glare.py
├── storage/                          # Auto-created media storage
│   ├── uploads/ results/ reports/ masks/
├── nginx/nginx.conf                  # Nginx reverse proxy config
├── docker-compose.yml                # Full-stack Docker orchestration
└── .env.example                      # Environment variable template
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop (for production deployment)
- CUDA GPU (optional, for faster inference)

---

### Option 1: Local Development

**1. Set up backend environment**
```bash
cd backend
pip install -r requirements.txt
```

**2. Copy and configure environment variables**
```bash
cp .env.example .env
# Edit .env — set JWT_SECRET and DATABASE_URL
```

**3. Start the backend**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

**4. Start the frontend**
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

**5. Access the app:**
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

### Option 2: Docker Compose (Production)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Place your trained model weights
cp runs/detect/car_scratches_model-2/weights/best.pt ai_model/weights/best_rtdetr.pt

# 3. Launch the full stack
docker compose up --build -d

# → App running at http://localhost
# → API at http://localhost/api/docs
```

---

## 🤖 Training RT-DETR v2

```bash
# Run training (GPU recommended)
python ai_model/train_rtdetr.py --epochs 150 --imgsz 1024 --batch -1

# Options:
#   --epochs    Number of training epochs (default: 150)
#   --imgsz     Input image size (default: 1024)
#   --batch     Batch size (-1 = auto)
#   --lr0       Initial learning rate (default: 1e-4)
#   --resume    Resume from last checkpoint
#   --device    GPU device (e.g. 0, cpu)

# Weights saved to:
# ai_model/weights/best_rtdetr.pt  ← best checkpoint
# ai_model/weights/best.onnx       ← ONNX export
```

**Training configuration:**
- Optimizer: AdamW with cosine LR scheduling
- Data augmentation: FlipLR, FlipUD, Rotation, HSV, Mosaic, Mixup
- Early stopping: 20 epochs patience
- Export: ONNX for production deployment

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov aiosqlite httpx

# Run full test suite with coverage
pytest tests/ -v --cov=backend/app --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v
pytest tests/test_severity.py -v
```

**Test coverage:**
- `test_auth.py` — JWT registration, login, token validation
- `test_api.py` — Full API flow: predict, list, dashboard endpoints
- `test_severity.py` — Severity scoring algorithm edge cases
- `test_measurement.py` — Bounding box measurement accuracy
- `test_glare.py` — Glare detection algorithm

---

## 📊 Dataset Audit

```bash
python dataset/audit_dataset.py --root car-scratches-1
# → Generates dataset/dataset_report.html with visual analysis
```

**Dataset statistics:**
| Split | Images |
|---|---|
| Train | 1,366 |
| Validation | 195 |
| Test | 97 |
| **Total** | **1,658+** |

---

## 🔑 API Reference

All endpoints are documented at `/api/docs` (Swagger UI) and `/api/redoc`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Create new account |
| `POST` | `/api/auth/login` | Login, receive JWT tokens |
| `GET` | `/api/auth/profile` | Get current user profile |
| `POST` | `/api/predict` | Upload image, run AI detection |
| `GET` | `/api/inspections` | List inspections (paginated) |
| `GET` | `/api/inspections/{id}` | Get single inspection |
| `DELETE` | `/api/inspections/{id}` | Delete inspection + files |
| `GET` | `/api/inspections/{id}/csv` | Export inspection as CSV |
| `POST` | `/api/reports/{id}/generate` | Generate PDF report |
| `GET` | `/api/reports/{id}` | Download PDF report |
| `GET` | `/api/dashboard` | Analytics dashboard data |
| `GET` | `/api/health` | Health check |

---

## 🎨 UI Features

- **Dark glassmorphism design** with animated gradients
- **Animated sidebar** with smooth collapse/expand
- **Drag & drop image upload** with live preview
- **Real-time progress bar** during AI analysis
- **Interactive Recharts** dashboard (area chart, bar chart, pie chart)
- **Severity gauge SVG** with animated fill
- **Image comparison toggle** (original vs annotated)
- **Responsive pagination** for inspection history
- **Delete confirmation modal** with framer-motion animations
- **PDF download** directly from the browser
- **CSV export** for each inspection

---

## 🛡️ Security

- **JWT** access tokens (30 min) + refresh tokens (7 days)
- **Bcrypt** password hashing (cost factor 12)
- **CORS** whitelist configuration
- **File validation** — type check + size limit (20 MB)
- **User isolation** — users only see their own inspections
- **Async SQLAlchemy** — no blocking DB calls

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **AI Model** | RT-DETR v2 Large (Ultralytics 8.3) |
| **Computer Vision** | OpenCV, NumPy, Pillow |
| **Backend Framework** | FastAPI 0.115 + Uvicorn |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Database** | PostgreSQL 16 + asyncpg |
| **Authentication** | python-jose JWT + passlib bcrypt |
| **PDF Reports** | ReportLab + qrcode |
| **Frontend Framework** | React 18 + TypeScript + Vite |
| **Styling** | TailwindCSS 3 |
| **State Management** | TanStack Query v5 |
| **Charts** | Recharts |
| **Animations** | Framer Motion |
| **Routing** | React Router v6 |
| **HTTP Client** | Axios |
| **Container** | Docker + Docker Compose |
| **Reverse Proxy** | Nginx 1.27 |
| **Testing** | Pytest + pytest-asyncio + httpx |

---

## 👨‍💻 Developer

**Jawad Shaikh** — Final Year Engineering Project

Built with ❤️ using Python 3.12, FastAPI, React, RT-DETR v2, and Docker.

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.
