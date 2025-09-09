import pytest
import json
from app import app

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Python CI/CD Application' in response.data

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'my-python-cicd-app'
    assert 'timestamp' in data

def test_api_info_endpoint(client):
    """Test info API endpoint"""
    response = client.get('/api/info')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['application'] == 'Python CI/CD Demo'
    assert data['version'] == '2.0.0'
    assert 'platform' in data
    assert 'python' in data

def test_api_status_endpoint(client):
    """Test status API endpoint"""
    response = client.get('/api/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'running'
    assert 'Jenkins CI/CD' in data['message']
    assert 'endpoints' in data

def test_invalid_endpoint(client):
    """Test invalid endpoint returns 404"""
    response = client.get('/invalid-endpoint')
    assert response.status_code == 404
