# Production API Demo Lesson10

##  Tính năng chính

###  Production Features
- **Monitoring**: Prometheus metrics collection  
- **Rate Limiting**: Redis-based với fallback memory
- **Circuit Breaker**: Bảo vệ external API calls
- **Structured Logging**: File + console logging
- **Health Checks**: Endpoint cho load balancers
- **Docker Deployment**: Container-ready
- **API Documentation**: Enhanced Swagger UI

### Security & Reliability
- **Rate Limiting**: Khác nhau cho từng endpoint
  - GET `/products`: 50 req/min
  - GET `/products/{id}`: 100 req/min
  - POST `/products`: 10 req/min
  - PUT `/products/{id}`: 20 req/min
  - DELETE `/products/{id}`: 5 req/min
  - TEST `/test/rate-limit`: 2 req/min
- **Circuit Breaker**: Tự động ngắt kết nối khi external service fail
- **Graceful Degradation**: API vẫn hoạt động khi external service down

##  Quick Start

### 1. Cài đặt Dependencies
```powershell
cd E:\WorkSpace\SOA_Practice\SOA\Lesson_10
pip install -r requirements.txt
```

### 2. Chạy với Docker (Recommended)
```powershell
docker-compose up -d
```

### 3. Hoặc chạy trực tiếp
```powershell
python app.py
```

