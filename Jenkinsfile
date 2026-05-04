pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    environment {
        APP_IMAGE     = "codevault:latest"
        APP_CONTAINER = "codevault-app"
        TEST_REPO     = "https://github.com/janjua911/codevault-tests.git"
        TEST_IMAGE    = "joyzoursky/python-chromedriver:3.9-selenium"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.PUSHER_EMAIL = sh(
                        script: "git log -1 --pretty=format:'%ae'",
                        returnStdout: true
                    ).trim()
                    echo "Push made by: ${env.PUSHER_EMAIL}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${APP_IMAGE} ."
            }
        }

        stage('Run Application') {
            steps {
                sh """
                    docker stop ${APP_CONTAINER} 2>/dev/null || true
                    docker rm   ${APP_CONTAINER} 2>/dev/null || true
                    docker run -d --name ${APP_CONTAINER} --network host ${APP_IMAGE}
                    sleep 8
                """
            }
        }

        stage('Run Selenium Tests') {
            steps {
                sh """
                    # Remove old test-suite if exists (root-owned from Docker)
                    sudo rm -rf test-suite 2>/dev/null || true

                    git clone ${TEST_REPO} test-suite

                    docker run --rm \
                        --network host \
                        -v \$(pwd)/test-suite:/tests \
                        -w /tests \
                        ${TEST_IMAGE} \
                        bash -c "pip install pytest pytest-html --quiet && \
                                 python -m pytest test_codevault.py -v \
                                 --junitxml=results.xml \
                                 --html=report.html --self-contained-html"

                    sudo chown -R jenkins:jenkins test-suite || true
                """
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-suite/results.xml'
                }
            }
        }
    }

    post {
        always {
            sh "docker stop ${APP_CONTAINER} 2>/dev/null || true"
            sh "docker rm   ${APP_CONTAINER} 2>/dev/null || true"
        }
        success {
            emailext(
                to: "${env.PUSHER_EMAIL}",
                subject: "✅ [CodeVault CI] Build #${BUILD_NUMBER} PASSED",
                body: "<h2 style='color:green'>All 21 tests passed!</h2><p>Build: #${BUILD_NUMBER}<br>Pusher: ${env.PUSHER_EMAIL}<br>Duration: ${currentBuild.durationString}</p><p><a href='${BUILD_URL}'>View Build</a></p>",
                mimeType: 'text/html',
                attachmentsPattern: 'test-suite/report.html'
            )
        }
        failure {
            emailext(
                to: "${env.PUSHER_EMAIL}",
                subject: "❌ [CodeVault CI] Build #${BUILD_NUMBER} FAILED",
                body: "<h2 style='color:red'>Pipeline failed!</h2><p>Build: #${BUILD_NUMBER}<br>Pusher: ${env.PUSHER_EMAIL}</p><p><a href='${BUILD_URL}console'>View Console</a></p>",
                mimeType: 'text/html'
            )
        }
    }
}
