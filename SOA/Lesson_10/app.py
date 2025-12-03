from fastapi import FastAPI, HTTPException, Request, status, Path
from fastapi.responses import PlainTextResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import time
import os
import uvicorn
import httpx
import requests
import pybreaker
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# CONFIGURATION

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
REDIS_URL = os.getenv("REDIS_URL", "memory://")  # Fallback to memory if Redis not available

# LOGGING SETUP
# Setup basic logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# METRICS SETUP (Prometheus)

from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest

registry = CollectorRegistry()

request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

request_duration = Histogram(
    'api_request_duration_seconds', 
    'API request duration',
    ['method', 'endpoint'],
    registry=registry
)

# RATE LIMITING SETUP

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
    default_limits=["100/minute"]
)

# CIRCUIT BREAKER SETUP

external_api_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=30,
    exclude=[KeyError]
)

def sync_external_call(product_id: int):
    """Sync wrapper for circuit breaker"""
    import requests
    
    if product_id == 999:
        raise Exception("Simulated circuit breaker failure")
    
    url = f"https://jsonplaceholder.typicode.com/posts/{product_id}"
    logger.info(f"Calling external API: {url}")
    
    response = requests.get(url, timeout=5.0)
    response.raise_for_status()
    return response.json()

external_api_call = external_api_breaker(sync_external_call)

# DATA MODELS

class Product(BaseModel):
    id: int = Field(..., description="Product ID", example=1)
    name: str = Field(..., description="Product name", example="Laptop Gaming")
    price: float = Field(..., gt=0, description="Product price", example=999.99)
    description: Optional[str] = Field(None, description="Product description", example="High-performance gaming laptop")
    in_stock: bool = Field(True, description="Stock availability", example=True)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Laptop Gaming",
                "price": 999.99,
                "description": "High-performance gaming laptop with RTX 4080",
                "in_stock": True
            }
        }

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Product name", example="New Product")
    price: float = Field(..., gt=0, description="Product price", example=29.99)
    description: Optional[str] = Field(None, max_length=500, description="Product description", example="A great new product")
    in_stock: bool = Field(True, description="Stock availability", example=True)

    class Config:
        schema_extra = {
            "example": {
                "name": "Wireless Mouse",
                "price": 29.99,
                "description": "Ergonomic wireless mouse with RGB lighting",
                "in_stock": True
            }
        }

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Product name")
    price: Optional[float] = Field(None, gt=0, description="Product price")
    description: Optional[str] = Field(None, max_length=500, description="Product description")
    in_stock: Optional[bool] = Field(None, description="Stock availability")

class HealthCheck(BaseModel):
    status: str = Field(..., description="Health status", example="healthy")
    timestamp: str = Field(..., description="Current timestamp", example="2025-12-03T17:20:41.553212")
    uptime: float = Field(..., description="Server uptime in seconds", example=165.42)

class APIResponse(BaseModel):
    message: str = Field(..., description="Response message", example="Operation successful")
    data: Optional[dict] = Field(None, description="Additional data")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error detail", example="Resource not found")

class CircuitBreakerStatus(BaseModel):
    circuit_breaker_state: str = Field(..., description="Circuit breaker state", example="STATE_CLOSED")
    fail_count: int = Field(..., description="Number of failures", example=0)
    result: dict = Field(..., description="Operation result")

class RateLimitTest(BaseModel):
    message: str = Field(..., description="Test message", example="Rate limit test successful")
    timestamp: str = Field(..., description="Request timestamp", example="2025-12-03T17:20:41.553212")

# FAKE DATABASE

# Simple in-memory database for demo
products_db = [
    {"id": 1, "name": "Laptop", "price": 999.99, "description": "Gaming laptop", "in_stock": True},
    {"id": 2, "name": "Mouse", "price": 29.99, "description": "Wireless mouse", "in_stock": True},
    {"id": 3, "name": "Keyboard", "price": 79.99, "description": "Mechanical keyboard", "in_stock": False}
]

# FASTAPI APP SETUP
app = FastAPI(
    title="Production API Demo",
    description="""
    Monitoring: Comprehensive metrics collection with Prometheus
    Rate Limiting: Multiple rate limits per endpoint with Redis backend
    Circuit Breaker: Resilient external API calls with automatic failure handling
    Logging: Structured logging to file and console
    Deployment: Ready for containerized deployment with Docker
    Documentation: Interactive API documentation with examples
    
    Test Endpoints
    /test/rate-limit` - Test rate limiting (5 requests per minute)
    /test/circuit-breaker` - Test circuit breaker with external API simulation
    
    Product Management
    Full CRUD operations for products
    Data validation and error handling
    Structured responses
    """,
    version="1.0.0",
    contact={
        "name": "22028171@vnu.edu.vn",
        "email": "22028171@vnu.edu.vn"
    },
    license_info={
        "name": "License MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "products",
            "description": "Product management operations. CRUD operations for managing products.",
        },
        {
            "name": "monitoring",
            "description": "System monitoring and health check endpoints.",
        },
        {
            "name": "testing",
            "description": "Testing endpoints for rate limiting and circuit breaker functionality.",
        },
    ],
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}")
    raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {exc.detail}")

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return {"error": "Internal server error", "detail": str(exc)}

app_start_time = time.time()

# MIDDLEWARE FOR METRICS & LOGGING

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware để collect metrics và logging"""
    start_time = time.time()
    method = request.method
    path = request.url.path

    logger.info(f"Request: {method} {path} from {get_remote_address(request)}")
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    status_code = response.status_code
    
    request_count.labels(method=method, endpoint=path, status=status_code).inc()
    request_duration.labels(method=method, endpoint=path).observe(duration)
    
    logger.info(f"Response: {method} {path} -> {status_code} ({duration:.3f}s)")
    
    return response


# EXTERNAL API CLIENT (với Circuit Breaker)

async def get_external_data(product_id: int):
    """Simulate external API call với circuit breaker protection"""
    return external_api_call(product_id)

# API ENDPOINTS

@app.get(
    "/",
    summary="Root endpoint",
    description="Welcome endpoint providing API information and navigation",
    response_model=dict,
    tags=["monitoring"]
)
async def root():
    """Root endpoint with API navigation"""
    return {
        "message": "Production API Demo",
        "version": "1.0.0", 
        "docs-swagger": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "features": [
            "Rate Limiting",
            "Circuit Breaker", 
            "Prometheus Metrics",
            "Structured Logging",
            "Docker Deployment"
        ]
    }

@app.get(
    "/health",
    response_model=HealthCheck,
    summary="Health check",
    description="Health check endpoint for load balancers and monitoring systems",
    tags=["monitoring"],
    responses={
        200: {
            "description": "Service is healthy",
            "model": HealthCheck,
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2025-12-03T17:20:41.553212",
                        "uptime": 165.42
                    }
                }
            }
        }
    }
)
async def health_check():
    """Health check endpoint cho load balancers"""
    uptime = time.time() - app_start_time
    
    health_data = HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        uptime=uptime
    )
    
    logger.info("Health check performed")
    return health_data

@app.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Prometheus metrics endpoint for monitoring and observability",
    tags=["monitoring"],
    responses={
        200: {
            "description": "Prometheus metrics in text format",
            "content": {
                "text/plain": {
                    "example": "# HELP python_gc_objects_collected_total Objects collected during gc\n# TYPE python_gc_objects_collected_total counter\npython_gc_objects_collected_total{generation=\"0\"} 123.0"
                }
            }
        }
    }
)
async def get_metrics():
    """Prometheus metrics endpoint"""
    logger.info("Metrics requested")
    return PlainTextResponse(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get(
    "/products",
    response_model=List[Product],
    summary="Get all products",
    description="Get all products from the database. Rate limited to 50 requests per minute.",
    tags=["products"],
    responses={
        200: {
            "description": "List of all products",
            "model": List[Product]
        },
        429: {
            "description": "Rate limit exceeded",
            "model": ErrorResponse
        }
    }
)
@limiter.limit("50/minute") 
async def get_products(request: Request):
    """Get all products (với rate limiting)"""
    logger.info("Getting all products")
    return products_db

@app.get(
    "/products/{product_id}",
    response_model=Product,
    summary="Get product by ID",
    description="Get a specific product by ID.  Rate limited to 100 requests per minute.",
    tags=["products"],
    responses={
        200: {
            "description": "Product found",
            "model": Product
        },
        404: {
            "description": "Product not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "Product not found"}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "model": ErrorResponse
        }
    }
)
@limiter.limit("100/minute")  
async def get_product(
    product_id: int = Path(..., description="Product ID to retrieve", example=1, ge=1),
    request: Request = None
):
    """
    Get product by ID (với external API integration và circuit breaker)
    """
    logger.info(f"Getting product {product_id}")
    
    product = next((p for p in products_db if p["id"] == product_id), None)
    
    if not product:
        logger.warning(f"Product {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        external_data = await get_external_data(product_id)
        product["external_info"] = {
            "title": external_data.get("title", "N/A"),
            "rating": 4.5 
        }
        logger.info(f"Product {product_id} enriched with external data")
    except pybreaker.CircuitBreakerError:
        logger.warning(f"Circuit breaker open for product {product_id}")
        product["external_info"] = {"error": "External service temporarily unavailable"}
    except Exception as e:
        logger.warning(f"Could not enrich product {product_id}: {str(e)}")
        product["external_info"] = {"error": "External service error"}
    
    return product

@app.post(
    "/products",
    response_model=Product,
    summary="Create new product",
    description="Create a new product. rate limiting applies (10 requests per minute).",
    tags=["products"],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Product created successfully",
            "model": Product
        },
        400: {
            "description": "Invalid product data",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {"detail": "Price must be positive"}
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "model": ErrorResponse
        }
    }
)
@limiter.limit("10/minute") 
async def create_product(product: ProductCreate, request: Request):
    """Create new product """
    logger.info(f"Creating product: {product.name}")
    
    if product.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    
    new_id = max([p["id"] for p in products_db]) + 1
    
    new_product = {
        "id": new_id,
        **product.dict()
    }
    
    products_db.append(new_product)
    
    logger.info(f"Product created with ID {new_id}")
    return new_product

@app.put(
    "/products/{product_id}",
    response_model=Product,
    summary="Update product",
    description="Update an existing product by ID. Rate limited to 20 requests per minute.",
    tags=["products"],
    responses={
        200: {
            "description": "Product updated successfully",
            "model": Product
        },
        404: {
            "description": "Product not found",
            "model": ErrorResponse
        },
        429: {
            "description": "Rate limit exceeded",
            "model": ErrorResponse
        }
    }
)
@limiter.limit("20/minute") 
async def update_product(
    product_id: int = Path(..., description="Product ID to update", example=1, ge=1),
    product_update: ProductUpdate = None,
    request: Request = None
):
    """Update product (với moderate rate limiting)"""
    logger.info(f"Updating product {product_id}")
    
    # Find product
    for i, product in enumerate(products_db):
        if product["id"] == product_id:
            update_data = product_update.dict(exclude_unset=True)
            products_db[i].update(update_data)
            
            logger.info(f"Product {product_id} updated")
            return products_db[i]
    
    logger.warning(f"Product {product_id} not found for update")
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete(
    "/products/{product_id}",
    response_model=APIResponse,
    summary="Delete product",
    description="Delete a product by ID. Very strict rate limiting applies (5 requests per minute).",
    tags=["products"],
    responses={
        200: {
            "description": "Product deleted successfully",
            "model": APIResponse,
            "content": {
                "application/json": {
                    "example": {
                        "message": "Product 'Laptop Gaming' deleted successfully",
                        "data": None
                    }
                }
            }
        },
        404: {
            "description": "Product not found",
            "model": ErrorResponse
        },
        429: {
            "description": "Rate limit exceeded",
            "model": ErrorResponse
        }
    }
)
@limiter.limit("5/minute") 
async def delete_product(
    product_id: int = Path(..., description="Product ID to delete", example=1, ge=1),
    request: Request = None
):
    """Delete product (với very strict rate limiting)"""
    logger.info(f"Deleting product {product_id}")
    
    # Find and remove product
    for i, product in enumerate(products_db):
        if product["id"] == product_id:
            deleted_product = products_db.pop(i)
            logger.info(f"Product {product_id} deleted: {deleted_product['name']}")
            return APIResponse(
                message=f"Product '{deleted_product['name']}' deleted successfully",
                data={"deleted_product_id": product_id}
            )
    
    logger.warning(f"Product {product_id} not found for deletion")
    raise HTTPException(status_code=404, detail="Product not found")

@app.get(
    "/test/circuit-breaker",
    response_model=CircuitBreakerStatus,
    summary="Test circuit breaker",
    description="Test the circuit breaker functionality by making external API calls",
    tags=["testing"],
    responses={
        200: {
            "description": "Circuit breaker test result",
            "model": CircuitBreakerStatus
        }
    }
)
async def test_circuit_breaker(request: Request):
    """Test circuit breaker functionality"""
    logger.info("Testing circuit breaker")
    
    # Print current state before test
    logger.info(f"Circuit breaker state before: {external_api_breaker.state.__class__.__name__}, fail count: {external_api_breaker.fail_counter}")
    
    try:
        result = await get_external_data(999)
        
        return CircuitBreakerStatus(
            circuit_breaker_state=external_api_breaker.state.__class__.__name__,
            fail_count=external_api_breaker.fail_counter,
            result=result
        )
    except pybreaker.CircuitBreakerError:
        logger.warning("Circuit breaker is open during test")
        return CircuitBreakerStatus(
            circuit_breaker_state=external_api_breaker.state.__class__.__name__,
            fail_count=external_api_breaker.fail_counter,
            result={"error": "Circuit breaker is open"}
        )
    except Exception as e:
        logger.error(f"Circuit breaker test failed: {str(e)}")
        # Log state after failure
        logger.info(f"Circuit breaker state after failure: {external_api_breaker.state.__class__.__name__}, fail count: {external_api_breaker.fail_counter}")
        return CircuitBreakerStatus(
            circuit_breaker_state=external_api_breaker.state.__class__.__name__,
            fail_count=external_api_breaker.fail_counter,
            result={"error": str(e)}
        )

@app.post(
    "/test/circuit-breaker/reset",
    response_model=CircuitBreakerStatus,
    summary="Reset circuit breaker",
    description="Manually reset the circuit breaker to initial state (count = 0, state = CLOSED)",
    tags=["testing"],
    responses={
        200: {
            "description": "Circuit breaker reset successful",
            "model": CircuitBreakerStatus
        }
    }
)
async def reset_circuit_breaker(request: Request):
    """Reset circuit breaker về trạng thái ban đầu"""
    logger.info("Resetting circuit breaker manually")
    
    # Reset circuit breaker
    external_api_breaker.close()  # Force close circuit
    external_api_breaker.fail_counter = 0  # Reset fail counter
    
    logger.info(f"Circuit breaker reset - State: {external_api_breaker.state.__class__.__name__}, Fail count: {external_api_breaker.fail_counter}")
    
    return CircuitBreakerStatus(
        circuit_breaker_state=external_api_breaker.state.__class__.__name__,
        fail_count=external_api_breaker.fail_counter,
        result={"message": "Circuit breaker reset successfully"}
    )

@app.get(
    "/test/rate-limit",
    response_model=RateLimitTest,
    summary="Test rate limiting",
    description="Test the rate limiting functionality. Very low limit (5 requests per minute) for easy testing.",
    tags=["testing"],
    responses={
        200: {
            "description": "Rate limit test successful",
            "model": RateLimitTest
        },
        429: {
            "description": "Rate limit exceeded - test successful!",
            "model": ErrorResponse
        }
    }
)
@limiter.limit("5/minute")  
async def test_rate_limit(request: Request):
    """Test rate limiting (chỉ 5 requests per minute)"""
    logger.info("Rate limit test endpoint called")
    return RateLimitTest(
        message="Rate limit test successful",
        timestamp=datetime.now().isoformat()
    )

# MAIN ENTRY POINT

if __name__ == "__main__":
    logger.info("Starting Production API Demo")
    
    # Start the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )