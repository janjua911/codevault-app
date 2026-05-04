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
                    docker run -d --name codevault-app --network host codevault:latest
                    sleep 5
                    curl -s http://localhost:5000 > /dev/null && echo "App is running"
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running Selenium tests...'
                sh '''
                    # Clean up (no sudo)
                    rm -rf codevault-tests || true
                    
                    # Clone tests repository
                    git clone https://github.com/janjua911/codevault-tests.git
                    
                    cd codevault-tests
                    
                    # Run tests using Docker container (no need to install Chrome on host)
                    docker run --rm \
                        -v $PWD:/tests \
                        -w /tests \
                        --network host \
                        python:3.9-slim \
                        bash -c "
                            pip install selenium pytest webdriver-manager
                            apt-get update
                            apt-get install -y wget gnupg
                            wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
                            echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list
                            apt-get update
                            apt-get install -y google-chrome-stable
                            python -m pytest test_codevault.py -v --tb=short
                        "
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
                rm -rf codevault-tests || true
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
