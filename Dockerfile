FROM python:3.9-slim

WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY cost.py .
COPY cron.py .

# 스케줄러 실행
CMD ["python", "cron.py"]
