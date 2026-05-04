pipeline {
    agent any
    
    environment {
        DOCKER_NETWORK = "host"
    }
    
    stages {

        stage('Checkout') {
            steps {
                echo '📦 Checking out code from GitHub...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh 'docker build -t codevault:latest .'
            }
        }
        
        stage('Run Application') {
            steps {
                echo '🚀 Starting Flask application...'
                sh '''
                    docker stop codevault-app || true
                    docker rm codevault-app || true
                    docker run -d --name codevault-app --network host codevault:latest
                    sleep 5
                    curl -s http://localhost:5000 > /dev/null && echo "✅ App is running on port 5000"
                '''
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                echo '🧪 Running Selenium tests...'
                sh '''
                    # 🔥 FIX 1: permission issue
                    chmod -R 777 codevault-tests || true
                    rm -rf codevault-tests || true
                    
                    # Clone fresh
                    git clone https://github.com/janjua911/codevault-tests.git
                    cd codevault-tests
                    
                    # 🔥 FIX 2: Modern Chrome install (NO apt-key)
                    cat > Dockerfile.test << 'DOCKERFILE'
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

RUN pip install selenium pytest webdriver-manager

WORKDIR /tests
COPY . .

CMD ["pytest", "test_codevault.py", "-v", "--tb=short"]
DOCKERFILE
                    
                    # Build test image
                    docker build -f Dockerfile.test -t codevault-tests:latest .
                    
                    # 🔥 FIX 3: run as Jenkins user (avoid permission issues)
                    docker run --rm -u $(id -u):$(id -g) \
                        --network host \
                        codevault-tests:latest
                '''
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up...'
            sh '''
                docker stop codevault-app || true
                docker rm codevault-app || true
                docker rmi codevault-tests:latest || true

                chmod -R 777 codevault-tests || true
                rm -rf codevault-tests || true
            '''
        }

        success {
            echo '🎉🎉🎉 PIPELINE SUCCESS! All tests passed! 🎉🎉🎉'
        }

        failure {
            echo '❌ Pipeline failed! Check logs above ❌'
        }
    }
}
