import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_basic_endpoints():
    print("TESTING BASIC ENDPOINTS")
    
    print("1. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
     
    print("2. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    print("3. Testing products endpoint...")
    response = requests.get(f"{BASE_URL}/products")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_rate_limiting():
    """Test rate limiting"""
    print("=== TESTING RATE LIMITING ===")
    print("Testing rate limit endpoint (limit: 2/minute)...")
    
    for i in range(5):
        try:
            response = requests.get(f"{BASE_URL}/test/rate-limit")
            print(f"Request {i+1}: Status {response.status_code}")
            if response.status_code == 200:
                print(f"  Success: {response.json()}")
            elif response.status_code == 429:
                print(f"  Rate limited: {response.json()}")
            time.sleep(1)
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
    print()

def test_circuit_breaker():
    """Test circuit breaker"""
    print("=== TESTING CIRCUIT BREAKER ===")
    print("Testing circuit breaker...")
    
    response = requests.get(f"{BASE_URL}/test/circuit-breaker")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_metrics():
    """Test metrics endpoint"""
    print("=== TESTING METRICS ===")
    print("Getting Prometheus metrics...")
    
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Status: {response.status_code}")
    print("Sample metrics:")
    lines = response.text.split('\n')[:10]  # First 10 lines
    for line in lines:
        if line and not line.startswith('#'):
            print(f"  {line}")
    print()

def test_crud_operations():
    """Test CRUD operations với rate limiting"""
    print("=== TESTING CRUD OPERATIONS ===")
    
    # Create product
    print("1. Creating a new product...")
    new_product = {
        "name": "Test Product",
        "price": 99.99,
        "description": "A test product",
        "in_stock": True
    }
    
    response = requests.post(f"{BASE_URL}/products", json=new_product)
    print(f"Create Status: {response.status_code}")
    if response.status_code == 201:
        created_product = response.json()
        print(f"Created product: {created_product}")
        product_id = created_product["id"]
        
        # Get specific product
        print(f"\n2. Getting product {product_id}...")
        response = requests.get(f"{BASE_URL}/products/{product_id}")
        print(f"Get Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Product details: {response.json()}")
        
        # Delete product
        print(f"\n3. Deleting product {product_id}...")
        response = requests.delete(f"{BASE_URL}/products/{product_id}")
        print(f"Delete Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Delete response: {response.json()}")
    print()

def main():
    """Main test function"""
    print("PRODUCTION API DEMO - TESTING")
    print("=" * 50)
    
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
        print("Server is running!")
        print()
        
        test_basic_endpoints()
        test_rate_limiting()
        test_circuit_breaker()
        test_metrics()
        test_crud_operations()
        
        print("All tests completed!")
        print("\n Check these URLs in your browser:")
        print(f"   - API Docs: {BASE_URL}/docs")
        print(f"   - Health: {BASE_URL}/health")
        print(f"   - Metrics: {BASE_URL}/metrics")
        
    except requests.exceptions.ConnectionError:
        print("Server is not running!")
        print("Start the server with: python app.py")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    main()