
# Production API Demo Lesson 10

##  Tính Năng Chính

###  Production Features

| Tính năng              | Mô tả                                    |
|------------------------|------------------------------------------|
| **Monitoring**         | Thu thập metrics Prometheus              |
| **Rate Limiting**      | Redis-based, fallback bộ nhớ             |
| **Circuit Breaker**    | Bảo vệ các external API calls            |
| **Structured Logging** | Ghi log ra file & console                |
| **Health Checks**      | Endpoint kiểm tra sức khỏe cho LB        |
| **Docker Deployment**  | Sẵn sàng chạy container                  |
| **API Documentation**  | Swagger UI nâng cao                      |

###  Security & Reliability

#### Rate Limiting cho từng endpoint

| Endpoint                  | Giới hạn (req/min) |
|---------------------------|--------------------|
| GET `/products`           | 50                 |
| GET `/products/{id}`      | 100                |
| POST `/products`          | 10                 |
| PUT `/products/{id}`      | 20                 |
| DELETE `/products/{id}`   | 5                  |
| TEST `/test/rate-limit`   | 5                  |

- **Circuit Breaker**: Tự động ngắt kết nối khi external service lỗi
- **Graceful Degradation**: API vẫn hoạt động khi external service down

---

##  Quick Start

### 1️. Cài đặt Dependencies

```powershell
cd E:\WorkSpace\SOA_Practice\SOA\Lesson_10
pip install -r requirements.txt
```

### 2️. Chạy với Docker (Khuyến nghị)

```powershell
docker-compose up -d
```

### 3️. Hoặc chạy trực tiếp

```powershell
python app.py
```

