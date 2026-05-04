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
                    docker run -d --name codevault-app -p 5001:5000 codevault:latest
                    sleep 5
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
                    
                    # Update test file to use port 5001
                    cd codevault-tests
                    sed -i 's/localhost:5000/localhost:5002/g' test_codevault.py
                    
                    # Run tests
                    docker run --rm \
                        --network host \
                        -v $PWD:/tests \
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
