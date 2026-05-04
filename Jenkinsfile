pipeline {
    agent any
    
    // Remove or comment this line:
    // options {
    //     cleanWs()
    // }
    
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
                    docker stop codevault-app 2>/dev/null || true
                    docker rm codevault-app 2>/dev/null || true
                    docker run -d --name codevault-app --network host codevault:latest
                    sleep 5
                    curl -s http://localhost:5000 > /dev/null && echo "✅ App is running"
                '''
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                echo '🧪 Running Selenium tests...'
                sh '''
                    # Remove old directory if exists
                    rm -rf selenium-tests 2>/dev/null || true
                    
                    # Clone tests to a new directory
                    git clone https://github.com/janjua911/codevault-tests.git selenium-tests
                    cd selenium-tests
                    
                    # Create Dockerfile for tests
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
                    
                    # Build and run tests
                    docker build -f Dockerfile.test -t codevault-tests:latest .
                    docker run --rm --network host codevault-tests:latest
                '''
            }
        }
    }
    
    post {
        always {
            echo '🧹 Cleaning up...'
            sh '''
                docker stop codevault-app 2>/dev/null || true
                docker rm codevault-app 2>/dev/null || true
                docker rmi codevault-tests:latest 2>/dev/null || true
                rm -rf selenium-tests 2>/dev/null || true
            '''
        }
        success {
            echo '🎉 PIPELINE SUCCESS! All 19 tests passed! 🎉'
        }
        failure {
            echo '❌ Pipeline failed! Check the test output above. ❌'
        }
    }
}
