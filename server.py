import os
import subprocess
import threading
import time
from flask import Flask, render_template_string

app = Flask(__name__)

# HTML template for the loading page
LOADING_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Project AEGIS - Loading</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .loading-container {
            text-align: center;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 2s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="loading-container">
        <div class="spinner"></div>
        <h1>Project AEGIS</h1>
        <p>Starting biomedical analytics platform...</p>
        <p><small>This may take a few moments</small></p>
    </div>
    <script>
        // Redirect to Streamlit after a delay
        setTimeout(function() {
            window.location.href = "http://localhost:8501";
        }, 3000);
        
        // Fallback redirect
        setTimeout(function() {
            window.location.reload();
        }, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(LOADING_PAGE)

def run_streamlit():
    """Run Streamlit in the background"""
    # Wait a bit for Flask to start
    time.sleep(2)
    
    # Set Streamlit configuration
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Run Streamlit
    subprocess.call([
        'streamlit', 'run', 'app.py',
        '--server.port=8501',
        '--server.address=0.0.0.0',
        '--server.headless=true',
        '--browser.gatherUsageStats=false'
    ])

if __name__ == '__main__':
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=run_streamlit)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)