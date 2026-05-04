pipeline {
    agent any

    environment {
        IMAGE_NAME = "codevault:latest"
        CONTAINER_NAME = "codevault-app"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                git branch: 'master', url: 'https://github.com/janjua911/codevault-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Run Application') {
            steps {
                echo 'Starting Flask app...'
                sh '''
                docker stop $CONTAINER_NAME || true
                docker rm $CONTAINER_NAME || true
                docker run -d --name $CONTAINER_NAME --network host $IMAGE_NAME
                sleep 5
                curl -s http://localhost:5000 || true
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running Selenium tests...'
                sh '''
                rm -rf codevault-tests || true
                git clone https://github.com/janjua911/codevault-tests.git

                docker run --rm \
                -v $(pwd)/codevault-tests:/tests \
                -w /tests \
                --network host \
                python:3.9-slim bash -c "

                apt-get update && apt-get install -y wget gnupg curl unzip

                # ✅ FIXED Chrome install (modern method)
                mkdir -p /etc/apt/keyrings
                curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google.gpg

                echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main' \
                > /etc/apt/sources.list.d/google-chrome.list

                apt-get update
                apt-get install -y google-chrome-stable

                pip install selenium pytest webdriver-manager

                pytest test_codevault.py -v --tb=short
                "
                '''
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh '''
            docker stop $CONTAINER_NAME || true
            docker rm $CONTAINER_NAME || true
            rm -rf codevault-tests || true
            '''
        }

        success {
            echo 'Pipeline passed! ✅'
        }

        failure {
            echo 'Pipeline failed! ❌'
        }
    }
}
