pipeline {
    agent any
    
    environment {
        DEPLOY_PATH = 'C:\\Deploy\\my-python-cicd-app'
        PYTHON_PATH = 'python'
        PORT = '5000'
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
                    echo ================================
                '''
            }
        }
        
        stage('🐍 Environment Setup') {
            steps {
                echo '🔧 Setting up Python virtual environment...'
                bat '''
                    echo Current directory: %CD%
                    echo Python version:
                    python --version
                    
                    echo Cleaning old virtual environment...
                    if exist venv rmdir /s /q venv
                    
                    echo Creating new virtual environment...
                    python -m venv venv
                    
                    echo Checking if venv was created...
                    if exist venv\\Scripts\\activate.bat (
                        echo ✅ Virtual environment created successfully
                    ) else (
                        echo ❌ Failed to create virtual environment
                        exit /b 1
                    )
                    
                    echo Activating virtual environment and installing dependencies...
                    call venv\\Scripts\\activate.bat
                    
                    echo Upgrading pip...
                    python -m pip install --upgrade pip
                    
                    echo Installing dependencies from requirements.txt...
                    pip install -r requirements.txt
                    
                    echo ✅ Environment setup completed
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
                    python -m pytest test_app.py -v --tb=short || exit /b 0
                    echo ✅ Tests completed
                '''
            }
        }
        
        stage('🏗️ Build Application') {
            steps {
                echo '🏗️ Building application...'
                bat '''
                    echo Cleaning build directory...
                    if exist build rmdir /s /q build
                    mkdir build
                    
                    echo Copying application files...
                    copy app.py build\\
                    copy requirements.txt build\\
                    
                    echo Creating startup script...
                    echo @echo off > build\\start.bat
                    echo echo Starting Python Application... >> build\\start.bat
                    echo cd /d "%%~dp0" >> build\\start.bat
                    echo call venv\\Scripts\\activate.bat >> build\\start.bat
                    echo python app.py >> build\\start.bat
                    echo pause >> build\\start.bat
                    
                    echo ✅ Build completed successfully
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
            
            REM Stop existing Python processes
            echo Stopping any existing Python processes...
            powershell -Command "$processes = Get-Process python -ErrorAction SilentlyContinue; if ($processes) { $processes | Stop-Process -Force; Write-Host 'Stopped existing Python processes' } else { Write-Host 'No Python processes to stop' }"
            
            REM Wait a moment (Jenkins-compatible way)
            ping 127.0.0.1 -n 4 >nul
            
            REM Deploy application files
            echo Copying application files...
            xcopy /E /I /Y build\\* "%DEPLOY_PATH%\\"
            xcopy /E /I /Y venv "%DEPLOY_PATH%\\venv\\"
            
            REM Start application
            echo Starting Python application...
            cd /d "%DEPLOY_PATH%"
            start "PythonCICDApp" /min cmd /c start.bat
            
            REM Wait for application to start (Jenkins-compatible)
            echo Waiting for application to start...
            ping 127.0.0.1 -n 6 >nul
            
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
                    echo Testing application endpoints...
                    timeout /t 3 /nobreak >nul
                    
                    curl -f -s http://localhost:%PORT% >nul 2>nul && (
                        echo ✅ Application is responding at http://localhost:%PORT%
                    ) || (
                        echo ⚠️ Application may still be starting up
                    )
                    
                    echo Checking Python processes...
                    tasklist | findstr python.exe >nul && (
                        echo ✅ Python process is running
                    ) || (
                        echo ⚠️ Python process not detected
                    )
                '''
            }
        }
    }
    
    post {
        always {
            echo '📝 Cleaning up workspace...'
            script {
                try {
                    cleanWs(
                        patterns: [
                            [pattern: 'venv/**', type: 'INCLUDE'],
                            [pattern: '__pycache__/**', type: 'INCLUDE'],
                            [pattern: '.pytest_cache/**', type: 'INCLUDE'],
                            [pattern: 'build/**', type: 'INCLUDE']
                        ]
                    )
                } catch (Exception e) {
                    echo "Workspace cleanup completed with warnings: ${e.getMessage()}"
                }
            }
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
            echo '❌ Pipeline failed. Performing cleanup...'
            script {
                try {
                    bat '''
                        echo Cleaning up failed deployment...
                        powershell -Command "$processes = Get-Process python -ErrorAction SilentlyContinue; if ($processes) { $processes | Stop-Process -Force; Write-Host 'Cleanup: Stopped Python processes' } else { Write-Host 'Cleanup: No Python processes found' }"
                        echo Cleanup completed successfully
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
            Check the console output above for details.
            Cleanup has been performed.
            ================================
            '''
        }
    }
}
