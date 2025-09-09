# Python CI/CD Application

A comprehensive Flask application demonstrating CI/CD pipeline with Jenkins on Windows.

## 🚀 Features

- Modern Flask web application with REST API
- Comprehensive test suite with pytest
- Code quality checks with flake8
- Automated CI/CD pipeline with Jenkins
- Windows-optimized deployment scripts
- Health monitoring endpoints
- Coverage reporting

## 🏗️ Architecture

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Git Repo │───▶│ Jenkins │───▶│ Local Deploy │
│ │ │ Pipeline │ │ │
│ - Source Code │ │ - Build │ │ - Running App │
│ - Tests │ │ - Test │ │ - Port 5000 │
│ - Jenkinsfile │ │ - Deploy │ │ - Monitoring │
└─────────────────┘ └─────────────────┘ └─────────────────┘


## 📱 Endpoints

- `GET /` - Main web interface
- `GET /health` - Health check (JSON)
- `GET /api/info` - System information (JSON)
- `GET /api/status` - Application status (JSON)

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- Java 17+ (for Jenkins)
- Git

### Setup
Clone repository
git clone <repository-url>
cd my-python-cicd-app

Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

Install dependencies
pip install -r requirements.txt

Run tests
pytest test_app.py -v

Start application
python app.py


## 🔧 Deployment

### Automatic (Jenkins)
Pipeline automatically triggers on Git push and deploys to `C:\Deploy\my-python-cicd-app`

### Manual
Run deployment script
deploy-manual.bat

Check status
check-status.bat

Access application
http://localhost:5000

## 📊 Monitoring

- Application logs: `C:\Deploy\my-python-cicd-app\logs\app.log`
- Health check: `http://localhost:5000/health`
- System info: `http://localhost:5000/api/info`

## 🔄 CI/CD Pipeline

1. **Checkout** - Get latest code from Git
2. **Environment Setup** - Create Python venv and install dependencies
3. **Code Quality & Testing** - Run tests and linting in parallel
4. **Build** - Package application with deployment scripts
5. **Deploy** - Deploy to local server with backup
6. **Verify** - Run smoke tests and verify endpoints

## 📈 Quality Gates

- ✅ Unit tests must pass
- ✅ Code coverage reporting
- ✅ Linting checks
- ✅ Smoke tests after deployment
- ✅ Health endpoint verification
