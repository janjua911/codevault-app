pipeline {
    agent any
    
    triggers {
        pollSCM('')
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
                    docker stop codevault-app 2>/dev/null || true
                    docker rm codevault-app 2>/dev/null || true
                    docker run -d --name codevault-app --network host codevault:latest
                    sleep 5
                '''
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                echo '🧪 Running Selenium tests...'
                sh '''
                    # Use timestamp to avoid folder conflict
                    TEST_DIR="tests_$(date +%s)"
                    
                    git clone https://github.com/janjua911/codevault-tests.git $TEST_DIR
                    cd $TEST_DIR
                    
                    docker run --rm \
                        --network host \
                        -v $PWD:/tests \
                        -w /tests \
                        joyzoursky/python-chromedriver:3.9-selenium \
                        bash -c "pip install pytest webdriver-manager selenium && python -m pytest test_codevault.py -v"
                    
                    cd ..
                    rm -rf $TEST_DIR
                '''
            }
        }
    }
    
    post {
        always {
            sh 'docker stop codevault-app 2>/dev/null || true'
            sh 'docker rm codevault-app 2>/dev/null || true'
        }
        success {
            echo '🎉✅ PIPELINE SUCCESS! All 19 tests passed! ✅🎉'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}
