pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t codevault:latest .
                '''
            }
        }
        
        stage('Run Application') {
            steps {
                echo 'Starting Flask application...'
                sh '''
                    docker stop codevault-app || true
                    docker rm codevault-app || true
                    # Use host network mode
                    docker run -d --name codevault-app --network host codevault:latest
                    sleep 5
                    # Check if app is running
                    curl http://localhost:5000 || echo "App starting..."
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running Selenium tests...'
                sh '''
                    # Clone tests repository
                    rm -rf codevault-tests
                    git clone https://github.com/janjua911/codevault-tests.git
                    
                    cd codevault-tests
                    
                    # Install dependencies
                    apt-get update
                    apt-get install -y wget gnupg
                    
                    # Install Chrome
                    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
                    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
                    apt-get update
                    apt-get install -y google-chrome-stable
                    
                    # Install Python packages
                    pip install selenium pytest webdriver-manager
                    
                    # Run tests
                    python -m pytest test_codevault.py -v --tb=short
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            sh '''
                docker stop codevault-app || true
                docker rm codevault-app || true
            '''
        }
        success {
            echo 'Pipeline completed successfully! ✅'
        }
        failure {
            echo 'Pipeline failed! ❌'
        }
    }
}
