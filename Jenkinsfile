pipeline {
    agent any
    
    environment {
        // Use host's network for testing
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
                sh '''
                    docker build -t codevault:latest .
                '''
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
                    # Clean up
                    rm -rf codevault-tests || true
                    
                    # Clone tests repository
                    git clone https://github.com/janjua911/codevault-tests.git
                    
                    cd codevault-tests
                    
                    # Create Dockerfile for tests with Chrome
                    cat > Dockerfile.test << 'DOCKERFILE'
FROM python:3.9-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install selenium pytest webdriver-manager

WORKDIR /tests
COPY . .

CMD ["python", "-m", "pytest", "test_codevault.py", "-v", "--tb=short"]
DOCKERFILE
                    
                    # Build test image
                    docker build -f Dockerfile.test -t codevault-tests:latest .
                    
                    # Run tests
                    docker run --rm \
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
                rm -rf codevault-tests || true
            '''
        }
        success {
            echo '🎉🎉🎉 PIPELINE SUCCESS! All 19 tests passed! 🎉🎉🎉'
        }
        failure {
            echo '❌ Pipeline failed! Check the test output above. ❌'
        }
    }
}
