#!/usr/bin/env python3
"""
Python Flask CI/CD Application
Demonstrates automated build, test, and deployment pipeline
"""
from flask import Flask, jsonify, render_template_string
import os
import sys
from datetime import datetime
import platform

app = Flask(__name__)

# HTML template for web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Python CI/CD App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .status { background: #27ae60; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .info { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .endpoint { background: #3498db; color: white; padding: 10px; margin: 5px 0; border-radius: 3px; }
        a { color: #2980b9; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🚀 Python CI/CD Application</h1>
        <div class="status">✅ Application is running successfully!</div>
        
        <div class="info">
            <h3>System Information</h3>
            <p><strong>Platform:</strong> {{ platform }}</p>
            <p><strong>Python Version:</strong> {{ python_version }}</p>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            <p><strong>Environment:</strong> {{ environment }}</p>
        </div>
        
        <div class="info">
            <h3>Available Endpoints</h3>
            <div class="endpoint">GET <a href="/health">/health</a> - Health check</div>
            <div class="endpoint">GET <a href="/api/info">/api/info</a> - System information (JSON)</div>
            <div class="endpoint">GET <a href="/api/status">/api/status</a> - Application status (JSON)</div>
        </div>
        
        <div class="info">
            <h3>CI/CD Pipeline Status</h3>
            <p>This application was built and deployed using Jenkins CI/CD pipeline.</p>
            <p>✅ Automated testing passed</p>
            <p>✅ Code quality checks completed</p>
            <p>✅ Deployment successful</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    """Main application page with web interface"""
    return render_template_string(HTML_TEMPLATE,
        platform=platform.system() + " " + platform.release(),
        python_version=sys.version.split(),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        environment=os.getenv('ENV', 'development')
    )

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'my-python-cicd-app',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'running'
    })

@app.route('/api/info')
def api_info():
    """System information API endpoint"""
    return jsonify({
        'application': 'Python CI/CD Demo',
        'version': '2.0.0',
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor()
        },
        'python': {
            'version': sys.version,
            'executable': sys.executable
        },
        'environment': {
            'working_dir': os.getcwd(),
            'env_type': os.getenv('ENV', 'development'),
            'java_home': os.getenv('JAVA_HOME', 'Not set'),
            'jenkins_home': os.getenv('JENKINS_HOME', 'Not set')
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    """Application status API endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'Application deployed successfully via Jenkins CI/CD',
        'endpoints': {
            'home': '/',
            'health': '/health',
            'info': '/api/info',
            'status': '/api/status'
        },
        'build_info': {
            'deployed_by': 'Jenkins CI/CD Pipeline',
            'deployment_time': datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting Python CI/CD Application...")
    print(f"📍 Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"🔧 Debug Mode: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
