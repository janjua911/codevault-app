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
                    docker run -d --name codevault-app -p 8081:5000 codevault:latest
                    sleep 5
                    docker ps | grep codevault
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
                    
                    # Update test file to use port 8081
                    sed -i 's/localhost:5000/localhost:8081/g' test_codevault.py
                    sed -i 's/127.0.0.1:5000/127.0.0.1:8081/g' test_codevault.py
                    
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
