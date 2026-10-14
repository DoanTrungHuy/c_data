# ==============================================================================
# C_Data - Vietnamese Job Aggregator Backend
# Dockerfile: Python 3.11 with asynchronous FastAPI, Celery & Scrapy/Playwright
# ==============================================================================

FROM python:3.11-slim

# Ngăn Python tạo các file .pyc và kích hoạt unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các gói hệ thống cần thiết cho việc biên dịch C extensions (psycopg2, lxml) và crawl
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    git \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . /app

# Cổng mặc định của FastAPI
EXPOSE 8000

# Lệnh khởi chạy mặc định (có thể được ghi đè trong docker-compose.yml)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
