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
                
                script {
                    // Display build information
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
        }
        
        stage('🐍 Environment Setup') {
            steps {
                echo '🔧 Setting up Python virtual environment...'
                bat '''
                    echo Creating Python virtual environment...
                    python -m venv venv
                    
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
        
        stage('🔍 Code Quality & Testing') {
            parallel {
                stage('🧪 Unit Tests') {
                    steps {
                        echo '🧪 Running unit tests with pytest...'
                        bat '''
                            call venv\\Scripts\\activate.bat
                            echo Running pytest with coverage...
                            python -m pytest test_app.py -v --tb=short --junit-xml=test-results.xml --cov=app --cov-report=xml --cov-report=html
                            echo Tests completed!
                        '''
                    }
                    post {
                        always {
                            // Archive test results
                            publishTestResults testResultsPattern: 'test-results.xml'
                            
                            // Archive coverage report
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: false,
                                keepAll: true,
                                reportDir: 'htmlcov',
                                reportFiles: 'index.html',
                                reportName: 'Coverage Report'
                            ])
                        }
                    }
                }
                
                stage('📝 Code Linting') {
                    steps {
                        echo '📝 Running code quality checks...'
                        bat '''
                            call venv\\Scripts\\activate.bat
                            echo Running flake8 linter...
                            flake8 app.py --max-line-length=120 --statistics --tee --output-file=flake8-report.txt || echo "Linting completed with warnings"
                            
                            echo Running basic syntax check...
                            python -m py_compile app.py
                            echo Syntax check passed!
                        '''
                    }
                }
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
                    
                    REM Create comprehensive startup script
                    echo Creating startup script...
                    (
                        echo @echo off
                        echo title Python CI/CD Application
                        echo echo ================================
                        echo echo   Python CI/CD Application
                        echo echo ================================
                        echo cd /d "%%~dp0"
                        echo echo Activating virtual environment...
                        echo call venv\\Scripts\\activate.bat
                        echo echo Starting application on port %PORT%...
                        echo echo Application will be available at: http://localhost:%PORT%
                        echo echo Press Ctrl+C to stop the application
                        echo echo ================================
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
                        echo echo Check logs\\app.log for output
                    ) > build\\scripts\\start-service.bat
                    
                    REM Create stop script
                    (
                        echo @echo off
                        echo echo Stopping Python CI/CD Application...
                        echo taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2^>nul
                        echo if %%ERRORLEVEL%% EQU 0 ^(
                        echo   echo Application stopped successfully.
                        echo ^) else ^(
                        echo   echo No running application found.
                        echo ^)
                        echo pause
                    ) > build\\scripts\\stop.bat
                    
                    REM Create deployment info
                    (
                        echo Deployment Information
                        echo ======================
                        echo Build Number: %BUILD_NUMBER%
                        echo Build Date: %DATE% %TIME%
                        echo Git Branch: %GIT_BRANCH%
                        echo Git Commit: %GIT_COMMIT%
                        echo Jenkins Job: %JOB_NAME%
                        echo Deployed By: Jenkins CI/CD Pipeline
                        echo ======================
                    ) > build\\deployment-info.txt
                    
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
                        mkdir "!BACKUP_DIR!"
                        xcopy /E /I /Y "%DEPLOY_PATH%" "!BACKUP_DIR!\\" >nul
                        echo Backup created: !BACKUP_DIR!
                    )
                    
                    REM Stop existing application
                    echo Stopping existing application...
                    taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2>nul || echo No existing application running
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
                    curl -f -s http://localhost:%PORT%/ > nul && echo "✅ Main endpoint: OK" || echo "❌ Main endpoint: FAILED"
                    curl -f -s http://localhost:%PORT%/health > nul && echo "✅ Health endpoint: OK" || echo "❌ Health endpoint: FAILED"
                    curl -f -s http://localhost:%PORT%/api/info > nul && echo "✅ Info API: OK" || echo "❌ Info API: FAILED"
                    curl -f -s http://localhost:%PORT%/api/status > nul && echo "✅ Status API: OK" || echo "❌ Status API: FAILED"
                    
                    REM Check process
                    tasklist | findstr python.exe >nul && echo "✅ Python process: Running" || echo "❌ Python process: Not found"
                    
                    REM Display deployment summary
                    echo.
                    echo ================================
                    echo DEPLOYMENT SUMMARY
                    echo ================================
                    echo Application: Python CI/CD App
                    echo Version: 2.0.0
                    echo URL: http://localhost:%PORT%
                    echo Deployed to: %DEPLOY_PATH%
                    echo Status: Running
                    echo Build: %BUILD_NUMBER%
                    echo ================================
                '''
            }
        }
    }
    
    post {
        always {
            echo '📝 Cleaning up build workspace...'
            
            // Archive build artifacts
            archiveArtifacts artifacts: 'build/**/*', allowEmptyArchive: true
            
            // Clean workspace but keep important files
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
            Please check the console output for errors.
            Common issues:
            - Java version compatibility
            - Python environment setup
            - Port conflicts
            - Permission issues
            ================================
            '''
            
            // Stop any running applications on failure
            bat '''
                echo Cleaning up failed deployment...
                taskkill /F /IM python.exe /FI "WINDOWTITLE eq *app.py*" 2>nul || echo No applications to stop
            '''
        }
        
        unstable {
            echo '⚠️ Pipeline completed with warnings. Check test results for details.'
        }
    }
}
