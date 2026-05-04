pipeline {
    agent any

    stages {

        stage('Clean Workspace') {
            steps {
                echo '🧹 Cleaning workspace...'
                cleanWs()
            }
        }

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

                    docker run -d --name codevault-app -p 5000:5000 codevault:latest

                    sleep 5
                    curl -s http://localhost:5000 > /dev/null && echo "✅ App is running"
                '''
            }
        }

        stage('Run Selenium Tests') {
            steps {
                echo '🧪 Running Selenium tests...'
                sh '''
                    docker run --rm --network host python:3.9-slim bash -c "

                    apt-get update && apt-get install -y git wget curl gnupg unzip

                    # Install Chrome
                    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
                    echo 'deb http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google.list

                    apt-get update && apt-get install -y google-chrome-stable

                    pip install selenium pytest webdriver-manager

                    git clone https://github.com/janjua911/codevault-tests.git

                    cd codevault-tests

                    pytest test_codevault.py -v --tb=short
                    "
                '''
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up containers...'
            sh '''
                docker stop codevault-app || true
                docker rm codevault-app || true
            '''
        }

        success {
            echo '🎉🎉🎉 PIPELINE SUCCESS! 🎉🎉🎉'
        }

        failure {
            echo '❌ Pipeline failed! Check logs above ❌'
        }
    }
}
