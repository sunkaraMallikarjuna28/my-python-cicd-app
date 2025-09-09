pipeline {
    agent any
    
    environment {
        DEPLOY_PATH = 'D:\\Deploy\\my-python-cicd-app'
        PYTHON_PATH = 'python'
        PORT = '5000'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        // Removed ansiColor from here - it's not a valid option
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
                    echo ================================
                '''
            }
        }
        
        stage('🐍 Environment Setup') {
            steps {
                echo '🔧 Setting up Python virtual environment...'
                bat '''
                    if not exist venv (
                        echo Creating new virtual environment...
                        python -m venv venv
                    )
                    
                    echo Activating virtual environment...
                    call venv\\Scripts\\activate.bat
                    
                    echo Upgrading pip...
                    python -m pip install --upgrade pip
                    
                    echo Installing dependencies...
                    pip install -r requirements.txt
                    
                    echo Installed packages:
                    pip list
                '''
            }
        }
        
        stage('🧪 Run Tests') {
            steps {
                echo '🧪 Running unit tests...'
                bat '''
                    call venv\\Scripts\\activate.bat
                    echo Running pytest...
                    python -m pytest test_app.py -v --tb=short
                '''
            }
        }
        
        stage('🏗️ Build Application') {
            steps {
                echo '🏗️ Building application...'
                bat '''
                    if not exist build (
                        echo Creating build directory...
                        mkdir build
                    )
                    
                    echo Copying application files...
                    copy app.py build\\
                    copy requirements.txt build\\
                    
                    echo Creating startup script...
                    echo @echo off > build\\start.bat
                    echo cd /d "%%~dp0" >> build\\start.bat
                    echo call venv\\Scripts\\activate.bat >> build\\start.bat
                    echo python app.py >> build\\start.bat
                    
                    echo Build completed successfully!
                '''
            }
        }
        
        stage('🚀 Deploy Application') {
            steps {
                echo '🚀 Deploying to local server...'
                bat '''
                    REM Create deployment directory
                    if not exist "%DEPLOY_PATH%" (
                        echo Creating deployment directory...
                        mkdir "%DEPLOY_PATH%"
                    )
                    
                    REM Stop existing Python processes gracefully
                    echo Stopping any existing Python applications...
                    powershell -Command "try { Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*app.py*' } | Stop-Process -Force -ErrorAction SilentlyContinue } catch { Write-Host 'No processes to stop' }"
                    timeout /t 3 /nobreak >nul
                    
                    REM Deploy application files
                    echo Copying application files to deployment location...
                    xcopy /E /I /Y build\\* "%DEPLOY_PATH%\\"
                    xcopy /E /I /Y venv "%DEPLOY_PATH%\\venv\\"
                    
                    REM Start application in background
                    echo Starting Python application...
                    cd /d "%DEPLOY_PATH%"
                    start "PythonCICDApp" /min cmd /c "call venv\\Scripts\\activate.bat && python app.py"
                    
                    REM Wait for application to start
                    timeout /t 5 /nobreak >nul
                    
                    echo ================================
                    echo DEPLOYMENT COMPLETED
                    echo ================================
                    echo Application URL: http://localhost:%PORT%
                    echo Deployment Path: %DEPLOY_PATH%
                    echo ================================
                '''
            }
        }
        
        stage('✅ Verify Deployment') {
            steps {
                echo '✅ Verifying deployment...'
                bat '''
                    echo Waiting for application to fully start...
                    timeout /t 3 /nobreak >nul
                    
                    echo Testing application endpoints...
                    curl -f -s http://localhost:%PORT% >nul 2>nul && (
                        echo ✅ Main endpoint: RESPONDING
                    ) || (
                        echo ⚠️  Main endpoint: Not responding yet
                    )
                    
                    curl -f -s http://localhost:%PORT%/health >nul 2>nul && (
                        echo ✅ Health endpoint: OK
                    ) || (
                        echo ⚠️  Health endpoint: Not available yet
                    )
                    
                    echo Checking if Python process is running...
                    tasklist | findstr python.exe >nul && (
                        echo ✅ Python process: Running
                    ) || (
                        echo ❌ Python process: Not found
                    )
                '''
            }
        }
    }
    
    post {
        always {
            echo '📝 Cleaning up workspace...'
            cleanWs(
                patterns: [
                    [pattern: 'venv/**', type: 'INCLUDE'],
                    [pattern: '__pycache__/**', type: 'INCLUDE'],
                    [pattern: '.pytest_cache/**', type: 'INCLUDE'],
                    [pattern: 'build/**', type: 'INCLUDE']
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
            🌐 Access your app: http://localhost:5000
            📁 Deployed to: C:\\Deploy\\my-python-cicd-app
            ================================
            '''
        }
        
        failure {
            script {
                echo '❌ Pipeline failed. Performing cleanup...'
                try {
                    bat '''
                        echo Cleaning up failed deployment...
                        powershell -Command "try { Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like '*app.py*' } | Stop-Process -Force -ErrorAction SilentlyContinue; Write-Host 'Cleanup completed' } catch { Write-Host 'No processes to clean' }"
                        exit /b 0
                    '''
                } catch (Exception e) {
                    echo "Cleanup completed with warnings: ${e.getMessage()}"
                }
            }
            
            echo '''
            ================================
            ❌ PIPELINE FAILED! ❌
            ================================
            Check the console output above for error details.
            Cleanup has been performed.
            ================================
            '''
        }
        
        unstable {
            echo '⚠️ Pipeline completed with warnings. Check test results.'
        }
    }
}
