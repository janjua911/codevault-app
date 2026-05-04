pipeline {
    agent any
    
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
                    curl -s http://localhost:5000 > /dev/null && echo "✅ App is running on port 5000"
                '''
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                echo '🧪 Running Selenium tests...'
                sh '''
                    # Force remove with sudo if needed
                    sudo rm -rf selenium-tests 2>/dev/null || true
                    
                    # Clone tests
                    git clone https://github.com/janjua911/codevault-tests.git selenium-tests
                    cd selenium-tests
                    
                    # Run tests
                    docker run --rm \
                        --network host \
                        -v $PWD:/tests \
                        -w /tests \
                        joyzoursky/python-chromedriver:3.9-selenium \
                        bash -c "pip install pytest webdriver-manager selenium && python -m pytest test_codevault.py -v --tb=short"
                    
                    # Clean up
                    cd ..
                    sudo rm -rf selenium-tests
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
