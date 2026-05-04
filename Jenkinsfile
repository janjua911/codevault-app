pipeline {
    agent any
    
    environment {
        // Your EC2 public IP (update this)
        EC2_IP = 'YOUR_EC2_PUBLIC_IP'
    }
    
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
                    docker run -d --name codevault-app -p 5000:5000 codevault:latest
                    sleep 5
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running Selenium tests...'
                sh '''
                    # Clone tests repository
                    git clone https://github.com/janjua911/codevault-tests.git
                    
                    # Run tests using Docker
                    docker run --rm \
                        --network host \
                        -v $PWD/codevault-tests:/tests \
                        -w /tests \
                        python:3.9-slim \
                        bash -c "pip install selenium pytest webdriver-manager && pytest test_codevault.py -v --tb=short"
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
