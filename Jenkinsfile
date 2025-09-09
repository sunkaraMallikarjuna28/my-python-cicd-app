pipeline {
    agent any
    
    environment {
        DEPLOY_PATH = 'C:\\Deploy\\my-python-cicd-app'
        BACKUP_PATH = 'C:\\Deploy\\backup'
        PYTHON_PATH = 'python'
        PORT = '5000'
        ENV = 'production'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    stages {
        stage('🔄 Checkout') {
            steps {
                echo '📥 Checking out source code from Git...'
                checkout scm
                
                bat '''
                    echo ================================
                    echo BUILD INFORMATION
                    echo ================================
                    echo Build Number: %BUILD_NUMBER%
                    echo Job Name: %JOB_NAME%
                    echo Workspace: %WORKSPACE%
                    echo Git Branch: %GIT_BRANCH%
                    echo Git Commit: %GIT_COMMIT%
                    echo ================================
                '''
            }
        }
        
        stage('🐍 Environment Setup') {
            steps {
                echo '🔧 Setting up Python virtual environment...'
                bat '''
                    echo Creating Python virtual environment...
                    if not exist venv (
                        python -m venv venv
                    )
                    
                    echo Activating virtual environment...
                    call venv\\Scripts\\activate.bat
                    
                    echo Upgrading pip...
                    python -m pip install --upgrade pip
                    
                    echo Installing dependencies...
                    pip install -r requirements.txt
                    
                    echo ================================
                    echo INSTALLED PACKAGES
                    echo ================================
                    pip list
                    echo ================================
                '''
            }
        }
        
        stage('🧪 Run Tests') {
            steps {
                echo '🧪 Running unit tests with pytest...'
                bat '''
                    call venv\\Scripts\\activate.bat
                    echo Running pytest...
                    python -m pytest test_app.py -v --tb=short
                    echo Tests completed!
                '''
            }
        }
        
        stage('🏗️ Build Application') {
            steps {
                echo '🏗️ Building application package...'
                bat '''
                    call venv\\Scripts\\activate.bat
                    
                    REM Create build directory structure
                    if not exist build mkdir build
                    if not exist build\\scripts mkdir build\\scripts
                    if not exist build\\logs mkdir build\\logs
                    
                    REM Copy application files
                    echo Copying application files...
                    copy app.py build\\
                    copy requirements.txt build\\
                    
                    REM Create startup script
                    echo Creating startup script...
                    (
                        echo @echo off
                        echo title Python CI/CD Application
                        echo cd /d "%%~dp0"
                        echo call venv\\Scripts\\activate.bat
                        echo echo Starting application on port %PORT%...
                        echo python app.py
                        echo pause
                    ) > build\\scripts\\start.bat
                    
                    REM Create service startup script (background)
                    (
                        echo @echo off
                        echo cd /d "%%~dp0\\.."
                        echo call venv\\Scripts\\activate.bat
                        echo start /B python app.py ^> logs\\app.log 2^>^&1
                        echo echo Application started in background
                    ) > build\\scripts\\start-service.bat
                    
                    REM Create stop script
                    (
                        echo @echo off
                        echo echo Stopping Python CI/CD Application...
                        echo taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2^>nul ^|^| echo No running application found
                        echo echo Application stopped.
                        echo pause
                    ) > build\\scripts\\stop.bat
                    
                    echo Build package created successfully!
                '''
            }
        }
        
        stage('🚀 Deploy to Local Server') {
            steps {
                echo '🚀 Deploying application to local server...'
                bat '''
                    REM Create deployment directories
                    if not exist "%DEPLOY_PATH%" mkdir "%DEPLOY_PATH%"
                    if not exist "%BACKUP_PATH%" mkdir "%BACKUP_PATH%"
                    if not exist "%DEPLOY_PATH%\\logs" mkdir "%DEPLOY_PATH%\\logs"
                    
                    REM Create backup of existing deployment
                    if exist "%DEPLOY_PATH%\\app.py" (
                        echo Creating backup of existing deployment...
                        for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set mydate=%%c%%a%%b
                        for /f "tokens=1-3 delims=:. " %%a in ('time /t') do set mytime=%%a%%b%%c
                        set BACKUP_DIR=%BACKUP_PATH%\\backup-!mydate!-!mytime!
                        mkdir "!BACKUP_DIR!" 2>nul
                        xcopy /E /I /Y "%DEPLOY_PATH%" "!BACKUP_DIR!\\" >nul 2>nul
                        echo Backup created: !BACKUP_DIR!
                    )
                    
                    REM Stop existing application (with proper error handling)
                    echo Stopping existing application...
                    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2>nul && echo "Stopped existing app" || echo "No existing application running"
                    timeout /t 3 /nobreak >nul
                    
                    REM Deploy new version
                    echo Deploying new application version...
                    xcopy /E /I /Y build\\* "%DEPLOY_PATH%\\" >nul
                    xcopy /E /I /Y venv "%DEPLOY_PATH%\\venv\\" >nul
                    
                    REM Set production environment
                    cd /d "%DEPLOY_PATH%"
                    echo ENV=production > .env
                    echo PORT=%PORT% >> .env
                    echo DEBUG=False >> .env
                    
                    REM Start the application
                    echo Starting application...
                    call scripts\\start-service.bat
                    
                    REM Wait for startup
                    timeout /t 8 /nobreak >nul
                    
                    echo.
                    echo ========================
                    echo DEPLOYMENT SUMMARY
                    echo ========================
                    echo Application: Python CI/CD App
                    echo URL: http://localhost:%PORT%
                    echo Deployed to: %DEPLOY_PATH%
                    echo Build: %BUILD_NUMBER%
                    echo ========================
                '''
            }
        }
        
        stage('✅ Verify Deployment') {
            steps {
                echo '✅ Verifying deployment and running smoke tests...'
                bat '''
                    echo Verifying application deployment...
                    timeout /t 5 /nobreak >nul
                    
                    REM Test endpoints
                    echo Testing application endpoints...
                    curl -f -s http://localhost:%PORT%/ >nul 2>nul && echo "✅ Main endpoint: OK" || echo "❌ Main endpoint: FAILED"
                    curl -f -s http://localhost:%PORT%/health >nul 2>nul && echo "✅ Health endpoint: OK" || echo "❌ Health endpoint: FAILED"
                    
                    REM Check process
                    tasklist | findstr python.exe >nul && echo "✅ Python process: Running" || echo "❌ Python process: Not found"
                    
                    echo.
                    echo Deployment verification completed!
                '''
            }
        }
    }
    
    post {
        always {
            echo '📝 Cleaning up build workspace...'
            cleanWs(
                patterns: [
                    [pattern: 'venv/**', type: 'INCLUDE'],
                    [pattern: '__pycache__/**', type: 'INCLUDE'],
                    [pattern: '.pytest_cache/**', type: 'INCLUDE']
                ]
            )
        }
        
        success {
            echo '''
            ================================
            🎉 PIPELINE SUCCESS! 🎉
            ================================
            ✅ All stages completed successfully
            ✅ Application deployed and verified
            🌐 Access your app at: http://localhost:5000
            📁 Deployed to: C:\\Deploy\\my-python-cicd-app
            ================================
            '''
        }
        
        failure {
            echo '''
            ================================
            ❌ PIPELINE FAILED! ❌
            ================================
            Cleaning up failed deployment...
            ================================
            '''
            
            // Graceful cleanup with proper error handling
            bat '''
                echo Stopping any running applications...
                taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2>nul && echo "Cleaned up processes" || echo "No processes to clean"
                exit /b 0
            '''
        }
        
        unstable {
            echo '⚠️ Pipeline completed with warnings. Check test results for details.'
        }
    }
}
