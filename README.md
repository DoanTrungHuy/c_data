# 🇻🇳 C_Data — Nền Tảng Tổng Hợp Việc Làm Việt Nam

> **Tìm việc làm phù hợp trên khắp Việt Nam — hoàn toàn miễn phí**

C_Data tự động thu thập tin tuyển dụng từ nhiều nguồn khác nhau (TopCV, VietnamWorks, CareerBuilder, TimViecNhanh...) và tập trung vào một website duy nhất, giúp mọi người ở Việt Nam — đặc biệt ở các tỉnh/thành nhỏ — dễ dàng tìm được việc làm phù hợp.

## 🚀 Khởi Chạy Nhanh

### Yêu cầu
- [Docker](https://www.docker.com/get-started) & Docker Compose
- Hoặc: Python 3.11+ & Node.js 20+

### Chạy với Docker (Khuyến nghị)

```bash
# 1. Clone project
git clone <repo-url> c_data
cd c_data

# 2. Tạo file .env
cp .env.example .env

# 3. Khởi chạy toàn bộ
docker compose up --build

# 4. Truy cập
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Chạy thủ công (Development)

#### Backend
```bash
cd backend

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Cài dependencies
pip install -r requirements.txt

# Cấu hình môi trường
set DATABASE_URL=postgresql+asyncpg://cdata_user:cdata_secret_2024@localhost:5432/cdata
set DATABASE_URL_SYNC=postgresql://cdata_user:cdata_secret_2024@localhost:5432/cdata
set REDIS_URL=redis://localhost:6379/0

# Chạy migration
alembic upgrade head

# Khởi động server
uvicorn app.main:app --reload --port 8000
```

#### Crawler (trong terminal riêng)
```bash
cd backend

# Chạy Celery Worker
celery -A app.worker worker --loglevel=info

# Chạy Celery Beat (scheduler)
celery -A app.worker beat --loglevel=info
```

#### Frontend
```bash
cd frontend

# Cài dependencies
npm install

# Khởi động
npm run dev
# Truy cập: http://localhost:3000
```

## 📁 Cấu Trúc Dự Án

```
c_data/
├── docker-compose.yml           # Orchestration tất cả services
├── .env.example                 # Template biến môi trường
│
├── backend/                     # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── worker.py           # Celery workers & scheduler
│   │   ├── core/               # Config, database setup
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic layer
│   │   ├── api/routes/         # API endpoints
│   │   └── data/               # Seed data (63 tỉnh/thành)
│   ├── crawlers/               # Job crawlers
│   │   ├── base.py             # Abstract base crawler
│   │   ├── topcv.py            # TopCV crawler
│   │   ├── vietnamworks.py     # VietnamWorks crawler
│   │   ├── careerbuilder.py    # CareerBuilder VN crawler
│   │   ├── timviecnhanh.py     # TimViecNhanh crawler
│   │   ├── scheduler.py        # Crawler scheduling
│   │   └── utils.py            # Shared utilities
│   └── alembic/                # Database migrations
│
└── frontend/                    # Next.js 14 Frontend
    ├── src/
    │   ├── app/                # Pages (App Router)
    │   │   ├── page.tsx        # Trang chủ
    │   │   ├── jobs/           # Danh sách & chi tiết việc làm
    │   │   └── about/          # Giới thiệu
    │   ├── components/         # React components
    │   ├── lib/                # API client & utilities
    │   ├── types/              # TypeScript types
    │   └── constants/          # Dữ liệu tĩnh (tỉnh/thành, ngành)
    └── public/                 # Static assets
```

## 🔌 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | `/api/v1/jobs` | Danh sách việc làm (phân trang, lọc) |
| GET | `/api/v1/jobs/search` | Tìm kiếm nâng cao |
| GET | `/api/v1/jobs/{id}` | Chi tiết việc làm |
| GET | `/api/v1/companies` | Danh sách công ty |
| GET | `/api/v1/companies/{id}` | Chi tiết công ty |
| GET | `/api/v1/provinces` | 63 tỉnh/thành phố |
| GET | `/api/v1/provinces/{code}/jobs` | Việc làm theo tỉnh |
| GET | `/api/v1/stats/dashboard` | Thống kê tổng quan |
| GET | `/health` | Health check |

## 🕷️ Crawlers

| Crawler | Nguồn | Đặc điểm |
|---------|-------|----------|
| TopCV | topcv.vn | Nguồn lớn nhất VN, nhiều job IT |
| VietnamWorks | vietnamworks.com | Job cao cấp, API + scraping |
| CareerBuilder | careerbuilder.vn | Đa ngành nghề |
| TimViecNhanh | timviecnhanh.com | Nhiều job tỉnh, lao động phổ thông |

Crawlers chạy tự động **2 lần/ngày** qua Celery Beat. Có thể điều chỉnh trong `.env`:
```
CRAWL_INTERVAL_HOURS=12
CRAWL_MAX_PAGES=50
CRAWL_DELAY_SECONDS=2
```

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Task Queue**: Celery + Redis
- **Crawlers**: Requests + BeautifulSoup4
- **Deploy**: Docker + Docker Compose

## 📝 License

MIT License — Mã nguồn mở, miễn phí cho mọi người.

---

*Được tạo ra tại Hạ Long, Quảng Ninh 🏖️ — với mong muốn giúp mọi người Việt Nam dễ dàng tìm được việc làm phù hợp.*
